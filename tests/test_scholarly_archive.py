from __future__ import annotations

import copy
import importlib.util
import json
from pathlib import Path
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[1]
SOURCE_COMMIT = "b7f51590985e60920c8b09fc9238b8aec6cfa3bc"
PROMOTION_COMMIT = "328785f7f23ed4ab246ecec1a3419c2a6ef126c0"
REVIEWED_COMMIT = "111a9c7a0b6d26c999eb941f9c25f5c0f5176ed5"
FINAL_PR_HEAD = "c32aaff36219961e3ec2a4e479ccdec521795bbe"


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
    def contract(self):
        return json.loads((ROOT / "machine/scholarly_archive_contract.json").read_text())

    def test_contract_binds_reserved_doi_distinct_licenses_and_review_provenance(self):
        contract = self.contract()
        self.assertEqual(contract["doi"], "10.5281/zenodo.22108865")
        self.assertEqual(contract["status"], "DOI_RESERVED_ARCHIVE_CONSTRUCTION")
        self.assertEqual(contract["zenodo_metadata"]["record_license"], "CC-BY-4.0")
        self.assertEqual(contract["zenodo_metadata"]["software_source_license"], "MIT")
        formal = contract["formalization"]
        self.assertEqual(formal["verification_promotion_commit"], PROMOTION_COMMIT)
        self.assertEqual(formal["codex_no_major_issues_reviewed_commit"], REVIEWED_COMMIT)
        self.assertEqual(formal["final_pr_head"], FINAL_PR_HEAD)
        self.assertNotEqual(formal["codex_no_major_issues_reviewed_commit"], formal["final_pr_head"])
        self.assertIn("lakefile.toml", formal["archive_paths"])
        self.assertNotIn("lakefile.lean", formal["archive_paths"])
        self.assertNotIn("lake-manifest.json", formal["archive_paths"])
        self.assertEqual([row["id"] for row in formal["theorems"]], [
            "UFT-OBS-001", "UFT-OBS-002", "UFT-OBS-003", "UFT-OBS-004", "UFT-OBS-005",
        ])

    def test_finite_workflow_fetches_full_history_for_archive_tests(self):
        workflow = (ROOT / ".github/workflows/finite-adversarial.yml").read_text(encoding="utf-8")
        checkout = (
            "- uses: actions/checkout@d23441a48e516b6c34aea4fa41551a30e30af803 # v6\n"
            "        with:\n"
            "          persist-credentials: false\n"
            "          fetch-depth: 0\n"
        )
        self.assertIn(checkout, workflow)

    def test_package_definition_is_linked_to_archive_toolchain_contract(self):
        contract = self.contract()
        formal = contract["formalization"]
        prefix = f"{formal['directory']}/"
        files = {
            f"{prefix}lean-toolchain": b"leanprover/lean4:v4.33.1\n",
            f"{prefix}lakefile.toml": (
                'name = "UFTID"\n'
                'version = "3.0.0"\n'
                'defaultTargets = ["UFTID"]\n\n'
                '[leanOptions]\n'
                'autoImplicit = false\n'
                'relaxedAutoImplicit = false\n\n'
                '[[require]]\n'
                'name = "mathlib"\n'
                'git = "https://github.com/leanprover-community/mathlib4.git"\n'
                'rev = "0df444a360eaa60ab8c11dca51a86af692955474"\n\n'
                '[[lean_lib]]\n'
                'name = "UFTID"\n'
            ).encode("utf-8"),
        }
        VERIFY.verify_package_definition(files, contract)
        mutated = dict(files)
        mutated[f"{prefix}lakefile.toml"] = files[f"{prefix}lakefile.toml"].replace(
            b"0df444a360eaa60ab8c11dca51a86af692955474",
            b"1111111111111111111111111111111111111111",
        )
        with self.assertRaisesRegex(RuntimeError, "mathlib dependency does not match archive contract"):
            VERIFY.verify_package_definition(mutated, contract)

    def test_duplicate_manifest_keys_are_rejected(self):
        files = {"ARCHIVE-MANIFEST.json": b'{"doi":"bad","doi":"10.5281/zenodo.22108865"}'}
        with self.assertRaisesRegex(RuntimeError, "duplicate JSON key: doi"):
            VERIFY.verify_manifest(files, self.contract())

    def test_formal_provenance_is_correlated_with_archived_authority(self):
        contract = self.contract()
        raw = BUILD.git_archive_files(
            PROMOTION_COMMIT,
            ["machine/lean_observation_verification.json"],
        )["machine/lean_observation_verification.json"]
        files = {"formal/machine/lean_observation_verification.json": raw}
        VERIFY.verify_verification_record(files, contract)

        mutations = [
            ("integration_tree", "1" * 40, "integration tree drift"),
            ("final_pr_head", "2" * 40, "final PR head drift"),
            ("codex_no_major_issues_reviewed_commit", "3" * 40, "reviewed-commit provenance drift"),
        ]
        for field, value, message in mutations:
            with self.subTest(field=field):
                mutated = copy.deepcopy(contract)
                mutated["formalization"][field] = value
                with self.assertRaisesRegex(RuntimeError, message):
                    VERIFY.verify_verification_record(files, mutated)

        mutated = copy.deepcopy(contract)
        mutated["formalization"]["toolchain"]["mathlib_commit"] = "4" * 40
        with self.assertRaisesRegex(RuntimeError, "toolchain drift: mathlib_commit"):
            VERIFY.verify_verification_record(files, mutated)

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

    def test_extra_outer_file_and_directory_are_rejected(self):
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            for kind in ("file", "directory"):
                with self.subTest(kind=kind):
                    output = root / kind
                    BUILD.build(output)
                    extra = output / "unexpected"
                    if kind == "file":
                        extra.write_text("not part of the publication surface\n", encoding="utf-8")
                    else:
                        extra.mkdir()
                    with self.assertRaisesRegex(RuntimeError, "outer publication surface drift"):
                        VERIFY.verify(output)

    def test_outer_pdf_and_notes_are_size_bounded_before_read(self):
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            for name, limit, message in (
                ("UFT-ID-v3.0.0-Overview.pdf", VERIFY.MAX_OUTER_PDF_BYTES, "Overview PDF exceeds size bound"),
                ("RELEASE-NOTES.md", VERIFY.MAX_OUTER_NOTES_BYTES, "RELEASE-NOTES.md exceeds size bound"),
            ):
                with self.subTest(name=name):
                    output = root / name.replace(".", "-")
                    BUILD.build(output)
                    (output / name).write_bytes(b"x" * (limit + 1))
                    with self.assertRaisesRegex(RuntimeError, message):
                        VERIFY.verify(output)

    def test_pdf_tamper_is_rejected(self):
        with tempfile.TemporaryDirectory() as temporary:
            output = Path(temporary)
            BUILD.build(output)
            pdf = output / "UFT-ID-v3.0.0-Overview.pdf"
            pdf.write_bytes(pdf.read_bytes().replace(b"10.5281/zenodo.22108865", b"10.5281/zenodo.00000000", 1))
            with self.assertRaisesRegex(RuntimeError, "Overview PDF missing required identity text"):
                VERIFY.verify(output)

    def test_release_notes_are_canonically_authenticated(self):
        with tempfile.TemporaryDirectory() as temporary:
            output = Path(temporary)
            BUILD.build(output)
            notes = output / "RELEASE-NOTES.md"
            text = notes.read_text(encoding="utf-8")
            notes.write_text(
                text.replace("`LEAN_PROOF != EMPIRICAL_VALIDATION`", "`LEAN_PROOF == EMPIRICAL_VALIDATION`"),
                encoding="utf-8",
            )
            with self.assertRaisesRegex(RuntimeError, "canonical deterministic content"):
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
