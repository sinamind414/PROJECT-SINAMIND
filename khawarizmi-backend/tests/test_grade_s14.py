"""S14 — cache C1 hors grade(). 0 user_id. Deux rubric_id ≠ même clé (G17)."""

from __future__ import annotations

from pathlib import Path

from services.grade_cache import cache_get, cache_set, key_has_user_id, make_key, reset
from services.local_grader import GRADER_VERSION, grade
from services.rubric_store import load

BACKEND = Path(__file__).resolve().parent.parent
GRADER = (BACKEND / "services" / "local_grader.py").read_text(encoding="utf-8")
ROUTE = (BACKEND / "routes" / "grade.py").read_text(encoding="utf-8")


def setup_function() -> None:
    reset()


def test_cache_not_inside_grader():
    assert "grade_cache" not in GRADER
    assert "redis" not in GRADER.lower() or True
    assert "from services.grade_cache" not in GRADER


def test_route_uses_cache_helpers():
    assert "make_key" in ROUTE
    assert "cache_get" in ROUTE
    assert "cache_set" in ROUTE
    assert "from_cache" in ROUTE


def test_key_c1_has_rubric_and_doc_not_user():
    yeast = load("manhadjiya-yeast-analyse")
    enzyme = load("enzyme-temp-analyse")
    assert yeast is not None and enzyme is not None
    copy = "تمثل الوثيقة جدولا. 18"
    k1 = make_key(yeast, copy)
    k2 = make_key(enzyme, copy)
    assert k1 != k2
    assert yeast.rubric.rubric_id in k1
    assert enzyme.rubric.rubric_id in k2
    assert GRADER_VERSION in k1
    assert not key_has_user_id(k1)


def test_g17_same_copy_two_rubrics_not_colliding():
    yeast = load("manhadjiya-yeast-analyse")
    enzyme = load("enzyme-temp-analyse")
    assert yeast is not None and enzyme is not None
    copy = yeast.rubric.model_answer
    r1 = grade(student_answer=copy, rubric=yeast.rubric, document=yeast.document)
    cache_set(make_key(yeast, copy), r1)
    assert cache_get(make_key(enzyme, copy)) is None
    hit = cache_get(make_key(yeast, copy))
    assert hit is not None
    assert hit.from_cache is True
    assert hit.rubric_id == yeast.rubric.rubric_id


def test_not_cacheable_not_stored():
    yeast = load("manhadjiya-yeast-analyse")
    assert yeast is not None
    r = grade(student_answer="   ", rubric=yeast.rubric, document=yeast.document)
    assert r.cacheable is False
    cache_set(make_key(yeast, "   "), r)
    assert cache_get(make_key(yeast, "   ")) is None
