"""Tests pour l'intégration Phase C: cost_logger + correction_prompt_v2."""
import json
from unittest.mock import MagicMock, patch

import pytest


@pytest.fixture
def mock_llm_response():
    """Réponse LLM mockée avec le format v2."""
    response = MagicMock()
    response.choices = [MagicMock()]
    response.choices[0].message.content = json.dumps({
        "score": 75,
        "errors": [
            {"line": "S1", "type": "methodology", "detail": "缺少关键词", "fix": "使用科学术语"}
        ],
        "feedback": "整体不错，但需要更多细节",
        "grade": "acquis"
    })
    response.choices[0].finish_reason = "stop"
    response.usage = MagicMock()
    response.usage.prompt_tokens = 150
    response.usage.completion_tokens = 80
    response._khawarizmi_provider = "test"
    response._khawarizmi_model = "test-model"
    return response


@pytest.fixture
def mock_llm_call(mock_llm_response):
    """LLR caller mocké."""
    async def _call(**kwargs):
        return mock_llm_response
    return _call


@pytest.mark.asyncio
async def test_v2_prompt_mapping(mock_llm_call):
    """Test que le prompt v2 est correctement mappé au format v1."""
    from services.correction_v2 import evaluate_answer_v2

    result = await evaluate_answer_v2(
        scenario_context="Test scenario",
        documents=None,
        question_prompt="Test question",
        question_skill="expliquer",
        verb_slug="expliquer",
        model_answer="Test model answer",
        learning_focus=None,
        score_max=10,
        student_answer="البروتينات تلعب دوراً مهماً في الكائنات الحية وتتكون من أحماض أمينية",
        llm_call=mock_llm_call,
        primary_client=MagicMock(),
        primary_model="test-model",
        request_id="test-v2-001",
        use_v2_prompt=True,
    )

    assert result["source"] == "llm_v2"
    assert 0 <= result["score"] <= 10
    assert result["feedback_ar"] != ""
    assert isinstance(result["highlights"], list)
    assert isinstance(result["errors"], list)


@pytest.mark.asyncio
async def test_cost_logger_integration(mock_llm_response):
    """Test que le cost_logger est appelé après un appel LLM réussi."""
    from services.correction_v2 import evaluate_answer_v2

    with patch("services.correction_v2.get_logger") as mock_get_logger:
        mock_logger = MagicMock()
        mock_get_logger.return_value = mock_logger

        async def _call(**kwargs):
            return mock_llm_response

        result = await evaluate_answer_v2(
            scenario_context="Test scenario",
            documents=None,
            question_prompt="Test question",
            question_skill="expliquer",
            verb_slug="expliquer",
            model_answer="Test model answer",
            learning_focus=None,
            score_max=10,
            student_answer="البروتينات تلعب دوراً مهماً في الكائنات الحية وتتكون من أحماض أمينية",
            llm_call=_call,
            primary_client=MagicMock(),
            primary_model="test-model",
            request_id="test-cost-001",
            use_v2_prompt=False,
        )

        # Vérifier que le logger a été appelé
        mock_logger.record.assert_called_once()
        call_kwargs = mock_logger.record.call_args[1]
        assert call_kwargs["model"] == "test-model"
        assert call_kwargs["input_tokens"] == 150
        assert call_kwargs["output_tokens"] == 80
        assert call_kwargs["verb_slug"] == "expliquer"


@pytest.mark.asyncio
async def test_v1_prompt_unchanged(mock_llm_call):
    """Test que le prompt v1 fonctionne toujours normalement."""
    from services.correction_v2 import evaluate_answer_v2

    result = await evaluate_answer_v2(
        scenario_context="Test scenario",
        documents=None,
        question_prompt="Test question",
        question_skill="expliquer",
        verb_slug="expliquer",
        model_answer="Test model answer",
        learning_focus=None,
        score_max=10,
        student_answer="البروتينات تلعب دوراً مهماً في الكائنات الحية وتتكون من أحماض أمينية",
        llm_call=mock_llm_call,
        primary_client=MagicMock(),
        primary_model="test-model",
        request_id="test-v1-001",
        use_v2_prompt=False,
    )

    # Le format v1 standard
    assert result["source"] == "llm"
    assert 0 <= result["score"] <= 10
    assert "highlights" in result
    assert "matched_criteria" in result
    assert "unmatched_criteria" in result
