"""S8 — 2ᵉ cerveau JS mort ; evaluate.py / ai_evaluate hors registre."""

from __future__ import annotations

from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent.parent
BACKEND = Path(__file__).resolve().parent.parent

INIT = (BACKEND / "routes" / "__init__.py").read_text(encoding="utf-8")
JS = (
    ROOT
    / "khawarizmi-frontend"
    / "src"
    / "lib"
    / "methodology-evaluator.ts"
).read_text(encoding="utf-8")
GRADER = (BACKEND / "services" / "local_grader.py").read_text(encoding="utf-8")


def test_evaluate_and_ai_evaluate_not_in_all_routers():
    assert "evaluate.router" not in INIT
    assert "ai_evaluate.router" not in INIT
    assert "from . import (" in INIT
    # présents comme fichiers, absents du registre
    assert (BACKEND / "routes" / "evaluate.py").is_file()
    assert (BACKEND / "routes" / "ai_evaluate.py").is_file()


def test_js_evaluator_always_ungraded():
    assert "source: \"ungraded\"" in JS
    assert "ungraded: true" in JS
    assert "return evaluateAnalyse" not in JS
    assert "ليست علامة بكالوريا رسمية" in JS


def test_grader_version_1_1_4():
    assert 'GRADER_VERSION = "1.1.7"' in GRADER
