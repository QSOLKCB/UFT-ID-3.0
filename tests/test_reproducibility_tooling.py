from __future__ import annotations

import importlib.util
from pathlib import Path
import shutil
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[1]


def load_module(name: str, relative_path: str, root: Path = ROOT):
    path = root / relative_path
    spec = importlib.util.spec_from_file_location(name, path)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"cannot load {path}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


RENDER = load_module("render_vopson_docs", "scripts/render_vopson_docs.py")
REPRO = load_module("validate_reproducibility", "scripts/validate_reproducibility.py")


def validate_mutation(mutator):
    with tempfile.TemporaryDirectory() as temporary:
        clone = Path(temporary) / "repo"
        shutil.copytree(
            ROOT,
            clone,
            ignore=shutil.ignore_patterns(".git", "__pycache__", ".pytest_cache", "artifacts"),
        )
        mutator(clone)
        return load_module(
            f"validate_reproducibility_{id(clone)}",
            "scripts/validate_reproducibility.py",
            clone,
        ).validate(clone)


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
    def assert_rejected(self, report, fragment: str):
        self.assertFalse(report["ok"], report)
        self.assertTrue(
            any(fragment in error for error in report["errors"]),
            report["errors"],
        )

    def test_repository_reproducibility_contract_passes(self):
        report = REPRO.validate()
        self.assertTrue(report["ok"], report["errors"])
        self.assertGreaterEqual(report["summary"]["action_pins"], 3)
        self.assertEqual(report["summary"]["runner"], "ubuntu-24.04")
        self.assertEqual(report["summary"]["workflows"], 2)

    def test_structural_parser_reads_effective_policy_fields(self):
        parsed = REPRO.parse_workflow(ROOT / ".github/workflows/finite-adversarial.yml")
        self.assertEqual(parsed["permissions"], {"contents": "read"})
        job = parsed["jobs"]["finite-results"]
        self.assertEqual(job["runner"], "ubuntu-24.04")
        self.assertEqual(job["matrix_python"], ["3.12", "3.13"])
        upload = next(
            step
            for step in job["steps"]
            if str(step.get("uses", "")).startswith("actions/upload-artifact@")
        )
        self.assertEqual(upload["with"]["retention-days"], 30)
        evidence = next(
            step
            for step in job["steps"]
            if step.get("name") == "Generate deterministic evidence bundle"
        )
        self.assertEqual(evidence["if"], "always()")

    def test_rejects_undeclared_yaml_workflow(self):
        def mutate(root: Path):
            path = root / ".github/workflows/rogue.yaml"
            path.write_text(
                "name: rogue\npermissions:\n  contents: read\njobs:\n  rogue:\n    runs-on: ubuntu-24.04\n    steps:\n      - run: echo rogue\n",
                encoding="utf-8",
            )

        self.assert_rejected(
            validate_mutation(mutate),
            "discovered GitHub workflows must exactly match machine contract",
        )

    def test_rejects_write_permissions(self):
        def mutate(root: Path):
            path = root / ".github/workflows/finite-adversarial.yml"
            text = path.read_text(encoding="utf-8").replace("contents: read", "contents: write", 1)
            path.write_text(text, encoding="utf-8")

        self.assert_rejected(
            validate_mutation(mutate),
            "top-level permissions must exactly equal",
        )

    def test_comments_cannot_spoof_runner_policy(self):
        def mutate(root: Path):
            path = root / ".github/workflows/finite-adversarial.yml"
            text = path.read_text(encoding="utf-8")
            text = text.replace(
                "    runs-on: ubuntu-24.04",
                "    runs-on: ubuntu-latest\n    # runs-on: ubuntu-24.04",
                1,
            )
            path.write_text(text, encoding="utf-8")

        self.assert_rejected(validate_mutation(mutate), "runs-on must equal ubuntu-24.04")

    def test_rejects_wrong_artifact_retention(self):
        def mutate(root: Path):
            path = root / ".github/workflows/vopson-corpus.yml"
            text = path.read_text(encoding="utf-8").replace("retention-days: 30", "retention-days: 7", 1)
            path.write_text(text, encoding="utf-8")

        self.assert_rejected(validate_mutation(mutate), "artifact retention-days must equal 30")

    def test_rejects_evidence_generation_without_always_condition(self):
        def mutate(root: Path):
            path = root / ".github/workflows/finite-adversarial.yml"
            text = path.read_text(encoding="utf-8").replace(
                "      - name: Generate deterministic evidence bundle\n        if: always()\n",
                "      - name: Generate deterministic evidence bundle\n",
                1,
            )
            path.write_text(text, encoding="utf-8")

        self.assert_rejected(validate_mutation(mutate), "evidence generation must use if: always()")

    def test_action_ref_requires_full_sha(self):
        match = REPRO.ACTION_REF_RE.fullmatch(
            "actions/checkout@" + "a" * 40
        )
        self.assertIsNotNone(match)
        self.assertIsNone(REPRO.ACTION_REF_RE.fullmatch("actions/checkout@v6"))


if __name__ == "__main__":
    unittest.main()
