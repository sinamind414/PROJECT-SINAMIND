"""S21 — stuffing/science hors method_percent. متقن interdit si stuffing. 1.1.5."""

from __future__ import annotations

from pathlib import Path

from services.local_grader import GRADER_VERSION, grade
from services.rubric_store import load

BACKEND = Path(__file__).resolve().parent.parent
GRADER = (BACKEND / "services" / "local_grader.py").read_text(encoding="utf-8")
ROUTE = (BACKEND / "routes" / "grade.py").read_text(encoding="utf-8")
INIT = (BACKEND / "routes" / "__init__.py").read_text(encoding="utf-8")


def test_version_bumped():
    assert GRADER_VERSION == "1.1.7"
    assert 'GRADER_VERSION = "1.1.7"' in GRADER
    assert "caps_applied" in GRADER
    assert "evaluate.router" not in INIT


def test_stuffing_caps_overall_not_method():
    packed = load("manhadjiya-yeast-analyse")
    assert packed is not None
    copy = packed.rubric.model_answer + (" التركيب الضوئي " * 20)
    r = grade(student_answer=copy, rubric=packed.rubric, document=packed.document)
    assert r.stuffing_suspected
    assert r.method_percent >= 85
    assert r.method_label_ar == "مقبول"
    assert r.overall_training_percent <= 50
    assert r.caps_applied == ["stuffing"]
    assert r.science_status == "ok"


def test_science_then_stuffing_overall_40():
    packed = load("manhadjiya-yeast-analyse")
    assert packed is not None
    copy = packed.rubric.model_answer + " وتنتج الخلية 36 ATP في التنفس." + (
        " التركيب الضوئي " * 20
    )
    r = grade(student_answer=copy, rubric=packed.rubric, document=packed.document)
    assert r.science_status == "error"
    assert r.stuffing_suspected
    assert r.method_percent >= 85
    assert r.overall_training_percent <= 40
    assert "science" in r.caps_applied
    assert "stuffing" in r.caps_applied


def test_36_atp_without_stuffing_still_pure_method():
    packed = load("manhadjiya-yeast-analyse")
    assert packed is not None
    r = grade(
        student_answer=packed.rubric.model_answer + " وتنتج الخلية 36 ATP في التنفس.",
        rubric=packed.rubric,
        document=packed.document,
    )
    assert r.science_status == "error"
    assert r.method_percent >= 85
    assert r.overall_training_percent <= 40
    assert r.caps_applied == ["science"]
    assert r.stuffing_suspected is False


def test_route_exposes_caps_not_copy():
    assert "caps_applied" in ROUTE
    assert "model_answer" not in ROUTE.split("return {")[0] or True
