"""S26 — P/O contextualisé. FADH2=2 n'est pas une faute NADH. 38 ATP juste. 1.1.5."""

from __future__ import annotations

from pathlib import Path

from services.grade_cache import filet_sha16, reset as cache_reset
from services.local_grader import GRADER_VERSION, grade
from services.rubric_store import load

BACKEND = Path(__file__).resolve().parent.parent
GRADER = (BACKEND / "services" / "local_grader.py").read_text(encoding="utf-8")
SAVOIR = (BACKEND / "services" / "savoir_corrector.py").read_text(encoding="utf-8")
INIT = (BACKEND / "routes" / "__init__.py").read_text(encoding="utf-8")


def setup_function() -> None:
    cache_reset()


def _yeast():
    packed = load("manhadjiya-yeast-analyse")
    assert packed is not None
    return packed


def test_fadh_po_2_is_not_capped():
    p = _yeast()
    r = grade(
        student_answer=p.rubric.model_answer + " P/O FADH2 = 2",
        rubric=p.rubric,
        document=p.document,
    )
    assert r.science_status == "ok"
    assert r.overall_training_percent == r.method_percent
    assert "science" not in r.caps_applied
    assert not any("po_nadh" in f for f in r.science_flags)


def test_nadh_po_2_still_caps():
    p = _yeast()
    r = grade(
        student_answer=p.rubric.model_answer + " P/O NADH = 2",
        rubric=p.rubric,
        document=p.document,
    )
    assert r.science_status == "error"
    assert r.overall_training_percent <= 40
    assert "science" in r.caps_applied


def test_38_atp_still_ok_36_still_cap():
    p = _yeast()
    ok = grade(
        student_answer=p.rubric.model_answer + " وتنتج الخلية 38 ATP في التنفس.",
        rubric=p.rubric,
        document=p.document,
    )
    assert ok.science_status == "ok"
    bad = grade(
        student_answer=p.rubric.model_answer + " وتنتج الخلية 36 ATP في التنفس.",
        rubric=p.rubric,
        document=p.document,
    )
    assert bad.science_status == "error"
    assert bad.overall_training_percent <= 40


def test_g7_defer_untouched():
    p = _yeast()
    r = grade(student_answer="38 ATP · P/O=3", rubric=p.rubric, document=p.document)
    assert r.sanity_code == "defer"
    assert r.cacheable is False


def test_bare_po_pattern_removed_version_unchanged():
    assert GRADER_VERSION == "1.1.6"
    assert 'r"p/o"' not in SAVOIR.split("po_nadh")[1].split("po_fadh")[0]
    assert "nadh.{0,20}atp" not in SAVOIR
    assert "filet_sha16" not in GRADER
    assert "evaluate.router" not in INIT
    assert "ai_evaluate.router" not in INIT
    assert len(filet_sha16()) == 16
