"""S6 — evaluate-v2 gelé : 0 LLM / 0 L2, même juge que grade()."""

from __future__ import annotations

import ast
from pathlib import Path

BACKEND = Path(__file__).resolve().parent.parent
SRC = (BACKEND / "routes" / "document_analysis_v2.py").read_text(encoding="utf-8")


def test_v2_forbids_generative_and_l2_imports():
    tree = ast.parse(SRC)
    banned = {
        "openai",
        "llm",
        "pipeline",
        "fallback_v2",
        "correction_v2",
        "correction_v2_retry",
        "socratic_tutor",
        "document_analysis_service",
    }
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
    assert not found, found


def test_v2_delegates_to_grade():
    assert "grade_or_none" in SRC
    assert "evaluate_with_cache" not in SRC
    assert "evaluate_answer_v2" not in SRC
    assert "VERB_RULES" not in SRC
    assert "get_socratic_hint" not in SRC
    assert "source\": \"local_rubric\"" in SRC or "source': 'local_rubric'" in SRC


def test_v2_hint_is_static_not_generative():
    assert "لا تلميح توليدي" in SRC
    assert "request_hint" in SRC
