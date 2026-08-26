#!/usr/bin/env python3
"""Independently verify the UFT-ID 3.0 three-file Zenodo surface."""
from __future__ import annotations

import argparse
import hashlib
import json
import re
import subprocess
import tarfile
import tempfile
import tomllib
import zipfile
from pathlib import Path, PurePosixPath

ROOT = Path(__file__).resolve().parents[1]
CONTRACT_PATH = ROOT / "machine/scholarly_archive_contract.json"
FIXED_ZIP_DT = (1980, 1, 1, 0, 0, 0)
EXPECTED_MODE = 0o100644
MAX_MEMBERS = 10000
MAX_FILE_BYTES = 64 * 1024 * 1024
MAX_TOTAL_BYTES = 256 * 1024 * 1024
MAX_COMPRESSION_RATIO = 300.0
MAX_OUTER_ZIP_BYTES = 256 * 1024 * 1024
MAX_OUTER_PDF_BYTES = 8 * 1024 * 1024
MAX_OUTER_NOTES_BYTES = 1024 * 1024


def sha256_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def sha256_file(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as fh:
        for chunk in iter(lambda: fh.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def reject_duplicate_object_pairs(pairs: list[tuple[str, object]]) -> dict[str, object]:
    result: dict[str, object] = {}
    for key, value in pairs:
        if key in result:
            raise ValueError(f"duplicate JSON key: {key}")
        result[key] = value
    return result


def strict_json_bytes(raw: bytes, *, label: str) -> object:
    try:
        text = raw.decode("utf-8")
    except UnicodeDecodeError as exc:
        raise RuntimeError(f"{label} is not UTF-8") from exc
    try:
        return json.loads(text, object_pairs_hook=reject_duplicate_object_pairs)
    except (json.JSONDecodeError, ValueError) as exc:
        raise RuntimeError(f"{label} is not strict JSON: {exc}") from exc


def load_contract() -> dict[str, object]:
    value = strict_json_bytes(CONTRACT_PATH.read_bytes(), label="scholarly archive contract")
    if not isinstance(value, dict):
        raise RuntimeError("scholarly archive contract must be a JSON object")
    return value


def run_git(*args: str) -> str:
    cp = subprocess.run(
        ["git", *args], cwd=ROOT, check=True, text=True,
        stdout=subprocess.PIPE, stderr=subprocess.PIPE,
    )
    return cp.stdout.strip()


def bounded_bytes(path: Path, limit: int, *, label: str) -> bytes:
    size = path.stat().st_size
    if size > limit:
        raise RuntimeError(f"{label} exceeds size bound")
    with path.open("rb") as fh:
        data = fh.read(limit + 1)
    if len(data) != size or len(data) > limit:
        raise RuntimeError(f"{label} exceeds size bound")
    return data


def safe_path(name: str, allowed_top: set[str]) -> PurePosixPath:
    if not name or "\\" in name or "\x00" in name:
        raise RuntimeError(f"unsafe archive path: {name!r}")
    path = PurePosixPath(name)
    if path.is_absolute() or not path.parts or ".." in path.parts:
        raise RuntimeError(f"unsafe archive path: {name}")
    if path.as_posix() != name:
        raise RuntimeError(f"non-canonical archive path: {name}")
    if path.parts[0] not in allowed_top:
        raise RuntimeError(f"unexpected top-level archive path: {name}")
    return path


def git_archive_files(ref: str, paths: list[str] | None = None) -> dict[str, bytes]:
    with tempfile.NamedTemporaryFile(prefix="uft-id-verify-", suffix=".tar", delete=False) as tmp:
        tar_path = Path(tmp.name)
        cmd = ["git", "archive", "--format=tar", ref]
        if paths:
            cmd.extend(["--", *paths])
        subprocess.run(cmd, cwd=ROOT, check=True, stdout=tmp)
    try:
        result: dict[str, bytes] = {}
        total = 0
        with tarfile.open(tar_path, "r:") as tf:
            members = tf.getmembers()
            if len(members) > MAX_MEMBERS:
                raise RuntimeError("expected Git archive exceeds member-count bound")
            for member in members:
                raw = member.name.rstrip("/")
                path = PurePosixPath(raw)
                if not raw or path.is_absolute() or ".." in path.parts or path.as_posix() != raw:
                    raise RuntimeError(f"unsafe expected Git path: {member.name}")
                if member.isdir():
                    continue
                if not member.isfile():
                    raise RuntimeError(f"expected Git archive has non-regular member: {raw}")
                if member.size > MAX_FILE_BYTES:
                    raise RuntimeError(f"expected Git file exceeds size bound: {raw}")
                total += member.size
                if total > MAX_TOTAL_BYTES:
                    raise RuntimeError("expected Git archive exceeds total size bound")
                source = tf.extractfile(member)
                if source is None:
                    raise RuntimeError(f"could not read expected Git member: {raw}")
                data = source.read(MAX_FILE_BYTES + 1)
                if len(data) != member.size:
                    raise RuntimeError(f"expected Git member size mismatch: {raw}")
                result[raw] = data
        return result
    finally:
        tar_path.unlink(missing_ok=True)


def read_zip(path: Path, contract: dict[str, object]) -> dict[str, bytes]:
    if path.stat().st_size > MAX_OUTER_ZIP_BYTES:
        raise RuntimeError("source ZIP exceeds outer size bound")
    source = contract["source_release"]
    formal = contract["formalization"]
    if not isinstance(source, dict) or not isinstance(formal, dict):
        raise RuntimeError("archive contract source/formalization sections malformed")
    allowed_top = {
        str(source["directory"]), str(formal["directory"]),
        "ARCHIVE-MANIFEST.json", "SHA256SUMS",
    }
    files: dict[str, bytes] = {}
    names: list[str] = []
    total = 0
    with zipfile.ZipFile(path, "r") as zf:
        infos = zf.infolist()
        if not infos or len(infos) > MAX_MEMBERS:
            raise RuntimeError("source ZIP member count outside allowed bounds")
        for info in infos:
            if info.is_dir():
                raise RuntimeError(f"directory entry forbidden in source ZIP: {info.filename}")
            name = safe_path(info.filename, allowed_top).as_posix()
            if name in files:
                raise RuntimeError(f"duplicate source ZIP member: {name}")
            if info.flag_bits & 0x1:
                raise RuntimeError(f"encrypted source ZIP member forbidden: {name}")
            if info.compress_type != zipfile.ZIP_DEFLATED:
                raise RuntimeError(f"unexpected ZIP compression method: {name}")
            if info.date_time != FIXED_ZIP_DT:
                raise RuntimeError(f"non-deterministic ZIP timestamp: {name}")
            mode = (info.external_attr >> 16) & 0o177777
            if mode != EXPECTED_MODE:
                raise RuntimeError(f"unexpected ZIP mode {oct(mode)}: {name}")
            if info.file_size > MAX_FILE_BYTES:
                raise RuntimeError(f"ZIP member exceeds size bound: {name}")
            total += info.file_size
            if total > MAX_TOTAL_BYTES:
                raise RuntimeError("ZIP exceeds total expanded-size bound")
            if info.file_size:
                if info.compress_size <= 0 or info.file_size / info.compress_size > MAX_COMPRESSION_RATIO:
                    raise RuntimeError(f"ZIP compression ratio outside bound: {name}")
            data = zf.read(info)
            if len(data) != info.file_size:
                raise RuntimeError(f"ZIP expanded-size mismatch: {name}")
            files[name] = data
            names.append(name)
    expected_order = sorted(names, key=lambda value: PurePosixPath(value).parts)
    if names != expected_order:
        raise RuntimeError("source ZIP entries are not deterministically ordered")
    return files


def verify_manifest(files: dict[str, bytes], contract: dict[str, object]) -> dict[str, object]:
    raw = files.get("ARCHIVE-MANIFEST.json")
    if raw is None:
        raise RuntimeError("source ZIP missing ARCHIVE-MANIFEST.json")
    manifest = strict_json_bytes(raw, label="ARCHIVE-MANIFEST.json")
    if not isinstance(manifest, dict):
        raise RuntimeError("archive manifest must be an object")
    metadata = contract["zenodo_metadata"]
    source = contract["source_release"]
    formal = contract["formalization"]
    surface = contract["publication_surface"]
    expected = {
        "protocol": "UFT-ID/SCHOLARLY-ARCHIVE/1",
        "schema_version": "1.0.0",
        "project": contract["project"],
        "version": contract["version"],
        "doi": contract["doi"],
        "repository": contract["repository"],
        "licenses": {
            "zenodo_scholarly_record": metadata["record_license"],
            "software_source": metadata["software_source_license"],
        },
        "source_release": source,
        "formalization": {
            "integration_commit": formal["integration_commit"],
            "integration_tree": formal["integration_tree"],
            "verification_promotion_commit": formal["verification_promotion_commit"],
            "verification_promotion_tree": formal["verification_promotion_tree"],
            "codex_no_major_issues_reviewed_commit": formal["codex_no_major_issues_reviewed_commit"],
            "final_pr_head": formal["final_pr_head"],
            "review_result": formal["review_result"],
            "directory": formal["directory"],
            "toolchain": formal["toolchain"],
            "theorems": formal["theorems"],
            "authority_rule": "selected Lean observation theorems only; no whole-program, empirical, or physical-ontology proof claim",
        },
        "publication_surface": surface,
    }
    if set(manifest) != set(expected) | {"files"}:
        raise RuntimeError("archive manifest top-level fields drifted")
    for key, value in expected.items():
        if manifest.get(key) != value:
            raise RuntimeError(f"archive manifest identity drift: {key}")

    rows = manifest.get("files")
    if not isinstance(rows, list):
        raise RuntimeError("archive manifest files must be a list")
    by_name: dict[str, dict[str, object]] = {}
    for row in rows:
        if not isinstance(row, dict) or set(row) != {"path", "bytes", "sha256"}:
            raise RuntimeError("malformed archive manifest file row")
        name = row.get("path")
        size = row.get("bytes")
        digest = row.get("sha256")
        if not isinstance(name, str) or not name or PurePosixPath(name).as_posix() != name or name in by_name:
            raise RuntimeError("archive manifest contains duplicate/non-canonical path")
        if not isinstance(size, int) or isinstance(size, bool) or size < 0:
            raise RuntimeError(f"archive manifest invalid byte count: {name}")
        if not isinstance(digest, str) or not re.fullmatch(r"[0-9a-f]{64}", digest):
            raise RuntimeError(f"archive manifest invalid SHA-256: {name}")
        by_name[name] = row
    expected_names = set(files) - {"ARCHIVE-MANIFEST.json"}
    if set(by_name) != expected_names:
        raise RuntimeError("archive manifest file inventory mismatch")
    for name in expected_names:
        data = files[name]
        row = by_name[name]
        if row["bytes"] != len(data) or row["sha256"] != sha256_bytes(data):
            raise RuntimeError(f"archive manifest hash mismatch: {name}")
    return manifest


def verify_internal_sums(files: dict[str, bytes]) -> None:
    raw = files.get("SHA256SUMS")
    if raw is None:
        raise RuntimeError("source ZIP missing SHA256SUMS")
    try:
        text = raw.decode("utf-8")
    except UnicodeDecodeError as exc:
        raise RuntimeError("SHA256SUMS is not UTF-8") from exc
    observed: dict[str, str] = {}
    for line in text.splitlines():
        match = re.fullmatch(r"([0-9a-f]{64})  (.+)", line)
        if match is None:
            raise RuntimeError("malformed SHA256SUMS row")
        digest, name = match.groups()
        if name in observed or name in {"SHA256SUMS", "ARCHIVE-MANIFEST.json"}:
            raise RuntimeError("invalid or duplicate SHA256SUMS path")
        observed[name] = digest
    expected_names = {
        name for name in files
        if name not in {"SHA256SUMS", "ARCHIVE-MANIFEST.json"}
    }
    if set(observed) != expected_names:
        raise RuntimeError("SHA256SUMS inventory mismatch")
    for name in expected_names:
        if observed[name] != sha256_bytes(files[name]):
            raise RuntimeError(f"SHA256SUMS mismatch: {name}")


def compare_git_layers(files: dict[str, bytes], contract: dict[str, object]) -> None:
    source = contract["source_release"]
    formal = contract["formalization"]
    source_prefix = f"{source['directory']}/"
    actual_source = {name[len(source_prefix):]: data for name, data in files.items() if name.startswith(source_prefix)}
    expected_source = git_archive_files(str(source["commit"]))
    if actual_source != expected_source:
        raise RuntimeError("reference-v3.0.0 is not byte-identical to the frozen source commit")

    formal_prefix = f"{formal['directory']}/"
    actual_formal = {name[len(formal_prefix):]: data for name, data in files.items() if name.startswith(formal_prefix)}
    paths = [str(value) for value in formal["archive_paths"]]
    expected_formal = git_archive_files(str(formal["verification_promotion_commit"]), paths)
    if actual_formal != expected_formal:
        raise RuntimeError("formal layer is not byte-identical to the bound verification-promotion commit")


def verify_package_definition(files: dict[str, bytes], contract: dict[str, object]) -> None:
    formal = contract["formalization"]
    prefix = f"{formal['directory']}/"
    toolchain = formal["toolchain"]
    toolchain_name = f"{prefix}lean-toolchain"
    lakefile_name = f"{prefix}lakefile.toml"
    try:
        lean_text = files[toolchain_name].decode("utf-8")
        lake_text = files[lakefile_name].decode("utf-8")
    except KeyError as exc:
        raise RuntimeError(f"formal layer missing tracked package authority: {exc.args[0]}") from exc
    except UnicodeDecodeError as exc:
        raise RuntimeError("tracked Lean package authority is not UTF-8") from exc

    expected_lean = f"leanprover/lean4:{toolchain['lean']}\n"
    if lean_text != expected_lean:
        raise RuntimeError("archived lean-toolchain does not match archive contract")

    try:
        package = tomllib.loads(lake_text)
    except tomllib.TOMLDecodeError as exc:
        raise RuntimeError("archived lakefile.toml is not valid TOML") from exc
    if package.get("name") != "UFTID" or package.get("version") != contract["version"]:
        raise RuntimeError("archived lakefile.toml package identity does not match archive contract")
    if package.get("defaultTargets") != ["UFTID"]:
        raise RuntimeError("archived lakefile.toml default target drift")
    if package.get("lean_lib") != [{"name": "UFTID"}]:
        raise RuntimeError("archived lakefile.toml Lean library declaration drift")
    expected_require = [{
        "name": "mathlib",
        "git": "https://github.com/leanprover-community/mathlib4.git",
        "rev": toolchain["mathlib_commit"],
    }]
    if package.get("require") != expected_require:
        raise RuntimeError("archived lakefile.toml mathlib dependency does not match archive contract")
    if "lake-manifest.json" in formal.get("archive_paths", []):
        raise RuntimeError("untracked lake-manifest.json must not be registered as reviewed formal source")


def verify_verification_record(files: dict[str, bytes], contract: dict[str, object]) -> dict[str, object]:
    formal = contract["formalization"]
    source = contract["source_release"]
    name = f"{formal['directory']}/machine/lean_observation_verification.json"
    raw = files.get(name)
    if raw is None:
        raise RuntimeError("formal layer missing Lean verification record")
    record = strict_json_bytes(raw, label="archived Lean verification record")
    if not isinstance(record, dict):
        raise RuntimeError("archived Lean verification record must be an object")
    if record.get("status") != "LEAN_VERIFIED":
        raise RuntimeError("archived Lean verification record is not LEAN_VERIFIED")

    expected_source = {key: source[key] for key in ("tag", "commit", "tree")}
    if record.get("source_release") != expected_source:
        raise RuntimeError("archived Lean verification source-release provenance drift")

    integration = record.get("formalization_integration")
    if not isinstance(integration, dict):
        raise RuntimeError("archived Lean verification integration provenance malformed")
    if integration.get("merge_commit") != formal["integration_commit"]:
        raise RuntimeError("archived Lean verification integration commit drift")
    if integration.get("merge_tree") != formal["integration_tree"]:
        raise RuntimeError("archived Lean verification integration tree drift")
    if integration.get("final_pr_head") != formal["final_pr_head"]:
        raise RuntimeError("archived Lean verification final PR head drift")

    review = record.get("review_evidence")
    if not isinstance(review, dict):
        raise RuntimeError("archived Lean verification review provenance malformed")
    if review.get("codex_no_major_issues_reviewed_commit") != formal["codex_no_major_issues_reviewed_commit"]:
        raise RuntimeError("archived Codex reviewed-commit provenance drift")
    if review.get("final_pr_head") != formal["final_pr_head"]:
        raise RuntimeError("archived Codex later-head provenance drift")
    if formal.get("review_result") != "no_major_issues":
        raise RuntimeError("archive contract review result is not the declared Codex result")

    record_toolchain = record.get("toolchain")
    if not isinstance(record_toolchain, dict):
        raise RuntimeError("archived Lean verification toolchain provenance malformed")
    for key in ("lean", "lake", "mathlib_commit", "lean_archive_sha256"):
        if record_toolchain.get(key) != formal["toolchain"].get(key):
            raise RuntimeError(f"archived Lean verification toolchain drift: {key}")

    expected = [(row["id"], row["source_blob_sha"]) for row in formal["theorems"]]
    observed = [(row.get("id"), row.get("source_blob_sha")) for row in record.get("theorems", [])]
    if observed != expected:
        raise RuntimeError("archived theorem/source-blob inventory drift")
    if record.get("current_deferred_theorem_ids") != []:
        raise RuntimeError("archived verification record has a current deferred theorem")
    return record


def verify_git_provenance(contract: dict[str, object]) -> None:
    source = contract["source_release"]
    formal = contract["formalization"]
    if run_git("rev-parse", f"{source['tag']}^{{commit}}") != str(source["commit"]):
        raise RuntimeError("source tag no longer resolves to bound commit")
    if run_git("rev-parse", f"{source['commit']}^{{tree}}") != str(source["tree"]):
        raise RuntimeError("source tree binding drift")

    identities = (
        ("integration", formal["integration_commit"], formal["integration_tree"]),
        ("verification-promotion", formal["verification_promotion_commit"], formal["verification_promotion_tree"]),
    )
    for label, commit, tree in identities:
        if run_git("rev-parse", f"{commit}^{{commit}}") != str(commit):
            raise RuntimeError(f"{label} commit unavailable")
        if run_git("rev-parse", f"{commit}^{{tree}}") != str(tree):
            raise RuntimeError(f"{label} tree binding drift")
    for field in ("codex_no_major_issues_reviewed_commit", "final_pr_head"):
        value = str(formal[field])
        if run_git("rev-parse", f"{value}^{{commit}}") != value:
            raise RuntimeError(f"{field} unavailable")


def verify_pdf(path: Path, contract: dict[str, object]) -> None:
    data = bounded_bytes(path, MAX_OUTER_PDF_BYTES, label="Overview PDF")
    if not data.startswith(b"%PDF-1.4") or b"xref\n" not in data or not data.rstrip().endswith(b"%%EOF"):
        raise RuntimeError("Overview PDF structure is not the deterministic PDF profile")
    page_count = len(re.findall(rb"/Type /Page\b", data))
    if page_count < 5:
        raise RuntimeError("Overview PDF is unexpectedly short")
    formal = contract["formalization"]
    source = contract["source_release"]
    required = [
        str(contract["doi"]), str(contract["version"]), str(contract["repository"]),
        str(source["commit"]), str(source["tree"]),
        str(formal["integration_commit"]), str(formal["verification_promotion_commit"]),
        str(formal["codex_no_major_issues_reviewed_commit"]), str(formal["final_pr_head"]),
        "UFT-OBS-005", "LEAN_VERIFIED", "Creative Commons Attribution 4.0", "MIT",
    ]
    text = data.decode("latin-1")
    for needle in required:
        if needle not in text:
            raise RuntimeError(f"Overview PDF missing required identity text: {needle}")


def expected_release_notes_text(contract: dict[str, object], source_zip: Path, overview_pdf: Path) -> str:
    zip_sha = sha256_file(source_zip)
    pdf_sha = sha256_file(overview_pdf)
    source = contract["source_release"]
    formal = contract["formalization"]
    return f"""# UFT-ID 3.0 Scholarly Archive Release Notes\n\nVersion: {contract['version']}\nZenodo DOI: {contract['doi']}\nRepository: {contract['repository']}\n\n## Publication surface\n\n- `{source_zip.name}`\n  - SHA-256: `{zip_sha}`\n- `{overview_pdf.name}`\n  - SHA-256: `{pdf_sha}`\n- `RELEASE-NOTES.md`\n  - its uploaded checksum is recorded independently by Zenodo; this file does not self-embed its own hash.\n\n## Provenance\n\nThe source archive contains two explicitly separate layers:\n\n- `reference-v3.0.0/`: exact immutable source tag `{source['tag']}`, commit `{source['commit']}`, tree `{source['tree']}`.\n- `formal/`: selected verified post-tag Lean layer from promotion commit `{formal['verification_promotion_commit']}`; formalization integration commit `{formal['integration_commit']}` remains separately recorded.\n\n`UFT-OBS-001` through `UFT-OBS-004` are `LEAN-OBS-BATCH-001`. `UFT-OBS-005` is the separately registered arithmetic `LEAN-OBS-BATCH-002`. The historical v3.0.0 batch-001 deferral of UFT-OBS-005 is preserved as history and is not a current deferral.\n\n## Toolchain\n\n- Lean: `{formal['toolchain']['lean']}`\n- Lake: `{formal['toolchain']['lake']}`\n- mathlib: `{formal['toolchain']['mathlib_commit']}`\n- Lean archive SHA-256: `{formal['toolchain']['lean_archive_sha256']}`\n\n## Licensing\n\nThe Zenodo scholarly record/overview uses Creative Commons Attribution 4.0 International as configured in Zenodo. Software source bytes retain the repository's MIT License. The archive records these as separate licensing domains.\n\n## Claim boundary\n\n`LEAN_VERIFIED != COMPLETE_SOFTWARE_FORMAL_VERIFICATION`\n\n`LEAN_PROOF != EMPIRICAL_VALIDATION`\n\n`SOURCE_RELEASE != LATER_LEAN_FORMALIZATION_LAYER`\n\n`CHECKSUM_MATCH != SEMANTIC_TRUTH`\n"""


def verify_release_notes(notes: Path, source_zip: Path, overview_pdf: Path, contract: dict[str, object]) -> None:
    raw = bounded_bytes(notes, MAX_OUTER_NOTES_BYTES, label="RELEASE-NOTES.md")
    try:
        text = raw.decode("utf-8")
    except UnicodeDecodeError as exc:
        raise RuntimeError("RELEASE-NOTES.md is not UTF-8") from exc
    expected = expected_release_notes_text(contract, source_zip, overview_pdf)
    if text != expected:
        raise RuntimeError("release notes do not match canonical deterministic content")
    own = sha256_bytes(raw)
    if own in text:
        raise RuntimeError("release notes must not self-embed their own SHA-256")


def optional_lean_check(files: dict[str, bytes], contract: dict[str, object], lake: str) -> None:
    formal = contract["formalization"]
    prefix = f"{formal['directory']}/"
    with tempfile.TemporaryDirectory(prefix="uft-id-archived-lean-") as temporary:
        root = Path(temporary)
        for name, data in files.items():
            if not name.startswith(prefix):
                continue
            rel = PurePosixPath(name[len(prefix):])
            target = root.joinpath(*rel.parts)
            target.parent.mkdir(parents=True, exist_ok=True)
            target.write_bytes(data)
        subprocess.run([lake, "update"], cwd=root, check=True)
        subprocess.run([lake, "exe", "cache", "get"], cwd=root, check=True)
        subprocess.run([lake, "build", "UFTID"], cwd=root, check=True)
        subprocess.run(["python", "scripts/verify_lean_observation_axioms.py", "--lake", lake], cwd=root, check=True)


def verify(directory: Path, *, lake: str | None = None) -> dict[str, object]:
    contract = load_contract()
    surface = contract["publication_surface"]
    expected_names = {str(surface["source_zip"]), str(surface["overview_pdf"]), str(surface["release_notes"])}
    entries = list(directory.iterdir())
    observed_names = {entry.name for entry in entries}
    if observed_names != expected_names:
        raise RuntimeError(f"outer publication surface drift: {sorted(observed_names)}")
    for entry in entries:
        if entry.is_symlink() or not entry.is_file():
            raise RuntimeError(f"outer publication surface contains non-regular entry: {entry.name}")

    source_zip = directory / str(surface["source_zip"])
    overview_pdf = directory / str(surface["overview_pdf"])
    notes = directory / str(surface["release_notes"])
    if source_zip.stat().st_size > MAX_OUTER_ZIP_BYTES:
        raise RuntimeError("source ZIP exceeds outer size bound")
    if overview_pdf.stat().st_size > MAX_OUTER_PDF_BYTES:
        raise RuntimeError("Overview PDF exceeds size bound")
    if notes.stat().st_size > MAX_OUTER_NOTES_BYTES:
        raise RuntimeError("RELEASE-NOTES.md exceeds size bound")

    verify_git_provenance(contract)
    files = read_zip(source_zip, contract)
    verify_manifest(files, contract)
    verify_internal_sums(files)
    compare_git_layers(files, contract)
    verify_package_definition(files, contract)
    verify_verification_record(files, contract)
    verify_pdf(overview_pdf, contract)
    verify_release_notes(notes, source_zip, overview_pdf, contract)
    if lake is not None:
        optional_lean_check(files, contract, lake)

    return {
        "status": "ok",
        "doi": contract["doi"],
        "artifacts": {
            source_zip.name: sha256_file(source_zip),
            overview_pdf.name: sha256_file(overview_pdf),
            notes.name: sha256_file(notes),
        },
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("directory", type=Path)
    parser.add_argument("--lake")
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args()
    result = verify(args.directory.resolve(), lake=args.lake)
    if args.json:
        print(json.dumps(result, indent=2, sort_keys=True))
    else:
        print(f"UFT-ID scholarly archive verification: ok ({result['doi']})")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
