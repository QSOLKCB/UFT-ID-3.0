from __future__ import annotations

import copy
import importlib.util
import json
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def load_module(name: str, path: Path):
    spec = importlib.util.spec_from_file_location(name, path)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"cannot load {path}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


V = load_module("lean_observation_freeze_validator", ROOT / "scripts/validate_lean_observation_foundation.py")


def documents():
    return {
        "freeze": json.loads((ROOT / "machine/lean_observation_foundation_contract.json").read_text()),
        "theorems": json.loads((ROOT / "machine/observation_theorems.json").read_text()),
        "counterexamples": json.loads((ROOT / "machine/observation_counterexamples.json").read_text()),
        "base_contract": json.loads((ROOT / "machine/contract.json").read_text()),
        "human": (ROOT / "theory/LEAN_OBSERVATION_FOUNDATION.md").read_text(),
        "roadmap": (ROOT / "ROADMAP.md").read_text(),
        "readme": (ROOT / "README4AI.md").read_text(),
    }


def validate_docs(docs):
    return V.validate_documents(
        docs["freeze"], docs["theorems"], docs["counterexamples"],
        docs["base_contract"], docs["human"], docs["roadmap"], docs["readme"],
        check_paths=False,
    )


class LeanObservationFoundationFreezeTests(unittest.TestCase):
    def assert_error_contains(self, docs, fragment: str):
        result = validate_docs(docs)
        self.assertEqual(result["status"], "error")
        self.assertTrue(any(fragment in error for error in result["errors"]), result["errors"])

    def test_canonical_freeze_validates(self):
        # Pure unit coverage intentionally avoids requiring repository-history
        # objects. Production validate() and the CLI require them by default.
        result = V.validate(require_basis_objects=False)
        self.assertEqual(result["status"], "ok", result["errors"])
        self.assertFalse(result["basis_objects_verified"])
        self.assertEqual(result["batch_id"], "LEAN-OBS-BATCH-001")
        self.assertEqual(result["theorem_count"], 4)
        self.assertEqual(result["deferred_count"], 1)
        self.assertEqual(result["module_count"], 3)

    def test_complete_pr9_basis_dependency_closure_is_frozen(self):
        freeze = documents()["freeze"]
        expected = [{"path": path, "git_blob_sha": sha} for path, sha in V.EXPECTED_SOURCE_BLOBS.items()]
        self.assertEqual(freeze["source_authorities"], expected)
        self.assertEqual(freeze["schema_version"], "1.0.1")
        self.assertEqual(V.EXPECTED_SOURCE_BLOBS["machine/contract.json"], "2aa342b83a698577c92ac7964ea0d8fcfc102a0b")
        self.assertEqual(V.EXPECTED_SOURCE_BLOBS["machine/formalization_contract.json"], "1c0827b5f760b08d8d375659667ca0067f722aa8")
        self.assertEqual(V.EXPECTED_SOURCE_BLOBS["ROADMAP.md"], "7a602769908e2ff83ae49a32539fd1a5a5340ce4")

    def test_registered_freeze_workflow_is_direct_and_human_triggered(self):
        workflow = (ROOT / ".github/workflows/vopson-corpus.yml").read_text(encoding="utf-8")
        self.assertEqual(V.workflow_contract_errors(workflow), [])
        authority = documents()["base_contract"]["lean_observation_foundation_authority"]
        self.assertEqual(authority["workflow"], ".github/workflows/vopson-corpus.yml")
        self.assertEqual(authority["frozen_validator"], "scripts/validate_lean_observation_foundation_pr21_frozen.py")

        mutated = workflow.replace('      - "theory/LEAN_OBSERVATION_FOUNDATION.md"\n', "", 1)
        self.assertTrue(any("path trigger drift" in e for e in V.workflow_contract_errors(mutated)))
        mutated = workflow.replace('      - "ROADMAP.md"\n', "", 1)
        self.assertTrue(any("path trigger drift" in e for e in V.workflow_contract_errors(mutated)))
        mutated = workflow.replace("        run: python scripts/validate_lean_observation_foundation.py\n", "        run: python -c 'pass'\n", 1)
        self.assertTrue(any("direct validator/policy drift" in e for e in V.workflow_contract_errors(mutated)))

    def test_workflow_paths_are_validated_per_event_not_by_global_count(self):
        workflow = (ROOT / ".github/workflows/vopson-corpus.yml").read_text(encoding="utf-8")
        required = '- "ROADMAP.md"'
        for event in ("pull_request", "push"):
            paths = V.workflow_event_paths(workflow, event)
            self.assertIsNotNone(paths)
            self.assertEqual(paths.count(required), 1)

        pull, push = workflow.split("  push:\n", 1)
        pull_duplicate = pull.replace(
            '      - "ROADMAP.md"\n',
            '      - "ROADMAP.md"\n      - "ROADMAP.md"\n',
            1,
        )
        push_missing = push.replace('      - "ROADMAP.md"\n', "", 1)
        mutated = pull_duplicate + "  push:\n" + push_missing
        errors = V.workflow_contract_errors(mutated)
        self.assertTrue(any("pull_request path trigger drift" in e for e in errors), errors)
        self.assertTrue(any("push path trigger drift" in e for e in errors), errors)

        pull_missing = pull.replace('      - "ROADMAP.md"\n', "", 1)
        push_duplicate = push.replace(
            '      - "ROADMAP.md"\n',
            '      - "ROADMAP.md"\n      - "ROADMAP.md"\n',
            1,
        )
        mutated = pull_missing + "  push:\n" + push_duplicate
        errors = V.workflow_contract_errors(mutated)
        self.assertTrue(any("pull_request path trigger drift" in e for e in errors), errors)
        self.assertTrue(any("push path trigger drift" in e for e in errors), errors)

    def test_basis_commit_object_mapping_logic_is_fail_closed(self):
        original = V.basis_git_blob_sha
        try:
            V.basis_git_blob_sha = lambda relpath: V.EXPECTED_SOURCE_BLOBS.get(relpath)
            self.assertEqual(V.basis_source_object_errors(), [])

            V.basis_git_blob_sha = lambda relpath: None
            errors = V.basis_source_object_errors()
            self.assertTrue(any("basis commit blob object unavailable" in error for error in errors), errors)
            self.assertIn("complete PR9 basis dependency closure was not resolved from readable Git blob objects", errors)
        finally:
            V.basis_git_blob_sha = original

    def test_first_batch_is_exactly_obs_001_through_004(self):
        freeze = documents()["freeze"]
        self.assertEqual(freeze["theorem_ids"], ["UFT-OBS-001", "UFT-OBS-002", "UFT-OBS-003", "UFT-OBS-004"])
        self.assertEqual(freeze["deferred_theorem_ids"], ["UFT-OBS-005"])

    def test_manifest_cannot_self_authorize_statement_drift(self):
        docs = documents()
        docs["freeze"]["theorems"][1]["statement"] = "The quotient is canonically the full codomain."
        self.assert_error_contains(docs, "UFT-OBS-002 frozen payload drift")

    def test_source_theorem_drift_breaks_the_freeze(self):
        docs = documents()
        theorem = next(x for x in docs["theorems"]["records"] if x["id"] == "UFT-OBS-003")
        theorem["hypotheses"] = ["O is any relation"]
        self.assert_error_contains(docs, "UFT-OBS-003 source/freeze theorem authority drift")

    def test_undeclared_claim_bearing_field_fails_closed(self):
        docs = documents()
        docs["freeze"]["empirically_validated"] = True
        self.assert_error_contains(docs, "top-level field set drift")

    def test_dependency_graph_is_exact_and_acyclic(self):
        docs = documents()
        docs["freeze"]["dependency_graph"]["UFT-OBS-001"] = ["UFT-OBS-002"]
        self.assert_error_contains(docs, "theorem dependency graph drift")
        self.assertTrue(V.graph_is_acyclic(V.EXPECTED_GRAPH))

    def test_module_map_cannot_silently_absorb_floor_sampling(self):
        docs = documents()
        docs["freeze"]["lean_module_map"][0]["theorem_ids"].append("UFT-OBS-005")
        self.assert_error_contains(docs, "module map drift")

    def test_toolchain_and_tag_remain_unclaimed(self):
        docs = documents()
        docs["freeze"]["toolchain"]["lean"] = "v4.fake"
        self.assert_error_contains(docs, "toolchain deferral drift")
        docs = documents()
        docs["freeze"]["release_gate"]["source_tag"] = "v3.0.0"
        self.assert_error_contains(docs, "post-merge release gate drift")

    def test_human_theorem_metadata_is_exact_bound(self):
        docs = documents()
        docs["human"] = docs["human"].replace(
            "**Lean status:** `NOT_IMPLEMENTED`",
            "**Lean status:** `PROVED`",
            1,
        )
        self.assert_error_contains(docs, "UFT-OBS-001 human Lean status drift")

    def test_counterexample_dependencies_remain_counterexamples(self):
        docs = documents()
        cx = next(x for x in docs["counterexamples"]["records"] if x["id"] == "CX-OBS-001")
        cx["claim_class"] = "THEOREM_TARGET"
        self.assert_error_contains(docs, "CX-OBS-001 counterexample dependency missing or reclassified")

    def test_human_status_and_verification_promotion_fail_closed(self):
        docs = documents()
        docs["human"] = docs["human"].replace(
            "**Status:** `SOURCE_THEOREM_BATCH_FROZEN_NO_LEAN_PROOF`",
            "**Status:** `LEAN_VERIFIED`",
            1,
        )
        self.assert_error_contains(docs, "human freeze status drift")

        docs = documents()
        docs["human"] += "\nAll frozen theorems have checked Lean proofs.\n"
        self.assert_error_contains(docs, "human Lean verification promotion")

    def test_readme_and_roadmap_lean_promotion_fail_closed(self):
        promotion = "\nAll frozen theorems are now formally verified in Lean.\n"

        docs = documents()
        docs["readme"] += promotion
        self.assert_error_contains(docs, "README4AI Lean verification promotion")

        docs = documents()
        docs["roadmap"] += promotion
        self.assert_error_contains(docs, "ROADMAP Lean verification promotion")

    def test_theorem_id_and_batch_scoped_lean_promotion_fail_closed(self):
        attacks = (
            "\nUFT-OBS-001 through UFT-OBS-004 have been proved in Lean.\n",
            "\nLEAN-OBS-BATCH-001 has been formally verified in Lean.\n",
            "\nLean proves UFT-OBS-001 through UFT-OBS-004.\n",
            "\nUFT-OBS-001 through UFT-OBS-004 now have Lean proofs.\n",
        )
        for field, label in (("human", "human freeze"), ("readme", "README4AI"), ("roadmap", "ROADMAP")):
            for attack in attacks:
                with self.subTest(field=field, attack=attack.strip()):
                    docs = documents()
                    docs[field] += attack
                    self.assert_error_contains(docs, f"{label} theorem-scoped Lean verification promotion")

    def test_readme_required_validation_sequence_includes_freeze(self):
        readme = documents()["readme"]
        required = readme.split("## Required validation commands\n", 1)[1].split("\n## ", 1)[0]
        observation = "python scripts/validate_observation_specs.py"
        freeze = "python scripts/validate_lean_observation_foundation.py"
        relation = "python scripts/validate_relation_core.py"
        self.assertEqual(required.count(freeze), 1)
        self.assertLess(required.index(observation), required.index(freeze))
        self.assertLess(required.index(freeze), required.index(relation))

    def test_pretag_lean_source_and_toolchain_files_are_rejected(self):
        candidates = (
            ROOT / "UFTID/Observation/Basic.lean",
            ROOT / "lean-toolchain",
            ROOT / "lakefile.toml",
            ROOT / "lake-manifest.json",
        )
        created_dirs: list[Path] = []
        try:
            for path in candidates:
                with self.subTest(path=str(path.relative_to(ROOT))):
                    if path.exists():
                        self.fail(f"canonical pre-tag tree unexpectedly already contains {path}")
                    path.parent.mkdir(parents=True, exist_ok=True)
                    if path.parent != ROOT:
                        created_dirs.append(path.parent)
                    path.write_text("pre-tag forbidden fixture\n", encoding="utf-8")
                    result = V.validate(require_basis_objects=False)
                    self.assertEqual(result["status"], "error")
                    self.assertIn(
                        f"pre-tag Lean source/toolchain forbidden: {path.relative_to(ROOT).as_posix()}",
                        result["errors"],
                    )
                    path.unlink()
        finally:
            for path in candidates:
                if path.exists():
                    path.unlink()
            for directory in sorted(set(created_dirs), key=lambda p: len(p.parts), reverse=True):
                try:
                    directory.rmdir()
                    parent = directory.parent
                    if parent != ROOT:
                        parent.rmdir()
                except OSError:
                    pass

    def test_pretag_scanner_ignores_non_lean_files(self):
        self.assertNotIn("theory/LEAN_OBSERVATION_FOUNDATION.md", V.pretag_lean_files(ROOT))

    def test_roadmap_must_leave_source_tag_pending(self):
        docs = documents()
        docs["roadmap"] = docs["roadmap"].replace(
            "- [ ] Pass the exact merged-main release gate and cut the immutable source tag.",
            "- [x] Pass the exact merged-main release gate and cut the immutable source tag.",
        )
        self.assert_error_contains(docs, "source-release tag must remain pending")


if __name__ == "__main__":
    unittest.main()
