"""Tests Tuteur Méthodologique — Semaine 4"""

import pytest

from methodology.tutor_prompts import get_verb_explanation, VERB_EXPLANATIONS
from methodology.chat_tutor import tutor_methodology_mode


class TestVerbExplanations:
    def test_all_10_verbs_present(self):
        assert len(VERB_EXPLANATIONS) == 10

    def test_explain_complex_verb(self):
        r = get_verb_explanation("وضّح في نص علمي")
        assert "Rédiger" in r["definition"]
        assert "structure" in r

    def test_explain_simple_verb(self):
        r = get_verb_explanation("صف")
        assert "Décrire" in r["definition"]

    def test_unknown_verb(self):
        r = get_verb_explanation("verbe_inconnu")
        assert "non reconnu" in r["definition"]


@pytest.mark.asyncio
class TestTutorMethodologyMode:
    async def test_explain_mode(self):
        r = await tutor_methodology_mode(
            instruction="وضّح في نص علمي",
            mode="explain",
        )
        assert r["mode"] == "explain"
        assert "Rédiger" in r["message"]

    async def test_correct_mode(self):
        r = await tutor_methodology_mode(
            instruction="صف خصائص الخلية",
            student_answer="الخلية تحتوي على جدار خلوي",
            mode="correct",
        )
        assert r["mode"] == "correct"
        assert "evaluation" in r

    async def test_correct_mode_no_answer(self):
        r = await tutor_methodology_mode(
            instruction="صف",
            mode="correct",
        )
        assert "error" in r

    async def test_diagnose_mode(self):
        r = await tutor_methodology_mode(
            instruction="أثبت",
            mode="diagnose",
        )
        assert r["mode"] == "diagnose"


class TestTutorEndpoint:
    def test_router_imports(self):
        from routes.tutor import router
        assert router.prefix == "/api/tutor"
