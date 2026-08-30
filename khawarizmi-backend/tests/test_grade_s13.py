"""S13 — colonnes 035 sur da_answers. Hash, pas la copie. Deux axes persistés."""

from __future__ import annotations

from pathlib import Path

from services.grade_adapter import persist_grade_columns
from services.local_grader import GRADER_VERSION, grade_question
from services.rubric_store import load

BACKEND = Path(__file__).resolve().parent.parent
DA = (BACKEND / "routes" / "document_analysis.py").read_text(encoding="utf-8")
V2 = (BACKEND / "routes" / "document_analysis_v2.py").read_text(encoding="utf-8")
MIG = (BACKEND / "migrations" / "versions" / "035_grade_columns.py").read_text(
    encoding="utf-8"
)


def test_migration_035_adds_grade_columns():
    assert "down_revision = \"034\"" in MIG or "down_revision = '034'" in MIG
    for col in (
        "rubric_version",
        "grader_version",
        "grading_engine",
        "science_status",
        "stuffing_suspected",
        "method_percent",
        "order_ok",
        "diagnosis_code",
    ):
        assert col in MIG


def test_da_inserts_persist_columns_and_hash():
    for src in (DA, V2):
        assert "persist_grade_columns" in src
        assert "hash_answer" in src
        assert "grading_engine" in src
        assert "method_percent" in src
        assert "diagnosis_code" in src
        assert '"answer_text": ans.answer' not in src


def test_persist_ungraded_is_honest():
    d = persist_grade_columns(None)
    assert d["grading_engine"] == "ungraded"
    assert d["method_percent"] == 0
    assert d["science_status"] == "not_applicable"
    assert d["diagnosis_code"] == "ungraded"


def test_persist_keeps_two_axes_on_science_cap():
    packed = load("manhadjiya-yeast-analyse")
    assert packed is not None
    r = grade_question(
        "manhadjiya-yeast-analyse",
        packed.rubric.model_answer + " وتنتج الخلية 36 ATP في التنفس.",
    )
    d = persist_grade_columns(r)
    assert d["grading_engine"] == "local_rubric"
    assert d["grader_version"] == GRADER_VERSION
    assert d["science_status"] == "error"
    assert d["method_percent"] >= 85
    assert r.overall_training_percent <= 40
    assert d["method_percent"] != r.overall_training_percent
