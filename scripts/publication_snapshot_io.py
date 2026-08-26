#!/usr/bin/env python3
"""Race-safe publication-surface I/O for UFT-ID scholarly reproduction."""
from __future__ import annotations

import hashlib
import os
import secrets
import shutil
import stat
import struct
from pathlib import Path

SOURCE_ZIP_NAME = "UFT-ID-3.0.0-source.zip"
MAX_OUTER_ZIP_BYTES = 256 * 1024 * 1024
MAX_OUTER_PDF_BYTES = 8 * 1024 * 1024
MAX_OUTER_NOTES_BYTES = 1024 * 1024
MAX_ZIP_MEMBERS = 10000
MAX_EOCD_SCAN_BYTES = 65557
EOCD_SIGNATURE = b"PK\x05\x06"
ZIP64_EOCD_SIGNATURE = b"PK\x06\x06"
ZIP64_LOCATOR_SIGNATURE = b"PK\x06\x07"
CENTRAL_DIRECTORY_SIGNATURE = b"PK\x01\x02"
CENTRAL_DIRECTORY_HEADER = struct.Struct("<4s6H3L5H2L")
PUBLICATION_FILE_NAMES = (
    SOURCE_ZIP_NAME,
    "UFT-ID-v3.0.0-Overview.pdf",
    "RELEASE-NOTES.md",
)
PUBLICATION_SIZE_LIMITS = {
    SOURCE_ZIP_NAME: MAX_OUTER_ZIP_BYTES,
    "UFT-ID-v3.0.0-Overview.pdf": MAX_OUTER_PDF_BYTES,
    "RELEASE-NOTES.md": MAX_OUTER_NOTES_BYTES,
}
VERIFIED_PUBLICATION_FILE_MODE = 0o400
VERIFIED_PUBLICATION_DIR_MODE = 0o500


def regular_open_flags() -> int:
    return os.O_RDONLY | getattr(os, "O_NOFOLLOW", 0) | getattr(os, "O_NONBLOCK", 0)


def hash_regular_fd(fd: int, size: int) -> str:
    h = hashlib.sha256()
    remaining = size
    while remaining:
        chunk = os.read(fd, min(1024 * 1024, remaining))
        if not chunk:
            raise RuntimeError("publication artifact changed size while hashing")
        h.update(chunk)
        remaining -= len(chunk)
    if os.read(fd, 1):
        raise RuntimeError("publication artifact changed size while hashing")
    return h.hexdigest()


def artifact_surface(
    directory: Path,
    names: list[str],
    *,
    expected_sizes: dict[str, int] | None = None,
) -> dict[str, dict[str, object]]:
    directory = directory.resolve()
    expected_names = sorted(names)
    observed: list[str] = []
    dir_fd = os.open(directory, os.O_RDONLY | getattr(os, "O_DIRECTORY", 0))
    try:
        with os.scandir(dir_fd) as entries:
            for entry in entries:
                observed.append(entry.name)
                if len(observed) > len(names):
                    raise RuntimeError(
                        f"publication surface drift: expected {expected_names}, "
                        f"got more than {len(names)} entries"
                    )
        if sorted(observed) != expected_names:
            raise RuntimeError(
                f"publication surface drift: expected {expected_names}, got {sorted(observed)}"
            )

        result: dict[str, dict[str, object]] = {}
        for name in names:
            limit = PUBLICATION_SIZE_LIMITS.get(name)
            if limit is None:
                raise RuntimeError(f"publication artifact has no size policy: {name}")
            try:
                fd = os.open(name, regular_open_flags(), dir_fd=dir_fd)
            except OSError as exc:
                raise RuntimeError(f"could not safely open publication artifact: {name}") from exc
            try:
                st = os.fstat(fd)
                if not stat.S_ISREG(st.st_mode):
                    raise RuntimeError(f"publication artifact is not a regular file: {name}")
                if st.st_size > limit:
                    raise RuntimeError(f"publication artifact exceeds size bound: {name}")
                if expected_sizes is not None and st.st_size != expected_sizes[name]:
                    raise RuntimeError(
                        f"publication artifact does not match canonical authority size: {name}"
                    )
                digest = hash_regular_fd(fd, st.st_size)
            finally:
                os.close(fd)
            result[name] = {"bytes": st.st_size, "sha256": digest}
        return result
    finally:
        os.close(dir_fd)


