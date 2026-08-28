"""S12 — observabilité /api/grade. 0 copie, 0 user_id, hors grade()."""

from __future__ import annotations

from pathlib import Path
from types import SimpleNamespace

from services.grade_metrics import record_result, record_ungraded, reset, snapshot
from services.local_grader import grade_question
from services.rubric_store import load

BACKEND = Path(__file__).resolve().parent.parent
GRADER = (BACKEND / "services" / "local_grader.py").read_text(encoding="utf-8")
ROUTE = (BACKEND / "routes" / "grade.py").read_text(encoding="utf-8")
METRICS = (BACKEND / "services" / "grade_metrics.py").read_text(encoding="utf-8")


def setup_function() -> None:
    reset()


def test_metrics_not_inside_grader():
    assert "grade_metrics" not in GRADER
    assert "redis" not in GRADER.lower() or "Redis" not in GRADER


def test_route_records_and_exposes_metrics():
    assert "record_ungraded" in ROUTE
    assert "record_result" in ROUTE
    assert 'get("/metrics")' in ROUTE or "@router.get(\"/metrics\")" in ROUTE


def test_snapshot_has_no_copy_or_user():
    record_ungraded("enzyme-activity-v1:analyse", 1.2)
    snap = snapshot()
    blob = str(snap)
    assert "answer" not in blob
    assert "user_id" not in blob
    assert "model_answer" not in blob
    assert snap["ungraded"] == 1
    assert snap["ungraded_by_question_id"]["enzyme-activity-v1:analyse"] == 1
    assert snap["cache_hits"] == 0


def test_record_result_axes():
    packed = load("manhadjiya-yeast-analyse")
    assert packed is not None
    r = grade_question(
        "manhadjiya-yeast-analyse",
        packed.rubric.model_answer + " وتنتج الخلية 36 ATP في التنفس.",
    )
    record_result(r, 0.4)
    snap = snapshot()
    assert snap["graded"] == 1
    assert snap["science_status"].get("error", 0) == 1
    assert "science.grave" in snap["diagnosis"] or any(
        "science" in k or "grave" in k for k in snap["diagnosis"]
    )


def test_no_plaintext_in_metrics_module():
    assert "student_answer" not in METRICS
    snap = snapshot()
    assert "answer" not in snap
    assert "user_id" not in snap


def test_record_result_stuffing_flag():
    record_result(
        SimpleNamespace(
            sanity_code="ok",
            science_status="ok",
            diagnosis=SimpleNamespace(code="stuffing"),
            stuffing_suspected=True,
        ),
        2.0,
    )
    snap = snapshot()
    assert snap["stuffing_suspected"] == 1
    assert snap["latency_ms_avg"] >= 0
