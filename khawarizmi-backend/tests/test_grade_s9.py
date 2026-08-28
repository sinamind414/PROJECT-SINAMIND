"""S9 — UI 2 axes + G12 : pas de بكالوريا collé au %, ungraded ≠ 0 %."""

from __future__ import annotations

import re
from pathlib import Path

from services.grade_adapter import to_verb_eval
from services.local_grader import TRAINING_BANNER_AR, grade
from services.rubric_store import load

ROOT = Path(__file__).resolve().parent.parent.parent
BACKEND = Path(__file__).resolve().parent.parent
FE = ROOT / "khawarizmi-frontend" / "src"

CARD = FE / "components" / "methodology" / "GradeResultCard.tsx"
SCENARIO = FE / "components" / "methodology" / "ScenarioRunner.tsx"
VERB_FLOW = FE / "components" / "methodology" / "VerbLessonFlow.tsx"
DIAG = FE / "app" / "diagnostic" / "global" / "page.tsx"
ACTION = FE / "app" / "action-verbs" / "[slug]" / "page.tsx"
BAC = FE / "components" / "bac_blanc" / "BacBlancImmersif.tsx"
CORR = FE / "app" / "annales" / "[slug]" / "exam" / "correction" / "page.tsx"

GLUE = re.compile(r"%\s*بكالوريا")


def test_grade_card_exists_with_two_axes():
    src = CARD.read_text(encoding="utf-8")
    assert "درجة التدريب" in src
    assert "منهج:" in src
    assert "محتوى:" in src
    assert TRAINING_BANNER_AR in src
    assert "formatTrainingPercent" in src
    assert 'ungraded ? "—"' in src or 'ungraded ? "—"' in src.replace("'", '"')


def test_g12_no_bac_glued_to_percent_on_grade_surfaces():
    for path in (CARD, SCENARIO, VERB_FLOW, DIAG, ACTION, BAC, CORR):
        src = path.read_text(encoding="utf-8")
        assert not GLUE.search(src), f"G12 collé dans {path}"


def test_surfaces_use_grade_result_card():
    assert "GradeResultCard" in SCENARIO.read_text(encoding="utf-8")
    assert "GradeResultCard" in VERB_FLOW.read_text(encoding="utf-8")
    assert "GradeResultCard" in DIAG.read_text(encoding="utf-8")
    assert "GradeResultCard" in ACTION.read_text(encoding="utf-8")
    assert "formatTrainingPercent" in BAC.read_text(encoding="utf-8")
    assert "formatTrainingPercent" in CORR.read_text(encoding="utf-8")


def test_scenario_does_not_paint_method_label_on_overall():
    src = SCENARIO.read_text(encoding="utf-8")
    assert "getSeverityLabel" not in src
    assert "FSRS mis à jour" not in src


def test_to_verb_eval_keeps_two_axes_on_science_cap():
    packed = load("manhadjiya-yeast-analyse")
    assert packed is not None
    r = grade(
        student_answer=packed.rubric.model_answer + " وتنتج الخلية 36 ATP في التنفس.",
        rubric=packed.rubric,
        document=packed.document,
    )
    d = to_verb_eval(r)
    assert d["science_status"] == "error"
    assert d["science_capped"] is True
    assert d["method_percent"] >= 85
    assert d["percentage"] <= 40
    assert d["overall_training_percent"] == d["percentage"]
    assert d["percentage"] != d["method_percent"]
    assert "تدريبية" in d["banner_ar"]
    blob = f"{d['percentage']}%{d['method_label_ar']}"
    assert "بكالوريا" not in blob


def test_adapter_source_stays_local():
    packed = load("manhadjiya-yeast-analyse")
    assert packed is not None
    r = grade(
        student_answer=packed.rubric.model_answer,
        rubric=packed.rubric,
        document=packed.document,
    )
    d = to_verb_eval(r)
    assert d["source"] == "local_rubric"
    assert d["ungraded"] is False
