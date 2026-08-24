#!/usr/bin/env python3
from __future__ import annotations

import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
BASE = "6f3aeb7f4ac14389e7a08d2976c8c0d16549c093"
OLD = "PR #10 Lean observation foundation is active only for theorem-batch and dependency-graph freezing."
NEW = "PR #10 Lean observation foundation is active. Source batch `LEAN-OBS-BATCH-001` is frozen in `machine/lean_observation_foundation_contract.json`, covering `UFT-OBS-001` through `UFT-OBS-004`; `UFT-OBS-005` remains deferred to a later arithmetic-focused batch."


def replace_once(relpath: str, old: str, new: str) -> None:
    path = ROOT / relpath
    text = path.read_text(encoding="utf-8")
    if text.count(old) != 1:
        raise RuntimeError(f"{relpath}: expected exactly one anchor for PR21 bootstrap advancement")
    path.write_text(text.replace(old, new, 1), encoding="utf-8")


def main() -> int:
    targets = [
        "scripts/validate_empirical_falsification_profile.py",
        "tests/test_post_efp_bootstrap_schedule.py",
    ]
    for rel in targets:
        if subprocess.run(["git", "diff", "--quiet", BASE, "--", rel]).returncode != 0:
            raise RuntimeError(f"guarded PR20 live bootstrap surface drifted from {BASE}: {rel}")

    replace_once("scripts/validate_empirical_falsification_profile.py", OLD, NEW)
    replace_once("tests/test_post_efp_bootstrap_schedule.py", OLD, NEW)

    validator = ROOT / "scripts/validate_empirical_falsification_profile.py"
    text = validator.read_text(encoding="utf-8")
    forbidden_anchor = '        "Lean remains deferred until source reproduction",\n'
    if text.count(forbidden_anchor) != 1:
        raise RuntimeError("EFP live forbidden bootstrap anchor drift")
    text = text.replace(forbidden_anchor, forbidden_anchor + f'        "{OLD}",\n', 1)
    validator.write_text(text, encoding="utf-8")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