def bounded_zip_member_count(path: Path, *, max_members: int = MAX_ZIP_MEMBERS) -> int:
    """Parse and bound one ZIP central directory from the same nonblocking fd."""
    try:
        fd = os.open(Path(path), regular_open_flags())
    except OSError as exc:
        raise RuntimeError("could not safely open source ZIP for preflight") from exc
    try:
        st = os.fstat(fd)
        size = st.st_size
        if not stat.S_ISREG(st.st_mode):
            raise RuntimeError("source ZIP is not a regular file")
        if size > MAX_OUTER_ZIP_BYTES:
            raise RuntimeError("source ZIP exceeds outer size bound")
        if size < 22:
            raise RuntimeError("source ZIP is too short to contain an EOCD record")

        scan = min(size, MAX_EOCD_SCAN_BYTES)
        tail_start = size - scan
        tail = os.pread(fd, scan, tail_start)
        if len(tail) != scan:
            raise RuntimeError("source ZIP changed while reading EOCD")
        tail_offset = tail.rfind(EOCD_SIGNATURE)
        if tail_offset < 0 or tail_offset + 22 > len(tail):
            raise RuntimeError("source ZIP EOCD record missing")
        eocd_offset = tail_start + tail_offset

        if eocd_offset >= 20 and os.pread(fd, 4, eocd_offset - 20) == ZIP64_LOCATOR_SIGNATURE:
            raise RuntimeError("ZIP64 locator is forbidden")
        if ZIP64_EOCD_SIGNATURE in tail[:tail_offset]:
            raise RuntimeError("ZIP64 EOCD record is forbidden")

        (
            signature,
            disk_number,
            central_directory_disk,
            entries_on_disk,
            total_entries,
            central_directory_bytes,
            central_directory_offset,
            comment_length,
        ) = struct.unpack_from("<4s4H2LH", tail, tail_offset)
        if signature != EOCD_SIGNATURE:
            raise RuntimeError("source ZIP EOCD signature mismatch")
        if disk_number != 0 or central_directory_disk != 0 or entries_on_disk != total_entries:
            raise RuntimeError("multi-disk ZIP archives are forbidden")
        if (
            total_entries == 0xFFFF
            or central_directory_bytes == 0xFFFFFFFF
            or central_directory_offset == 0xFFFFFFFF
        ):
            raise RuntimeError("ZIP64 member enumeration is forbidden")
        if tail_offset + 22 + comment_length != len(tail):
            raise RuntimeError("source ZIP EOCD/comment length drift")
        if total_entries == 0 or total_entries > max_members:
            raise RuntimeError("source ZIP member count outside allowed bounds")
        if central_directory_offset >= eocd_offset:
            raise RuntimeError("source ZIP central-directory bounds drift")
        if central_directory_offset + central_directory_bytes != eocd_offset:
            raise RuntimeError("source ZIP central-directory bounds drift")

        observed = 0
        cursor = central_directory_offset
        remaining = central_directory_bytes
        while remaining:
            if remaining < CENTRAL_DIRECTORY_HEADER.size:
                raise RuntimeError("truncated source ZIP central-directory record")
            header = os.pread(fd, CENTRAL_DIRECTORY_HEADER.size, cursor)
            if len(header) != CENTRAL_DIRECTORY_HEADER.size:
                raise RuntimeError("truncated source ZIP central-directory header")
            (
                record_signature,
                _made_by,
                _needed,
                _flags,
                _compression,
                _mtime,
                _mdate,
                _crc,
                compressed_size,
                uncompressed_size,
                filename_length,
                extra_length,
                record_comment_length,
                disk_start,
                _internal_attributes,
                _external_attributes,
                local_header_offset,
            ) = CENTRAL_DIRECTORY_HEADER.unpack(header)
            if record_signature != CENTRAL_DIRECTORY_SIGNATURE:
                raise RuntimeError("invalid source ZIP central-directory record")
            if disk_start != 0:
                raise RuntimeError("multi-disk ZIP member is forbidden")
            if (
                compressed_size == 0xFFFFFFFF
                or uncompressed_size == 0xFFFFFFFF
                or local_header_offset == 0xFFFFFFFF
            ):
                raise RuntimeError("ZIP64 central-directory member is forbidden")
            record_size = (
                CENTRAL_DIRECTORY_HEADER.size
                + filename_length
                + extra_length
                + record_comment_length
            )
            if record_size > remaining:
                raise RuntimeError("source ZIP central-directory record exceeds bounds")
            cursor += record_size
            remaining -= record_size
            observed += 1
            if observed > max_members:
                raise RuntimeError("source ZIP member count outside allowed bounds")

        if observed == 0:
            raise RuntimeError("source ZIP member count outside allowed bounds")
        if observed != total_entries:
            raise RuntimeError("source ZIP central-directory member count disagrees with EOCD")
        return observed
    finally:
        os.close(fd)


