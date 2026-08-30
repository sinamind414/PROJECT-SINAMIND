"""S24 — métriques caps_applied (S21 visible). Hors grade(). 1.1.5."""

from __future__ import annotations

from pathlib import Path
from types import SimpleNamespace

from services.grade_metrics import record_result, reset, snapshot
from services.local_grader import GRADER_VERSION, grade
from services.rubric_store import load

BACKEND = Path(__file__).resolve().parent.parent
GRADER = (BACKEND / "services" / "local_grader.py").read_text(encoding="utf-8")
METRICS = (BACKEND / "services" / "grade_metrics.py").read_text(encoding="utf-8")
INIT = (BACKEND / "routes" / "__init__.py").read_text(encoding="utf-8")


def setup_function() -> None:
    reset()


def test_science_cap_counted():
    packed = load("manhadjiya-yeast-analyse")
    assert packed is not None
    r = grade(
        student_answer=packed.rubric.model_answer + " وتنتج الخلية 36 ATP في التنفس.",
        rubric=packed.rubric,
        document=packed.document,
    )
    assert r.caps_applied == ["science"]
    record_result(r, 1.0)
    snap = snapshot()
    assert snap["caps_applied"].get("science") == 1
    assert snap["caps_applied"].get("stuffing", 0) == 0
    blob = str(snap)
    assert "user_id" not in blob
    assert "model_answer" not in blob


def test_stuffing_and_science_both_counted():
    packed = load("manhadjiya-yeast-analyse")
    assert packed is not None
    r = grade(
        student_answer=packed.rubric.model_answer
        + " وتنتج الخلية 36 ATP في التنفس."
        + (" التركيب الضوئي " * 20),
        rubric=packed.rubric,
        document=packed.document,
    )
    assert "science" in r.caps_applied
    assert "stuffing" in r.caps_applied
    record_result(r, 1.0)
    snap = snapshot()
    assert snap["caps_applied"].get("science") == 1
    assert snap["caps_applied"].get("stuffing") == 1


def test_missing_caps_attr_does_not_crash():
    record_result(
        SimpleNamespace(
            sanity_code="ok",
            science_status="ok",
            diagnosis=SimpleNamespace(code="all_correct"),
            stuffing_suspected=False,
        ),
        0.1,
    )
    snap = snapshot()
    assert snap["caps_applied"] == {}
    assert snap["graded"] == 1


def test_grader_untouched_no_version_bump():
    assert GRADER_VERSION == "1.1.8"
    assert "grade_metrics" not in GRADER
    assert "caps_applied" in METRICS
    assert "evaluate.router" not in INIT
    assert "ai_evaluate.router" not in INIT
    assert "student_answer" not in METRICS
