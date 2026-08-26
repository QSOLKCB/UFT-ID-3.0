#!/usr/bin/env python3
"""Authenticate and privately extract the pinned Lean distribution."""
from __future__ import annotations

import hashlib
import os
import stat
import subprocess
from pathlib import Path

MAX_LEAN_ARCHIVE_BYTES = 1024 * 1024 * 1024


def _regular_open_flags() -> int:
    return os.O_RDONLY | getattr(os, "O_NOFOLLOW", 0) | getattr(os, "O_NONBLOCK", 0)


def stage_pinned_lean_archive(
    source: Path,
    toolchain: dict[str, object],
    destination: Path,
) -> dict[str, object]:
    source = Path(source)
    if source.is_symlink():
        raise RuntimeError("Lean archive symlinks are forbidden")
    source = source.resolve()
    try:
        source_fd = os.open(source, _regular_open_flags())
    except OSError as exc:
        raise RuntimeError("could not safely open Lean archive") from exc
    destination.parent.mkdir(parents=True, exist_ok=True)
    destination_fd: int | None = None
    try:
        st = os.fstat(source_fd)
        if not stat.S_ISREG(st.st_mode):
            raise RuntimeError("Lean archive is not a regular file")
        if st.st_size <= 0 or st.st_size > MAX_LEAN_ARCHIVE_BYTES:
            raise RuntimeError("Lean archive size outside allowed bound")
        flags = os.O_WRONLY | os.O_CREAT | os.O_EXCL | getattr(os, "O_NOFOLLOW", 0)
        destination_fd = os.open(destination, flags, 0o400)
        h = hashlib.sha256()
        remaining = st.st_size
        while remaining:
            chunk = os.read(source_fd, min(1024 * 1024, remaining))
            if not chunk:
                raise RuntimeError("Lean archive changed size while staging")
            h.update(chunk)
            view = memoryview(chunk)
            written = 0
            while written < len(view):
                count = os.write(destination_fd, view[written:])
                if count <= 0:
                    raise RuntimeError("could not stage Lean archive")
                written += count
            remaining -= len(chunk)
        if os.read(source_fd, 1):
            raise RuntimeError("Lean archive changed size while staging")
        os.fsync(destination_fd)
        observed = h.hexdigest()
        expected = str(toolchain["lean_archive_sha256"])
        if observed != expected:
            raise RuntimeError(
                f"Lean archive SHA-256 mismatch: expected {expected}, got {observed}"
            )
        return {"bytes": st.st_size, "sha256": observed}
    finally:
        os.close(source_fd)
        if destination_fd is not None:
            os.close(destination_fd)


def extract_pinned_lean_toolchain(
    staged_archive: Path,
    destination: Path,
) -> tuple[Path, Path]:
    destination.mkdir(mode=0o700)
    proc = subprocess.run(
        [
            "/usr/bin/tar",
            "--zstd",
            "-xf",
            str(staged_archive),
            "-C",
            str(destination),
            "--strip-components=1",
        ],
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        check=False,
    )
    if proc.returncode != 0:
        raise RuntimeError(
            "could not extract pinned Lean archive:\n"
            + proc.stdout
            + ("\n" + proc.stderr if proc.stderr else "")
        )
    lake_path = destination / "bin/lake"
    lean_path = destination / "bin/lean"
    if not lake_path.is_file() or not lean_path.is_file():
        raise RuntimeError("pinned Lean archive is missing Lean/Lake executables")
    return lake_path, lean_path
