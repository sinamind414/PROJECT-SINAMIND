"""S33 — theme_min_hits=2 sur les grilles levure. Rubrics 1.0.1.

F4 (audit 2026-08-30) : une copie 100 % tectonique + «الخميرة» une seule fois
passait le filet hors-sujet (theme_min_hits=1) → note 0 mais diagnostic faux.
"""

from __future__ import annotations

import json
from pathlib import Path

from services.local_grader import grade
from services.rubric_store import load

BACKEND = Path(__file__).resolve().parent.parent

_TECTONIQUE_1_THEME = (
    "تمثل الوثيقة منحنى تباعد الصفائح عند الأعراف المحيطية مثل الخميرة لا علاقة. "
    "كلما ابتعدت الصفيحة ازداد الخندق المحيطي. نستنتج غوص اللوح في الاندساس."
)


def _raw(qid: str) -> dict:
    packed = load(qid)
    assert packed is not None
    path = BACKEND / "data" / packed.rubric_path
    return json.loads(path.read_text(encoding="utf-8"))


class TestThemeMinHits:
    def test_rubriques_levure_a_2(self):
        for qid in ("yeast-glucose-interpret", "manhadjiya-yeast-analyse"):
            raw = _raw(qid)
            assert raw["theme_min_hits"] == 2, qid
            assert raw["version"] == "1.0.1", qid

    def test_tectonique_une_mention_theme_hors_sujet(self):
        """Avant : science=ok + diag verb_slip. Maintenant : off_topic cap 40."""
        p = load("yeast-glucose-interpret")
        assert p is not None
        r = grade(
            student_answer=_TECTONIQUE_1_THEME,
            rubric=p.rubric,
            document=p.document,
        )
        assert r.science_status == "error"
        assert r.diagnosis is not None and r.diagnosis.code == "off_topic"
        assert r.overall_training_percent <= 40

    def test_modeles_passent_toujours(self):
        """≥ 2 variantes de thème distinctes dans chaque modèle levure."""
        for qid in ("yeast-glucose-interpret", "manhadjiya-yeast-analyse"):
            p = load(qid)
            assert p is not None
            r = grade(
                student_answer=p.rubric.model_answer,
                rubric=p.rubric,
                document=p.document,
            )
            assert r.science_status == "ok", qid
            assert r.method_percent >= 85, qid

    def test_copie_vraie_avec_deux_themes_pas_hors_sujet(self):
        """Une copie qui cite خميرة + غلوكوز ne doit PAS être hors-sujet."""
        p = load("yeast-glucose-interpret")
        assert p is not None
        copy = (
            "نلاحظ أن عدد خلايا الخميرة يبلغ 18 في وسط يحتوي على الغلوكوز "
            "مقابل 6 بدونه، لأن الغلوكوز مادة أيض توفر طاقة للتنفس فتتكاثر الخميرة. "
            "نستنتج أن نمو الخميرة مرتبط بتوفر الغلوكوز."
        )
        r = grade(student_answer=copy, rubric=p.rubric, document=p.document)
        assert r.science_status == "ok"
        assert r.method_percent == 100

    def test_golden_geologie_sans_theme_toujours_hors_sujet(self):
        p = load("manhadjiya-yeast-analyse")
        assert p is not None
        geo = (
            "تمثل الوثيقة منحنى تباعد الصفائح عند الأعراف المحيطية. "
            "كلما ابتعدت الصفيحة ازداد الخندق المحيطي. نستنتج غوص اللوح في الاندساس."
        )
        r = grade(student_answer=geo, rubric=p.rubric, document=p.document)
        assert r.diagnosis is not None and r.diagnosis.code == "off_topic"
