"""S29 — proclitique كال (كالخميرة = خميرة). 1.1.9. Pas de stemming, pas فل."""

from __future__ import annotations

from pathlib import Path

from services.arabic import normalize_arabic
from services.local_grader import (
    GRADER_VERSION,
    _PROCLITICS,
    _hit_pos,
    grade,
)
from services.rubric_store import load

BACKEND = Path(__file__).resolve().parent.parent
GRADER = (BACKEND / "services" / "local_grader.py").read_text(encoding="utf-8")
INIT = (BACKEND / "routes" / "__init__.py").read_text(encoding="utf-8")


def _n(s: str) -> str:
    return normalize_arabic(s)


def test_kal_compound_matches_bare_noun():
    assert _hit_pos(_n("كالخميرة"), _n("خميرة")) is not None


def test_existing_proclitics_still_match():
    assert _hit_pos(_n("فالخميرة"), _n("خميرة")) is not None
    assert _hit_pos(_n("الخميرة"), _n("خميرة")) is not None
    assert _hit_pos(_n("كخميرة"), _n("خميرة")) is not None
    assert _hit_pos(_n("والخميرة"), _n("خميرة")) is not None


def test_short_copy_does_not_invent_long_needle():
    """On n'efface pas la copie pour inventer un mot plus long. كن ≠ لكن."""
    assert _hit_pos(_n("كن"), _n("لكن")) is None


def test_al_variant_still_sees_kal_prefix():
    """ك + الخميرة était déjà une forme. Régression."""
    assert _hit_pos(_n("كالخميرة"), _n("الخميرة")) is not None


def test_yeast_theme_hits_with_kal():
    packed = load("manhadjiya-yeast-analyse")
    assert packed is not None
    copy = (
        "تمثل الوثيقة جدولا يوضح كالخميرة. "
        "يزداد العدد من 9 إلى 18. "
        "فكلما تواجد الغلوكوز تزايد عدد الخلايا. "
        "نستنتج أن الغلوكوز عنصر ضروري لنمو."
    )
    r = grade(student_answer=copy, rubric=packed.rubric, document=packed.document)
    assert r.science_status == "ok"
    assert r.sanity_code == "ok"


def test_no_stemming_no_fal_rare_version():
    assert GRADER_VERSION == "1.1.9"
    assert 'GRADER_VERSION = "1.1.9"' in GRADER
    assert "كال" in _PROCLITICS
    assert "فل" not in _PROCLITICS
    assert "openai" not in GRADER
    assert "evaluate.router" not in INIT
    assert "ai_evaluate.router" not in INIT
