from __future__ import annotations

import importlib.util
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


V = load_module(
    "lean_observation_freeze_validator_codex_flow_defaults",
    ROOT / "scripts/validate_lean_observation_foundation.py",
)


class FlowStyleInheritedDefaultsRegressions(unittest.TestCase):
    def test_flow_style_inherited_shell_defaults_fail_closed(self):
        workflow = (ROOT / ".github/workflows/vopson-corpus.yml").read_text(encoding="utf-8")
        self.assertEqual(V.workflow_contract_errors(workflow), [])

        workflow_level = workflow.replace(
            "jobs:\n",
            'defaults: {run: {shell: "bash -n {0}"}}\n\njobs:\n',
            1,
        )
        errors = V.workflow_contract_errors(workflow_level)
        self.assertTrue(
            any("workflow scope" in error and "defaults.run.shell" in error for error in errors),
            errors,
        )

        job_level = workflow.replace(
            "  validate-corpus:\n",
            '  validate-corpus:\n    defaults: {run: {shell: "bash -n {0}"}}\n',
            1,
        )
        errors = V.workflow_contract_errors(job_level)
        self.assertTrue(
            any("validate-corpus" in error and "defaults.run.shell" in error for error in errors),
            errors,
        )

    def test_quoted_flow_style_defaults_key_is_also_rejected(self):
        workflow = (ROOT / ".github/workflows/vopson-corpus.yml").read_text(encoding="utf-8")
        mutated = workflow.replace(
            "jobs:\n",
            '"defaults": {"run": {"shell": "bash -n {0}"}}\n\njobs:\n',
            1,
        )
        errors = V.workflow_contract_errors(mutated)
        self.assertTrue(
            any("workflow scope" in error and "defaults.run.shell" in error for error in errors),
            errors,
        )


if __name__ == "__main__":
    unittest.main()
