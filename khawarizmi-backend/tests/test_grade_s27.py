"""S27 — filet ATP : chiffres orientaux + 38 annule 36/32. 1.1.6."""

from __future__ import annotations

from pathlib import Path

from services.local_grader import GRADER_VERSION, grade
from services.rubric_store import load

BACKEND = Path(__file__).resolve().parent.parent
GRADER = (BACKEND / "services" / "local_grader.py").read_text(encoding="utf-8")
INIT = (BACKEND / "routes" / "__init__.py").read_text(encoding="utf-8")


def _yeast():
    packed = load("manhadjiya-yeast-analyse")
    assert packed is not None
    return packed


def test_eastern_36_atp_caps():
    p = _yeast()
    r = grade(
        student_answer=p.rubric.model_answer + " وتنتج الخلية ٣٦ ATP في التنفس.",
        rubric=p.rubric,
        document=p.document,
    )
    assert r.science_status == "error"
    assert r.overall_training_percent <= 40
    assert "science" in r.caps_applied


def test_eastern_38_atp_ok():
    p = _yeast()
    r = grade(
        student_answer=p.rubric.model_answer + " وتنتج الخلية ٣٨ ATP في التنفس.",
        rubric=p.rubric,
        document=p.document,
    )
    assert r.science_status == "ok"
    assert "science" not in r.caps_applied


def test_laysa_36_bal_38_not_capped():
    p = _yeast()
    r = grade(
        student_answer=p.rubric.model_answer + " ليس 36 ATP بل 38 ATP",
        rubric=p.rubric,
        document=p.document,
    )
    assert r.science_status == "ok"
    assert r.overall_training_percent == r.method_percent


def test_36_alone_still_caps_38_alone_ok():
    p = _yeast()
    bad = grade(
        student_answer=p.rubric.model_answer + " وتنتج الخلية 36 ATP في التنفس.",
        rubric=p.rubric,
        document=p.document,
    )
    assert bad.science_status == "error"
    ok = grade(
        student_answer=p.rubric.model_answer + " وتنتج الخلية 38 ATP في التنفس.",
        rubric=p.rubric,
        document=p.document,
    )
    assert ok.science_status == "ok"


def test_no_fusion_no_llm_version_bumped():
    assert GRADER_VERSION == "1.1.7"
    assert 'GRADER_VERSION = "1.1.7"' in GRADER
    assert "savoir_corrector._normalize" not in GRADER or "_normalize" in GRADER
    assert "openai" not in GRADER
    assert "evaluate.router" not in INIT
    assert "ai_evaluate.router" not in INIT
    assert "_INDIC_DIGITS" in GRADER
    assert "_HAS_38_ATP" in GRADER
