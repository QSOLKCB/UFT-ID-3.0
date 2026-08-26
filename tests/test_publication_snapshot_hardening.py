from __future__ import annotations

import importlib.util
import os
from pathlib import Path
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[1]
PUBLICATION_SOURCE_COMMIT = "9bffc6b59ba109824079dd00d87ab39993ad7f93"


def load_module(name: str, relative_path: str):
    spec = importlib.util.spec_from_file_location(name, ROOT / relative_path)
    if spec is None or spec.loader is None:
        raise RuntimeError("cannot load reproduction module")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


REPRODUCE = load_module(
    "reproduce_scholarly_archive_snapshot_hardening",
    "scripts/reproduce_scholarly_archive.py",
)
BUILD = load_module(
    "build_scholarly_archive_snapshot_hardening",
    "scripts/build_scholarly_archive.py",
)


def build_surface(destination: Path) -> None:
    BUILD.build(destination)


class PublicationSnapshotHardeningTests(unittest.TestCase):
    def test_fifo_publication_artifact_fails_promptly_as_non_regular(self):
        names = list(REPRODUCE.PUBLICATION_FILE_NAMES)
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            os.mkfifo(root / REPRODUCE.SOURCE_ZIP_NAME)
            for name in names[1:]:
                (root / name).write_bytes(b"x")
            with self.assertRaisesRegex(RuntimeError, "not a regular file"):
                REPRODUCE.artifact_surface(root, names)

    def test_direct_caller_supplied_lake_wrapper_is_never_accepted(self):
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            with self.assertRaisesRegex(RuntimeError, "caller-supplied --lake executables are unsupported"):
                REPRODUCE.reproduce(
                    root,
                    publication_source_commit=PUBLICATION_SOURCE_COMMIT,
                    axiom_json_out=root.parent / "axioms.json",
                    lake=str(root / "fake-lake"),
                )

    def test_fake_lean_archive_fails_sha_before_toolchain_extraction(self):
        toolchain = REPRODUCE.load_contract()["lean_toolchain"]
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            fake = root / "lean.tar.zst"
            fake.write_bytes(b"fake exact-version wrapper payload")
            staged = root / "staged.tar.zst"
            with self.assertRaisesRegex(RuntimeError, "Lean archive SHA-256 mismatch"):
                REPRODUCE.stage_pinned_lean_archive(fake, toolchain, staged)

    def test_post_authentication_input_replacement_cannot_change_snapshot(self):
        names = list(REPRODUCE.PUBLICATION_FILE_NAMES)
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary) / "input"
            root.mkdir()
            build_surface(root)
            with REPRODUCE.trusted_publication_snapshot(
                root,
                PUBLICATION_SOURCE_COMMIT,
                names,
            ) as (snapshot, canonical, _report):
                self.assertNotEqual(snapshot.resolve(), root.resolve())
                (root / REPRODUCE.SOURCE_ZIP_NAME).write_bytes(b"replacement-after-auth")
                observed = REPRODUCE.artifact_surface(
                    snapshot,
                    names,
                    expected_sizes={name: int(canonical[name]["bytes"]) for name in names},
                )
                REPRODUCE.require_exact_artifact_digests(observed, canonical)

    def test_verified_retention_directory_is_a_distinct_read_only_snapshot(self):
        names = list(REPRODUCE.PUBLICATION_FILE_NAMES)
        with tempfile.TemporaryDirectory() as temporary:
            base = Path(temporary)
            canonical_root = base / "canonical"
            canonical_root.mkdir()
            build_surface(canonical_root)
            canonical = REPRODUCE.artifact_surface(canonical_root, names)
            retained_root = base / "retained"
            retained = REPRODUCE.materialize_verified_publication(
                canonical_root,
                retained_root,
                names,
                canonical,
            )
            REPRODUCE.require_exact_artifact_digests(retained, canonical)
            (canonical_root / "RELEASE-NOTES.md").write_bytes(b"changed source after retention")
            retained_again = REPRODUCE.artifact_surface(
                retained_root,
                names,
                expected_sizes={name: int(canonical[name]["bytes"]) for name in names},
            )
            REPRODUCE.require_exact_artifact_digests(retained_again, canonical)
            self.assertEqual(retained_root.stat().st_mode & 0o777, 0o500)
            for name in names:
                self.assertEqual((retained_root / name).stat().st_mode & 0o777, 0o400)

    def test_workflow_retains_only_the_verified_snapshot_and_passes_pinned_archive(self):
        text = (ROOT / ".github/workflows/publication-reproduction.yml").read_text(encoding="utf-8")
        self.assertIn("--output \"$GITHUB_WORKSPACE/artifacts/zenodo-input\"", text)
        self.assertIn("artifacts/zenodo-input \\", text)
        self.assertIn("--lean-archive \"$archive\"", text)
        self.assertIn("--verified-publication-out artifacts/zenodo", text)
        self.assertNotIn("--lake \"$install_dir/bin/lake\"", text)
        self.assertIn("path: artifacts/zenodo/", text)


if __name__ == "__main__":
    unittest.main()
