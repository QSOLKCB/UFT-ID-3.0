#!/usr/bin/env python3
"""Build deterministic UFT-ID 3.0 Zenodo scholarly artifacts."""
from __future__ import annotations

import argparse
import hashlib
import json
import subprocess
import tarfile
import tempfile
import textwrap
import zipfile
from pathlib import Path, PurePosixPath

ROOT = Path(__file__).resolve().parents[1]
CONTRACT_PATH = ROOT / "machine/scholarly_archive_contract.json"
OVERVIEW_SOURCE = ROOT / "docs/ZENODO-OVERVIEW.md"
FIXED_ZIP_DT = (1980, 1, 1, 0, 0, 0)
FIXED_PDF_DATE = "D:20260826000000Z"
MAX_GIT_MEMBERS = 10000
MAX_FILE_BYTES = 64 * 1024 * 1024
MAX_TOTAL_BYTES = 256 * 1024 * 1024


def load_contract() -> dict[str, object]:
    value = json.loads(CONTRACT_PATH.read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise RuntimeError("scholarly archive contract must be a JSON object")
    return value


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


def sha256_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def sha256_file(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as fh:
        for chunk in iter(lambda: fh.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def safe_git_path(name: str) -> PurePosixPath:
    if not name or "\\" in name or "\x00" in name:
        raise RuntimeError(f"unsafe Git archive path: {name!r}")
    path = PurePosixPath(name.rstrip("/"))
    if path.is_absolute() or not path.parts or ".." in path.parts:
        raise RuntimeError(f"unsafe Git archive path: {name}")
    if path.as_posix() != name.rstrip("/"):
        raise RuntimeError(f"non-canonical Git archive path: {name}")
    return path


def assert_git_bindings(contract: dict[str, object]) -> None:
    source = contract["source_release"]
    formal = contract["formalization"]
    if not isinstance(source, dict) or not isinstance(formal, dict):
        raise RuntimeError("archive contract source/formalization sections are malformed")
    tag = str(source["tag"])
    commit = str(source["commit"])
    tree = str(source["tree"])
    if run_git("rev-parse", f"{tag}^{{commit}}") != commit:
        raise RuntimeError(f"{tag} does not resolve to the bound source commit")
    if run_git("rev-parse", f"{commit}^{{tree}}") != tree:
        raise RuntimeError("bound source commit tree drifted")
    promotion = str(formal["verification_promotion_commit"])
    if run_git("rev-parse", f"{promotion}^{{commit}}") != promotion:
        raise RuntimeError("verification-promotion commit is unavailable or ambiguous")


def git_archive_files(ref: str, paths: list[str] | None = None) -> dict[str, bytes]:
    with tempfile.NamedTemporaryFile(prefix="uft-id-archive-", suffix=".tar", delete=False) as tmp:
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
            if len(members) > MAX_GIT_MEMBERS:
                raise RuntimeError("Git archive exceeds member-count bound")
            for member in members:
                path = safe_git_path(member.name)
                if member.isdir():
                    continue
                if not member.isfile():
                    raise RuntimeError(f"Git archive contains non-regular member: {path}")
                if member.size > MAX_FILE_BYTES:
                    raise RuntimeError(f"Git archive member exceeds size bound: {path}")
                total += member.size
                if total > MAX_TOTAL_BYTES:
                    raise RuntimeError("Git archive exceeds total expanded-size bound")
                source = tf.extractfile(member)
                if source is None:
                    raise RuntimeError(f"could not read Git archive member: {path}")
                data = source.read(MAX_FILE_BYTES + 1)
                if len(data) != member.size:
                    raise RuntimeError(f"Git archive member size mismatch: {path}")
                result[path.as_posix()] = data
        return result
    finally:
        tar_path.unlink(missing_ok=True)


def write_layer(base: Path, prefix: str, files: dict[str, bytes]) -> None:
    for rel in sorted(files, key=lambda value: PurePosixPath(value).parts):
        target = base / prefix / rel
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_bytes(files[rel])


def iter_stage_files(stage: Path, *, include_sums: bool = True) -> list[Path]:
    paths = [p for p in stage.rglob("*") if p.is_file() and not p.is_symlink()]
    if not include_sums:
        paths = [p for p in paths if p.name != "SHA256SUMS"]
    return sorted(paths, key=lambda p: PurePosixPath(p.relative_to(stage).as_posix()).parts)


def write_internal_sums(stage: Path) -> None:
    rows = []
    for path in iter_stage_files(stage, include_sums=False):
        rel = path.relative_to(stage).as_posix()
        if rel == "ARCHIVE-MANIFEST.json":
            continue
        rows.append(f"{sha256_file(path)}  {rel}")
    (stage / "SHA256SUMS").write_text("\n".join(rows) + "\n", encoding="utf-8")


def manifest_files(stage: Path) -> list[dict[str, object]]:
    rows: list[dict[str, object]] = []
    for path in iter_stage_files(stage):
        rel = path.relative_to(stage).as_posix()
        if rel == "ARCHIVE-MANIFEST.json":
            continue
        rows.append({"path": rel, "bytes": path.stat().st_size, "sha256": sha256_file(path)})
    return rows


def write_archive_manifest(stage: Path, contract: dict[str, object]) -> None:
    source = contract["source_release"]
    formal = contract["formalization"]
    metadata = contract["zenodo_metadata"]
    surface = contract["publication_surface"]
    payload = {
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
        "files": manifest_files(stage),
    }
    (stage / "ARCHIVE-MANIFEST.json").write_text(
        json.dumps(payload, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )


def deterministic_zip(stage: Path, output: Path) -> None:
    with zipfile.ZipFile(output, "w", compression=zipfile.ZIP_DEFLATED, compresslevel=9) as zf:
        for path in iter_stage_files(stage):
            rel = path.relative_to(stage).as_posix()
            info = zipfile.ZipInfo(rel, FIXED_ZIP_DT)
            info.compress_type = zipfile.ZIP_DEFLATED
            info.external_attr = (0o100644 & 0xFFFF) << 16
            info.create_system = 3
            zf.writestr(info, path.read_bytes(), compress_type=zipfile.ZIP_DEFLATED, compresslevel=9)


def pdf_escape(text: str) -> str:
    return text.replace("\\", "\\\\").replace("(", "\\(").replace(")", "\\)")


def overview_pages(source: str) -> list[list[str]]:
    pages: list[list[str]] = [[]]
    for raw in source.splitlines():
        line = raw.strip()
        if line == "<!-- PAGEBREAK -->":
            if pages[-1]:
                pages.append([])
            continue
        if not line:
            if pages[-1] and pages[-1][-1] != "":
                pages[-1].append("")
            continue
        if line.startswith("#"):
            line = line.lstrip("#").strip().upper()
        width = 86 if len(line) > 86 else 92
        wrapped = textwrap.wrap(line, width=width, break_long_words=True, break_on_hyphens=False) or [""]
        pages[-1].extend(wrapped)
    pages = [page for page in pages if page]
    if len(pages) < 5:
        raise RuntimeError("overview source must render at least five deterministic pages")
    for page in pages:
        if len(page) > 57:
            raise RuntimeError("overview page exceeds deterministic line budget")
    return pages


def build_pdf_bytes(source: str, *, title: str) -> bytes:
    pages = overview_pages(source)
    objects: list[bytes] = []
    page_obj_numbers = [4 + 2 * i for i in range(len(pages))]
    objects.append(b"<< /Type /Catalog /Pages 2 0 R >>")
    kids = " ".join(f"{n} 0 R" for n in page_obj_numbers)
    objects.append(f"<< /Type /Pages /Kids [{kids}] /Count {len(pages)} >>".encode("ascii"))
    objects.append(b"<< /Type /Font /Subtype /Type1 /BaseFont /Helvetica >>")
    for index, lines in enumerate(pages):
        page_no = 4 + 2 * index
        content_no = page_no + 1
        page_obj = (
            f"<< /Type /Page /Parent 2 0 R /MediaBox [0 0 595 842] "
            f"/Resources << /Font << /F1 3 0 R >> >> /Contents {content_no} 0 R >>"
        ).encode("ascii")
        commands = ["BT", "/F1 9 Tf", "50 792 Td", "12 TL"]
        for line in lines:
            commands.append(f"({pdf_escape(line)}) Tj")
            commands.append("T*")
        commands.append("ET")
        stream = ("\n".join(commands) + "\n").encode("ascii")
        content_obj = b"<< /Length " + str(len(stream)).encode("ascii") + b" >>\nstream\n" + stream + b"endstream"
        objects.extend([page_obj, content_obj])
    info_no = len(objects) + 1
    info = (
        f"<< /Title ({pdf_escape(title)}) /Producer (UFT-ID deterministic stdlib PDF writer) "
        f"/CreationDate ({FIXED_PDF_DATE}) /ModDate ({FIXED_PDF_DATE}) >>"
    ).encode("ascii")
    objects.append(info)

    out = bytearray(b"%PDF-1.4\n%UFTID\n")
    offsets = [0]
    for number, obj in enumerate(objects, start=1):
        offsets.append(len(out))
        out.extend(f"{number} 0 obj\n".encode("ascii"))
        out.extend(obj)
        out.extend(b"\nendobj\n")
    xref = len(out)
    out.extend(f"xref\n0 {len(objects)+1}\n".encode("ascii"))
    out.extend(b"0000000000 65535 f \n")
    for offset in offsets[1:]:
        out.extend(f"{offset:010d} 00000 n \n".encode("ascii"))
    out.extend(
        (
            f"trailer\n<< /Size {len(objects)+1} /Root 1 0 R /Info {info_no} 0 R >>\n"
            f"startxref\n{xref}\n%%EOF\n"
        ).encode("ascii")
    )
    return bytes(out)


def release_notes_text(contract: dict[str, object], zip_path: Path, pdf_path: Path) -> str:
    zip_sha = sha256_file(zip_path)
    pdf_sha = sha256_file(pdf_path)
    source = contract["source_release"]
    formal = contract["formalization"]
    return f"""# UFT-ID 3.0 Scholarly Archive Release Notes\n\nVersion: {contract['version']}\nZenodo DOI: {contract['doi']}\nRepository: {contract['repository']}\n\n## Publication surface\n\n- `{zip_path.name}`\n  - SHA-256: `{zip_sha}`\n- `{pdf_path.name}`\n  - SHA-256: `{pdf_sha}`\n- `RELEASE-NOTES.md`\n  - its uploaded checksum is recorded independently by Zenodo; this file does not self-embed its own hash.\n\n## Provenance\n\nThe source archive contains two explicitly separate layers:\n\n- `reference-v3.0.0/`: exact immutable source tag `{source['tag']}`, commit `{source['commit']}`, tree `{source['tree']}`.\n- `formal/`: selected verified post-tag Lean layer from promotion commit `{formal['verification_promotion_commit']}`; formalization integration commit `{formal['integration_commit']}` remains separately recorded.\n\n`UFT-OBS-001` through `UFT-OBS-004` are `LEAN-OBS-BATCH-001`. `UFT-OBS-005` is the separately registered arithmetic `LEAN-OBS-BATCH-002`. The historical v3.0.0 batch-001 deferral of UFT-OBS-005 is preserved as history and is not a current deferral.\n\n## Toolchain\n\n- Lean: `{formal['toolchain']['lean']}`\n- Lake: `{formal['toolchain']['lake']}`\n- mathlib: `{formal['toolchain']['mathlib_commit']}`\n- Lean archive SHA-256: `{formal['toolchain']['lean_archive_sha256']}`\n\n## Licensing\n\nThe Zenodo scholarly record/overview uses Creative Commons Attribution 4.0 International as configured in Zenodo. Software source bytes retain the repository's MIT License. The archive records these as separate licensing domains.\n\n## Claim boundary\n\n`LEAN_VERIFIED != COMPLETE_SOFTWARE_FORMAL_VERIFICATION`\n\n`LEAN_PROOF != EMPIRICAL_VALIDATION`\n\n`SOURCE_RELEASE != LATER_LEAN_FORMALIZATION_LAYER`\n\n`CHECKSUM_MATCH != SEMANTIC_TRUTH`\n"""


def build(output_dir: Path) -> dict[str, object]:
    contract = load_contract()
    assert_git_bindings(contract)
    surface = contract["publication_surface"]
    source = contract["source_release"]
    formal = contract["formalization"]
    if not isinstance(surface, dict) or not isinstance(source, dict) or not isinstance(formal, dict):
        raise RuntimeError("archive contract publication/source/formalization sections are malformed")

    output_dir.mkdir(parents=True, exist_ok=True)
    zip_path = output_dir / str(surface["source_zip"])
    pdf_path = output_dir / str(surface["overview_pdf"])
    notes_path = output_dir / str(surface["release_notes"])

    with tempfile.TemporaryDirectory(prefix="uft-id-scholarly-stage-") as temporary:
        stage = Path(temporary)
        reference_files = git_archive_files(str(source["commit"]))
        formal_paths = [str(value) for value in formal["archive_paths"]]
        formal_files = git_archive_files(str(formal["verification_promotion_commit"]), formal_paths)
        write_layer(stage, str(source["directory"]), reference_files)
        write_layer(stage, str(formal["directory"]), formal_files)
        write_internal_sums(stage)
        write_archive_manifest(stage, contract)
        deterministic_zip(stage, zip_path)

    overview = OVERVIEW_SOURCE.read_text(encoding="utf-8")
    pdf_path.write_bytes(build_pdf_bytes(overview, title="UFT-ID 3.0 Lean 4 Observation Formalization"))
    notes_path.write_text(release_notes_text(contract, zip_path, pdf_path), encoding="utf-8")

    return {
        "status": "ok",
        "doi": contract["doi"],
        "artifacts": {
            zip_path.name: {"bytes": zip_path.stat().st_size, "sha256": sha256_file(zip_path)},
            pdf_path.name: {"bytes": pdf_path.stat().st_size, "sha256": sha256_file(pdf_path)},
            notes_path.name: {"bytes": notes_path.stat().st_size, "sha256": sha256_file(notes_path)},
        },
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path, default=ROOT / "artifacts/zenodo")
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args()
    result = build(args.output.resolve())
    if args.json:
        print(json.dumps(result, indent=2, sort_keys=True))
    else:
        print(f"UFT-ID scholarly archive build: ok ({result['doi']})")
        for name, info in result["artifacts"].items():
            print(f"{info['sha256']}  {name}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
