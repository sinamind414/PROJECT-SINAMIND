"""S11 — schéma dessiné = 0 auto ; evaluation_mode sans GPT/L2."""

from __future__ import annotations

import ast
from pathlib import Path

BACKEND = Path(__file__).resolve().parent.parent
ROOT = BACKEND.parent

DUAL = (BACKEND / "routes" / "dual_coding.py").read_text(encoding="utf-8")
EVAL_MODE = (BACKEND / "services" / "ai_modes" / "evaluation_mode.py").read_text(
    encoding="utf-8"
)
INIT = (BACKEND / "routes" / "__init__.py").read_text(encoding="utf-8")


def _banned_imports(src: str, banned: set[str]) -> set[str]:
    tree = ast.parse(src)
    found: set[str] = set()
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            for alias in node.names:
                root = alias.name.split(".")[0]
                if root in banned or alias.name in banned:
                    found.add(alias.name)
        elif isinstance(node, ast.ImportFrom):
            mod = node.module or ""
            root = mod.split(".")[0]
            if root in banned or mod in banned:
                found.add(mod)
    return found


def test_dual_coding_evaluate_does_not_call_vision():
    assert "evaluer_schema_photo" not in DUAL
    assert "ungraded=True" in DUAL or "ungraded: bool = True" in DUAL
    assert "لا تصحيح آلي للرسم" in DUAL
    assert "score=0" in DUAL


def test_evaluation_mode_does_not_import_llm():
    found = _banned_imports(
        EVAL_MODE,
        {
            "openai",
            "llm",
            "pipeline",
            "fallback_v2",
            "methodology",
            "evaluate",
        },
    )
    assert not found, found
    assert "evaluate_with_fallback" not in EVAL_MODE
    assert "evaluate_methodology" not in EVAL_MODE
    assert "grade_or_none" in EVAL_MODE
    assert "ungraded" in EVAL_MODE


def test_evaluate_still_not_mounted():
    assert "evaluate.router" not in INIT
    assert "ai_evaluate.router" not in INIT


def test_no_evaluate_with_fallback_in_live_services():
    live = [
        BACKEND / "services" / "ai_modes" / "evaluation_mode.py",
        BACKEND / "routes" / "flashcards.py",
        BACKEND / "routes" / "exercices.py",
        BACKEND / "routes" / "dual_coding.py",
        BACKEND / "routes" / "document_analysis_v2.py",
        BACKEND / "routes" / "methodology.py",
    ]
    for path in live:
        src = path.read_text(encoding="utf-8")
        assert "evaluate_with_fallback" not in src, path.name
