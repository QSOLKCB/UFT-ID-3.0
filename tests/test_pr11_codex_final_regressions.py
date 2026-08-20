from __future__ import annotations

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


V = load_module("pr11_relation_validator_final", ROOT / "scripts/validate_relation_core.py")
E = load_module("pr11_relation_experiment_final", ROOT / "experiments/relation/run.py")


def canonical_documents():
    return {
        "contract": json.loads((ROOT / "machine/relation_contract.json").read_text()),
        "theorems": json.loads((ROOT / "machine/relation_theorems.json").read_text()),
        "counterexamples": json.loads((ROOT / "machine/relation_counterexamples.json").read_text()),
        "selection": json.loads((ROOT / "machine/genus_selection_specimen.json").read_text()),
        "cross_repo_patterns": json.loads((ROOT / "machine/cross_repo_patterns.json").read_text()),
        "roadmap_state": json.loads((ROOT / "machine/roadmap_state.json").read_text()),
        "base_contract": json.loads((ROOT / "machine/contract.json").read_text()),
        "human": (ROOT / "theory/RELATION_CALCULUS.md").read_text(),
        "roadmap": (ROOT / "ROADMAP.md").read_text(),
    }


def validate_docs(value):
    return V.validate_documents(
        value["contract"],
        value["theorems"],
        value["counterexamples"],
        value["selection"],
        value["cross_repo_patterns"],
        value["roadmap_state"],
        value["base_contract"],
        value["human"],
        value["roadmap"],
        check_paths=False,
    )


class PR11FinalCodexRegressions(unittest.TestCase):
    def assert_error_contains(self, value, fragment: str):
        result = validate_docs(value)
        self.assertEqual(result["status"], "error")
        self.assertTrue(any(fragment in error for error in result["errors"]), result["errors"])

    def test_unhashable_carrier_members_fail_closed_as_value_error(self):
        malformed_members = (["bad"], {"bad": True})
        for malformed in malformed_members:
            with self.subTest(malformed=malformed):
                with self.assertRaisesRegex(ValueError, "states must be non-empty strings"):
                    E.reachable(("a", malformed), (), "a")
                with self.assertRaisesRegex(ValueError, "states must be non-empty strings"):
                    E.relation_properties(("a", malformed), ())

    def test_additive_xin_authority_promotion_is_rejected(self):
        value = canonical_documents()
        marker = V.XIN_ROADMAP_END
        contradiction = (
            "\n\nXin et al. is current PR11 theorem evidence and proves "
            "cosmological E8 genus 10.\n"
        )
        self.assertIn(marker, value["roadmap"])
        value["roadmap"] = value["roadmap"].replace(marker, contradiction + marker, 1)

        # All older protective anchors still exist. The complete-section identity,
        # rather than keyword presence, must reject the additive contradiction.
        for anchor in V.XIN_ROADMAP_ANCHORS:
            self.assertIn(anchor, value["roadmap"])
        self.assert_error_contains(value, "ROADMAP Xin positive-control canonical section drift")

    def test_human_theorem_claim_class_change_and_removal_are_rejected(self):
        for replacement in ("**Claim class:** `EMPIRICAL`.", ""):
            with self.subTest(replacement=replacement):
                value = canonical_documents()
                section = V.theorem_section(value["human"], "UFT-RW-003")
                self.assertIn("**Claim class:** `PROVED`.", section)
                mutated = section.replace("**Claim class:** `PROVED`.", replacement, 1)
                value["human"] = value["human"].replace(section, mutated, 1)
                self.assert_error_contains(value, "UFT-RW-003 human claim class drift")

    def test_human_theorem_additive_physical_promotion_is_rejected(self):
        value = canonical_documents()
        section = V.theorem_section(value["human"], "UFT-RW-003")
        self.assertTrue(section)
        mutated = section + "\nThis theorem proves universal physical ontology.\n"
        value["human"] = value["human"].replace(section, mutated, 1)

        # Statement, hypotheses, and claim class remain untouched; exact human
        # theorem-section identity must still reject the additive promotion.
        self.assertIn(V.EXPECTED_STATEMENTS["UFT-RW-003"], mutated)
        self.assertIn("**Claim class:** `PROVED`.", mutated)
        self.assert_error_contains(value, "UFT-RW-003 human theorem canonical payload drift")


if __name__ == "__main__":
    unittest.main()
