"""S7 — /api/evaluate/methodology gelé. 0 evaluate_methodology."""

from __future__ import annotations

import ast
from pathlib import Path

BACKEND = Path(__file__).resolve().parent.parent
SRC = (BACKEND / "routes" / "methodology.py").read_text(encoding="utf-8")


def test_methodology_route_does_not_import_old_evaluator():
    tree = ast.parse(SRC)
    banned = {"methodology", "openai", "llm", "pipeline", "fallback_v2"}
    found: set[str] = set()
    for node in ast.walk(tree):
        if isinstance(node, ast.ImportFrom):
            mod = node.module or ""
            if mod.split(".")[0] in banned or mod.startswith("methodology"):
                found.add(mod)
        elif isinstance(node, ast.Import):
            for alias in node.names:
                if alias.name.split(".")[0] in banned:
                    found.add(alias.name)
    assert not found, found
    assert "from methodology.evaluator import evaluate_methodology" not in SRC
    assert "ungraded_http" in SRC
    assert "grade_or_none" in SRC
