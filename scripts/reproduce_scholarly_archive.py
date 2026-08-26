#!/usr/bin/env python3
"""Reconstruct UFT-ID publication bytes and Lean evidence from trusted snapshots."""
from __future__ import annotations

import argparse
import contextlib
import importlib.util
import json
import os
import subprocess
import sys
import tempfile
import zipfile
from pathlib import Path

_THIS = Path(__file__).resolve()
ROOT = _THIS.parents[1]
CONTRACT_PATH = ROOT / "machine/scholarly_archive_reproduction_contract.json"


def _load_sibling(module_name: str, filename: str):
    path = _THIS.with_name(filename)
    spec = importlib.util.spec_from_file_location(module_name, path)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"cannot load publication helper: {filename}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


_legacy = _load_sibling("_uft_reproduce_legacy", "reproduce_scholarly_archive_legacy.py")
_io = _load_sibling("_uft_publication_snapshot_io", "publication_snapshot_io.py")
_toolchain = _load_sibling("_uft_publication_toolchain", "publication_toolchain.py")

# Preserve the established helper/test API unless this façade overrides it below.
for _name in dir(_legacy):
    if not _name.startswith("__"):
        globals()[_name] = getattr(_legacy, _name)

# Canonical live I/O policy comes from the hardened snapshot module.
SOURCE_ZIP_NAME = _io.SOURCE_ZIP_NAME
MAX_OUTER_ZIP_BYTES = _io.MAX_OUTER_ZIP_BYTES
MAX_ZIP_MEMBERS = _io.MAX_ZIP_MEMBERS
MAX_EOCD_SCAN_BYTES = _io.MAX_EOCD_SCAN_BYTES
EOCD_SIGNATURE = _io.EOCD_SIGNATURE
ZIP64_EOCD_SIGNATURE = _io.ZIP64_EOCD_SIGNATURE
ZIP64_LOCATOR_SIGNATURE = _io.ZIP64_LOCATOR_SIGNATURE
CENTRAL_DIRECTORY_SIGNATURE = _io.CENTRAL_DIRECTORY_SIGNATURE
CENTRAL_DIRECTORY_HEADER = _io.CENTRAL_DIRECTORY_HEADER
PUBLICATION_FILE_NAMES = _io.PUBLICATION_FILE_NAMES
PUBLICATION_SIZE_LIMITS = _io.PUBLICATION_SIZE_LIMITS
artifact_surface = _io.artifact_surface
safe_atomic_write = _io.safe_atomic_write
materialize_verified_publication = _io.materialize_verified_publication
stage_pinned_lean_archive = _toolchain.stage_pinned_lean_archive
extract_pinned_lean_toolchain = _toolchain.extract_pinned_lean_toolchain


def bounded_zip_member_count(path: Path) -> int:
    return _io.bounded_zip_member_count(path, max_members=MAX_ZIP_MEMBERS)


def require_exact_artifact_digests(
    observed: dict[str, dict[str, object]],
    canonical: dict[str, dict[str, object]],
) -> None:
    _io.require_exact_artifact_digests(observed, canonical)


def reject_publication_output_aliases(directory: Path, output: Path) -> None:
    _io.reject_output_alias(directory, output)


def extract_formal_layer(source_zip: Path, destination: Path) -> list[str]:
    """Use existing extraction semantics with the live wrapper policy constants."""
    names = (
        "MAX_FORMAL_FILE_BYTES",
        "MAX_FORMAL_TOTAL_BYTES",
        "MAX_OUTER_ZIP_BYTES",
        "MAX_ZIP_MEMBERS",
        "MAX_EOCD_SCAN_BYTES",
    )
    previous = {name: getattr(_legacy, name) for name in names}
    try:
        for name in names:
            setattr(_legacy, name, globals()[name])
        return _legacy.extract_formal_layer(source_zip, destination)
    finally:
        for name, value in previous.items():
            setattr(_legacy, name, value)


def revalidate_publication_surface(
    directory: Path,
    names: list[str],
    canonical: dict[str, dict[str, object]],
) -> dict[str, dict[str, object]]:
    expected_sizes = {name: int(canonical[name]["bytes"]) for name in names}
    observed = artifact_surface(directory, names, expected_sizes=expected_sizes)
    require_exact_artifact_digests(observed, canonical)
    return observed


