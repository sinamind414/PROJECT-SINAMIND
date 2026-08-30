"""S28 — cache hit n'écrit pas FSRS. Hors grade(). 1.1.6."""

from __future__ import annotations

from pathlib import Path
from types import SimpleNamespace

from services.grade_adapter import may_write_fsrs
from services.local_grader import GRADER_VERSION

BACKEND = Path(__file__).resolve().parent.parent
GRADER = (BACKEND / "services" / "local_grader.py").read_text(encoding="utf-8")
ROUTE = (BACKEND / "routes" / "grade.py").read_text(encoding="utf-8")
ADAPTER = (BACKEND / "services" / "grade_adapter.py").read_text(encoding="utf-8")
INIT = (BACKEND / "routes" / "__init__.py").read_text(encoding="utf-8")


def test_cache_hit_does_not_write_fsrs():
    assert may_write_fsrs(
        SimpleNamespace(
            from_cache=True,
            sanity_code="ok",
            method_percent=90,
            science_status="ok",
        )
    ) is False


def test_fresh_ok_still_may_write():
    assert may_write_fsrs(
        SimpleNamespace(
            from_cache=False,
            sanity_code="ok",
            method_percent=90,
            science_status="ok",
        )
    ) is True
    assert may_write_fsrs(
        SimpleNamespace(
            sanity_code="ok",
            method_percent=90,
            science_status="ok",
        )
    ) is True


def test_route_skips_fsrs_on_hit():
    # branche cache : record puis return, pas _maybe_write_fsrs avant return
    chunk = ROUTE.split("if hit is not None:")[1].split("result = grade(")[0]
    assert "_maybe_write_fsrs" not in chunk
    assert "should_count_quota" not in chunk
    assert "_maybe_write_fsrs" in ROUTE
    assert "from_cache" in ADAPTER


def test_grader_untouched():
    assert GRADER_VERSION == "1.1.9"
    assert "may_write_fsrs" not in GRADER
    assert "openai" not in GRADER
    assert "evaluate.router" not in INIT
    assert "ai_evaluate.router" not in INIT
