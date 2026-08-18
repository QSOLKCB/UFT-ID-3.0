from __future__ import annotations

import importlib.util
from pathlib import Path
import unittest

ROOT = Path(__file__).resolve().parents[1]


def load_module(name: str, relative_path: str):
    path = ROOT / relative_path
    spec = importlib.util.spec_from_file_location(name, path)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"cannot load {path}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


RENDER = load_module("render_vopson_docs", "scripts/render_vopson_docs.py")
REPRO = load_module("validate_reproducibility", "scripts/validate_reproducibility.py")


class RendererTests(unittest.TestCase):
    def test_replace_table_preserves_prose_and_replaces_only_table(self):
        original = "# Title\n\n## Data\n\n| old |\n|---|\n| x |\n\nTail\n"
        rendered = RENDER.replace_table(
            original,
            "## Data",
            ["| new |", "|---|", "| y |"],
        )
        self.assertIn("| new |", rendered)
        self.assertNotIn("| old |", rendered)
        self.assertTrue(rendered.endswith("Tail\n"))

    def test_canonical_human_tables_are_current(self):
        report = RENDER.render(check=True)
        self.assertTrue(report["ok"], report)
        self.assertEqual(report["changed"], [])


class ReproducibilityPolicyTests(unittest.TestCase):
    def test_repository_reproducibility_contract_passes(self):
        report = REPRO.validate()
        self.assertTrue(report["ok"], report["errors"])
        self.assertGreaterEqual(report["summary"]["action_pins"], 3)
        self.assertEqual(report["summary"]["runner"], "ubuntu-24.04")

    def test_action_regex_rejects_mutable_tags(self):
        self.assertIsNone(REPRO.USES_RE.match("      - uses: actions/checkout@v6"))
        self.assertIsNotNone(
            REPRO.USES_RE.match(
                "      - uses: actions/checkout@" + "a" * 40 + " # v6"
            )
        )


if __name__ == "__main__":
    unittest.main()
