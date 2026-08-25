from __future__ import annotations

import importlib.util
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
VALIDATOR = ROOT / "scripts/validate_lean_observation_foundation.py"


def load_validator():
    spec = importlib.util.spec_from_file_location(
        "lean_observation_projection_boundary", VALIDATOR
    )
    if spec is None or spec.loader is None:
        raise RuntimeError(f"cannot load {VALIDATOR}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


class LeanObservationProjectionBoundaryRegressions(unittest.TestCase):
    def setUp(self):
        self.v = load_validator()
        self.canonical_blobs = dict(
            self.v._impl._frozen.EXPECTED_CURRENT_AUTHORITY_BLOBS
        )
        self.canonical_modes = dict(
            self.v._impl._frozen.EXPECTED_CURRENT_AUTHORITY_MODES
        )

    def capture_projection(self, *, blobs, modes):
        captured = {}
        original = self.v._IMPL_TRACKED_AUTHORITY_OBJECT_ERRORS

        def capture(root, *, expected_blobs=None, expected_modes=None, runner=None):
            captured["blobs"] = expected_blobs
            captured["modes"] = expected_modes
            return []

        self.v._IMPL_TRACKED_AUTHORITY_OBJECT_ERRORS = capture
        try:
            errors = self.v.tracked_authority_object_errors(
                expected_blobs=blobs,
                expected_modes=modes,
            )
        finally:
            self.v._IMPL_TRACKED_AUTHORITY_OBJECT_ERRORS = original

        self.assertEqual(errors, [])
        return captured

    def test_exact_production_pair_overlays_live_authorities_in_both_maps(self):
        captured = self.capture_projection(
            blobs=dict(self.canonical_blobs),
            modes=dict(self.canonical_modes),
        )
        expected_blobs = dict(self.canonical_blobs)
        expected_blobs.update(self.v._LIVE_AUTHORITY_BLOBS)
        expected_modes = dict(self.canonical_modes)
        expected_modes.update(self.v._LIVE_AUTHORITY_MODES)
        self.assertEqual(captured["blobs"], expected_blobs)
        self.assertEqual(captured["modes"], expected_modes)

    def test_live_registry_covers_posttag_package_and_verification_files(self):
        required_blob_paths = {
            ".github/workflows/vopson-corpus.yml",
            "README4AI.md",
            "machine/roadmap_state.json",
            "machine/lean_observation_verification.json",
            "scripts/validate_lean_observation_foundation_pr21_final_frozen.py",
            "scripts/validate_lean_observation_foundation_pr22_batch2_precompiler.py",
            "scripts/validate_lean_observation_foundation_pr22_combined_review_frozen.py",
            "scripts/verify_lean_observation_axioms.py",
            "lean-toolchain",
            "lakefile.toml",
            "UFTID.lean",
            "UFTID/Observation/Basic.lean",
            "UFTID/Observation/Quotient.lean",
            "UFTID/Observation/Reconstruction.lean",
            "UFTID/Observation/Sampling.lean",
        }
        self.assertTrue(required_blob_paths.issubset(self.v._LIVE_AUTHORITY_BLOBS))
        self.assertTrue(required_blob_paths.issubset(self.v._LIVE_AUTHORITY_MODES))
        self.assertEqual(
            self.v._LIVE_AUTHORITY_MODES["scripts/validate_lean_observation_foundation.py"],
            "100755",
        )
        self.assertNotIn(
            "scripts/validate_lean_observation_foundation.py",
            self.v._LIVE_AUTHORITY_BLOBS,
        )

    def test_modified_explicit_pair_is_forwarded_unchanged(self):
        cases = []

        hostile_blobs = dict(self.canonical_blobs)
        blob_key = next(iter(hostile_blobs))
        hostile_blobs[blob_key] = "0" * 40
        cases.append(("blob mutation", hostile_blobs, dict(self.canonical_modes)))

        hostile_modes = dict(self.canonical_modes)
        mode_key = next(iter(hostile_modes))
        hostile_modes[mode_key] = "100755" if hostile_modes[mode_key] != "100755" else "100644"
        cases.append(("mode mutation", dict(self.canonical_blobs), hostile_modes))

        for label, blobs, modes in cases:
            with self.subTest(label=label):
                captured = self.capture_projection(blobs=blobs, modes=modes)
                self.assertEqual(captured["blobs"], blobs)
                self.assertEqual(captured["modes"], modes)

    def test_live_workflow_contract_terminates_without_recursive_reentry(self):
        workflow = self.v.WORKFLOW.read_text(encoding="utf-8")
        self.assertEqual(self.v.workflow_contract_errors(workflow), [])


if __name__ == "__main__":
    unittest.main()
