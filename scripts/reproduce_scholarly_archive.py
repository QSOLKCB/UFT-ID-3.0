#!/usr/bin/env python3
"""Reconstruct and verify the archived Lean layer in an isolated directory."""
from __future__ import annotations

import argparse
import hashlib
import json
import math
import os
import re
import secrets
import stat
import struct
import subprocess
import sys
import tempfile
import zipfile
from pathlib import Path, PurePosixPath

ROOT = Path(__file__).resolve().parents[1]
CONTRACT_PATH = ROOT / "machine/scholarly_archive_reproduction_contract.json"
SOURCE_ZIP_NAME = "UFT-ID-3.0.0-source.zip"
MAX_FORMAL_FILE_BYTES = 64 * 1024 * 1024
MAX_FORMAL_TOTAL_BYTES = 256 * 1024 * 1024
MAX_OUTER_ZIP_BYTES = 256 * 1024 * 1024
MAX_OUTER_PDF_BYTES = 8 * 1024 * 1024
MAX_OUTER_NOTES_BYTES = 1024 * 1024
MAX_EVIDENCE_BYTES = 4 * 1024 * 1024
MAX_ZIP_MEMBERS = 10000
MAX_EOCD_SCAN_BYTES = 65557
EXPECTED_MODE = 0o100644
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


def reject_duplicates(pairs):
    value = {}
    for key, item in pairs:
        if key in value:
            raise ValueError(f"duplicate JSON object key: {key}")
        value[key] = item
    return value


def reject_constant(token: str):
    raise ValueError(f"non-finite JSON number: {token}")


def finite_float(token: str) -> float:
    value = float(token)
    if not math.isfinite(value):
        raise ValueError(f"non-finite JSON number: {token}")
    return value


def load_json_bytes(data: bytes, label: str) -> dict[str, object]:
    try:
        text = data.decode("utf-8")
    except UnicodeDecodeError as exc:
        raise RuntimeError(f"{label} is not UTF-8") from exc
    value = json.loads(
        text,
        object_pairs_hook=reject_duplicates,
        parse_constant=reject_constant,
        parse_float=finite_float,
    )
    if not isinstance(value, dict):
        raise RuntimeError(f"{label} must be a JSON object")
    return value


def load_contract() -> dict[str, object]:
    return load_json_bytes(CONTRACT_PATH.read_bytes(), str(CONTRACT_PATH.relative_to(ROOT)))


