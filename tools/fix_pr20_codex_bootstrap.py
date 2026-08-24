#!/usr/bin/env python3
from __future__ import annotations

from pathlib import Path
import subprocess

ROOT = Path(__file__).resolve().parents[1]


def replace_once(text: str, old: str, new: str, label: str) -> str:
    count = text.count(old)
    if count != 1:
        raise RuntimeError(f"{label}: expected exactly one anchor, found {count}")
    return text.replace(old, new, 1)


readme_path = ROOT / "README4AI.md"
readme = readme_path.read_text(encoding="utf-8")
old_efp = (
    "The active planned PR #18 surface defines a synthetic conformance procedure for deciding whether a calibrated "
    "profile-matched evidence record crosses one versioned scoped rejection boundary. It specializes the PR8 "
    "`FalsificationSpec` scaffold without converting synthetic fixtures, matching hashes, or procedural labels into "
    "empirical evidence or preregistration proof."
)
new_efp = (
    "The completed planned PR #18 surface defines a synthetic conformance procedure for deciding whether a calibrated "
    "profile-matched evidence record crosses one versioned scoped rejection boundary. It specializes the PR8 "
    "`FalsificationSpec` scaffold without converting synthetic fixtures, matching hashes, or procedural labels into "
    "empirical evidence or preregistration proof. Live scheduling authority is PR #10 Lean observation foundation, "
    "active only for first-theorem-batch and dependency-graph freezing."
)
readme = replace_once(readme, old_efp, new_efp, "EFP bootstrap status")

old_lean = (
    "Lean remains deferred until source reproduction, notation freeze, theorem freeze, and counterexample freeze. "
    "Detailed formalization/publication workflow planning is ROADMAP-only; see `ROADMAP.md`. This bootstrap surface "
    "does not promote deferred QSOL-CONTEXT, source-tag, Lean, or Zenodo planning into current canonical implementation authority."
)
new_lean = (
    "PR #10 Lean observation foundation is active only for theorem-batch and dependency-graph freezing. Lean proof "
    "implementation, source tagging, QSOL-CONTEXT target binding, and Zenodo publication are not claimed by this "
    "rollover and remain gated by the ordered workflow in `ROADMAP.md`. Detailed formalization/publication workflow "
    "planning remains ROADMAP-only and is not promoted into current proof, empirical, or publication authority."
)
readme = replace_once(readme, old_lean, new_lean, "Lean bootstrap status")
readme_path.write_text(readme, encoding="utf-8")

new_readme_blob = subprocess.check_output(
    ["git", "hash-object", "README4AI.md"], cwd=ROOT, text=True
).strip()

graph_path = ROOT / "scripts/validate_graph_realization.py"
graph = graph_path.read_text(encoding="utf-8")
old_pin = '"readme4ai": "0c29ebbde089ff62ad8eb0ec96746ad8d1ade8db"'
new_pin = f'"readme4ai": "{new_readme_blob}"'
graph = replace_once(graph, old_pin, new_pin, "graph README4AI blob pin")
graph_path.write_text(graph, encoding="utf-8")

validator_path = ROOT / "scripts/validate_empirical_falsification_profile.py"
validator = validator_path.read_text(encoding="utf-8")
validator = replace_once(
    validator,
    'ROADMAP_STATE = ROOT / "machine/roadmap_state.json"\n',
    'ROADMAP_STATE = ROOT / "machine/roadmap_state.json"\nREADME4AI = ROOT / "README4AI.md"\n',
    "EFP live bootstrap path",
)
anchor = '''def validate() -> dict[str, object]:\n    old_json = _frozen.load_json\n'''
insert = '''def _live_bootstrap_errors() -> list[str]:\n    errors: list[str] = []\n    text = README4AI.read_text(encoding="utf-8")\n    required = (\n        "The completed planned PR #18 surface defines a synthetic conformance procedure",\n        "Live scheduling authority is PR #10 Lean observation foundation, active only for first-theorem-batch and dependency-graph freezing.",\n        "PR #10 Lean observation foundation is active only for theorem-batch and dependency-graph freezing.",\n    )\n    for phrase in required:\n        if text.count(phrase) != 1:\n            errors.append(f"README4AI live schedule anchor drift: {phrase}")\n    forbidden = (\n        "The active planned PR #18 surface",\n        "Lean remains deferred until source reproduction",\n    )\n    for phrase in forbidden:\n        if phrase in text:\n            errors.append(f"README4AI stale schedule anchor present: {phrase}")\n    return errors\n\n\ndef validate() -> dict[str, object]:\n    old_json = _frozen.load_json\n'''
validator = replace_once(validator, anchor, insert, "EFP live bootstrap validator")
validator = replace_once(
    validator,
    '    errors.extend(_live_roadmap_errors())\n',
    '    errors.extend(_live_roadmap_errors())\n    errors.extend(_live_bootstrap_errors())\n',
    "EFP bootstrap validation call",
)
validator_path.write_text(validator, encoding="utf-8")

test_path = ROOT / "tests/test_post_efp_bootstrap_schedule.py"
test_path.write_text('''from __future__ import annotations\n\nimport importlib.util\nfrom pathlib import Path\nimport unittest\n\nROOT = Path(__file__).resolve().parents[1]\nVALIDATOR = ROOT / "scripts/validate_empirical_falsification_profile.py"\nREADME = ROOT / "README4AI.md"\n\n\ndef load_validator():\n    spec = importlib.util.spec_from_file_location("post_efp_bootstrap_validator", VALIDATOR)\n    if spec is None or spec.loader is None:\n        raise RuntimeError("cannot load EFP live validator")\n    module = importlib.util.module_from_spec(spec)\n    spec.loader.exec_module(module)\n    return module\n\n\nclass PostEfpBootstrapScheduleTests(unittest.TestCase):\n    def test_bootstrap_matches_live_pr10_schedule(self):\n        validator = load_validator()\n        result = validator.validate()\n        self.assertEqual(result["status"], "ok", result["errors"])\n        text = README.read_text(encoding="utf-8")\n        self.assertIn("The completed planned PR #18 surface defines a synthetic conformance procedure", text)\n        self.assertIn("Live scheduling authority is PR #10 Lean observation foundation, active only for first-theorem-batch and dependency-graph freezing.", text)\n        self.assertIn("PR #10 Lean observation foundation is active only for theorem-batch and dependency-graph freezing.", text)\n        self.assertNotIn("The active planned PR #18 surface", text)\n        self.assertNotIn("Lean remains deferred until source reproduction", text)\n\n    def test_stale_pr18_active_bootstrap_fails_closed(self):\n        validator = load_validator()\n        original = README.read_text(encoding="utf-8")\n        mutated = original.replace(\n            "The completed planned PR #18 surface defines a synthetic conformance procedure",\n            "The active planned PR #18 surface defines a synthetic conformance procedure",\n            1,\n        )\n        self.assertNotEqual(mutated, original)\n        try:\n            README.write_text(mutated, encoding="utf-8")\n            result = validator.validate()\n        finally:\n            README.write_text(original, encoding="utf-8")\n        self.assertEqual(result["status"], "error")\n        self.assertTrue(any("README4AI" in error for error in result["errors"]), result["errors"])\n\n\nif __name__ == "__main__":\n    unittest.main()\n''', encoding="utf-8")

print({"status": "patched", "readme_blob": new_readme_blob})