def require_exact_artifact_digests(
    observed: dict[str, dict[str, object]],
    canonical: dict[str, dict[str, object]],
) -> None:
    if set(observed) != set(canonical):
        raise RuntimeError("publication artifact inventory does not match canonical authority bytes")
    for name in sorted(canonical):
        if (
            observed[name].get("bytes") != canonical[name].get("bytes")
            or observed[name].get("sha256") != canonical[name].get("sha256")
        ):
            raise RuntimeError(f"publication artifact does not match canonical authority bytes: {name}")


def reject_output_alias(directory: Path, output: Path) -> None:
    root = directory.resolve()
    resolved = output.resolve(strict=False)
    try:
        resolved.relative_to(root)
    except ValueError:
        pass
    else:
        raise RuntimeError(
            "reproduction output must be outside protected publication directory: "
            f"{resolved}"
        )
    try:
        output_stat = resolved.stat()
    except FileNotFoundError:
        return
    for name in PUBLICATION_FILE_NAMES:
        protected = root / name
        try:
            protected_stat = protected.stat()
        except FileNotFoundError:
            continue
        if os.path.samestat(output_stat, protected_stat):
            raise RuntimeError(
                "reproduction output hard-link aliases protected publication artifact: "
                f"{name}"
            )


def _reject_destination_at_write_time(parent_fd: int, name: str, roots: list[Path]) -> None:
    try:
        st = os.stat(name, dir_fd=parent_fd, follow_symlinks=False)
    except FileNotFoundError:
        return
    if stat.S_ISLNK(st.st_mode):
        raise RuntimeError("reproduction output destination became a symlink")
    if not stat.S_ISREG(st.st_mode):
        raise RuntimeError("reproduction output destination is not a regular file")
    for root in roots:
        for publication_name in PUBLICATION_FILE_NAMES:
            protected = root / publication_name
            try:
                protected_stat = protected.stat()
            except FileNotFoundError:
                continue
            if os.path.samestat(st, protected_stat):
                raise RuntimeError(
                    "reproduction output hard-link aliases protected publication artifact: "
                    f"{publication_name}"
                )


