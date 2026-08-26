#!/usr/bin/env python3
"""Reconstruct and verify the archived Lean layer in an isolated directory."""
from __future__ import annotations

import argparse
import hashlib
import json
import math
import os
import re
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
MAX_ZIP_MEMBERS = 10000
MAX_EOCD_SCAN_BYTES = 65557
EXPECTED_MODE = 0o100644
EOCD_SIGNATURE = b"PK\x05\x06"


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

    offset = tail.rfind(EOCD_SIGNATURE)
    if offset < 0 or offset + 22 > len(tail):
        raise RuntimeError("source ZIP EOCD record missing")
    (
        signature,
        disk_number,
        central_directory_disk,
        entries_on_disk,
        total_entries,
        _central_directory_bytes,
        _central_directory_offset,
        comment_length,
    ) = struct.unpack_from("<4s4H2LH", tail, offset)
    if signature != EOCD_SIGNATURE:
        raise RuntimeError("source ZIP EOCD signature mismatch")
    if disk_number != 0 or central_directory_disk != 0 or entries_on_disk != total_entries:
        raise RuntimeError("multi-disk ZIP archives are forbidden")
    if total_entries == 0xFFFF:
        raise RuntimeError("ZIP64 member enumeration is forbidden")
    if offset + 22 + comment_length != len(tail):
        raise RuntimeError("source ZIP EOCD/comment length drift")
    if total_entries == 0 or total_entries > MAX_ZIP_MEMBERS:
        raise RuntimeError("source ZIP member count outside allowed bounds")
    return total_entries


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


def reject_publication_output_aliases(directory: Path, output: Path) -> None:
    publication_root = directory.resolve()
    resolved = output.resolve()
    try:
        resolved.relative_to(publication_root)
    except ValueError:
        return
    raise RuntimeError(
        "reproduction output must be outside protected publication directory: "
        f"{resolved}"
    )


def require_exact_artifact_digests(
    observed: dict[str, dict[str, object]],
    canonical: dict[str, dict[str, object]],
) -> None:
    if set(observed) != set(canonical):
        raise RuntimeError("publication artifact inventory does not match canonical authority bytes")
    for name in sorted(canonical):
        if observed[name].get("bytes") != canonical[name].get("bytes") or observed[name].get("sha256") != canonical[name].get("sha256"):
            raise RuntimeError(f"publication artifact does not match canonical authority bytes: {name}")


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

    # The detached verifier at the immutable authority commit constructs
    # ZipFile before applying its own member-count policy. Bound the hostile ZIP
    # here first so authentication cannot reach that unbounded path.
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
    axiom_json_out = axiom_json_out.resolve()
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
    artifacts = artifact_surface(directory, exact_files)
    verified_artifacts = authority_verification.get("artifacts")
    if not isinstance(verified_artifacts, dict):
        raise RuntimeError("detached publication authority omitted artifact digests")
    for name, metadata in artifacts.items():
        if verified_artifacts.get(name) != metadata["sha256"]:
            raise RuntimeError(f"detached publication authority digest mismatch: {name}")

    source_zip = directory / SOURCE_ZIP_NAME

    axiom_json_out.parent.mkdir(parents=True, exist_ok=True)
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
        run_checked(
            [
                sys.executable,
                "scripts/verify_lean_observation_axioms.py",
                "--lake",
                str(lake_path),
                "--json-out",
                str(axiom_json_out),
            ],
            isolated,
            env=toolchain_env,
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
        record_toolchain = verification_record.get("toolchain")
        if not isinstance(record_toolchain, dict):
            raise RuntimeError("isolated archived verification toolchain record malformed")
        if record_toolchain.get("lean") != toolchain["lean"]:
            raise RuntimeError("isolated archived Lean version disagrees with reproduction contract")
        if record_toolchain.get("lake") != toolchain["lake"]:
            raise RuntimeError("isolated archived Lake version disagrees with reproduction contract")
        if record_toolchain.get("mathlib_commit") != toolchain["mathlib_commit"]:
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

    directory = args.directory.resolve()
    json_out = args.json_out.resolve()
    axiom_json_out = args.axiom_json_out.resolve()

    # Reject aliases before entering the general error-report path. In
    # particular, an invalid --json-out must never overwrite a publication file
    # even with an error receipt.
    try:
        reject_publication_output_aliases(directory, json_out)
        reject_publication_output_aliases(directory, axiom_json_out)
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

    json_out.parent.mkdir(parents=True, exist_ok=True)
    json_out.write_text(
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
