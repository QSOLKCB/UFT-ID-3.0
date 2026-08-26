#!/usr/bin/env python3
"""Reconstruct and verify the archived Lean layer in an isolated directory."""
from __future__ import annotations

import argparse
import hashlib
import json
import math
import os
import stat
import subprocess
import sys
import tempfile
import zipfile
from pathlib import Path, PurePosixPath

ROOT = Path(__file__).resolve().parents[1]
CONTRACT_PATH = ROOT / "machine/scholarly_archive_reproduction_contract.json"
MAX_FORMAL_FILE_BYTES = 64 * 1024 * 1024
MAX_FORMAL_TOTAL_BYTES = 256 * 1024 * 1024
EXPECTED_MODE = 0o100644


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


def sha256_file(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as fh:
        for chunk in iter(lambda: fh.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


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


def extract_formal_layer(source_zip: Path, destination: Path) -> list[str]:
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
        for info in zf.infolist():
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


def run_checked(command: list[str], cwd: Path) -> str:
    proc = subprocess.run(
        command,
        cwd=cwd,
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


def artifact_surface(directory: Path, names: list[str]) -> dict[str, dict[str, object]]:
    observed = sorted(path.name for path in directory.iterdir())
    if observed != sorted(names):
        raise RuntimeError(f"publication surface drift: expected {sorted(names)}, got {observed}")
    result: dict[str, dict[str, object]] = {}
    for name in names:
        path = directory / name
        if not path.is_file() or path.is_symlink():
            raise RuntimeError(f"publication artifact is not a regular file: {name}")
        result[name] = {"bytes": path.stat().st_size, "sha256": sha256_file(path)}
    return result


def reproduce(
    directory: Path,
    *,
    lake: str,
    publication_source_commit: str,
    axiom_json_out: Path,
) -> dict[str, object]:
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
    artifacts = artifact_surface(directory, exact_files)
    source_zip = directory / "UFT-ID-3.0.0-source.zip"

    axiom_json_out = axiom_json_out.resolve()
    axiom_json_out.parent.mkdir(parents=True, exist_ok=True)
    with tempfile.TemporaryDirectory(prefix="uft-id-publication-formal-") as temporary:
        isolated = Path(temporary)
        members = extract_formal_layer(source_zip, isolated)

        lake_path = str(Path(lake).resolve())
        lake_version = run_checked([lake_path, "--version"], isolated)
        lean_version = run_checked([lake_path, "env", "lean", "--version"], isolated)
        run_checked([lake_path, "update"], isolated)
        run_checked([lake_path, "exe", "cache", "get"], isolated)
        build_output = run_checked([lake_path, "build", "UFTID"], isolated)
        run_checked(
            [
                sys.executable,
                "scripts/verify_lean_observation_axioms.py",
                "--lake",
                lake_path,
                "--json-out",
                str(axiom_json_out),
            ],
            isolated,
        )

        axiom_report = load_json_bytes(axiom_json_out.read_bytes(), axiom_json_out.name)
        if axiom_report.get("status") != "ok":
            raise RuntimeError("isolated archived axiom audit did not report ok")
        verification_record = load_json_bytes(
            (isolated / "machine/lean_observation_verification.json").read_bytes(),
            "archived Lean verification record",
        )
        if verification_record.get("status") != "LEAN_VERIFIED":
            raise RuntimeError("isolated archived verification record is not LEAN_VERIFIED")
        if verification_record.get("toolchain", {}).get("lean") != toolchain["lean"]:
            raise RuntimeError("isolated archived Lean version disagrees with reproduction contract")
        if verification_record.get("toolchain", {}).get("mathlib_commit") != toolchain["mathlib_commit"]:
            raise RuntimeError("isolated archived mathlib revision disagrees with reproduction contract")

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
        "artifacts": artifacts,
        "isolated_formal_layer": {
            "member_count": len(members),
            "lean_version_output": lean_version,
            "lake_version_output": lake_version,
            "build_result": "success",
            "build_output_tail": build_output[-1000:],
            "axiom_audit_status": axiom_report["status"],
            "axiom_audit_sha256": sha256_file(axiom_json_out),
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

    try:
        report = reproduce(
            args.directory.resolve(),
            lake=args.lake,
            publication_source_commit=args.publication_source_commit,
            axiom_json_out=args.axiom_json_out,
        )
    except (OSError, RuntimeError, ValueError, json.JSONDecodeError, zipfile.BadZipFile) as exc:
        report = {
            "type": "uft-id-scholarly-archive-reproduction",
            "schema_version": "1.0.0",
            "status": "error",
            "errors": [str(exc)],
        }

    args.json_out.parent.mkdir(parents=True, exist_ok=True)
    args.json_out.write_text(
        json.dumps(report, indent=2, sort_keys=True, allow_nan=False) + "\n",
        encoding="utf-8",
    )
    if report.get("status") == "ok":
        print("UFT-ID scholarly archive isolated formal reproduction: ok")
        return 0
    for error in report.get("errors", []):
        print(error)
    return 1


if __name__ == "__main__":
    raise SystemExit(main())
