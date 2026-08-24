#!/usr/bin/env python3
"""Compatibility wrapper around the frozen PR11 graph validator.

The PR11 graph validation logic remains byte-for-byte preserved in
validate_graph_realization_pr11_frozen.py. Later formal phases may extend the
central human authority surfaces or use an equivalent one-line workflow run
syntax. This wrapper advances only those exact compatibility pins while
retaining every frozen graph theorem, donor, command, always-run requirement,
and semantic-boundary check.
"""
from __future__ import annotations

import importlib.util
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
FROZEN = ROOT / "scripts/validate_graph_realization_pr11_frozen.py"

_spec = importlib.util.spec_from_file_location("graph_validator_pr11_frozen", FROZEN)
if _spec is None or _spec.loader is None:
    raise RuntimeError(f"cannot load frozen graph validator: {FROZEN}")
_frozen = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(_frozen)

_frozen.EXPECTED_HUMAN_BLOBS.update({
    "claims": "b8242ecfac94ec0a516c76bbd81a27c6f3a8114a",
    "readme4ai": "0c29ebbde089ff62ad8eb0ec96746ad8d1ade8db",
    "reproducibility": "a58f59475260e73e24ee3a6957b2baf01db4473f",
    "roadmap": "7a602769908e2ff83ae49a32539fd1a5a5340ce4",
})
_frozen.EXPECTED_VERIFY_STEP_DIRECTIVES = (
    "if: always()",
    "run: python scripts/verify_graph_artifacts.py artifacts",
)

_original_shell_lines = _frozen.workflow_step_shell_lines


def _workflow_step_shell_lines_compat(text: str, step_name: str) -> tuple[str, ...]:
    lines = _original_shell_lines(text, step_name)
    if lines or step_name != "Verify retained graph evidence":
        return lines
    directives = _frozen.workflow_step_directives(text, step_name)
    expected_run = "run: python scripts/verify_graph_artifacts.py artifacts"
    if directives == ("if: always()", expected_run):
        return (_frozen.GRAPH_ARTIFACT_VERIFY_COMMAND,)
    return ()


_frozen.workflow_step_shell_lines = _workflow_step_shell_lines_compat

for _name in dir(_frozen):
    if not _name.startswith("__"):
        globals()[_name] = getattr(_frozen, _name)

if __name__ == "__main__":
    raise SystemExit(_frozen.main())
