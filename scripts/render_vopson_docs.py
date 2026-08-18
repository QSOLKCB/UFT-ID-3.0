#!/usr/bin/env python3
"""Render or verify machine-derived Vopson Markdown tables.

The prose remains hand-authored. Only the table immediately following each
canonical heading is replaced from the JSON authority.
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path
import sys
from typing import Sequence

SCRIPT_DIR = Path(__file__).resolve().parent
if str(SCRIPT_DIR) not in sys.path:
    sys.path.insert(0, str(SCRIPT_DIR))

import validate_vopson_corpus as corpus_validator  # noqa: E402

ROOT = Path(__file__).resolve().parents[1]
CORPUS_JSON = ROOT / "research/vopson/corpus.json"
GRAPH_JSON = ROOT / "research/vopson/CLAIM_GRAPH.json"
CORPUS_MD = ROOT / "research/vopson/CORPUS.md"
GRAPH_MD = ROOT / "research/vopson/CLAIM_GRAPH.md"


def replace_table(text: str, heading: str, rows: Sequence[str]) -> str:
    """Replace the first Markdown table below ``heading`` deterministically."""

    lines = text.splitlines()
    try:
        heading_index = lines.index(heading)
    except ValueError as exc:
        raise ValueError(f"missing heading: {heading}") from exc

    table_start: int | None = None
    table_end: int | None = None
    for index in range(heading_index + 1, len(lines)):
        stripped = lines[index].strip()
        if stripped.startswith("## ") and index > heading_index + 1:
            break
        if table_start is None and stripped.startswith("|"):
            table_start = index
        elif table_start is not None and not stripped.startswith("|"):
            table_end = index
            break

    if table_start is None:
        insertion = heading_index + 1
        while insertion < len(lines) and not lines[insertion].strip():
            insertion += 1
        new_lines = lines[:insertion] + list(rows) + [""] + lines[insertion:]
    else:
        if table_end is None:
            table_end = len(lines)
        new_lines = lines[:table_start] + list(rows) + lines[table_end:]

    return "\n".join(new_lines).rstrip() + "\n"


def expected_documents() -> dict[Path, str]:
    corpus = corpus_validator.load_json(CORPUS_JSON)
    graph = corpus_validator.load_json(GRAPH_JSON)

    corpus_text = replace_table(
        CORPUS_MD.read_text(encoding="utf-8"),
        corpus_validator.CORPUS_HEADING,
        corpus_validator.render_corpus_table(list(corpus.get("works", []))),
    )
    graph_text = replace_table(
        GRAPH_MD.read_text(encoding="utf-8"),
        corpus_validator.GRAPH_HEADING,
        corpus_validator.render_claim_table(list(graph.get("nodes", []))),
    )
    return {CORPUS_MD: corpus_text, GRAPH_MD: graph_text}


def render(*, check: bool) -> dict[str, object]:
    changed: list[str] = []
    documents = expected_documents()
    for path, expected in documents.items():
        actual = path.read_text(encoding="utf-8")
        if actual == expected:
            continue
        changed.append(path.relative_to(ROOT).as_posix())
        if not check:
            path.write_text(expected, encoding="utf-8")

    return {
        "ok": not (check and changed),
        "mode": "check" if check else "write",
        "changed": changed,
        "documents": [path.relative_to(ROOT).as_posix() for path in documents],
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--check", action="store_true", help="fail if generated tables are stale")
    parser.add_argument("--json", action="store_true", help="emit a machine-readable report")
    args = parser.parse_args()

    report = render(check=args.check)
    if args.json:
        print(json.dumps(report, indent=2, sort_keys=True))
    elif report["changed"]:
        verb = "stale" if args.check else "updated"
        for path in report["changed"]:
            print(f"{verb}: {path}")
    else:
        print("Vopson human/machine tables are synchronized")

    raise SystemExit(0 if report["ok"] else 1)


if __name__ == "__main__":
    main()