def safe_atomic_write(
    path: Path,
    data: bytes,
    *,
    publication_root: Path,
    additional_publication_roots: tuple[Path, ...] | list[Path] = (),
) -> None:
    roots = [publication_root.resolve()]
    for candidate in additional_publication_roots:
        resolved = candidate.resolve(strict=False)
        if resolved not in roots:
            roots.append(resolved)
    path = path.resolve(strict=False)
    for root in roots:
        reject_output_alias(root, path)
    path.parent.mkdir(parents=True, exist_ok=True)
    parent = path.parent.resolve()
    name = path.name
    if not name or name in {".", ".."}:
        raise RuntimeError("invalid reproduction output filename")

    dir_fd = os.open(parent, os.O_RDONLY | getattr(os, "O_DIRECTORY", 0))
    temp_name = f".{name}.tmp.{os.getpid()}.{secrets.token_hex(8)}"
    temp_fd: int | None = None
    try:
        _reject_destination_at_write_time(dir_fd, name, roots)
        flags = os.O_WRONLY | os.O_CREAT | os.O_EXCL | getattr(os, "O_NOFOLLOW", 0)
        temp_fd = os.open(temp_name, flags, 0o600, dir_fd=dir_fd)
        view = memoryview(data)
        written = 0
        while written < len(view):
            count = os.write(temp_fd, view[written:])
            if count <= 0:
                raise RuntimeError("could not write reproduction output")
            written += count
        os.fsync(temp_fd)
        os.close(temp_fd)
        temp_fd = None
        _reject_destination_at_write_time(dir_fd, name, roots)
        os.replace(temp_name, name, src_dir_fd=dir_fd, dst_dir_fd=dir_fd)
        os.fsync(dir_fd)
    finally:
        if temp_fd is not None:
            os.close(temp_fd)
        try:
            os.unlink(temp_name, dir_fd=dir_fd)
        except FileNotFoundError:
            pass
        os.close(dir_fd)


def materialize_verified_publication(
    canonical_root: Path,
    destination: Path,
    names: list[str],
    canonical: dict[str, dict[str, object]],
) -> dict[str, dict[str, object]]:
    destination = destination.resolve(strict=False)
    destination.parent.mkdir(parents=True, exist_ok=True)
    try:
        os.lstat(destination)
    except FileNotFoundError:
        pass
    else:
        raise RuntimeError("verified publication output directory must not already exist")
    destination.mkdir(mode=0o700)
    try:
        src_fd = os.open(canonical_root, os.O_RDONLY | getattr(os, "O_DIRECTORY", 0))
        dst_fd = os.open(destination, os.O_RDONLY | getattr(os, "O_DIRECTORY", 0))
        try:
            for name in names:
                src = os.open(name, regular_open_flags(), dir_fd=src_fd)
                dst: int | None = None
                try:
                    st = os.fstat(src)
                    if not stat.S_ISREG(st.st_mode):
                        raise RuntimeError(f"canonical publication member is not regular: {name}")
                    if st.st_size != int(canonical[name]["bytes"]):
                        raise RuntimeError(f"canonical publication member size drift: {name}")
                    flags = os.O_WRONLY | os.O_CREAT | os.O_EXCL | getattr(os, "O_NOFOLLOW", 0)
                    dst = os.open(name, flags, 0o600, dir_fd=dst_fd)
                    h = hashlib.sha256()
                    remaining = st.st_size
                    while remaining:
                        chunk = os.read(src, min(1024 * 1024, remaining))
                        if not chunk:
                            raise RuntimeError(f"canonical publication member changed size: {name}")
                        h.update(chunk)
                        view = memoryview(chunk)
                        written = 0
                        while written < len(view):
                            count = os.write(dst, view[written:])
                            if count <= 0:
                                raise RuntimeError(f"could not retain publication member: {name}")
                            written += count
                        remaining -= len(chunk)
                    if os.read(src, 1):
                        raise RuntimeError(f"canonical publication member changed size: {name}")
                    if h.hexdigest() != canonical[name]["sha256"]:
                        raise RuntimeError(f"canonical publication member digest drift: {name}")
                    os.fsync(dst)
                    os.fchmod(dst, VERIFIED_PUBLICATION_FILE_MODE)
                finally:
                    os.close(src)
                    if dst is not None:
                        os.close(dst)
            os.fsync(dst_fd)
        finally:
            os.close(src_fd)
            os.close(dst_fd)
        os.chmod(destination, VERIFIED_PUBLICATION_DIR_MODE)
        retained = artifact_surface(
            destination,
            names,
            expected_sizes={name: int(canonical[name]["bytes"]) for name in names},
        )
        require_exact_artifact_digests(retained, canonical)
        return retained
    except Exception:
        try:
            os.chmod(destination, 0o700)
            for child in destination.iterdir():
                try:
                    child.chmod(0o600)
                except OSError:
                    pass
            shutil.rmtree(destination)
        except OSError:
            pass
        raise
