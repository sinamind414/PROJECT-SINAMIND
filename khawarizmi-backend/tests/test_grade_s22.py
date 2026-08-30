"""S22 / B4 — defer consomme evaluate_limit. G7 reste defer ≠ 0. FSRS non."""

from __future__ import annotations

from pathlib import Path
from types import SimpleNamespace

from services.grade_adapter import may_write_fsrs
from services.grade_quota import should_count_quota
from services.local_grader import GRADER_VERSION, grade
from services.rubric_store import load

BACKEND = Path(__file__).resolve().parent.parent
GRADER = (BACKEND / "services" / "local_grader.py").read_text(encoding="utf-8")
ROUTE = (BACKEND / "routes" / "grade.py").read_text(encoding="utf-8")
QUOTA = (BACKEND / "services" / "grade_quota.py").read_text(encoding="utf-8")
INIT = (BACKEND / "routes" / "__init__.py").read_text(encoding="utf-8")


def test_defer_counts_ok_counts_stops_do_not():
    assert should_count_quota(sanity_code="ok", from_cache=False) is True
    assert should_count_quota(sanity_code="defer", from_cache=False) is True
    assert should_count_quota(sanity_code="defer", from_cache=True) is False
    assert should_count_quota(sanity_code="ok", from_cache=True) is False
    assert should_count_quota(sanity_code="empty", from_cache=False) is False
    assert should_count_quota(sanity_code="too_short", from_cache=False) is False
    assert should_count_quota(sanity_code="not_arabic", from_cache=False) is False
    assert should_count_quota(sanity_code="gibberish", from_cache=False) is False


def test_g7_atp_is_defer_counts_no_fsrs_not_zero():
    packed = load("manhadjiya-yeast-analyse")
    assert packed is not None
    r = grade(
        student_answer="38 ATP · P/O=3",
        rubric=packed.rubric,
        document=packed.document,
    )
    assert r.sanity_code == "defer"
    assert r.cacheable is False
    assert r.method_percent >= 0
    assert should_count_quota(sanity_code=r.sanity_code, from_cache=False) is True
    assert may_write_fsrs(r) is False


def test_n1_dump_still_not_arabic_zero_quota():
    packed = load("manhadjiya-yeast-analyse")
    assert packed is not None
    dump = "1 2 3 4 5 6 7 8 9 10 20 37 80 100 0 2,5 4,8 18 6 10 5"
    r = grade(student_answer=dump, rubric=packed.rubric, document=packed.document)
    assert r.sanity_code == "not_arabic"
    assert r.method_percent == 0
    assert should_count_quota(sanity_code=r.sanity_code, from_cache=False) is False
    assert not may_write_fsrs(r)


def test_empty_still_free():
    packed = load("manhadjiya-yeast-analyse")
    assert packed is not None
    r = grade(student_answer="   ", rubric=packed.rubric, document=packed.document)
    assert r.sanity_code == "empty"
    assert should_count_quota(sanity_code=r.sanity_code, from_cache=False) is False


def test_no_invented_defer_daily_counter():
    assert "DEFER_DAILY_LIMIT" not in QUOTA
    assert "DEFER_DAILY_LIMIT" not in ROUTE
    assert "defer_limit:" not in ROUTE
    assert "redis" not in QUOTA.lower()


def test_route_still_gates_on_should_count():
    assert "should_count_quota" in ROUTE
    # S36 : helper partagé rate_limit.enforce_evaluate_quota (plus de wrapper local)
    assert "enforce_evaluate_quota" in ROUTE
    assert "evaluate.router" not in INIT
    assert "ai_evaluate.router" not in INIT


def test_grader_untouched_no_version_bump():
    assert GRADER_VERSION == "1.2.0"
    assert "grade_quota" not in GRADER
    assert "evaluate_limit" not in GRADER
    assert "should_count_quota" not in GRADER
    assert "openai" not in GRADER


def test_fsrs_still_ignores_defer():
    assert not may_write_fsrs(
        SimpleNamespace(sanity_code="defer", method_percent=80, science_status="ok")
    )
