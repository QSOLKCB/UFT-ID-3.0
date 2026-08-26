from __future__ import annotations

import importlib.util
import json
import os
from pathlib import Path
import subprocess
import struct
import sys
import tempfile
import unittest
from unittest import mock
import zipfile

ROOT = Path(__file__).resolve().parents[1]
PUBLICATION_SOURCE_COMMIT = "9bffc6b59ba109824079dd00d87ab39993ad7f93"
PUBLICATION_SOURCE_TREE = "b98895d3720bf757b5f78758f8879d6c9cf916cc"


def load_module(name: str, relative_path: str):
    spec = importlib.util.spec_from_file_location(name, ROOT / relative_path)
    if spec is None or spec.loader is None:
        raise RuntimeError("cannot load reproduction module")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


REPRODUCE = load_module("reproduce_scholarly_archive", "scripts/reproduce_scholarly_archive.py")
VERIFY = load_module("verify_scholarly_archive_for_reproduction_tests", "scripts/verify_scholarly_archive.py")


def add_member(zf: zipfile.ZipFile, name: str, data: bytes) -> None:
    info = zipfile.ZipInfo(name, (1980, 1, 1, 0, 0, 0))
    info.compress_type = zipfile.ZIP_DEFLATED
    info.external_attr = (0o100644 & 0xFFFF) << 16
    info.create_system = 3
    zf.writestr(info, data, compress_type=zipfile.ZIP_DEFLATED, compresslevel=9)


def set_eocd_member_count(path: Path, count: int) -> None:
    data = bytearray(path.read_bytes())
    offset = data.rfind(REPRODUCE.EOCD_SIGNATURE)
    if offset < 0:
        raise RuntimeError("test ZIP has no EOCD record")
    struct.pack_into("<H", data, offset + 8, count)
    struct.pack_into("<H", data, offset + 10, count)
    path.write_bytes(data)


def build_canonical_surface(destination: Path) -> None:
    subprocess.run(
        [
            sys.executable,
            str(ROOT / "scripts/build_scholarly_archive.py"),
            "--output",
            str(destination),
            "--json",
        ],
        cwd=ROOT,
        check=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
    )


