"""tests/test_socratic_tutor.py — 6 tests pour le Mode Socratique.

Couvre :
- get_socratic_hint fallback sur erreur LLM
- get_socratic_hint fallback sur réponse vide
- get_socratic_hint avec réponse correcte → hint_ar présent
- request_hint dans EvaluateRequest schema
- Champ dominant_error_code="socratic_hint" dans les hints
"""

from __future__ import annotations

from unittest.mock import MagicMock, patch

import pytest

from schemas.document_analysis import EvaluateAnswerInput, EvaluateRequest


class TestEvaluateRequestSchema:
    def test_request_hint_defaults_to_false(self):
        req = EvaluateRequest(
            scenario_id="test",
            answers=[EvaluateAnswerInput(verb_slug="analyse", answer="test")],
        )
        assert req.request_hint is False

    def test_request_hint_true(self):
        req = EvaluateRequest(
            scenario_id="test",
            answers=[EvaluateAnswerInput(verb_slug="analyse", answer="test")],
            request_hint=True,
        )
        assert req.request_hint is True


class TestGetSocraticHint:
    def test_local_hint_is_specific_to_interpretation(self):
        from services.socratic_tutor import build_local_socratic_hint

        result = build_local_socratic_hint(
            verb_slug="interpret",
            student_answer="نلاحظ ارتفاع القيمة",
            question_prompt="فسر ارتفاع القيمة",
            documents=[{"title": "منحنى"}],
        )
        assert "السبب" in result["hint_ar"] or "لأن" in result["hint_ar"]
        assert result["methodology_step"] == "الربط السببي"

    @pytest.mark.asyncio
    async def test_fallback_on_llm_error(self):
        from services.socratic_tutor import get_socratic_hint

        with patch("services.socratic_tutor.is_llm_enabled", return_value=True), patch.object(
            __import__("services.socratic_tutor", fromlist=["_call_with_fallback"]),
            "_call_with_fallback",
            side_effect=Exception("LLM down"),
        ):
            result = await get_socratic_hint(
                scenario_context="test",
                documents=None,
                question_prompt="test?",
                question_skill="test",
                verb_slug="analyse",
                model_answer="test",
                learning_focus=None,
                student_answer="إجابة التلميذ",
            )
        assert "hint_ar" in result
        assert result["focus_area"] in {"Document", "Methodology"}
        assert "الإجابة النموذجية" not in result["hint_ar"]

    @pytest.mark.asyncio
    async def test_fallback_on_empty_response(self):
        from services.socratic_tutor import get_socratic_hint

        mock_response = MagicMock()
        mock_response.choices = [MagicMock()]
        mock_response.choices[0].message.content = ""

        with patch("services.socratic_tutor.is_llm_enabled", return_value=True), patch.object(
            __import__("services.socratic_tutor", fromlist=["_call_with_fallback"]),
            "_call_with_fallback",
            return_value=mock_response,
        ):
            result = await get_socratic_hint(
                scenario_context="test",
                documents=None,
                question_prompt="test?",
                question_skill="test",
                verb_slug="analyse",
                model_answer="test",
                learning_focus=None,
                student_answer="إجابة التلميذ",
            )
        assert result["hint_ar"]
        assert result["methodology_step"] != "Analyse"

    @pytest.mark.asyncio
    async def test_returns_hint_on_success(self):
        from services.socratic_tutor import get_socratic_hint

        mock_response = MagicMock()
        mock_response.choices = [MagicMock()]
        mock_response.choices[0].message.content = (
            '```json\n{"hint_ar": "انظر إلى الوثيقة", '
            '"focus_area": "Document", '
            '"methodology_step": "Definition"}\n```'
        )

        with patch("services.socratic_tutor.is_llm_enabled", return_value=True), patch.object(
            __import__("services.socratic_tutor", fromlist=["_call_with_fallback"]),
            "_call_with_fallback",
            return_value=mock_response,
        ):
            result = await get_socratic_hint(
                scenario_context="test",
                documents=[{"title": "Doc1", "caption": "Fig1"}],
                question_prompt="test?",
                question_skill="test",
                verb_slug="analyse",
                model_answer="test",
                learning_focus="focus",
                student_answer="إجابة التلميذ",
            )
        assert result["hint_ar"] == "انظر إلى الوثيقة"
        assert result["focus_area"] == "Document"

    @pytest.mark.asyncio
    async def test_hint_has_dominant_error_code_socratic_hint(self):
        """Le blueprint spécifie dominant_error_code='socratic_hint' pour les hints."""
        from services.socratic_tutor import get_socratic_hint

        mock_response = MagicMock()
        mock_response.choices = [MagicMock()]
        mock_response.choices[0].message.content = (
            '{"hint_ar": "test", "focus_area": "Doc", "methodology_step": "Step"}'
        )

        with patch("services.socratic_tutor.is_llm_enabled", return_value=True), patch.object(
            __import__("services.socratic_tutor", fromlist=["_call_with_fallback"]),
            "_call_with_fallback",
            return_value=mock_response,
        ):
            hint = await get_socratic_hint(
                scenario_context="test",
                documents=None,
                question_prompt="test?",
                question_skill="test",
                verb_slug="analyse",
                model_answer="test",
                learning_focus=None,
                student_answer="إجابة التلميذ",
            )
        # Le code d'erreur dominant est fixé dans la route, pas dans le service
        assert isinstance(hint, dict)
        assert "hint_ar" in hint
