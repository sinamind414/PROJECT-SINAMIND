"""
tests/test_correction_prompt.py — 19 tests pour la construction du prompt.

Couvre :
- Prompt système (non vide, en arabe)
- Méthodologie par verbe (10 verbes couverts)
- Construction du prompt (champs obligatoires, documents, formats)
"""

import pytest

from prompts.correction_prompt import (
    SYSTEM_PROMPT_AR,
    VERB_METHODOLOGY_AR,
    build_correction_prompt,
)


# ── Prompt système ───────────────────────────────


class TestSystemPrompt:
    """Vérifie que le prompt système est bien formé."""

    def test_system_prompt_not_empty(self):
        assert SYSTEM_PROMPT_AR
        assert len(SYSTEM_PROMPT_AR) > 100

    def test_system_prompt_contains_json_instruction(self):
        assert "JSON" in SYSTEM_PROMPT_AR

    def test_system_prompt_contains_arabic(self):
        """Le prompt doit contenir du texte arabe."""
        arabic_chars = [c for c in SYSTEM_PROMPT_AR if "\u0600" <= c <= "\u06FF"]
        assert len(arabic_chars) > 50

    def test_system_prompt_mentions_score(self):
        assert "score" in SYSTEM_PROMPT_AR.lower() or "النقطة" in SYSTEM_PROMPT_AR

    def test_system_prompt_mentions_highlights(self):
        assert "highlights" in SYSTEM_PROMPT_AR or "highlight" in SYSTEM_PROMPT_AR.lower()


# ── Méthodologie par verbe ───────────────────────


class TestVerbMethodology:
    """Vérifie la couverture des verbes dans VERB_METHODOLOGY_AR."""

    EXPECTED_VERBS = [
        "analyse",
        "interpret",
        "deduce",
        "hypothesis",
        "scientific-text",
        "compare",
        "justify",
    ]

    def test_all_main_verbs_covered(self):
        for verb in self.EXPECTED_VERBS:
            assert verb in VERB_METHODOLOGY_AR, f"Verbe '{verb}' manquant"

    def test_methodology_content_not_empty(self):
        for verb, content in VERB_METHODOLOGY_AR.items():
            assert content, f"Méthodologie vide pour '{verb}'"
            assert len(content) > 20, f"Méthodologie trop courte pour '{verb}'"

    def test_methodology_contains_arabic(self):
        for verb, content in VERB_METHODOLOGY_AR.items():
            arabic_chars = [c for c in content if "\u0600" <= c <= "\u06FF"]
            assert len(arabic_chars) > 10, f"Pas assez d'arabe dans la méthodologie de '{verb}'"

    def test_analyse_forbids_interpretation(self):
        """Le verbe 'analyse' doit mentionner l'interdiction de causalité."""
        content = VERB_METHODOLOGY_AR["analyse"]
        assert "الممنوع" in content or "لا تفسير" in content


# ── Construction du prompt ───────────────────────


class TestBuildPrompt:
    """Vérifie build_correction_prompt."""

    BASE_KWARGS = {
        "scenario_context": "دراسة تأثير التغذية على نسبة الغلوكوز في الدم",
        "documents": None,
        "question_prompt": "حلّل الوثيقة 1",
        "question_skill": "تحليل وثيقة",
        "verb_slug": "analyse",
        "model_answer": "نلاحظ من خلال الوثيقة أن نسبة الغلوكوز تزداد بعد الوجبة",
        "learning_focus": "التنظيم الهرموني لنسبة السكر في الدم",
        "score_max": 8,
        "student_answer": "نلاحظ أن النسبة تزداد",
    }

    def test_returns_string(self):
        result = build_correction_prompt(**self.BASE_KWARGS)
        assert isinstance(result, str)

    def test_contains_context(self):
        result = build_correction_prompt(**self.BASE_KWARGS)
        assert "التغذية" in result

    def test_contains_question(self):
        result = build_correction_prompt(**self.BASE_KWARGS)
        assert "حلّل الوثيقة" in result

    def test_contains_model_answer(self):
        result = build_correction_prompt(**self.BASE_KWARGS)
        assert "الإجابة النموذجية" in result

    def test_contains_student_answer(self):
        result = build_correction_prompt(**self.BASE_KWARGS)
        assert "إجابة التلميذ" in result
        assert "نلاحظ أن النسبة تزداد" in result

    def test_contains_score_max(self):
        result = build_correction_prompt(**self.BASE_KWARGS)
        assert "8" in result

    def test_contains_methodology(self):
        result = build_correction_prompt(**self.BASE_KWARGS)
        assert "المنهجية" in result

    def test_with_documents(self):
        docs = [
            {"title": "وثيقة 1", "caption": "منحنى تغير نسبة الغلوكوز", "data": None},
            {"title": "وثيقة 2", "caption": "جدول المقارنة", "data": {"rows": [1, 2, 3]}},
        ]
        kwargs = {**self.BASE_KWARGS, "documents": docs}
        result = build_correction_prompt(**kwargs)
        assert "وثيقة 1" in result
        assert "وثيقة 2" in result
        assert "منحنى" in result

    def test_without_learning_focus(self):
        kwargs = {**self.BASE_KWARGS, "learning_focus": None}
        result = build_correction_prompt(**kwargs)
        assert isinstance(result, str)
        # Le prompt doit fonctionner même sans learning_focus
        assert "حلّل الوثيقة" in result
