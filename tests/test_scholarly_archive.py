from __future__ import annotations

import importlib.util
import json
from pathlib import Path
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[1]


def load_module(name: str, rel: str):
    path = ROOT / rel
    spec = importlib.util.spec_from_file_location(name, path)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"cannot load {path}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


BUILD = load_module("build_scholarly_archive", "scripts/build_scholarly_archive.py")
VERIFY = load_module("verify_scholarly_archive", "scripts/verify_scholarly_archive.py")


class ScholarlyArchiveTests(unittest.TestCase):
    def test_contract_binds_reserved_doi_and_distinct_licenses(self):
        contract = json.loads((ROOT / "machine/scholarly_archive_contract.json").read_text())
        self.assertEqual(contract["doi"], "10.5281/zenodo.22108865")
        self.assertEqual(contract["status"], "DOI_RESERVED_ARCHIVE_CONSTRUCTION")
        self.assertEqual(contract["zenodo_metadata"]["record_license"], "CC-BY-4.0")
        self.assertEqual(contract["zenodo_metadata"]["software_source_license"], "MIT")
        self.assertEqual(contract["formalization"]["verification_promotion_commit"], "328785f7f23ed4ab246ecec1a3419c2a6ef126c0")
        self.assertEqual([row["id"] for row in contract["formalization"]["theorems"]], [
            "UFT-OBS-001", "UFT-OBS-002", "UFT-OBS-003", "UFT-OBS-004", "UFT-OBS-005",
        ])

    def test_build_is_byte_deterministic_and_verifies(self):
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            first = root / "first"
            second = root / "second"
            result_a = BUILD.build(first)
            result_b = BUILD.build(second)
            self.assertEqual(result_a["doi"], "10.5281/zenodo.22108865")
            self.assertEqual(result_a["artifacts"], result_b["artifacts"])
            for name in result_a["artifacts"]:
                self.assertEqual((first / name).read_bytes(), (second / name).read_bytes())
            verified = VERIFY.verify(first)
            self.assertEqual(verified["status"], "ok")
            self.assertEqual(verified["doi"], "10.5281/zenodo.22108865")

    def test_extra_outer_file_is_rejected(self):
        with tempfile.TemporaryDirectory() as temporary:
            output = Path(temporary)
            BUILD.build(output)
            (output / "unexpected.txt").write_text("not part of the publication surface\n", encoding="utf-8")
            with self.assertRaisesRegex(RuntimeError, "outer publication surface drift"):
                VERIFY.verify(output)

    def test_pdf_tamper_is_rejected(self):
        with tempfile.TemporaryDirectory() as temporary:
            output = Path(temporary)
            BUILD.build(output)
            pdf = output / "UFT-ID-v3.0.0-Overview.pdf"
            pdf.write_bytes(pdf.read_bytes().replace(b"10.5281/zenodo.22108865", b"10.5281/zenodo.00000000", 1))
            with self.assertRaisesRegex(RuntimeError, "Overview PDF missing required identity text"):
                VERIFY.verify(output)

    def test_release_notes_do_not_self_hash(self):
        with tempfile.TemporaryDirectory() as temporary:
            output = Path(temporary)
            BUILD.build(output)
            notes = output / "RELEASE-NOTES.md"
            text = notes.read_text(encoding="utf-8")
            digest = BUILD.sha256_file(notes)
            self.assertNotIn(digest, text)
            self.assertIn("UFT-ID-3.0.0-source.zip", text)
            self.assertIn("UFT-ID-v3.0.0-Overview.pdf", text)


if __name__ == "__main__":
    unittest.main()
