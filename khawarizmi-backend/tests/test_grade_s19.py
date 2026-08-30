"""S19 — ceinture sha16 sur la clé cache C1. Hors grade(). 0 user_id. 0 copie."""

from __future__ import annotations

from pathlib import Path

from services.grade_cache import canon_sha16, key_has_user_id, make_key, reset
from services.local_grader import GRADER_VERSION
from services.rubric_store import PackedRubric, load

BACKEND = Path(__file__).resolve().parent.parent
GRADER = (BACKEND / "services" / "local_grader.py").read_text(encoding="utf-8")
CACHE = (BACKEND / "services" / "grade_cache.py").read_text(encoding="utf-8")
INIT = (BACKEND / "routes" / "__init__.py").read_text(encoding="utf-8")


def setup_function() -> None:
    reset()


def test_sha16_stable_and_hex16():
    yeast = load("manhadjiya-yeast-analyse")
    assert yeast is not None
    h1 = canon_sha16(yeast)
    h2 = canon_sha16(yeast)
    assert h1 == h2
    assert len(h1) == 16
    assert all(c in "0123456789abcdef" for c in h1)


def test_make_key_includes_sha16_not_user():
    yeast = load("manhadjiya-yeast-analyse")
    assert yeast is not None
    copy = "تمثل الوثيقة جدولا. 18"
    key = make_key(yeast, copy)
    assert canon_sha16(yeast) in key
    assert yeast.rubric.rubric_id in key
    assert GRADER_VERSION in key
    assert not key_has_user_id(key)
    assert copy not in key


def test_g17_two_rubrics_still_distinct():
    yeast = load("manhadjiya-yeast-analyse")
    enzyme = load("enzyme-temp-analyse")
    assert yeast is not None and enzyme is not None
    copy = "تمثل الوثيقة جدولا. 18"
    assert make_key(yeast, copy) != make_key(enzyme, copy)
    assert canon_sha16(yeast) != canon_sha16(enzyme)


def test_edit_criteria_without_version_bump_changes_key():
    yeast = load("manhadjiya-yeast-analyse")
    assert yeast is not None
    copy = "تمثل الوثيقة جدولا. 18"
    k1 = make_key(yeast, copy)
    rubric = yeast.rubric.model_copy(deep=True)
    c0 = rubric.criteria[0].model_copy(deep=True)
    c0.variants = list(c0.variants) + ["كلمةجديدةللاختبار"]
    rubric.criteria = [c0, *rubric.criteria[1:]]
    packed = PackedRubric(
        rubric=rubric,
        document=yeast.document,
        rubric_path=yeast.rubric_path,
        document_path=yeast.document_path,
    )
    assert packed.rubric.version == yeast.rubric.version
    assert canon_sha16(packed) != canon_sha16(yeast)
    assert make_key(packed, copy) != k1


def test_model_answer_change_does_not_bust_key():
    yeast = load("manhadjiya-yeast-analyse")
    assert yeast is not None
    copy = "تمثل الوثيقة جدولا. 18"
    k1 = make_key(yeast, copy)
    rubric = yeast.rubric.model_copy(deep=True)
    rubric.model_answer = rubric.model_answer + " ."
    packed = PackedRubric(
        rubric=rubric,
        document=yeast.document,
        rubric_path=yeast.rubric_path,
        document_path=yeast.document_path,
    )
    assert make_key(packed, copy) == k1


def test_grader_untouched():
    assert "canon_sha16" not in GRADER
    assert "grade_cache" not in GRADER
    assert GRADER_VERSION == "1.1.8"
    assert "openai" not in GRADER


def test_cache_sha16_not_storing_copy():
    assert "model_answer" in CACHE  # pop from dump
    assert "student_answer" in CACHE  # sanitize pop
    assert "evaluate.router" not in INIT
    assert "ai_evaluate.router" not in INIT
