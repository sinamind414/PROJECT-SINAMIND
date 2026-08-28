"""S17 — quota /api/grade : sanity==ok seulement. Cache/vide/defer/422 ne consomment pas."""

from __future__ import annotations

from pathlib import Path
from types import SimpleNamespace

from services.grade_adapter import may_write_fsrs
from services.grade_quota import should_count_quota
from services.local_grader import GRADER_VERSION, grade
from services.rubric_store import load

BACKEND = Path(__file__).resolve().parent.parent
ROOT = BACKEND.parent
GRADER = (BACKEND / "services" / "local_grader.py").read_text(encoding="utf-8")
ROUTE = (BACKEND / "routes" / "grade.py").read_text(encoding="utf-8")
QUOTA = (BACKEND / "services" / "grade_quota.py").read_text(encoding="utf-8")
INIT = (BACKEND / "routes" / "__init__.py").read_text(encoding="utf-8")


def test_quota_only_sanity_ok_not_cache():
    assert should_count_quota(sanity_code="ok", from_cache=False) is True
    assert should_count_quota(sanity_code="ok", from_cache=True) is False
    assert should_count_quota(sanity_code="empty", from_cache=False) is False
    assert should_count_quota(sanity_code="too_short", from_cache=False) is False
    assert should_count_quota(sanity_code="not_arabic", from_cache=False) is False
    assert should_count_quota(sanity_code="gibberish", from_cache=False) is False
    assert should_count_quota(sanity_code="defer", from_cache=False) is False


def test_empty_copy_does_not_count():
    packed = load("manhadjiya-yeast-analyse")
    assert packed is not None
    r = grade(student_answer="   ", rubric=packed.rubric, document=packed.document)
    assert r.sanity_code == "empty"
    assert should_count_quota(sanity_code=r.sanity_code, from_cache=False) is False
    assert not may_write_fsrs(r)


def test_model_answer_counts_and_may_fsrs():
    packed = load("manhadjiya-yeast-analyse")
    assert packed is not None
    r = grade(
        student_answer=packed.rubric.model_answer,
        rubric=packed.rubric,
        document=packed.document,
    )
    assert r.sanity_code == "ok"
    assert should_count_quota(sanity_code=r.sanity_code, from_cache=False) is True
    assert may_write_fsrs(r) is True


def test_capped_mastery_does_not_write_fsrs():
    packed = load("manhadjiya-yeast-analyse")
    assert packed is not None
    r = grade(
        student_answer=packed.rubric.model_answer + " وتنتج الخلية 36 ATP في التنفس.",
        rubric=packed.rubric,
        document=packed.document,
    )
    assert r.science_status == "error"
    assert r.method_percent >= 85
    assert may_write_fsrs(r) is False
    assert should_count_quota(sanity_code=r.sanity_code, from_cache=False) is True


def test_route_wires_quota_and_fsrs_not_copy():
    assert "should_count_quota" in ROUTE
    assert "evaluate_limit" in ROUTE
    assert "_enforce_evaluate_quota" in ROUTE
    assert "may_write_fsrs" in ROUTE
    assert "_maybe_write_fsrs" in ROUTE
    assert "hash_answer" not in ROUTE
    assert "INSERT INTO da_answers" not in ROUTE
    assert "student_answer" in ROUTE  # argument de grade() seulement
    assert "from_cache=False" in ROUTE or "from_cache=False" in ROUTE.replace(" ", "")


def test_quota_module_has_no_io():
    assert "redis" not in QUOTA.lower()
    assert "fastapi" not in QUOTA.lower()
    assert "sql" not in QUOTA.lower()
    assert "openai" not in QUOTA.lower()


def test_grader_untouched():
    assert "grade_quota" not in GRADER
    assert "evaluate_limit" not in GRADER
    assert "update_memory" not in GRADER
    assert GRADER_VERSION == "1.1.5"
    assert "openai" not in GRADER


def test_evaluate_still_not_mounted():
    assert "evaluate.router" not in INIT
    assert "ai_evaluate.router" not in INIT


def test_may_write_fsrs_unchanged():
    assert not may_write_fsrs(
        SimpleNamespace(sanity_code="defer", method_percent=80, science_status="ok")
    )
    assert may_write_fsrs(
        SimpleNamespace(sanity_code="ok", method_percent=40, science_status="error")
    )
