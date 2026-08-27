"""S5 — mixins au load + $lex: fichier git. Pas de parseur livre."""

from __future__ import annotations

from pathlib import Path

from services.lexicon import in_file, lexicon_path, synonyms
from services.local_grader import grade
from services.rubric_store import load, reset_caches

BACKEND = Path(__file__).resolve().parent.parent


def setup_function() -> None:
    reset_caches()


def test_lexicon_file_exists_and_covers_l0_keys():
    assert lexicon_path().is_file()
    for key in (
        "glucose",
        "enzyme",
        "adn",
        "transcription",
        "traduction",
        "ach",
        "synapse",
        "arm",
        "trn",
        "rarn",
    ):
        assert in_file(key), key
        assert synonyms(key), key


def test_lex_glucose_matches_savoir_extract():
    syns = synonyms("glucose")
    assert "glucose" in syns
    assert "سكر" in syns  # largeur connue, pas élargie ici


def test_unknown_lex_is_empty():
    assert synonyms("cle-inventee-s5") == []
    assert not in_file("cle-inventee-s5")


def test_mixin_merged_on_proteine_adn():
    packed = load("proteine-adn-scientific-text")
    assert packed is not None
    tv = packed.rubric.theme_variants
    assert "ARNm" in tv or "$lex:arm" in tv
    assert packed.rubric.total_points == 5.0
    r = grade(
        student_answer=packed.rubric.model_answer,
        rubric=packed.rubric,
        document=packed.document,
    )
    assert r.method_percent >= 85
    assert r.science_status == "ok"


def test_yeast_has_no_invented_mixin():
    packed = load("manhadjiya-yeast-analyse")
    assert packed is not None
    assert packed.rubric.chapter_slug == "respiration-levure"
    assert not (BACKEND / "data" / "rubrics" / "mixins" / "respiration-levure.json").exists()
    assert not (BACKEND / "data" / "rubrics" / "mixins" / "lactose.json").exists()


def test_expand_lex_from_file_not_only_savoir():
    from services.local_grader import _expand_variants

    expanded = _expand_variants(["$lex:glucose"])
    assert any("غلوكوز" in x or "glucose" in x for x in expanded)
