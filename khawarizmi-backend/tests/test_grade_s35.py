"""S35 — diagnostics justes + cache bruyant (audit F9/F10). 1.2.0.

F10a : bourrage sans chiffre → diag `stuffing` (avant `unanchored`) —
       le diagnostic nomme le cap appliqué (50).
F10b : defer + hors-sujet → `sanity.defer` (avant `off_topic`) — une copie
       non-arabe n'est pas « hors sujet », elle est illisible pour la grille.
F9   : digest cache sans pepper → WARNING loggé une fois (avant : silence).
"""

from __future__ import annotations

import logging
import os

# config.py instancie Settings() à l'import : SECRET_KEY requis (pas de
# conftest ici). Clé de test locale — le test monkeypatche hash_answer de
# toute façon pour forcer le fallback.
os.environ.setdefault("SECRET_KEY", "s35-test-secret-key-0123456789")

from services.grade_cache import _digest, reset  # noqa: E402
from services.local_grader import GRADER_VERSION, grade  # noqa: E402
from services.rubric_store import load  # noqa: E402


def _yeast():
    packed = load("yeast-glucose-interpret")
    assert packed is not None
    return packed


_BOURRAGE = " ".join(
    ["الغلوكوز غلوكوز الخميرة خميرة تنفس تخمر طاقة مادة أيض نمو تكاثر"] * 3
)


class TestDiagStuffingAvantUnanchored:
    def test_bourrage_sans_chiffre_diag_stuffing(self):
        p = _yeast()
        r = grade(student_answer=_BOURRAGE, rubric=p.rubric, document=p.document)
        assert r.stuffing_suspected is True
        assert "stuffing" in r.caps_applied
        assert r.diagnosis is not None and r.diagnosis.code == "stuffing"

    def test_vraie_copie_sans_chiffre_diag_unanchored(self):
        """stuffing=False + pas de chiffre → unanchored seul (ordre intact)."""
        p = _yeast()
        copy = (
            "نلاحظ أن عدد الخلايا أكبر في الوسط الذي يحتوي على الغلوكوز، "
            "ويعود ذلك إلى دور الغلوكوز كمادة أيضية توفر الطاقة اللازمة "
            "لتنفس الخميرة وتكاثرها."
        )
        r = grade(student_answer=copy, rubric=p.rubric, document=p.document)
        assert r.stuffing_suspected is False
        assert r.diagnosis is not None and r.diagnosis.code == "unanchored"


class TestDeferHorsSujet:
    def test_copie_anglaise_diag_defer_pas_off_topic(self):
        p = _yeast()
        r = grade(
            student_answer="the cell produces 36 ATP and 2 ATP",
            rubric=p.rubric,
            document=p.document,
        )
        assert r.sanity_code == "defer"
        assert r.diagnosis is not None
        assert r.diagnosis.code == "sanity.defer"
        assert "بالعربية" in r.diagnosis.label_ar
        assert "أعد كتابة" in r.next_step_ar

    def test_copie_arabe_hors_sujet_diag_off_topic_intact(self):
        """S33 intact : une vraie copie arabe hors-sujet reste off_topic."""
        p = _yeast()
        off = (
            "تمثل الوثيقة منحنى تباعد الصفائح عند الأعراف المحيطية. "
            "كلما ابتعدت الصفيحة ازداد الخندق المحيطي. نستنتج غوص اللوح."
        )
        r = grade(student_answer=off, rubric=p.rubric, document=p.document)
        assert r.sanity_code == "ok"
        assert r.diagnosis is not None and r.diagnosis.code == "off_topic"


class TestCacheDigestBruyant:
    def test_fallback_sha256_warn_une_fois(self, caplog, monkeypatch):
        """SECRET_KEY absent → SHA-256 sec + 1 warning (pas de silence)."""

        def _no_pepper(text: str) -> str:
            raise ValueError("SECRET_KEY non défini")

        import services.hashing as hashing

        monkeypatch.setattr(hashing, "hash_answer", _no_pepper)
        reset()
        with caplog.at_level(logging.WARNING, logger="services.grade_cache"):
            d1 = _digest("copie eleve arabe")
            d2 = _digest("autre copie")
        assert len(d1) == 64 and len(d2) == 64
        warnings = [r for r in caplog.records if "NON pepperé" in r.message]
        assert len(warnings) == 1, "le warning doit être loggé UNE fois"
        reset()

    def test_version_bump(self):
        """F10 change le GradeResult (diagnosis) → cache invalidé via 1.2.0."""
        assert GRADER_VERSION == "1.2.0"
