"""S23 / B2 — filet_sha16 (Savoir + $lex) dans la clé cache. Hors grade(). 1.1.5."""

from __future__ import annotations

from pathlib import Path

from services.grade_cache import (
    canon_sha16,
    filet_sha16,
    key_has_user_id,
    make_key,
    reset,
)
from services.local_grader import GRADER_VERSION
from services.rubric_store import load
from services.savoir_corrector import _GRAVE_ERRORS, _SYNONYMS

BACKEND = Path(__file__).resolve().parent.parent
GRADER = (BACKEND / "services" / "local_grader.py").read_text(encoding="utf-8")
CACHE = (BACKEND / "services" / "grade_cache.py").read_text(encoding="utf-8")
INIT = (BACKEND / "routes" / "__init__.py").read_text(encoding="utf-8")


def setup_function() -> None:
    reset()


def teardown_function() -> None:
    reset()


def test_filet_sha16_stable_hex16():
    h1 = filet_sha16()
    h2 = filet_sha16()
    assert h1 == h2
    assert len(h1) == 16
    assert all(c in "0123456789abcdef" for c in h1)


def test_make_key_includes_filet_and_rubric_sha_not_user():
    yeast = load("manhadjiya-yeast-analyse")
    assert yeast is not None
    copy = "تمثل الوثيقة جدولا. 18"
    key = make_key(yeast, copy)
    assert filet_sha16() in key
    assert canon_sha16(yeast) in key
    assert GRADER_VERSION in key
    assert not key_has_user_id(key)
    assert copy not in key
    assert "model_answer" not in key


def test_grave_edit_without_version_bump_changes_key():
    yeast = load("manhadjiya-yeast-analyse")
    assert yeast is not None
    copy = "تمثل الوثيقة جدولا. 18"
    k1 = make_key(yeast, copy)
    ver = GRADER_VERSION
    _GRAVE_ERRORS.append((r"zzz_s23_probe", "probe", 0.0))
    filet_sha16.cache_clear()
    try:
        k2 = make_key(yeast, copy)
        assert k1 != k2
        assert filet_sha16() in k2
        assert ver == "1.1.7"
    finally:
        _GRAVE_ERRORS.pop()
        filet_sha16.cache_clear()
    assert make_key(yeast, copy) == k1


def test_synonyms_edit_changes_key_not_canon_sha():
    yeast = load("manhadjiya-yeast-analyse")
    assert yeast is not None
    copy = "تمثل الوثيقة جدولا. 18"
    sha_r = canon_sha16(yeast)
    k1 = make_key(yeast, copy)
    _SYNONYMS.setdefault("s23_probe", []).append("كلمةس23")
    filet_sha16.cache_clear()
    try:
        assert canon_sha16(yeast) == sha_r
        assert make_key(yeast, copy) != k1
    finally:
        syns = _SYNONYMS.get("s23_probe") or []
        if "كلمةس23" in syns:
            syns.remove("كلمةس23")
        if not syns:
            _SYNONYMS.pop("s23_probe", None)
        filet_sha16.cache_clear()


def test_grader_untouched_no_version_bump():
    assert GRADER_VERSION == "1.1.7"
    assert "filet_sha16" not in GRADER
    assert "grade_cache" not in GRADER
    assert "openai" not in GRADER
    assert "evaluate.router" not in INIT
    assert "ai_evaluate.router" not in INIT


def test_cache_module_still_drops_copy():
    assert "filet_sha16" in CACHE
    assert "student_answer" in CACHE
    assert "user_id" in CACHE
