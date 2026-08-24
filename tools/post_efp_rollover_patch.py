#!/usr/bin/env python3
from __future__ import annotations

import hashlib
import json
from pathlib import Path
import pprint
import re
import shutil

ROOT = Path(__file__).resolve().parents[1]
MERGE = "516cff5d6a45af54d6fc4ae9c72c2e8e9c668637"
OLD_BASIS = "353e55a11a8cb6d6bcf571110e0fd6f32823fc77"
EFP_REVIEW_HEAD = "dd53d44787c571636c68bfe68b6cec4ba0ce0b7a"
ACTIVE_STATUS = "active-first-theorem-batch-freeze"
EFP_COMPLETE = f"complete-merged-{MERGE}"
OLD_LEAN_RULE = "Lean deferral does not prevent repository-contained mathematical proofs, finite conformance witnesses, or later theorem targets from being frozen."
NEW_LEAN_RULE = "Lean activation begins with theorem-batch and dependency-graph freezing; mathematical proof, Lean proof, runtime conformance, and empirical validation remain separately typed authorities."

OLD_STATE_PATH = ROOT / "machine/roadmap_state.json"
OLD_STATE = json.loads(OLD_STATE_PATH.read_text(encoding="utf-8"))

NEW_RULES = [NEW_LEAN_RULE if rule == OLD_LEAN_RULE else rule for rule in OLD_STATE["rules"]]
NEW_STATE = {
    "type": "uft-id-roadmap-state",
    "schema_version": "1.7.0",
    "snapshot_date": "2026-08-24",
    "basis_commit": MERGE,
    "completed": [5, 6, 7, 8, 9, 11, 12, 13, 14, 15, 16, 17, 18],
    "active_planned_surface": 10,
    "deferred": [],
    "sequence": [
        {"planned_pr": 9, "surface": "deterministic-observation-calculus", "status": "complete"},
        {"planned_pr": 10, "surface": "lean-observation-foundation", "status": ACTIVE_STATUS},
        {"planned_pr": 11, "surface": "relation-first-recovery-core-plus-graph-realization-interlude", "status": "complete-merged-a72dab3170e9880ca8bf120766d8547d6cc0110b"},
        {"planned_pr": 12, "surface": "bridge-core", "status": "complete-merged-2242f96564f4d27af4ba641b45f45f011a49a7c7"},
        {"planned_pr": 13, "surface": "epistemic-bridge-specialization", "status": "complete-merged-083aa9ae9e812cae86302d856f70ad83e5cf806b"},
        {"planned_pr": 14, "surface": "representation-and-congruence-calculus", "status": "complete-merged-a094ec469f311bc6cc11442ee5f850f5dc130e2f"},
        {"planned_pr": 15, "surface": "information-comparability-core", "status": "complete-merged-22b589c4e2e2042d180d64db837f092a007e0813"},
        {"planned_pr": 16, "surface": "recovery-specializations", "status": "complete-merged-2f2cdd2af195a2e74a55e14abfbc4f88e0901a8f"},
        {"planned_pr": 17, "surface": "continuum-stochastic-prevalence-obligations", "status": "complete-merged-353e55a11a8cb6d6bcf571110e0fd6f32823fc77"},
        {"planned_pr": 18, "surface": "empirical-falsification-profile", "status": EFP_COMPLETE},
    ],
    "compatibility_note": "machine/formalization_contract.json retains the PR9-era roadmap_rebase snapshot; frozen PR11, BridgeCore, Epistemic Bridge, Representation, Information Comparability, Recovery, CSP, and EFP theorem authorities retain their historical semantics. This file is the live post-EFP schedule authority with PR #10 activated for first-theorem-batch freezing.",
    "fixture_policy": "Minimal fixtures travel with the theorem or counterexample that requires them.",
    "rules": NEW_RULES,
}


def replace_once(text: str, old: str, new: str, label: str) -> str:
    count = text.count(old)
    if count != 1:
        raise RuntimeError(f"{label}: expected one anchor, found {count}")
    return text.replace(old, new, 1)


def write(path: Path, text: str) -> None:
    path.write_text(text, encoding="utf-8")


def git_blob_sha(data: bytes) -> str:
    return hashlib.sha1(f"blob {len(data)}\0".encode() + data).hexdigest()


