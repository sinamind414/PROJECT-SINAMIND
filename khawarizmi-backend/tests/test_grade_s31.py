"""S31 — filet ATP : 38 n'annule 36 qu'à ≤ 90 chars. 1.2.0.

F2 (audit 2026-08-30) : l'exemption «38 annule 36» était aveugle à la position —
un «38 ATP» posé n'importe où lavait un «36 ATP» affirmé comme fait.
"""

from __future__ import annotations

from pathlib import Path

from services.local_grader import (
    GRADER_VERSION,
    _ATP_38_WINDOW,
    _has_38_near,
    grade,
)
from services.arabic import normalize_arabic
from services.rubric_store import load

BACKEND = Path(__file__).resolve().parent.parent
GRADER = (BACKEND / "services" / "local_grader.py").read_text(encoding="utf-8")

_FILLER = (
    "تشمل مراحل التنفس الهوائي التحلل السكري في الهيولى ثم حلقة كريبس "
    "في مطرس الميتوكوندري ثم الفسفرة التأكسدية على المستغلات الداخلية "
    "للغشاء الداخلي للميتوكوندري حيث تمر الإلكترونات في سلسلة نقلها."
)


def _yeast():
    packed = load("yeast-glucose-interpret")
    assert packed is not None
    return packed


class TestFenetre38:
    def test_38_loin_du_36_cappe(self):
        """36 affirmé + 38 à > 90 chars : faute grave, cap 40 (avant : 100 %)."""
        p = _yeast()
        copy = (
            p.rubric.model_answer
            + " وتنتج الخلية 36 ATP في التنفس الخلوي. "
            + _FILLER
            + " بينما يعطي التنفس الكلي 38 ATP."
        )
        r = grade(student_answer=copy, rubric=p.rubric, document=p.document)
        assert r.science_status == "error"
        assert r.overall_training_percent <= 40
        assert "science" in r.caps_applied
        assert any("38" in f and "36" in f for f in r.science_flags)

    def test_correction_adjacente_toujours_exempte(self):
        """S27 intact : «ليس 36 بل 38» = correction, pas de cap."""
        p = _yeast()
        copy = p.rubric.model_answer + " ليس 36 ATP بل 38 ATP"
        r = grade(student_answer=copy, rubric=p.rubric, document=p.document)
        assert r.science_status == "ok"
        assert r.overall_training_percent == r.method_percent

    def test_36_atp_seul_toujours_cappe(self):
        p = _yeast()
        r = grade(
            student_answer=p.rubric.model_answer + " وتنتج الخلية 36 ATP.",
            rubric=p.rubric,
            document=p.document,
        )
        assert r.science_status == "error"
        assert r.overall_training_percent <= 40

    def test_38_atp_seul_toujours_ok(self):
        p = _yeast()
        r = grade(
            student_answer=p.rubric.model_answer + " وتنتج الخلية 38 ATP.",
            rubric=p.rubric,
            document=p.document,
        )
        assert r.science_status == "ok"


class TestHelper:
    def test_fenetre_90(self):
        assert _ATP_38_WINDOW == 90

    def test_has_38_near_positions(self):
        sav = normalize_arabic("ينتج 36 atp هنا") + " " + "حشو " * 60 + "ثم 38 atp"
        assert _has_38_near(sav, sav.index("36")) is False
        near = normalize_arabic("ليس 36 بل 38 atp")
        assert _has_38_near(near, near.index("36")) is True

    def test_version_bump_et_fenetres_fermees(self):
        assert GRADER_VERSION == "1.2.0"
        assert 'GRADER_VERSION = "1.2.0"' in GRADER
        assert "_has_38_near" in GRADER
        # l'ancienne exemption position-blind est bien morte
        assert "_HAS_38_ATP.search(sav)" not in GRADER
