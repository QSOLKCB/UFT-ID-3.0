#!/usr/bin/env python3
from pathlib import Path

path = Path("tests/test_pr11_relation_core.py")
text = path.read_text(encoding="utf-8")
text = text.replace(
    "roadmap clock/state are advanced to the current Empirical Falsification Profile\nphase.",
    "roadmap clock/state are advanced to the current PR #10 theorem-batch-freeze\nphase.",
    1,
)
text = text.replace(
    '    self.assert_error_contains(value, "active planned surface must be PR18")\n',
    '    self.assert_error_contains(value, "active planned surface must be PR10")\n',
    1,
)
anchor = '''def _updated_future_snapshot_test(self):\n'''
insert = '''def _updated_complete_roadmap_state_semantic_drift(self):\n    mutations = {\n        "deferred": [10],\n        "compatibility_note": "PR8 and PR9 authority is obsolete.",\n        "fixture_policy": "Any decorative example is sufficient proof.",\n        "rules": ["COMPATIBILITY => UNIQUE_PHYSICAL_SELECTION"],\n    }\n    for field, replacement in mutations.items():\n        with self.subTest(field=field):\n            value = _FROZEN.canonical_documents()\n            value["roadmap_state"][field] = replacement\n            self.assert_error_contains(value, "live roadmap state canonical payload drift")\n\n\n'''
if text.count(anchor) != 1:
    raise SystemExit(f"future-test anchor drift: {text.count(anchor)}")
text = text.replace(anchor, insert + anchor, 1)
assign = '_FROZEN.PR11RelationMutationTests.test_rejects_live_roadmap_active_surface_drift = _updated_active_surface_test\n'
replacement = assign + '_FROZEN.PR11RelationMutationTests.test_rejects_complete_roadmap_state_semantic_drift = _updated_complete_roadmap_state_semantic_drift\n'
if text.count(assign) != 1:
    raise SystemExit(f"assignment anchor drift: {text.count(assign)}")
text = text.replace(assign, replacement, 1)
path.write_text(text, encoding="utf-8")