def _run_detached_authority(
    authority_root: Path,
    canonical_root: Path,
    names: list[str],
) -> tuple[dict[str, dict[str, object]], dict[str, object]]:
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
    bounded_zip_member_count(canonical_root / SOURCE_ZIP_NAME)

    verifier = authority_root / "scripts/verify_scholarly_archive.py"
    proc = subprocess.run(
        [sys.executable, str(verifier), str(canonical_root), "--json"],
        cwd=authority_root,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        check=False,
    )
    if proc.returncode != 0:
        raise RuntimeError(
            "detached publication authority rejected its canonical archive bytes:\n"
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
    return canonical, report


@contextlib.contextmanager
def trusted_publication_snapshot(
    directory: Path,
    expected_commit: str,
    exact_files: list[str] | None = None,
):
    """Authenticate caller bytes, then yield only a private canonical rebuild."""
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
    # This preflight never feeds execution. It only rejects hostile input early.
    artifact_surface(directory, names)
    bounded_zip_member_count(directory / SOURCE_ZIP_NAME)

    with tempfile.TemporaryDirectory(prefix="uft-id-publication-authority-") as temporary:
        temporary_root = Path(temporary)
        authority_root = temporary_root / "authority"
        canonical_root = temporary_root / "canonical"
        canonical_root.mkdir(mode=0o700)
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
            canonical, report = _run_detached_authority(authority_root, canonical_root, names)
            expected_sizes = {name: int(canonical[name]["bytes"]) for name in names}
            supplied = artifact_surface(directory, names, expected_sizes=expected_sizes)
            require_exact_artifact_digests(supplied, canonical)
            yield canonical_root, canonical, report
        finally:
            subprocess.run(
                ["git", "worktree", "remove", "--force", str(authority_root)],
                cwd=ROOT,
                text=True,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                check=False,
            )


def authenticate_publication_surface(
    directory: Path,
    expected_commit: str,
    exact_files: list[str] | None = None,
) -> dict[str, object]:
    with trusted_publication_snapshot(directory, expected_commit, exact_files) as (
        _snapshot,
        canonical,
        report,
    ):
        return {
            "status": "ok",
            "artifacts": dict(report["artifacts"]),
            "artifact_metadata": canonical,
        }


def reproduce(
    directory: Path,
    *,
    publication_source_commit: str,
    axiom_json_out: Path,
    lean_archive: Path | None = None,
    verified_publication_out: Path | None = None,
    lake: str | None = None,
) -> dict[str, object]:
    """Reproduce only from a trusted canonical publication and pinned Lean archive."""
    directory = directory.resolve()
    axiom_json_out = axiom_json_out.resolve(strict=False)
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
    if lake is not None:
        raise RuntimeError("caller-supplied --lake executables are unsupported; use the pinned Lean archive")
    if lean_archive is None:
        raise RuntimeError("pinned Lean archive is required")
    if verified_publication_out is None:
        raise RuntimeError("verified publication output directory is required")

    verified_publication_out = verified_publication_out.resolve(strict=False)
    reject_publication_output_aliases(directory, axiom_json_out)
    reject_publication_output_aliases(directory, verified_publication_out)
    exact_files = [str(value) for value in surface["exact_files"]]

    with trusted_publication_snapshot(directory, expected_commit, exact_files) as (
        canonical_root,
        canonical_metadata,
        authority_report,
    ):
        verified_artifacts = authority_report.get("artifacts")
        if not isinstance(verified_artifacts, dict):
            raise RuntimeError("detached publication authority omitted artifact digests")

        with tempfile.TemporaryDirectory(prefix="uft-id-publication-formal-") as temporary:
            temporary_root = Path(temporary)
            isolated = temporary_root / "formal"
            isolated.mkdir(mode=0o700)
            # Crucial boundary: extraction reads the private canonical snapshot, never caller paths.
            members = extract_formal_layer(canonical_root / SOURCE_ZIP_NAME, isolated)

            staged_archive = temporary_root / "lean-archive.tar.zst"
            lean_archive_metadata = stage_pinned_lean_archive(
                lean_archive,
                toolchain,
                staged_archive,
            )
            lake_path, lean_path = extract_pinned_lean_toolchain(
                staged_archive,
                temporary_root / "lean-toolchain",
            )
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
            verification_record = load_json_bytes(
                bounded_read_bytes(
                    isolated / "machine/lean_observation_verification.json",
                    MAX_EVIDENCE_BYTES,
                    label="archived Lean verification record",
                ),
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

        safe_atomic_write(axiom_json_out, axiom_bytes, publication_root=directory)
        # Retention is materialized from the private canonical snapshot after all external commands.
        retained_artifacts = materialize_verified_publication(
            canonical_root,
            verified_publication_out,
            exact_files,
            canonical_metadata,
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
            "artifacts": retained_artifacts,
            "authority_verification": {
                "status": authority_report["status"],
                "artifacts": verified_artifacts,
            },
            "verified_publication_snapshot": {
                "directory": str(verified_publication_out),
                "read_only": True,
            },
            "isolated_formal_layer": {
                "member_count": len(members),
                "lean_version_output": lean_version,
                "lake_version_output": lake_version,
                "lean_archive_sha256": lean_archive_metadata["sha256"],
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
    parser.add_argument("--lean-archive", type=Path)
    parser.add_argument("--verified-publication-out", type=Path)
    parser.add_argument("--lake", help=argparse.SUPPRESS)
    parser.add_argument("--publication-source-commit", required=True)
    parser.add_argument("--json-out", type=Path, required=True)
    parser.add_argument("--axiom-json-out", type=Path, required=True)
    args = parser.parse_args()

    directory = args.directory.resolve()
    json_out = args.json_out.resolve(strict=False)
    axiom_json_out = args.axiom_json_out.resolve(strict=False)
    verified_publication_out = (
        args.verified_publication_out.resolve(strict=False)
        if args.verified_publication_out is not None
        else None
    )
    try:
        reject_publication_output_aliases(directory, json_out)
        reject_publication_output_aliases(directory, axiom_json_out)
        if verified_publication_out is not None:
            reject_publication_output_aliases(directory, verified_publication_out)
        reject_evidence_output_aliases(json_out, axiom_json_out)
    except (OSError, RuntimeError, ValueError) as exc:
        print(exc)
        return 1

    try:
        report = reproduce(
            directory,
            publication_source_commit=args.publication_source_commit,
            axiom_json_out=axiom_json_out,
            lean_archive=args.lean_archive,
            verified_publication_out=verified_publication_out,
            lake=args.lake,
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
    additional_roots: list[Path] = []
    if verified_publication_out is not None and verified_publication_out.exists():
        additional_roots.append(verified_publication_out)
    try:
        safe_atomic_write(
            json_out,
            report_bytes,
            publication_root=directory,
            additional_publication_roots=additional_roots,
        )
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
