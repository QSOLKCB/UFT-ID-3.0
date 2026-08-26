from __future__ import annotations

import importlib.util
import json
from pathlib import Path
import tempfile
import unittest
import zipfile

ROOT = Path(__file__).resolve().parents[1]
PUBLICATION_SOURCE_COMMIT = "9bffc6b59ba109824079dd00d87ab39993ad7f93"
PUBLICATION_SOURCE_TREE = "b98895d3720bf757b5f78758f8879d6c9cf916cc"


def load_module(name: str, relative_path: str):
    path = ROOT / relative_path
    spec = importlib.util.spec_from_file_location(name, path)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"cannot load {path}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


REPRODUCE = load_module("reproduce_scholarly_archive", "scripts/reproduce_scholarly_archive.py")


def add_member(zf: zipfile.ZipFile, name: str, data: bytes) -> None:
    info = zipfile.ZipInfo(name, (1980, 1, 1, 0, 0, 0))
    info.compress_type = zipfile.ZIP_DEFLATED
    info.external_attr = (0o100644 & 0xFFFF) << 16
    info.create_system = 3
    zf.writestr(info, data, compress_type=zipfile.ZIP_DEFLATED, compresslevel=9)


class ScholarlyArchiveReproductionTests(unittest.TestCase):
    def test_contract_binds_merged_publication_authority(self):
        contract = json.loads(
            (ROOT / "machine/scholarly_archive_reproduction_contract.json").read_text(encoding="utf-8")
        )
        self.assertEqual(contract["doi"], "10.5281/zenodo.22108865")
        self.assertEqual(contract["publication_source"]["merge_commit"], PUBLICATION_SOURCE_COMMIT)
        self.assertEqual(contract["publication_source"]["merge_tree"], PUBLICATION_SOURCE_TREE)
        self.assertEqual(
            contract["publication_surface"]["exact_files"],
            [
                "UFT-ID-3.0.0-source.zip",
                "UFT-ID-v3.0.0-Overview.pdf",
                "RELEASE-NOTES.md",
            ],
        )
        self.assertEqual(contract["pipeline"]["lean_reproduction_python"], "3.12")

    def test_workflow_builds_from_detached_merged_main_and_retains_exact_bytes(self):
        text = (ROOT / ".github/workflows/publication-reproduction.yml").read_text(encoding="utf-8")
        self.assertIn(f"UFT_PUBLICATION_SOURCE_COMMIT: {PUBLICATION_SOURCE_COMMIT}", text)
        self.assertIn('git worktree add --detach "$publication_root" "$UFT_PUBLICATION_SOURCE_COMMIT"', text)
        self.assertIn('python "$publication_root/scripts/build_scholarly_archive.py"', text)
        self.assertIn('python "$publication_root/scripts/verify_scholarly_archive.py"', text)
        self.assertIn("Reproduce archived formal layer in isolation", text)
        self.assertIn("scripts/reproduce_scholarly_archive.py", text)
        self.assertIn("path: artifacts/zenodo/", text)
        self.assertIn("name: uft-id-zenodo-publication-py${{ matrix.python-version }}", text)
        self.assertIn("fetch-depth: 0", text)
        self.assertNotIn("actions/download-artifact@", text)

    def test_formal_extraction_is_prefix_scoped_and_requires_authority_files(self):
        required = {
            "lean-toolchain": b"leanprover/lean4:v4.33.1\n",
            "lakefile.toml": b'name = "UFTID"\n',
            "UFTID.lean": b"import UFTID.Observation.Basic\n",
            "machine/lean_observation_verification.json": b'{"status":"LEAN_VERIFIED"}\n',
            "scripts/verify_lean_observation_axioms.py": b"print('audit')\n",
            "UFTID/Observation/Basic.lean": b"theorem x : True := by trivial\n",
        }
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            source_zip = root / "source.zip"
            with zipfile.ZipFile(source_zip, "w") as zf:
                add_member(zf, "reference-v3.0.0/README.md", b"reference\n")
                for name, data in required.items():
                    add_member(zf, f"formal/{name}", data)
            destination = root / "formal"
            members = REPRODUCE.extract_formal_layer(source_zip, destination)
            self.assertEqual(set(members), set(required))
            self.assertFalse((destination / "README.md").exists())
            self.assertTrue((destination / "machine/lean_observation_verification.json").is_file())

    def test_formal_extraction_rejects_parent_escape(self):
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            source_zip = root / "source.zip"
            with zipfile.ZipFile(source_zip, "w") as zf:
                add_member(zf, "formal/../escape.txt", b"escape\n")
            with self.assertRaisesRegex(RuntimeError, "unsafe ZIP path"):
                REPRODUCE.extract_formal_layer(source_zip, root / "formal")

    def test_publication_surface_rejects_extra_outer_entry(self):
        names = [
            "UFT-ID-3.0.0-source.zip",
            "UFT-ID-v3.0.0-Overview.pdf",
            "RELEASE-NOTES.md",
        ]
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            for name in names:
                (root / name).write_bytes(b"x")
            (root / "extra").mkdir()
            with self.assertRaisesRegex(RuntimeError, "publication surface drift"):
                REPRODUCE.artifact_surface(root, names)

    def test_reproducer_rejects_wrong_publication_source_before_execution(self):
        with tempfile.TemporaryDirectory() as temporary:
            with self.assertRaisesRegex(RuntimeError, "publication source commit does not match"):
                REPRODUCE.reproduce(
                    Path(temporary),
                    lake="lake",
                    publication_source_commit="0" * 40,
                    axiom_json_out=Path(temporary) / "axioms.json",
                )


if __name__ == "__main__":
    unittest.main()
