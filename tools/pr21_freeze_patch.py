#!/usr/bin/env python3
from __future__ import annotations

import hashlib
import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
BASE = "6f3aeb7f4ac14389e7a08d2976c8c0d16549c093"


def replace_once(path: str, old: str, new: str) -> None:
    target = ROOT / path
    text = target.read_text(encoding="utf-8")
    count = text.count(old)
    if count != 1:
        raise RuntimeError(f"{path}: expected one replacement anchor, found {count}: {old[:80]!r}")
    target.write_text(text.replace(old, new, 1), encoding="utf-8")


def replace_all(path: str, old: str, new: str, expected_count: int) -> None:
    target = ROOT / path
    text = target.read_text(encoding="utf-8")
    count = text.count(old)
    if count != expected_count:
        raise RuntimeError(f"{path}: expected {expected_count} anchors, found {count}: {old[:80]!r}")
    target.write_text(text.replace(old, new), encoding="utf-8")


def git_blob_sha(path: Path) -> str:
    data = path.read_bytes()
    return hashlib.sha1(f"blob {len(data)}\0".encode("ascii") + data).hexdigest()


def main() -> int:
    # Refuse to patch target files if they drifted from the exact post-PR20 source basis.
    guarded = [
        "machine/contract.json",
        "README4AI.md",
        "AGENTS.md",
        "docs/REPRODUCIBILITY.md",
        "ROADMAP.md",
        ".github/workflows/finite-adversarial.yml",
        "scripts/validate_graph_realization.py",
    ]
    import subprocess
    for rel in guarded:
        result = subprocess.run(["git", "diff", "--quiet", BASE, "--", rel])
        if result.returncode != 0:
            raise RuntimeError(f"guarded PR21 target drifted from {BASE}: {rel}")

    # Register the freeze as a first-class repository authority without changing
    # the base contract schema version used by historical validators.
    authority = '''  "lean_observation_foundation_authority": {
    "machine_contract": "machine/lean_observation_foundation_contract.json",
    "human": "theory/LEAN_OBSERVATION_FOUNDATION.md",
    "validator": "scripts/validate_lean_observation_foundation.py",
    "tests": "tests/test_lean_observation_foundation.py",
    "source_theorems": "machine/observation_theorems.json",
    "source_counterexamples": "machine/observation_counterexamples.json",
    "source_observation_contract": "machine/observation_contract.json",
    "workflow": ".github/workflows/finite-adversarial.yml",
    "rule": "The first Lean observation batch freezes source theorem identity and dependency/module mapping only; it does not claim Lean proof, select a toolchain, or create the immutable source-release tag."
  },
'''
    replace_once(
        "machine/contract.json",
        '  "vopson_corpus_authority": {\n',
        authority + '  "vopson_corpus_authority": {\n',
    )

    readme_old = (
        "PR #10 Lean observation foundation is active only for theorem-batch and dependency-graph freezing. "
        "Lean proof implementation, source tagging, QSOL-CONTEXT target binding, and Zenodo publication are not claimed by this rollover and remain gated by the ordered workflow in `ROADMAP.md`. "
        "Detailed formalization/publication workflow planning remains ROADMAP-only and is not promoted into current proof, empirical, or publication authority."
    )
    readme_new = '''PR #10 Lean observation foundation is active. Source batch `LEAN-OBS-BATCH-001` is frozen in `machine/lean_observation_foundation_contract.json`, covering `UFT-OBS-001` through `UFT-OBS-004`; `UFT-OBS-005` remains deferred to a later arithmetic-focused batch.

No Lean proof object is claimed by this freeze. Lean/Lake/Mathlib remain unpinned. After PR #21 merges, the next gate is exact merged-`main` CI plus hostile review, then tag that exact merged commit/tree before Lean proof implementation. QSOL-CONTEXT target binding and Zenodo publication remain later ordered gates in `ROADMAP.md`.

Canonical source-freeze surfaces:

```text
machine/lean_observation_foundation_contract.json
theory/LEAN_OBSERVATION_FOUNDATION.md
scripts/validate_lean_observation_foundation.py
tests/test_lean_observation_foundation.py
```

```text
MATHEMATICAL_PROOF != LEAN_PROOF
SOURCE_THEOREM != LEAN_ARTIFACT
THEOREM_BATCH_FREEZE != SOURCE_RELEASE_TAG
SOURCE_RELEASE_TAG != LEAN_VERIFIED
```'''
    replace_once("README4AI.md", readme_old, readme_new)

    replace_once(
        "AGENTS.md",
        "python scripts/validate_reproducibility.py\npython -m unittest discover -s tests -v",
        "python scripts/validate_reproducibility.py\npython scripts/validate_lean_observation_foundation.py\npython -m unittest discover -s tests -v",
    )
    replace_once(
        "AGENTS.md",
        "Lean remains deferred. When it begins, compile it in CI, map theorem IDs to the\npaper, distinguish imported theorems from UFT-ID results, and never claim an\nontology is proved merely because an abstract theorem compiles.",
        "PR #10 source theorem freezing is active, but Lean proof implementation remains\ngated until the frozen batch is merged, exact merged-main CI/audit is green, and\nan immutable source-release tag binds the target commit/tree. When Lean proof work\nbegins, compile it in CI, map theorem IDs to the source authority, distinguish\nimported theorems from UFT-ID results, and never claim an ontology is proved merely\nbecause an abstract theorem compiles.",
    )

    replace_once(
        "docs/REPRODUCIBILITY.md",
        "python scripts/validate_observation_specs.py\npython scripts/validate_relation_core.py",
        "python scripts/validate_observation_specs.py\npython scripts/validate_lean_observation_foundation.py\npython scripts/validate_relation_core.py",
    )
    repro_anchor = "## Graph-realization conformance boundary\n"
    repro_section = '''## Lean observation source-freeze boundary

`LEAN-OBS-BATCH-001` freezes source theorem identity for `UFT-OBS-001` through `UFT-OBS-004`, their dependency/counterexample links, and the expected future Lean module/declaration map. `UFT-OBS-005` remains explicitly deferred.

Canonical validation:

```bash
python scripts/validate_observation_specs.py
python scripts/validate_lean_observation_foundation.py
```

The freeze validator recomputes Git blob identities for the pinned PR9 source authority and rejects statement, hypothesis, nonclaim, dependency, module-map, toolchain, source-tag, or bootstrap drift.

```text
SOURCE_THEOREM_FREEZE != LEAN_PROOF
THEOREM_BATCH_FREEZE != SOURCE_RELEASE_TAG
SOURCE_RELEASE_TAG != LEAN_VERIFIED
```

No deterministic Lean receipt is created in this phase because no Lean toolchain or proof source exists yet.

'''
    replace_once("docs/REPRODUCIBILITY.md", repro_anchor, repro_section + repro_anchor)

    replace_once(
        "ROADMAP.md",
        "**Status:** ACTIVE — theorem-batch/dependency-graph freeze only. No Lean proof object, source-release tag, or DOI is claimed by this rollover.",
        "**Status:** ACTIVE — first theorem batch frozen by PR #21; exact merged-main release gate and immutable source tag are next. No Lean proof object, source-release tag, or DOI is claimed by this freeze PR.",
    )
    replace_once(
        "ROADMAP.md",
        "- [ ] Freeze the first PR #10 theorem batch and dependency graph.\n- [ ] Name exact source theorem IDs, statements, hypotheses, scopes, nonclaims, and counterexamples.\n- [ ] Define the expected Lean module map without adding proof claims yet.\n- [ ] Keep `MATHEMATICAL_PROOF`, `LEAN_PROOF`, `RUNTIME_CONFORMANCE`, and `EMPIRICAL_VALIDATION` separately typed.",
        "- [x] Freeze the first PR #10 theorem batch and dependency graph.\n- [x] Name exact source theorem IDs, statements, hypotheses, scopes, nonclaims, and counterexamples.\n- [x] Define the expected Lean module map without adding proof claims yet.\n- [x] Keep `MATHEMATICAL_PROOF`, `LEAN_PROOF`, `RUNTIME_CONFORMANCE`, and `EMPIRICAL_VALIDATION` separately typed.\n\nFrozen batch: `LEAN-OBS-BATCH-001`, covering `UFT-OBS-001` through `UFT-OBS-004`. `UFT-OBS-005` remains explicitly deferred to a later arithmetic-focused Lean batch. The live PR #10 phase remains active until the exact merged-main release gate is green and the immutable source tag is cut.",
    )
    replace_once(
        "ROADMAP.md",
        "**Status:** ROADMAP-ONLY workflow contract for deferred PR #10 and later formalization releases.",
        "**Status:** ROADMAP-ONLY workflow contract for active PR #10 and later formalization releases.",
    )
    replace_once(
        "ROADMAP.md",
        "- [ ] Freeze the first PR #10 theorem batch and dependency graph.\n- [ ] Pass the exact merged-main release gate and cut the immutable source tag.",
        "- [x] Freeze the first PR #10 theorem batch and dependency graph.\n- [ ] Pass the exact merged-main release gate and cut the immutable source tag.",
    )

    # Run the new validator whenever its human authority changes and execute it
    # immediately after the frozen PR9 observation authority.
    replace_all(
        ".github/workflows/finite-adversarial.yml",
        '      - "theory/OBSERVATION_CALCULUS.md"\n',
        '      - "theory/OBSERVATION_CALCULUS.md"\n      - "theory/LEAN_OBSERVATION_FOUNDATION.md"\n',
        2,
    )
    replace_once(
        ".github/workflows/finite-adversarial.yml",
        "      - name: Run PR9 observation witnesses\n        run: |\n          python experiments/observation/run.py --json > /tmp/pr9-observation.json\n          python experiments/run_pr9.py --hash-only > /tmp/pr9-observation-receipt.json\n\n      - name: Validate PR11 relation and selection authority surface",
        "      - name: Run PR9 observation witnesses\n        run: |\n          python experiments/observation/run.py --json > /tmp/pr9-observation.json\n          python experiments/run_pr9.py --hash-only > /tmp/pr9-observation-receipt.json\n\n      - name: Validate PR10 Lean observation source freeze\n        run: python scripts/validate_lean_observation_foundation.py\n\n      - name: Validate PR11 relation and selection authority surface",
    )

    # Central graph authority pins human bootstrap surfaces exactly. Refresh only
    # the files changed by this freeze PR.
    graph = ROOT / "scripts/validate_graph_realization.py"
    text = graph.read_text(encoding="utf-8")
    pins = {
        "readme4ai": git_blob_sha(ROOT / "README4AI.md"),
        "reproducibility": git_blob_sha(ROOT / "docs/REPRODUCIBILITY.md"),
        "roadmap": git_blob_sha(ROOT / "ROADMAP.md"),
    }
    for key, value in pins.items():
        pattern = rf'(\"{key}\": \"?)[0-9a-f]{{40}}(\"?,)'
        text, count = re.subn(pattern, rf'\g<1>{value}\g<2>', text, count=1)
        if count != 1:
            raise RuntimeError(f"graph human blob pin not found exactly once: {key}")
    graph.write_text(text, encoding="utf-8")

    # Sanity-check machine JSON after textual registration.
    json.loads((ROOT / "machine/contract.json").read_text(encoding="utf-8"))
    print(json.dumps({"status": "patched", "batch": "LEAN-OBS-BATCH-001", "basis": BASE, "graph_pins": pins}, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
