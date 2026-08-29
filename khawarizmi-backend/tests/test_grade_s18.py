"""S18 — validate_rubrics : goldens négatifs (hors-sujet, 36 ATP, vide). Bloque le merge."""

from __future__ import annotations

import importlib.util
from pathlib import Path

from services.local_grader import GRADER_VERSION
from services.rubric_store import list_question_ids

BACKEND = Path(__file__).resolve().parent.parent
VAL = (BACKEND / "scripts" / "validate_rubrics.py").read_text(encoding="utf-8")
GRADER = (BACKEND / "services" / "local_grader.py").read_text(encoding="utf-8")
GOLDEN = (BACKEND / "tests" / "golden" / "test_rubric_l0.py").read_text(encoding="utf-8")
INIT = (BACKEND / "routes" / "__init__.py").read_text(encoding="utf-8")


def _mod():
    spec = importlib.util.spec_from_file_location(
        "validate_rubrics_s18", BACKEND / "scripts" / "validate_rubrics.py"
    )
    assert spec is not None and spec.loader is not None
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def test_validator_has_negative_goldens():
    assert "GEOLOGY" in VAL
    assert "ATP36" in VAL
    assert "overall_training_percent > 40" in VAL
    assert 'science_status != "error"' in VAL
    assert "model_answer vide" in VAL


def test_negatives_match_pytest_golden_copies():
    """Même copies que golden L0 (le JSON est coupé en deux chaînes)."""
    mod = _mod()
    assert "تباعد الصفائح" in GOLDEN
    assert "تباعد الصفائح" in mod.GEOLOGY
    assert "36 ATP" in GOLDEN
    assert "36 ATP" in mod.ATP36
    assert "غوص اللوح" in GOLDEN
    assert "غوص اللوح" in mod.GEOLOGY


def test_all_l0_pass_negatives():
    mod = _mod()
    ids = list_question_ids()
    assert len(ids) >= 10
    for qid in ids:
        fails = mod.check_question(qid)
        assert fails == [], fails


def test_grader_untouched():
    assert "validate_rubrics" not in GRADER
    assert "GEOLOGY" not in GRADER
    assert GRADER_VERSION == "1.1.7"
    assert "openai" not in GRADER


def test_evaluate_still_not_mounted():
    assert "evaluate.router" not in INIT
    assert "ai_evaluate.router" not in INIT
