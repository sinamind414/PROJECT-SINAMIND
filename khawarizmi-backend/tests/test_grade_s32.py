"""S32 — stuffing : l'ancre du doc exige un marqueur de structure. 1.2.0.

F3 (audit 2026-08-30) : kp_full/obj_full exemptait TOTALEMENT le bourrage —
un lexique répété + le chiffre magique du document passait à 75 % sans cap.
"""

from __future__ import annotations

from pathlib import Path

from services.local_grader import GRADER_VERSION, _STRUCTURE_MARKERS, grade
from services.rubric_store import load

BACKEND = Path(__file__).resolve().parent.parent
GRADER = (BACKEND / "services" / "local_grader.py").read_text(encoding="utf-8")

_BOURRAGE = " ".join(
    ["الغلوكوز غلوكوز الخميرة خميرة تنفس تخمر طاقة مادة أيض نمو تكاثر"] * 3
)


def _yeast():
    packed = load("yeast-glucose-interpret")
    assert packed is not None
    return packed


class TestBourrageAncore:
    def test_bourrage_plus_chiffre_doc_detecte(self):
        """Avant : exemption aveugle → 75 % sans cap. Maintenant : cap 50."""
        p = _yeast()
        r = grade(
            student_answer=_BOURRAGE + " العدد يصل 18 ",
            rubric=p.rubric,
            document=p.document,
        )
        assert r.stuffing_suspected is True
        assert "stuffing" in r.caps_applied
        assert r.overall_training_percent <= 50

    def test_bourrage_plus_chiffre_avec_marqueur_exempte(self):
        """Un chiffre ancré + un connecteur = vraie copie, pas du bourrage."""
        p = _yeast()
        copy = _BOURRAGE + " العدد يصل 18 لأن الغلوكوز مادة أيض "
        r = grade(student_answer=copy, rubric=p.rubric, document=p.document)
        assert r.stuffing_suspected is False

    def test_bourrage_sans_chiffre_toujours_detecte(self):
        p = _yeast()
        r = grade(
            student_answer=_BOURRAGE, rubric=p.rubric, document=p.document
        )
        assert r.stuffing_suspected is True
        assert r.overall_training_percent <= 50


class TestModelesNonRegressent:
    def test_modele_ratio_100_exempte(self):
        """enzyme-temp-interpret : 13 tokens, ratio 1.0, ancré — sauvé par «لأن»."""
        p = load("enzyme-temp-interpret")
        assert p is not None
        r = grade(
            student_answer=p.rubric.model_answer,
            rubric=p.rubric,
            document=p.document,
        )
        assert r.stuffing_suspected is False
        assert r.method_percent == 100

    def test_modele_yeast_exempte(self):
        p = _yeast()
        r = grade(
            student_answer=p.rubric.model_answer,
            rubric=p.rubric,
            document=p.document,
        )
        assert r.stuffing_suspected is False

    def test_bonne_copie_longue_exempte(self):
        p = _yeast()
        copy = (
            "نلاحظ في الوثيقة أن عدد الخلايا عند توفر الغلوكوز يبلغ 18 خلية مقابل 6 بدونه. "
            "هذا لأن الغلوكوز مادة أيض توفر الطاقة اللازمة لتنفس الخميرة وتكاثرها. "
            "فكلما زاد تركيز الغلوكوز في الوسط زاد عدد الخلايا. "
            "نستنتج أن نمو الخميرة وتكاثرها مرتبط بتوفر الغلوكوز في وسط الزرع."
        )
        r = grade(student_answer=copy, rubric=p.rubric, document=p.document)
        assert r.stuffing_suspected is False
        assert r.method_percent == 100


class TestContrat:
    def test_liste_fermee_marqueurs(self):
        assert "لان" in _STRUCTURE_MARKERS
        assert "نستنتج" in _STRUCTURE_MARKERS
        assert "بالتالي" in _STRUCTURE_MARKERS
        # pas de parsing : liste courte, pas de stemming
        assert len(_STRUCTURE_MARKERS) <= 12

    def test_version(self):
        assert GRADER_VERSION == "1.2.0"
        assert 'GRADER_VERSION = "1.2.0"' in GRADER
        assert "_STRUCTURE_MARKERS" in GRADER
