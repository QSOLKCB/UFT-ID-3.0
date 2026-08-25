from __future__ import annotations

import copy
from contextlib import contextmanager
import importlib.util
import json
from pathlib import Path
import tempfile
from types import SimpleNamespace
import unittest


ROOT = Path(__file__).resolve().parents[1]
WORKFLOW = ROOT / ".github/workflows/vopson-corpus.yml"


def load_module(name: str, path: Path):
    spec = importlib.util.spec_from_file_location(name, path)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"cannot load {path}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


V = load_module(
    "lean_observation_freeze_codex7",
    ROOT / "scripts/validate_lean_observation_foundation.py",
)
ARTIFACTS = load_module(
    "lean_observation_freeze_artifacts_codex7",
    ROOT / "scripts/verify_lean_observation_foundation_artifact.py",
)


def canonical_documents() -> dict[str, object]:
    return {
        "freeze": V.load_json(V.FREEZE),
        "theorems": V.load_json(V.SOURCE_THEOREMS),
        "counterexamples": V.load_json(V.SOURCE_COUNTEREXAMPLES),
        "base_contract": V.load_json(V.BASE_CONTRACT),
        "human": V.HUMAN.read_text(encoding="utf-8"),
        "roadmap": V.ROADMAP.read_text(encoding="utf-8"),
        "readme": V.README4AI.read_text(encoding="utf-8"),
    }


def validate_documents(docs: dict[str, object]):
    return V.validate_documents(
        docs["freeze"],
        docs["theorems"],
        docs["counterexamples"],
        docs["base_contract"],
        docs["human"],
        docs["roadmap"],
        docs["readme"],
        check_paths=False,
    )


def canonical_retained_payload() -> dict[str, object]:
    payload = V.validate(require_basis_objects=False)
    payload["basis_objects_verified"] = True
    return payload


@contextmanager
def stub_live_validator(payload: dict[str, object]):
    original = ARTIFACTS.load_module
    ARTIFACTS.load_module = lambda name, path: SimpleNamespace(
        validate=lambda: copy.deepcopy(payload)
    )
    try:
        yield
    finally:
        ARTIFACTS.load_module = original