# 1. Canonical live machine schedule.
OLD_STATE_PATH.write_text(json.dumps(NEW_STATE, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")

# 2. Human roadmap rollover. Preserve historical compatibility blocks.
roadmap_path = ROOT / "ROADMAP.md"
roadmap = roadmap_path.read_text(encoding="utf-8")
roadmap = replace_once(
    roadmap,
    "- [x] Planned PR #17 — Continuum, stochastic, and prevalence obligations, delivered in GitHub PR #18 and merged at `353e55a11a8cb6d6bcf571110e0fd6f32823fc77`.\n",
    "- [x] Planned PR #17 — Continuum, stochastic, and prevalence obligations, delivered in GitHub PR #18 and merged at `353e55a11a8cb6d6bcf571110e0fd6f32823fc77`.\n"
    f"- [x] Planned PR #18 — Empirical Falsification Profile, delivered in GitHub PR #19 and merged at `{MERGE}` after a clean hostile Codex P1/P2 review of exact head `{EFP_REVIEW_HEAD}`.\n",
    "completed PR18 line",
)
roadmap = replace_once(roadmap, "## Deferred independent proof track\n", "## Active independent proof track\n", "proof-track heading")
roadmap = replace_once(
    roadmap,
    "- [ ] PR #10 — Lean observation foundation.\n",
    "- [ ] PR #10 — Lean observation foundation. **ACTIVE — first theorem-batch freeze and dependency graph.**\n",
    "PR10 live bullet",
)
lean_entry = f'''\n### Active now — planned PR #10\n\n**Status:** ACTIVE — theorem-batch/dependency-graph freeze only. No Lean proof object, source-release tag, or DOI is claimed by this rollover.\n\nImmediate entry task:\n\n- [ ] Freeze the first PR #10 theorem batch and dependency graph.\n- [ ] Name exact source theorem IDs, statements, hypotheses, scopes, nonclaims, and counterexamples.\n- [ ] Define the expected Lean module map without adding proof claims yet.\n- [ ] Keep `MATHEMATICAL_PROOF`, `LEAN_PROOF`, `RUNTIME_CONFORMANCE`, and `EMPIRICAL_VALIDATION` separately typed.\n\nThe exact `Active now — planned PR #18` heading later in this live section is retained only as a merged-validator compatibility anchor. Its status is COMPLETE and it is not current scheduling authority.\n'''
anchor = "```text\nMATHEMATICAL_PROOF != LEAN_PROOF\nLEAN_PROOF != RUNTIME_CONFORMANCE != EMPIRICAL_VALIDATION\n```\n"
roadmap = replace_once(roadmap, anchor, anchor + lean_entry, "PR10 activation section")
roadmap = replace_once(
    roadmap,
    "**Status:** ACTIVE, implemented by the current change.\n",
    f"**Status:** COMPLETE, delivered in GitHub PR #19 and merged at `{MERGE}` after the exact-green-head hostile Codex P1/P2 review returned no major issues. The heading is retained for merged-validator compatibility; live scheduling authority has rolled to PR #10.\n",
    "PR18 live status",
)
roadmap = replace_once(
    roadmap,
    "- [ ] Complete a fresh hostile Codex P1/P2 review on the exact green head.\n",
    f"- [x] Complete a fresh hostile Codex P1/P2 review on the exact green head `{EFP_REVIEW_HEAD}` — Codex reported no major issues before merge.\n",
    "hostile review checkbox",
)
roadmap_path.write_text(roadmap, encoding="utf-8")

# 3. Freeze merged EFP validator and install a live schedule wrapper.
efp_live = ROOT / "scripts/validate_empirical_falsification_profile.py"
efp_frozen = ROOT / "scripts/validate_empirical_falsification_profile_pr19_frozen.py"
if efp_frozen.exists():
    raise RuntimeError("EFP PR19 frozen validator already exists")
shutil.copyfile(efp_live, efp_frozen)

wrapper = f'''#!/usr/bin/env python3\n"""Live compatibility wrapper for the merged PR #19 Empirical Falsification Profile authority.\n\nThe exact EFP validator merged in GitHub PR #19 is preserved in\nvalidate_empirical_falsification_profile_pr19_frozen.py. This wrapper replays\nthat authority against its historical PR18-active roadmap state, then\nindependently validates the post-EFP schedule where PR #18 is complete and\nPR #10 is active only for first-theorem-batch/dependency-graph freezing.\nEFP theorem, counterexample, evidence, receipt, and decision semantics remain\nfrozen.\n"""\nfrom __future__ import annotations\n\nimport copy\nimport importlib.util\nimport json\nfrom pathlib import Path\n\nROOT = Path(__file__).resolve().parents[1]\nFROZEN = ROOT / "scripts/validate_empirical_falsification_profile_pr19_frozen.py"\nROADMAP_STATE = ROOT / "machine/roadmap_state.json"\n\n_spec = importlib.util.spec_from_file_location("efp_validator_pr19_frozen", FROZEN)\nif _spec is None or _spec.loader is None:\n    raise RuntimeError(f"cannot load frozen EFP validator: {{FROZEN}}")\n_frozen = importlib.util.module_from_spec(_spec)\n_spec.loader.exec_module(_frozen)\n\nfor _name in dir(_frozen):\n    if not _name.startswith("__") and _name not in {{"validate", "main"}}:\n        globals()[_name] = getattr(_frozen, _name)\n\nHISTORICAL_ROADMAP_STATE = {pprint.pformat(OLD_STATE, width=120, sort_dicts=False)}\nEXPECTED_LIVE_ROADMAP = {pprint.pformat(NEW_STATE, width=120, sort_dicts=False)}\n\n_original_load_json = _frozen.load_json\n_original_load_module = _frozen.load_module\n\ndef _historical_load_json(path: Path):\n    if path.resolve() == _frozen.PATHS["roadmap_state"].resolve():\n        return copy.deepcopy(HISTORICAL_ROADMAP_STATE)\n    return _original_load_json(path)\n\ndef _live_roadmap_errors() -> list[str]:\n    errors: list[str] = []\n    roadmap = _original_load_json(ROADMAP_STATE)\n    if roadmap.get("schema_version") != "1.7.0": errors.append("EFP live roadmap schema drift")\n    if roadmap.get("snapshot_date") != "2026-08-24": errors.append("EFP contract/result/roadmap snapshot disagreement")\n    if roadmap.get("basis_commit") != "{MERGE}": errors.append("EFP live roadmap basis commit must be merged PR #19")\n    if roadmap.get("active_planned_surface") != 10: errors.append("EFP live roadmap active surface must be PR #10")\n    if roadmap.get("completed") != [5,6,7,8,9,11,12,13,14,15,16,17,18]: errors.append("EFP live roadmap completed set drift")\n    if roadmap.get("deferred") != []: errors.append("EFP live roadmap deferred set drift")\n    sequence = roadmap.get("sequence")\n    if not isinstance(sequence, list):\n        errors.append("EFP live roadmap sequence malformed")\n    else:\n        by_pr = {{item.get("planned_pr"): item for item in sequence if isinstance(item, dict)}}\n        if by_pr.get(10, {{}}).get("status") != "{ACTIVE_STATUS}": errors.append("EFP live roadmap PR10 activation drift")\n        if by_pr.get(18, {{}}).get("status") != "{EFP_COMPLETE}": errors.append("EFP live roadmap PR18 completion drift")\n    if roadmap != EXPECTED_LIVE_ROADMAP: errors.append("EFP live roadmap canonical payload drift")\n    serialized = json.dumps(roadmap, sort_keys=True).casefold()\n    for token in _frozen.PRIVATE_PATTERNS:\n        if token.casefold() in serialized: errors.append(f"EFP live roadmap contains forbidden private locator: {{token}}")\n    return errors\n\ndef validate() -> dict[str, object]:\n    old_json = _frozen.load_json\n    old_module = _frozen.load_module\n    try:\n        _frozen.load_json = _historical_load_json\n        _frozen.load_module = globals().get("load_module", _original_load_module)\n        result = _frozen.validate()\n    finally:\n        _frozen.load_json = old_json\n        _frozen.load_module = old_module\n    errors = list(result.get("errors", []))\n    errors.extend(_live_roadmap_errors())\n    result["errors"] = errors\n    result["status"] = "error" if errors else "ok"\n    return result\n\ndef main() -> int:\n    parser = __import__("argparse").ArgumentParser()\n    parser.add_argument("--json", action="store_true")\n    args = parser.parse_args()\n    result = validate()\n    if args.json:\n        print(json.dumps(result, indent=2, sort_keys=True, allow_nan=False))\n    elif result["status"] == "ok":\n        print(f"Empirical Falsification Profile authority: ok ({{result['result_count']}} results, {{result['boundary_count']}} hard boundaries)")\n    else:\n        for error in result["errors"]: print(error)\n    return 0 if result["status"] == "ok" else 1\n\nif __name__ == "__main__":\n    raise SystemExit(main())\n'''
efp_live.write_text(wrapper, encoding="utf-8")

# 4. Receipt closure now includes the frozen EFP validator depended on by the live wrapper.
for rel in ("experiments/run_empirical_falsification_profile.py", "scripts/verify_empirical_falsification_profile_artifacts.py"):
    path = ROOT / rel
    text = path.read_text(encoding="utf-8")
    anchor = '    "scripts/validate_empirical_falsification_profile.py",\n'
    text = replace_once(text, anchor, anchor + '    "scripts/validate_empirical_falsification_profile_pr19_frozen.py",\n', f"{rel} frozen EFP closure")
    path.write_text(text, encoding="utf-8")

# 5. Advance live schedule wrappers only. Historical state literals remain untouched.

def patch_live_tail(rel: str, marker: str = "def _live_roadmap_errors") -> None:
    path = ROOT / rel
    text = path.read_text(encoding="utf-8")
    if marker not in text:
        raise RuntimeError(f"{rel}: live marker missing")
    prefix, tail = text.split(marker, 1)
    tail = tail.replace('roadmap.get("schema_version") != "1.6.0"', 'roadmap.get("schema_version") != "1.7.0"')
    tail = tail.replace(f'roadmap.get("basis_commit") != "{OLD_BASIS}"', f'roadmap.get("basis_commit") != "{MERGE}"')
    tail = tail.replace("basis commit must be merged CSP PR", "basis commit must be merged EFP PR #19")
    tail = tail.replace('roadmap.get("active_planned_surface") != 18', 'roadmap.get("active_planned_surface") != 10')
    tail = tail.replace("active surface must be PR #18", "active surface must be PR #10")
    tail = tail.replace("active planned surface must be PR18", "active planned surface must be PR10")
    tail = tail.replace("[5,6,7,8,9,11,12,13,14,15,16,17]", "[5,6,7,8,9,11,12,13,14,15,16,17,18]")
    tail = tail.replace("[5, 6, 7, 8, 9, 11, 12, 13, 14, 15, 16, 17]", "[5, 6, 7, 8, 9, 11, 12, 13, 14, 15, 16, 17, 18]")
    tail = tail.replace('roadmap.get("deferred") != [10]', 'roadmap.get("deferred") != []')
    tail = tail.replace('by_pr.get(18,{}).get("status") != "active-implemented-in-current-change"', f'by_pr.get(18,{{}}).get("status") != "{EFP_COMPLETE}"')
    tail = tail.replace('by_pr.get(18, {}).get("status") != "active-implemented-in-current-change"', f'by_pr.get(18, {{}}).get("status") != "{EFP_COMPLETE}"')
    tail = tail.replace("PR18 active-state drift", "PR18 completion drift")
    tail = tail.replace("PR #18 active-state drift", "PR #18 completion drift")
    tail = tail.replace(OLD_LEAN_RULE, NEW_LEAN_RULE)
    path.write_text(prefix + marker + tail, encoding="utf-8")

for rel in (
    "scripts/validate_epistemic_bridge.py",
    "scripts/validate_representation_calculus.py",
    "scripts/validate_information_comparability.py",
    "scripts/validate_recovery_specializations.py",
    "scripts/validate_continuum_stochastic_prevalence.py",
):
    patch_live_tail(rel)

# BridgeCore has an explicit live block before validate().
bridge = ROOT / "scripts/validate_bridge_core.py"
text = bridge.read_text(encoding="utf-8")
marker = "EXPECTED_LIVE_ROADMAP = {"
pre, live = text.split(marker, 1)
start_body, rest = live.split("\n}\n", 1)
new_block = pprint.pformat({k: NEW_STATE[k] for k in ("type", "schema_version", "snapshot_date", "basis_commit", "completed", "active_planned_surface", "deferred")}, width=120, sort_dicts=False)
# pprint emits a full dict, so replace marker+old body through closing brace.
text = pre + "EXPECTED_LIVE_ROADMAP = " + new_block + "\n" + rest
text = text.replace('by_pr.get(18, {}).get("status") != "active-implemented-in-current-change"', f'by_pr.get(18, {{}}).get("status") != "{EFP_COMPLETE}"')
text = text.replace("BridgeCore live roadmap active surface must be PR #18", "BridgeCore live roadmap must mark planned PR #18 complete")
bridge.write_text(text, encoding="utf-8")

# Relation wrapper owns an exact live roadmap payload, so replace its live constants wholesale.
relation = ROOT / "scripts/validate_relation_core.py"
text = relation.read_text(encoding="utf-8")
seq_start = text.index("EXPECTED_ROADMAP_SEQUENCE = [")
state_start = text.index("EXPECTED_ROADMAP_STATE = {", seq_start)
live_fn = text.index("\ndef _live_roadmap_errors", state_start)
seq_repr = pprint.pformat([(x["planned_pr"], x["surface"], x["status"]) for x in NEW_STATE["sequence"]], width=140)
state_repr = pprint.pformat(NEW_STATE, width=140, sort_dicts=False)
text = text[:seq_start] + "EXPECTED_ROADMAP_SEQUENCE = " + seq_repr + "\n\nEXPECTED_ROADMAP_STATE = " + state_repr + "\n" + text[live_fn:]
text = text.replace('roadmap_state.get("active_planned_surface") != 18', 'roadmap_state.get("active_planned_surface") != 10')
text = text.replace("live roadmap active planned surface must be PR18", "live roadmap active planned surface must be PR10")
text = text.replace("[5, 6, 7, 8, 9, 11, 12, 13, 14, 15, 16, 17]", "[5, 6, 7, 8, 9, 11, 12, 13, 14, 15, 16, 17, 18]")
relation.write_text(text, encoding="utf-8")

# 6. Tests: live EFP schedule now guards PR10 activation instead of PR18 activation.
test = ROOT / "tests/test_empirical_falsification_profile.py"
text = test.read_text(encoding="utf-8")
text = replace_once(
    text,
    '        self.assertIn("EFP roadmap active surface must be PR #18", result["errors"])\n',
    '        self.assertIn("EFP live roadmap active surface must be PR #10", result["errors"])\n',
    "EFP live roadmap regression diagnostic",
)
# Bind the new frozen-validator receipt dependency explicitly.
anchor = '        self.assertTrue(expected.issubset(set(R.CORE_FILES)))\n'
text = replace_once(
    text,
    anchor,
    '        self.assertIn("scripts/validate_empirical_falsification_profile_pr19_frozen.py", R.CORE_FILES)\n' + anchor,
    "EFP frozen validator receipt regression",
)
test.write_text(text, encoding="utf-8")

# 7. Refresh graph validator's exact ROADMAP Git-blob pin after human tracker rollover.
graph = ROOT / "scripts/validate_graph_realization.py"
text = graph.read_text(encoding="utf-8")
new_roadmap_blob = git_blob_sha(roadmap_path.read_bytes())
text, count = re.subn(r'("roadmap": ")[0-9a-f]{40}(",)', rf'\g<1>{new_roadmap_blob}\2', text, count=1)
if count != 1:
    raise RuntimeError("graph roadmap blob pin anchor drift")
graph.write_text(text, encoding="utf-8")

# 8. Sanity checks: historical compatibility anchors must still exist.
roadmap_after = roadmap_path.read_text(encoding="utf-8")
for required in (
    "# Historical post-audit grammar retained for validator compatibility",
    "## Active now — planned PR #16",
    "**Status:** HISTORICAL COMPATIBILITY ANCHOR ONLY.",
    "python scripts/validate_recovery_specializations.py",
    "python experiments/recovery_specializations/run.py --json",
    "python experiments/run_recovery_specializations.py --json",
    "## Active now — planned PR #17",
):
    if required not in roadmap_after:
        raise RuntimeError(f"historical compatibility anchor lost: {required}")

print(json.dumps({
    "status": "patched",
    "merge": MERGE,
    "active_planned_surface": NEW_STATE["active_planned_surface"],
    "completed": NEW_STATE["completed"],
    "roadmap_blob": new_roadmap_blob,
}, indent=2))