class ScholarlyArchiveReproductionTests(unittest.TestCase):
    def test_contract_binds_merged_publication_authority(self):
        contract = json.loads((ROOT / "machine/scholarly_archive_reproduction_contract.json").read_text(encoding="utf-8"))
        self.assertEqual(contract["doi"], "10.5281/zenodo.22108865")
        self.assertEqual(contract["publication_source"]["merge_commit"], PUBLICATION_SOURCE_COMMIT)
        self.assertEqual(contract["publication_source"]["merge_tree"], PUBLICATION_SOURCE_TREE)
        self.assertEqual(contract["publication_surface"]["exact_files"], ["UFT-ID-3.0.0-source.zip", "UFT-ID-v3.0.0-Overview.pdf", "RELEASE-NOTES.md"])
        self.assertEqual(contract["pipeline"]["canonical_publication_python"], "3.12")

    def test_workflow_builds_from_detached_merged_main_and_retains_one_canonical_surface(self):
        text = (ROOT / ".github/workflows/publication-reproduction.yml").read_text(encoding="utf-8")
        self.assertIn(f"UFT_PUBLICATION_SOURCE_COMMIT: {PUBLICATION_SOURCE_COMMIT}", text)
        self.assertIn('git worktree add --detach "$publication_root" "$UFT_PUBLICATION_SOURCE_COMMIT"', text)
        self.assertIn('python "$publication_root/scripts/build_scholarly_archive.py"', text)
        self.assertIn('python "$publication_root/scripts/verify_scholarly_archive.py"', text)
        self.assertIn("scripts/reproduce_scholarly_archive.py", text)
        self.assertIn("path: artifacts/zenodo/", text)
        self.assertIn("name: uft-id-zenodo-publication", text)
        self.assertNotIn("actions/download-artifact@", text)

    def test_formal_extraction_is_prefix_scoped_and_requires_authority_files(self):
        required = {"lean-toolchain": b"leanprover/lean4:v4.33.1\n", "lakefile.toml": b'name = "UFTID"\n', "UFTID.lean": b"import UFTID.Observation.Basic\n", "machine/lean_observation_verification.json": b'{"status":"LEAN_VERIFIED"}\n', "scripts/verify_lean_observation_axioms.py": b"print('audit')\n", "UFTID/Observation/Basic.lean": b"theorem x : True := by trivial\n"}
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            source_zip = root / "source.zip"
            with zipfile.ZipFile(source_zip, "w") as zf:
                add_member(zf, "reference-v3.0.0/README.md", b"reference\n")
                for name, data in required.items():
                    add_member(zf, f"formal/{name}", data)
            members = REPRODUCE.extract_formal_layer(source_zip, root / "formal")
            self.assertEqual(set(members), set(required))
            self.assertFalse((root / "formal" / "README.md").exists())

    def test_formal_extraction_rejects_parent_escape(self):
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            source_zip = root / "source.zip"
            with zipfile.ZipFile(source_zip, "w") as zf:
                add_member(zf, "formal/../escape.txt", b"escape\n")
            with self.assertRaisesRegex(RuntimeError, "unsafe ZIP path"):
                REPRODUCE.extract_formal_layer(source_zip, root / "formal")

    def test_formal_extraction_rejects_too_many_outer_members_before_zipfile_processing(self):
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            source_zip = root / "source.zip"
            with zipfile.ZipFile(source_zip, "w") as zf:
                for index in range(5):
                    add_member(zf, f"noise/{index}.txt", b"")
            with mock.patch.object(REPRODUCE, "MAX_ZIP_MEMBERS", 4):
                with self.assertRaisesRegex(RuntimeError, "member count outside allowed bounds"):
                    REPRODUCE.extract_formal_layer(source_zip, root / "formal")

    def test_member_preflight_counts_actual_central_directory_records(self):
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            source_zip = root / "source.zip"
            with zipfile.ZipFile(source_zip, "w") as zf:
                for index in range(5):
                    add_member(zf, f"noise/{index}.txt", b"")

            set_eocd_member_count(source_zip, 1)
            with self.assertRaisesRegex(
                RuntimeError,
                "central-directory member count disagrees with EOCD",
            ):
                REPRODUCE.bounded_zip_member_count(source_zip)

            with mock.patch.object(REPRODUCE.zipfile, "ZipFile") as zip_constructor:
                with self.assertRaisesRegex(
                    RuntimeError,
                    "central-directory member count disagrees with EOCD",
                ):
                    REPRODUCE.extract_formal_layer(source_zip, root / "formal")
                zip_constructor.assert_not_called()

    def test_authentication_preflights_zip_before_launching_detached_verifier(self):
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            source_zip = root / REPRODUCE.SOURCE_ZIP_NAME
            with zipfile.ZipFile(source_zip, "w") as zf:
                for index in range(5):
                    add_member(zf, f"noise/{index}.txt", b"")
            names = [REPRODUCE.SOURCE_ZIP_NAME, "UFT-ID-v3.0.0-Overview.pdf", "RELEASE-NOTES.md"]
            for name in names[1:]:
                (root / name).write_bytes(b"x")
            with mock.patch.object(REPRODUCE, "MAX_ZIP_MEMBERS", 4), mock.patch.object(REPRODUCE.subprocess, "run") as run:
                with self.assertRaisesRegex(RuntimeError, "member count outside allowed bounds"):
                    REPRODUCE.authenticate_publication_surface(root, PUBLICATION_SOURCE_COMMIT, names)
                run.assert_not_called()

    def test_publication_surface_rejects_extra_outer_entry(self):
        names = ["UFT-ID-3.0.0-source.zip", "UFT-ID-v3.0.0-Overview.pdf", "RELEASE-NOTES.md"]
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            for name in names:
                (root / name).write_bytes(b"x")
            (root / "extra").mkdir()
            with self.assertRaisesRegex(RuntimeError, "publication surface drift"):
                REPRODUCE.artifact_surface(root, names)

    def test_rejects_all_report_outputs_inside_protected_publication_directory(self):
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            for output in (root / "receipt.json", root / "nested" / "axioms.json"):
                with self.assertRaisesRegex(RuntimeError, "outside protected publication directory"):
                    REPRODUCE.reject_publication_output_aliases(root, output)
            safe = root.parent / "receipt.json"
            REPRODUCE.reject_publication_output_aliases(root, safe)

    def test_rejects_hard_linked_report_output_outside_publication_directory(self):
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary) / "zenodo"
            root.mkdir()
            protected = root / "RELEASE-NOTES.md"
            protected.write_text("sentinel\n", encoding="utf-8")
            external_alias = root.parent / "receipt.json"
            os.link(protected, external_alias)

            with self.assertRaisesRegex(
                RuntimeError,
                "hard-link aliases protected publication artifact",
            ):
                REPRODUCE.reject_publication_output_aliases(root, external_alias)

            self.assertTrue(os.path.samestat(protected.stat(), external_alias.stat()))

    def test_main_does_not_overwrite_publication_artifact_on_json_output_alias(self):
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            protected = root / "RELEASE-NOTES.md"
            protected.write_text("sentinel\n", encoding="utf-8")
            argv = [
                "reproduce_scholarly_archive.py",
                str(root),
                "--lake",
                "lake",
                "--publication-source-commit",
                PUBLICATION_SOURCE_COMMIT,
                "--json-out",
                str(protected),
                "--axiom-json-out",
                str(root.parent / "axioms.json"),
            ]
            with mock.patch.object(sys, "argv", argv):
                self.assertEqual(REPRODUCE.main(), 1)
            self.assertEqual(protected.read_text(encoding="utf-8"), "sentinel\n")

    def test_exact_canonical_digest_comparison_rejects_byte_different_artifact(self):
        canonical = {"UFT-ID-v3.0.0-Overview.pdf": {"bytes": 3, "sha256": "a"}}
        altered = {"UFT-ID-v3.0.0-Overview.pdf": {"bytes": 4, "sha256": "b"}}
        with self.assertRaisesRegex(RuntimeError, "does not match canonical authority bytes"):
            REPRODUCE.require_exact_artifact_digests(altered, canonical)

    def test_canonical_rebuild_rejects_alternate_pdf_that_semantic_verifier_accepts(self):
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            build_canonical_surface(root)
            source_zip = root / REPRODUCE.SOURCE_ZIP_NAME
            overview = root / "UFT-ID-v3.0.0-Overview.pdf"
            notes = root / "RELEASE-NOTES.md"
            data = overview.read_bytes()
            self.assertIn(b"%%EOF", data)
            overview.write_bytes(data.replace(b"%%EOF", b"% alternate-byte-surface\n%%EOF", 1))
            contract = VERIFY.load_contract()
            notes.write_text(
                VERIFY.expected_release_notes_text(contract, source_zip, overview),
                encoding="utf-8",
            )
            self.assertEqual(VERIFY.verify(root)["status"], "ok")
            with self.assertRaisesRegex(RuntimeError, "does not match canonical authority bytes"):
                REPRODUCE.authenticate_publication_surface(
                    root,
                    PUBLICATION_SOURCE_COMMIT,
                    [REPRODUCE.SOURCE_ZIP_NAME, "UFT-ID-v3.0.0-Overview.pdf", "RELEASE-NOTES.md"],
                )

    def test_runtime_toolchain_mismatch_fails_closed(self):
        toolchain = REPRODUCE.load_contract()["lean_toolchain"]
        REPRODUCE.validate_runtime_toolchain("Lean (version 4.33.1, x86_64-unknown-linux-gnu, commit deadbeef, Release)", "Lake version 5.0.0-src+819816b (Lean version 4.33.1)", toolchain)
        with self.assertRaisesRegex(RuntimeError, "runtime Lean version mismatch"):
            REPRODUCE.validate_runtime_toolchain("Lean (version 4.32.0, x86_64-unknown-linux-gnu, commit deadbeef, Release)", "Lake version 5.0.0-src+819816b (Lean version 4.32.0)", toolchain)

    def test_reproducer_rejects_wrong_publication_source_before_execution(self):
        with tempfile.TemporaryDirectory() as temporary:
            with self.assertRaisesRegex(RuntimeError, "publication source commit does not match"):
                REPRODUCE.reproduce(Path(temporary), lake="lake", publication_source_commit="0" * 40, axiom_json_out=Path(temporary).parent / "axioms.json")


if __name__ == "__main__":
    unittest.main()