class CodexSeventhBatchRegressions(unittest.TestCase):
    def test_complete_claim_surfaces_are_exact_git_blob_bound(self):
        docs = canonical_documents()
        surfaces = (
            ("human", "human freeze"),
            ("readme", "README4AI"),
            ("roadmap", "ROADMAP"),
        )
        for field, label in surfaces:
            with self.subTest(field=field, mutation="canonical hash"):
                expected = (
                    V.EXPECTED_LIVE_README_BLOB
                    if field == "readme"
                    else V.EXPECTED_CLAIM_SURFACE_BLOBS[label]
                )
                self.assertEqual(V.text_git_blob_sha(docs[field]), expected)

        attacks = (
            "We have now published the immutable source-release tag.",
            "We published the immutable source release tag.",
            "Source tagging is complete.",
            "UFT-OBS-001 confirms that observationally equivalent states are physically identical.",
            "UFT-OBS-002 covers the quotient as the full codomain Y.",
            "UFT-OBS-003 guarantees that the original physical state persisted and was observed directly.",
            "UFT-OBS-004 excludes partial, representative, probabilistic, and task-specific reconstruction.",
            "An unanticipated paraphrase cannot be whitelisted by omission.",
        )
        for field, label in surfaces:
            for attack in attacks:
                with self.subTest(field=field, attack=attack):
                    mutated = canonical_documents()
                    mutated[field] += f"\n{attack}\n"
                    result = validate_documents(mutated)
                    self.assertEqual(result["status"], "error")
                    self.assertIn(
                        f"Lean observation {label} complete claim surface Git blob drift",
                        result["errors"],
                    )

    def test_artifact_verifier_is_exact_blob_bound(self):
        self.assertEqual(V.artifact_verifier_blob_errors(), [])
        self.assertEqual(
            V.local_git_blob_sha(V.ARTIFACT_VERIFIER),
            V.EXPECTED_ARTIFACT_VERIFIER_BLOB,
        )
        original = V.local_git_blob_sha
        try:
            V.local_git_blob_sha = lambda path: "0" * 40
            errors = V.artifact_verifier_blob_errors()
            self.assertTrue(
                any("retained-artifact verifier blob drift" in error for error in errors),
                errors,
            )
        finally:
            V.local_git_blob_sha = original

    def test_exact_retained_validation_payload_is_accepted(self):
        payload = canonical_retained_payload()
        self.assertEqual(payload["status"], "ok", payload["errors"])
        self.assertTrue(payload["basis_objects_verified"])
        with tempfile.TemporaryDirectory() as temp_dir:
            path = Path(temp_dir) / ARTIFACTS.VALIDATION_FILE
            path.write_text(
                json.dumps(payload, indent=2, sort_keys=True, allow_nan=False) + "\n",
                encoding="utf-8",
            )
            with stub_live_validator(payload):
                result = ARTIFACTS.verify(Path(temp_dir))
        self.assertEqual(result["status"], "ok")
        self.assertEqual(result["batch_id"], "LEAN-OBS-BATCH-001")
        self.assertTrue(result["basis_objects_verified"])

    def test_retained_validation_fails_closed_on_missing_or_malformed_json(self):
        cases = (
            (None, "missing or empty retained Lean freeze artifact"),
            ("", "missing or empty retained Lean freeze artifact"),
            ("not-json\n", "invalid retained Lean freeze artifact JSON"),
            ("[]\n", "must be a JSON object"),
            ('{"status":"error","status":"ok"}\n', "invalid retained Lean freeze artifact JSON"),
            ('{"status":NaN}\n', "invalid retained Lean freeze artifact JSON"),
            ('{"status":Infinity}\n', "invalid retained Lean freeze artifact JSON"),
        )
        for contents, diagnostic in cases:
            with self.subTest(contents=contents):
                with tempfile.TemporaryDirectory() as temp_dir:
                    if contents is not None:
                        (Path(temp_dir) / ARTIFACTS.VALIDATION_FILE).write_text(
                            contents,
                            encoding="utf-8",
                        )
                    with self.assertRaisesRegex(RuntimeError, diagnostic):
                        ARTIFACTS.verify(Path(temp_dir))

    def test_retained_validation_fails_closed_on_error_or_payload_drift(self):
        canonical = canonical_retained_payload()
        self.assertEqual(canonical["status"], "ok", canonical["errors"])
        attacks = []

        error_payload = copy.deepcopy(canonical)
        error_payload["status"] = "error"
        error_payload["errors"] = ["simulated failure"]
        attacks.append((error_payload, "artifact is not successful"))

        unverified_basis = copy.deepcopy(canonical)
        unverified_basis["basis_objects_verified"] = False
        attacks.append((unverified_basis, "did not verify basis Git objects"))

        drifted_count = copy.deepcopy(canonical)
        drifted_count["theorem_count"] = 999
        attacks.append((drifted_count, "full payload drift"))

        float_count = copy.deepcopy(canonical)
        float_count["theorem_count"] = 4.0
        attacks.append((float_count, "canonical byte drift"))

        missing_field = copy.deepcopy(canonical)
        missing_field.pop("module_count")
        attacks.append((missing_field, "field set drift"))

        attacks.append((copy.deepcopy(canonical), "canonical byte drift"))

        for payload, diagnostic in attacks:
            with self.subTest(diagnostic=diagnostic):
                with tempfile.TemporaryDirectory() as temp_dir:
                    (Path(temp_dir) / ARTIFACTS.VALIDATION_FILE).write_text(
                        json.dumps(payload, sort_keys=True),
                        encoding="utf-8",
                    )
                    with stub_live_validator(canonical):
                        with self.assertRaisesRegex(RuntimeError, diagnostic):
                            ARTIFACTS.verify(Path(temp_dir))

    def test_workflow_retained_verifier_step_is_exact_and_blocking(self):
        workflow = WORKFLOW.read_text(encoding="utf-8")
        self.assertEqual(V.workflow_contract_errors(workflow), [])
        verifier_path = '- "scripts/verify_lean_observation_foundation_artifact.py"'
        for event in ("pull_request", "push"):
            paths = V.workflow_event_paths(workflow, event)
            self.assertIsNotNone(paths)
            self.assertEqual(paths.count(verifier_path), 1)

        canonical = (
            "      - name: Verify retained Lean observation freeze evidence\n"
            "        if: always()\n"
            "        run: python scripts/verify_lean_observation_foundation_artifact.py artifacts\n"
        )
        attacks = (
            canonical.replace("if: always()", "if: false"),
            canonical.replace(
                "run: python scripts/verify_lean_observation_foundation_artifact.py artifacts",
                "run: python -c 'print(0)'",
            ),
            canonical.replace(
                "run: python scripts/verify_lean_observation_foundation_artifact.py artifacts",
                "run: python scripts/verify_lean_observation_foundation_artifact.py artifacts || true",
            ),
            canonical.replace(
                "        run:",
                "        continue-on-error: true\n        run:",
            ),
        )
        for attack in attacks:
            with self.subTest(attack=attack):
                mutated = workflow.replace(canonical, attack, 1)
                errors = V.workflow_contract_errors(mutated)
                self.assertIn(
                    "registered Lean-freeze retained-artifact verification step must be exact and blocking",
                    errors,
                )

        for attack in ("", canonical + canonical):
            with self.subTest(envelope=repr(attack)):
                mutated = workflow.replace(canonical, attack, 1)
                self.assertIn(
                    "registered Lean-freeze workflow missing unique retained-artifact verification step",
                    V.workflow_contract_errors(mutated),
                )


if __name__ == "__main__":
    unittest.main()
