#!/usr/bin/env python3
from __future__ import annotations

from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
source_path = ROOT / "tools/pr21_latest_codex_fix_v2.py"
text = source_path.read_text(encoding="utf-8")
old1 = '''        mutated = workflow.replace('      - "theory/LEAN_OBSERVATION_FOUNDATION.md"\\n', "", 1)
'''
new1 = '''        mutated = workflow.replace('      - "theory/LEAN_OBSERVATION_FOUNDATION.md"\\\\n', "", 1)
'''
old2 = '''        mutated = workflow.replace("        run: python scripts/validate_lean_observation_foundation.py\\n", "        run: python -c 'pass'\\n", 1)
'''
new2 = '''        mutated = workflow.replace("        run: python scripts/validate_lean_observation_foundation.py\\\\n", "        run: python -c 'pass'\\\\n", 1)
'''
if text.count(old1) != 1 or text.count(old2) != 1:
    raise RuntimeError("v2 generated-test escape anchors drifted")
text = text.replace(old1, new1, 1).replace(old2, new2, 1)
namespace = {"__name__": "__main__", "__file__": str(source_path)}
exec(compile(text, str(source_path), "exec"), namespace)
