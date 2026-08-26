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


def sha256_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def sha256_file(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as fh:
        for chunk in iter(lambda: fh.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def load_contract() -> dict[str, object]:
    value = json.loads(CONTRACT_PATH.read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise RuntimeError("scholarly archive contract must be a JSON object")
    return value


def run_git(*args: str) -> str:
    cp = subprocess.run(
        ["git", *args], cwd=ROOT, check=True, text=True,
        stdout=subprocess.PIPE, stderr=subprocess.PIPE,
    )
    return cp.stdout.strip()


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
    try:
        manifest = json.loads(raw.decode("utf-8"))
    except (UnicodeDecodeError, json.JSONDecodeError) as exc:
        raise RuntimeError("ARCHIVE-MANIFEST.json is not valid UTF-8 JSON") from exc
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
            "final_reviewed_head": formal["final_reviewed_head"],
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


def verify_verification_record(files: dict[str, bytes], contract: dict[str, object]) -> None:
    formal = contract["formalization"]
    name = f"{formal['directory']}/machine/lean_observation_verification.json"
    raw = files.get(name)
    if raw is None:
        raise RuntimeError("formal layer missing Lean verification record")
    record = json.loads(raw.decode("utf-8"))
    if record.get("status") != "LEAN_VERIFIED":
        raise RuntimeError("archived Lean verification record is not LEAN_VERIFIED")
    expected = [(row["id"], row["source_blob_sha"]) for row in formal["theorems"]]
    observed = [(row.get("id"), row.get("source_blob_sha")) for row in record.get("theorems", [])]
    if observed != expected:
        raise RuntimeError("archived theorem/source-blob inventory drift")
    if record.get("current_deferred_theorem_ids") != []:
        raise RuntimeError("archived verification record has a current deferred theorem")


def verify_pdf(path: Path, contract: dict[str, object]) -> None:
    data = path.read_bytes()
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
        "UFT-OBS-005", "LEAN_VERIFIED", "CC BY 4.0", "MIT",
    ]
    text = data.decode("latin-1")
    for needle in required:
        if needle not in text:
            raise RuntimeError(f"Overview PDF missing required identity text: {needle}")


def verify_release_notes(notes: Path, source_zip: Path, overview_pdf: Path, contract: dict[str, object]) -> None:
    text = notes.read_text(encoding="utf-8")
    required = [
        str(contract["doi"]), source_zip.name, overview_pdf.name,
        sha256_file(source_zip), sha256_file(overview_pdf),
        "SOURCE_RELEASE != LATER_LEAN_FORMALIZATION_LAYER",
        "CC BY 4.0", "MIT",
    ]
    for needle in required:
        if needle not in text:
            raise RuntimeError(f"release notes missing required text: {needle}")
    own = sha256_file(notes)
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
    observed_names = {path.name for path in directory.iterdir() if path.is_file()}
    if observed_names != expected_names:
        raise RuntimeError(f"outer publication surface drift: {sorted(observed_names)}")

    source_zip = directory / str(surface["source_zip"])
    overview_pdf = directory / str(surface["overview_pdf"])
    notes = directory / str(surface["release_notes"])

    source = contract["source_release"]
    formal = contract["formalization"]
    if run_git("rev-parse", f"{source['tag']}^{{commit}}") != str(source["commit"]):
        raise RuntimeError("source tag no longer resolves to bound commit")
    if run_git("rev-parse", f"{source['commit']}^{{tree}}") != str(source["tree"]):
        raise RuntimeError("source tree binding drift")
    if run_git("rev-parse", f"{formal['verification_promotion_commit']}^{{commit}}") != str(formal["verification_promotion_commit"]):
        raise RuntimeError("verification-promotion commit unavailable")

    files = read_zip(source_zip, contract)
    verify_manifest(files, contract)
    verify_internal_sums(files)
    compare_git_layers(files, contract)
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
