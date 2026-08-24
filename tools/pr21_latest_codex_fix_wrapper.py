#!/usr/bin/env python3
from __future__ import annotations

from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
source_path = ROOT / "tools/pr21_latest_codex_fix.py"
text = source_path.read_text(encoding="utf-8")

start = "    step = '''      - name: Validate Lean observation source freeze\\n"
end = "        run: python scripts/validate_lean_observation_foundation.py\\n'''\\n    if text.count(step)"
if text.count(start) != 1 or text.count(end) != 1:
    raise RuntimeError("staging helper delimiter anchors drifted")
text = text.replace(start, '    step = """      - name: Validate Lean observation source freeze\\n', 1)
text = text.replace(end, '        run: python scripts/validate_lean_observation_foundation.py\\n"""\\n    if text.count(step)', 1)

old_import_patch = '''    text = text.replace(
        "import hashlib\\nimport importlib.util\\nimport json\\nimport os\\nimport re\\n",
        "import hashlib\\nimport importlib.util\\nimport json\\nimport os\\nimport re\\nimport subprocess\\n",
        1,
    )
'''
new_import_patch = '''    text = text.replace(
        "import hashlib\\nimport importlib.util\\nimport json\\nimport re\\n",
        "import hashlib\\nimport importlib.util\\nimport json\\nimport os\\nimport re\\nimport subprocess\\n",
        1,
    )
'''
if text.count(old_import_patch) != 1:
    raise RuntimeError("staging helper import patch anchor drifted")
text = text.replace(old_import_patch, new_import_patch, 1)

namespace = {"__name__": "__main__", "__file__": str(source_path)}
exec(compile(text, str(source_path), "exec"), namespace)