def sha256_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def sha256_file(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as fh:
        for chunk in iter(lambda: fh.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def bounded_read_bytes(path: Path, limit: int, *, label: str) -> bytes:
    size = path.stat().st_size
    if size > limit:
        raise RuntimeError(f"{label} exceeds size bound")
    with path.open("rb") as fh:
        data = fh.read(limit + 1)
    if len(data) != size or len(data) > limit:
        raise RuntimeError(f"{label} exceeds size bound")
    return data


def run_git(*args: str) -> str:
    cp = subprocess.run(
        ["git", *args],
        cwd=ROOT,
        check=True,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
    )
    return cp.stdout.strip()


def canonical_member(name: str) -> PurePosixPath:
    if not name or "\\" in name or "\x00" in name:
        raise RuntimeError(f"unsafe ZIP path: {name!r}")
    path = PurePosixPath(name)
    if path.is_absolute() or not path.parts or ".." in path.parts:
        raise RuntimeError(f"unsafe ZIP path: {name}")
    if path.as_posix() != name:
        raise RuntimeError(f"non-canonical ZIP path: {name}")
    return path


def bounded_zip_member_count(path: Path) -> int:
    size = path.stat().st_size
    if size > MAX_OUTER_ZIP_BYTES:
        raise RuntimeError("source ZIP exceeds outer size bound")
    if size < 22:
        raise RuntimeError("source ZIP is too short to contain an EOCD record")

    with path.open("rb") as fh:
        scan = min(size, MAX_EOCD_SCAN_BYTES)
        fh.seek(size - scan)
        tail = fh.read(scan)

    tail_offset = tail.rfind(EOCD_SIGNATURE)
    if tail_offset < 0 or tail_offset + 22 > len(tail):
        raise RuntimeError("source ZIP EOCD record missing")
    eocd_offset = size - scan + tail_offset

    if eocd_offset >= 20:
        with path.open("rb") as fh:
            fh.seek(eocd_offset - 20)
            if fh.read(4) == ZIP64_LOCATOR_SIGNATURE:
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
    if total_entries == 0 or total_entries > MAX_ZIP_MEMBERS:
        raise RuntimeError("source ZIP member count outside allowed bounds")

    central_directory_end = central_directory_offset + central_directory_bytes
    if central_directory_offset >= eocd_offset or central_directory_end != eocd_offset:
        raise RuntimeError("source ZIP central-directory bounds drift")

    observed_entries = 0
    with path.open("rb") as fh:
        fh.seek(central_directory_offset)
        remaining = central_directory_bytes
        while remaining:
            if remaining < CENTRAL_DIRECTORY_HEADER.size:
                raise RuntimeError("truncated source ZIP central-directory record")
            header = fh.read(CENTRAL_DIRECTORY_HEADER.size)
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
                comment_length,
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
                + comment_length
            )
            if record_size > remaining:
                raise RuntimeError("source ZIP central-directory record exceeds bounds")
            fh.seek(record_size - CENTRAL_DIRECTORY_HEADER.size, os.SEEK_CUR)
            remaining -= record_size
            observed_entries += 1
            if observed_entries > MAX_ZIP_MEMBERS:
                raise RuntimeError("source ZIP member count outside allowed bounds")

    if observed_entries == 0:
        raise RuntimeError("source ZIP member count outside allowed bounds")
    if observed_entries != total_entries:
        raise RuntimeError("source ZIP central-directory member count disagrees with EOCD")
    return observed_entries


def extract_formal_layer(source_zip: Path, destination: Path) -> list[str]:
    expected_members = bounded_zip_member_count(source_zip)
    extracted: list[str] = []
    total = 0
    seen: set[str] = set()
    required = {
        "lean-toolchain",
        "lakefile.toml",
        "UFTID.lean",
        "machine/lean_observation_verification.json",
        "scripts/verify_lean_observation_axioms.py",
    }

    with zipfile.ZipFile(source_zip, "r") as zf:
        infos = zf.infolist()
        if len(infos) != expected_members:
            raise RuntimeError("source ZIP member-count metadata drift")
        for info in infos:
            path = canonical_member(info.filename)
            if path.parts[0] != "formal":
                continue
            if info.is_dir():
                raise RuntimeError(f"directory entry forbidden in formal archive layer: {info.filename}")
            rel = PurePosixPath(*path.parts[1:])
            if not rel.parts:
                raise RuntimeError("empty formal-layer member")
            rel_name = rel.as_posix()
            if rel_name in seen:
                raise RuntimeError(f"duplicate formal-layer member: {rel_name}")
            seen.add(rel_name)

            mode = (info.external_attr >> 16) & 0o177777
            if mode != EXPECTED_MODE or stat.S_IFMT(mode) != stat.S_IFREG:
                raise RuntimeError(f"formal-layer member is not canonical regular file: {rel_name}")
            if info.file_size > MAX_FORMAL_FILE_BYTES:
                raise RuntimeError(f"formal-layer member exceeds size bound: {rel_name}")
            total += info.file_size
            if total > MAX_FORMAL_TOTAL_BYTES:
                raise RuntimeError("formal layer exceeds total expanded-size bound")

            data = zf.read(info)
            if len(data) != info.file_size:
                raise RuntimeError(f"formal-layer size mismatch: {rel_name}")
            target = destination.joinpath(*rel.parts)
            target.parent.mkdir(parents=True, exist_ok=True)
            target.write_bytes(data)
            extracted.append(rel_name)

    missing = sorted(required - set(extracted))
    if missing:
        raise RuntimeError(f"formal layer missing required authority files: {missing}")
    return sorted(extracted, key=lambda value: PurePosixPath(value).parts)


def run_checked(
    command: list[str],
    cwd: Path,
    *,
    env: dict[str, str] | None = None,
) -> str:
    proc = subprocess.run(
        command,
        cwd=cwd,
        env=env,
        check=False,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
    )
    if proc.returncode != 0:
        raise RuntimeError(
            f"command failed ({proc.returncode}): {' '.join(command)}\n"
            + proc.stdout
            + ("\n" + proc.stderr if proc.stderr else "")
        )
    return proc.stdout.strip()


def _hash_regular_fd(fd: int, size: int) -> str:
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
    dir_flags = os.O_RDONLY | getattr(os, "O_DIRECTORY", 0)
    dir_fd = os.open(directory, dir_flags)
    try:
        with os.scandir(dir_fd) as entries:
            for entry in entries:
                observed.append(entry.name)
                if len(observed) > len(names):
                    raise RuntimeError(
                        f"publication surface drift: expected {expected_names}, got more than {len(names)} entries"
                    )
        if sorted(observed) != expected_names:
            raise RuntimeError(f"publication surface drift: expected {expected_names}, got {sorted(observed)}")

        result: dict[str, dict[str, object]] = {}
        nofollow = getattr(os, "O_NOFOLLOW", 0)
        for name in names:
            limit = PUBLICATION_SIZE_LIMITS.get(name)
            if limit is None:
                raise RuntimeError(f"publication artifact has no size policy: {name}")
            fd = os.open(name, os.O_RDONLY | nofollow, dir_fd=dir_fd)
            try:
                st = os.fstat(fd)
                if not stat.S_ISREG(st.st_mode):
                    raise RuntimeError(f"publication artifact is not a regular file: {name}")
                if st.st_size > limit:
                    raise RuntimeError(f"publication artifact exceeds size bound: {name}")
                if expected_sizes is not None and st.st_size != expected_sizes[name]:
                    raise RuntimeError(f"publication artifact does not match canonical authority size: {name}")
                digest = _hash_regular_fd(fd, st.st_size)
            finally:
                os.close(fd)
            result[name] = {"bytes": st.st_size, "sha256": digest}
        return result
    finally:
        os.close(dir_fd)


def reject_publication_output_aliases(directory: Path, output: Path) -> None:
    publication_root = directory.resolve()
    resolved = output.resolve()
    try:
        resolved.relative_to(publication_root)
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
        protected = publication_root / name
        try:
            protected_stat = protected.stat()
        except FileNotFoundError:
            continue
        if os.path.samestat(output_stat, protected_stat):
            raise RuntimeError(
                "reproduction output hard-link aliases protected publication artifact: "
                f"{name}"
            )


def reject_evidence_output_aliases(json_out: Path, axiom_json_out: Path) -> None:
    first = json_out.resolve()
    second = axiom_json_out.resolve()
    if first == second:
        raise RuntimeError("reproduction evidence outputs must be distinct files")
    try:
        first_stat = first.stat()
        second_stat = second.stat()
    except FileNotFoundError:
        return
    if os.path.samestat(first_stat, second_stat):
        raise RuntimeError("reproduction evidence outputs must not hard-link alias each other")


def _reject_destination_at_write_time(
    parent_fd: int,
    name: str,
    publication_root: Path,
) -> None:
    try:
        st = os.stat(name, dir_fd=parent_fd, follow_symlinks=False)
    except FileNotFoundError:
        return
    if stat.S_ISLNK(st.st_mode):
        raise RuntimeError("reproduction output destination became a symlink")
    if not stat.S_ISREG(st.st_mode):
        raise RuntimeError("reproduction output destination is not a regular file")
    for publication_name in PUBLICATION_FILE_NAMES:
        protected = publication_root / publication_name
        try:
            protected_stat = protected.stat()
        except FileNotFoundError:
            continue
        if os.path.samestat(st, protected_stat):
            raise RuntimeError(
                "reproduction output hard-link aliases protected publication artifact: "
                f"{publication_name}"
            )


def safe_atomic_write(path: Path, data: bytes, *, publication_root: Path) -> None:
    publication_root = publication_root.resolve()
    path = path.resolve(strict=False)
    reject_publication_output_aliases(publication_root, path)
    path.parent.mkdir(parents=True, exist_ok=True)
    parent = path.parent.resolve()
    name = path.name
    if not name or name in {".", ".."}:
        raise RuntimeError("invalid reproduction output filename")

    dir_flags = os.O_RDONLY | getattr(os, "O_DIRECTORY", 0)
    dir_fd = os.open(parent, dir_flags)
    temp_name = f".{name}.tmp.{os.getpid()}.{secrets.token_hex(8)}"
    temp_fd: int | None = None
    try:
        _reject_destination_at_write_time(dir_fd, name, publication_root)
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

        _reject_destination_at_write_time(dir_fd, name, publication_root)
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


def revalidate_publication_surface(
    directory: Path,
    names: list[str],
    canonical: dict[str, dict[str, object]],
) -> dict[str, dict[str, object]]:
    expected_sizes = {name: int(canonical[name]["bytes"]) for name in names}
    observed = artifact_surface(directory, names, expected_sizes=expected_sizes)
    require_exact_artifact_digests(observed, canonical)
    return observed


def authenticate_publication_surface(
    directory: Path,
    expected_commit: str,
    exact_files: list[str] | None = None,
) -> dict[str, object]:
    """Bind supplied bytes to a trusted detached canonical rebuild before execution."""
    contract = load_contract()
    surface = contract.get("publication_surface")
    if not isinstance(surface, dict):
        raise RuntimeError("reproduction publication surface malformed")
    contract_files = [str(value) for value in surface.get("exact_files", [])]
    names = contract_files if exact_files is None else [str(value) for value in exact_files]
    if not names or names != contract_files:
        raise RuntimeError("publication surface file list does not match reproduction contract")
    if SOURCE_ZIP_NAME not in names:
        raise RuntimeError("reproduction publication surface is missing the source ZIP")

    directory = directory.resolve()
    supplied = artifact_surface(directory, names)
    bounded_zip_member_count(directory / SOURCE_ZIP_NAME)

    with tempfile.TemporaryDirectory(prefix="uft-id-publication-authority-") as temporary:
        temporary_root = Path(temporary)
        authority_root = temporary_root / "authority"
        canonical_root = temporary_root / "canonical"
        canonical_root.mkdir()
        add = subprocess.run(
            ["git", "worktree", "add", "--detach", str(authority_root), expected_commit],
            cwd=ROOT,
            text=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            check=False,
        )
        if add.returncode != 0:
            raise RuntimeError(
                "could not create detached publication authority worktree:\n"
                + add.stdout
                + ("\n" + add.stderr if add.stderr else "")
            )
        try:
            builder = authority_root / "scripts/build_scholarly_archive.py"
            build = subprocess.run(
                [sys.executable, str(builder), "--output", str(canonical_root), "--json"],
                cwd=authority_root,
                text=True,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                check=False,
            )
            if build.returncode != 0:
                raise RuntimeError(
                    "detached publication authority could not rebuild canonical bytes:\n"
                    + build.stdout
                    + ("\n" + build.stderr if build.stderr else "")
                )
            canonical = artifact_surface(canonical_root, names)
            expected_sizes = {name: int(canonical[name]["bytes"]) for name in names}
            supplied = artifact_surface(directory, names, expected_sizes=expected_sizes)
            require_exact_artifact_digests(supplied, canonical)

            verifier = authority_root / "scripts/verify_scholarly_archive.py"
            proc = subprocess.run(
                [sys.executable, str(verifier), str(directory), "--json"],
                cwd=authority_root,
                text=True,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                check=False,
            )
            if proc.returncode != 0:
                raise RuntimeError(
                    "detached publication authority rejected supplied archive bytes:\n"
                    + proc.stdout
                    + ("\n" + proc.stderr if proc.stderr else "")
                )
            report = load_json_bytes(
                proc.stdout.encode("utf-8"),
                "detached publication authority verification",
            )
            if report.get("status") != "ok":
                raise RuntimeError("detached publication authority verification did not report ok")
            verified = report.get("artifacts")
            if not isinstance(verified, dict):
                raise RuntimeError("detached publication authority omitted artifact digests")
            for name in names:
                if verified.get(name) != canonical[name]["sha256"]:
                    raise RuntimeError(
                        "detached publication authority digest disagrees with canonical authority bytes: "
                        f"{name}"
                    )
            return {
                "status": "ok",
                "artifacts": {name: canonical[name]["sha256"] for name in names},
                "artifact_metadata": canonical,
            }
        finally:
            subprocess.run(
                ["git", "worktree", "remove", "--force", str(authority_root)],
                cwd=ROOT,
                text=True,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                check=False,
            )


def validate_runtime_toolchain(
    lean_version_output: str,
    lake_version_output: str,
    toolchain: dict[str, object],
) -> None:
    expected_lean = str(toolchain["lean"])
    expected_lake = str(toolchain["lake"])
    lean_match = re.search(r"Lean \(version ([^, )]+)", lean_version_output)
    if lean_match is None:
        raise RuntimeError("could not parse runtime Lean version")
    observed_lean = f"v{lean_match.group(1)}"
    if observed_lean != expected_lean:
        raise RuntimeError(
            f"runtime Lean version mismatch: expected {expected_lean}, got {observed_lean}"
        )
    lake_match = re.search(
        r"Lake version ([^ ]+) \(Lean version ([^)]+)\)",
        lake_version_output,
    )
    if lake_match is None:
        raise RuntimeError("could not parse runtime Lake version")
    observed_lake = lake_match.group(1)
    observed_lake_lean = f"v{lake_match.group(2)}"
    if observed_lake != expected_lake:
        raise RuntimeError(
            f"runtime Lake version mismatch: expected {expected_lake}, got {observed_lake}"
        )
    if observed_lake_lean != expected_lean:
        raise RuntimeError(
            "runtime Lake/Lean pairing mismatch: "
            f"expected {expected_lean}, got {observed_lake_lean}"
        )


def reproduce(
    directory: Path,
    *,
    lake: str,
    publication_source_commit: str,
    axiom_json_out: Path,
) -> dict[str, object]:
    directory = directory.resolve()
    axiom_json_out = axiom_json_out.resolve(strict=False)
    reject_publication_output_aliases(directory, axiom_json_out)

    contract = load_contract()
    expected_source = contract["publication_source"]
    surface = contract["publication_surface"]
    toolchain = contract["lean_toolchain"]
    if not isinstance(expected_source, dict) or not isinstance(surface, dict) or not isinstance(toolchain, dict):
        raise RuntimeError("reproduction contract sections malformed")

    expected_commit = str(expected_source["merge_commit"])
    if publication_source_commit != expected_commit:
        raise RuntimeError("publication source commit does not match reproduction contract")
    if run_git("rev-parse", f"{expected_commit}^{{commit}}") != expected_commit:
        raise RuntimeError("publication source commit unavailable")
    if run_git("rev-parse", f"{expected_commit}^{{tree}}") != str(expected_source["merge_tree"]):
        raise RuntimeError("publication source tree drift")

    exact_files = [str(value) for value in surface["exact_files"]]
    authority_verification = authenticate_publication_surface(directory, expected_commit, exact_files)
    verified_artifacts = authority_verification.get("artifacts")
    canonical_metadata = authority_verification.get("artifact_metadata")
    if not isinstance(verified_artifacts, dict) or not isinstance(canonical_metadata, dict):
        raise RuntimeError("detached publication authority omitted canonical artifact metadata")

    source_zip = directory / SOURCE_ZIP_NAME
    axiom_bytes = b""
    with tempfile.TemporaryDirectory(prefix="uft-id-publication-formal-") as temporary:
        isolated = Path(temporary)
        members = extract_formal_layer(source_zip, isolated)

        lake_path = Path(lake).resolve()
        if not lake_path.is_file():
            raise RuntimeError("pinned Lake executable is missing")
        lean_path = lake_path.parent / "lean"
        if not lean_path.is_file():
            raise RuntimeError("pinned Lean executable beside Lake is missing")

        toolchain_env = os.environ.copy()
        prior_path = toolchain_env.get("PATH", "")
        toolchain_env["PATH"] = (
            str(lake_path.parent)
            if not prior_path
            else str(lake_path.parent) + os.pathsep + prior_path
        )

        lake_version = run_checked([str(lake_path), "--version"], isolated, env=toolchain_env)
        lean_version = run_checked([str(lean_path), "--version"], isolated, env=toolchain_env)
        validate_runtime_toolchain(lean_version, lake_version, toolchain)
        run_checked([str(lake_path), "update"], isolated, env=toolchain_env)
        run_checked([str(lake_path), "exe", "cache", "get"], isolated, env=toolchain_env)
        build_output = run_checked([str(lake_path), "build", "UFTID"], isolated, env=toolchain_env)

        internal_axiom_out = isolated / ".publication-axiom-report.json"
        run_checked(
            [
                sys.executable,
                "scripts/verify_lean_observation_axioms.py",
                "--lake",
                str(lake_path),
                "--json-out",
                str(internal_axiom_out),
            ],
            isolated,
            env=toolchain_env,
        )
        axiom_bytes = bounded_read_bytes(
            internal_axiom_out,
            MAX_EVIDENCE_BYTES,
            label="isolated archived axiom audit",
        )
        axiom_report = load_json_bytes(axiom_bytes, internal_axiom_out.name)
        if axiom_report.get("status") != "ok":
            raise RuntimeError("isolated archived axiom audit did not report ok")
        verification_bytes = bounded_read_bytes(
            isolated / "machine/lean_observation_verification.json",
            MAX_EVIDENCE_BYTES,
            label="archived Lean verification record",
        )
        verification_record = load_json_bytes(
            verification_bytes,
            "archived Lean verification record",
        )
        if verification_record.get("status") != "LEAN_VERIFIED":
            raise RuntimeError("isolated archived verification record is not LEAN_VERIFIED")
        record_toolchain = verification_record.get("toolchain")
        if not isinstance(record_toolchain, dict):
            raise RuntimeError("isolated archived verification toolchain record malformed")
        if record_toolchain.get("lean") != toolchain["lean"]:
            raise RuntimeError("isolated archived Lean version disagrees with reproduction contract")
        if record_toolchain.get("lake") != toolchain["lake"]:
            raise RuntimeError("isolated archived Lake version disagrees with reproduction contract")
        if record_toolchain.get("mathlib_commit") != toolchain["mathlib_commit"]:
            raise RuntimeError("isolated archived mathlib revision disagrees with reproduction contract")

    final_artifacts = revalidate_publication_surface(
        directory, exact_files, canonical_metadata
    )

    safe_atomic_write(axiom_json_out, axiom_bytes, publication_root=directory)
    final_artifacts = revalidate_publication_surface(
        directory, exact_files, canonical_metadata
    )

    return {
        "type": "uft-id-scholarly-archive-reproduction",
        "schema_version": "1.0.0",
        "status": "ok",
        "doi": contract["doi"],
        "version": contract["version"],
        "publication_source": {
            "commit": expected_commit,
            "tree": expected_source["merge_tree"],
        },
        "artifacts": final_artifacts,
        "authority_verification": {
            "status": authority_verification["status"],
            "artifacts": verified_artifacts,
        },
        "isolated_formal_layer": {
            "member_count": len(members),
            "lean_version_output": lean_version,
            "lake_version_output": lake_version,
            "build_result": "success",
            "build_output_tail": build_output[-1000:],
            "axiom_audit_status": axiom_report["status"],
            "axiom_audit_sha256": sha256_bytes(axiom_bytes),
            "observed_axioms_by_theorem": axiom_report.get("observed_axioms_by_theorem"),
        },
        "boundaries": contract["hard_boundaries"],
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("directory", type=Path)
    parser.add_argument("--lake", required=True)
    parser.add_argument("--publication-source-commit", required=True)
    parser.add_argument("--json-out", type=Path, required=True)
    parser.add_argument("--axiom-json-out", type=Path, required=True)
    args = parser.parse_args()

    directory = args.directory.resolve()
    json_out = args.json_out.resolve(strict=False)
    axiom_json_out = args.axiom_json_out.resolve(strict=False)

    try:
        reject_publication_output_aliases(directory, json_out)
        reject_publication_output_aliases(directory, axiom_json_out)
        reject_evidence_output_aliases(json_out, axiom_json_out)
    except (OSError, RuntimeError, ValueError) as exc:
        print(exc)
        return 1

    try:
        report = reproduce(
            directory,
            lake=args.lake,
            publication_source_commit=args.publication_source_commit,
            axiom_json_out=axiom_json_out,
        )
    except (
        OSError,
        RuntimeError,
        ValueError,
        json.JSONDecodeError,
        zipfile.BadZipFile,
        subprocess.SubprocessError,
    ) as exc:
        report = {
            "type": "uft-id-scholarly-archive-reproduction",
            "schema_version": "1.0.0",
            "status": "error",
            "errors": [str(exc)],
        }

    report_bytes = (
        json.dumps(report, indent=2, sort_keys=True, allow_nan=False) + "\n"
    ).encode("utf-8")
    try:
        safe_atomic_write(json_out, report_bytes, publication_root=directory)
    except (OSError, RuntimeError, ValueError) as exc:
        print(exc)
        return 1

    if report.get("status") == "ok":
        print("UFT-ID scholarly archive isolated formal reproduction: ok")
        return 0
    for error in report.get("errors", []):
        print(error)
    return 1


if __name__ == "__main__":
    raise SystemExit(main())
