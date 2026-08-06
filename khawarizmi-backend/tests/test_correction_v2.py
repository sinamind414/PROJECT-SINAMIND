"""
tests/test_correction_v2.py — 19 tests pour le pipeline complet.

Couvre :
- Rejet sanity (charabia, vide)
- Succès LLM avec highlights
- Echec LLM (exception)
- Parsing JSON tolérant (fence markdown, texte avant/après)
- Post-validation (clamp score, highlights invalides, types normalisés)
- Cas unmatched_criteria en strings et dicts
"""

import json
from unittest.mock import AsyncMock, MagicMock

import pytest

from services.correction_v2 import (
    _extract_json_from_response,
    _normalize_unmatched,
    _validate_highlights,
    evaluate_answer_v2,
)

# ── Helpers / Fixtures ───────────────────────────


def _make_llm_response(content: str) -> MagicMock:
    """Crée un mock de réponse LLM OpenAI."""
    response = MagicMock()
    response.choices = [MagicMock()]
    response.choices[0].message.content = content
    return response


def _good_llm_json(score: int = 5, score_max: int = 8) -> str:
    """JSON valide typique retourné par le LLM."""
    return json.dumps({
        "score": score,
        "matched_criteria": ["تقديم الوثيقة", "ذكر التغيرات"],
        "unmatched_criteria": [
            {
                "criterion": "المقارنة بين المراحل",
                "why_ar": "لم يقارن التلميذ بين المرحلتين",
                "from_model_answer": "في المرحلة الأولى... أما في المرحلة الثانية..."
            }
        ],
        "highlights": [
            {"start": 0, "end": 10, "type": "good_element", "message_ar": "تقديم جيد"},
            {"start": 15, "end": 25, "type": "missing_link", "message_ar": "ينقص الربط"},
        ],
        "feedback_ar": "إجابة متوسطة. ذكرت بعض العناصر لكن ينقص التفصيل.",
        "advice_ar": "حاول ذكر القيم الرقمية الموجودة في الوثيقة.",
        "confidence": 0.85,
    }, ensure_ascii=False)


BASE_KWARGS = {
    "scenario_context": "دراسة تأثير التغذية على نسبة الغلوكوز",
    "documents": [{"title": "وثيقة 1", "caption": "منحنى", "data": None}],
    "question_prompt": "حلّل الوثيقة 1",
    "question_skill": "تحليل وثيقة",
    "verb_slug": "analyse",
    "model_answer": "نلاحظ من الوثيقة أن نسبة الغلوكوز تزداد من 0.8 إلى 1.4 غ/ل",
    "learning_focus": "التنظيم الهرموني",
    "score_max": 8,
}


# ── Tests : rejet sanity ─────────────────────────


class TestSanityRejection:
    """Le pipeline doit rejeter le charabia sans appeler le LLM."""

    @pytest.mark.asyncio
    async def test_gibberish_returns_zero(self):
        mock_llm = AsyncMock()
        result = await evaluate_answer_v2(
            **BASE_KWARGS,
            student_answer="ERRETREZR",
            llm_call=mock_llm,
            primary_client=MagicMock(),
            primary_model="test-model",
        )
        assert result["source"] == "sanity"
        assert result["score"] == 0
        assert result["percentage"] == 0
        mock_llm.assert_not_called()

    @pytest.mark.asyncio
    async def test_empty_returns_zero(self):
        mock_llm = AsyncMock()
        result = await evaluate_answer_v2(
            **BASE_KWARGS,
            student_answer="",
            llm_call=mock_llm,
            primary_client=MagicMock(),
            primary_model="test-model",
        )
        assert result["source"] == "sanity"
        assert result["score"] == 0
        mock_llm.assert_not_called()

    @pytest.mark.asyncio
    async def test_gibberish_has_highlights(self):
        mock_llm = AsyncMock()
        result = await evaluate_answer_v2(
            **BASE_KWARGS,
            student_answer="BVCGGCVUVUY",
            llm_call=mock_llm,
            primary_client=MagicMock(),
            primary_model="test-model",
        )
        assert result["source"] == "sanity"
        # Les highlights doivent couvrir tout le texte
        if result["highlights"]:
            h = result["highlights"][0]
            assert h["type"] == "gibberish"

    @pytest.mark.asyncio
    async def test_sanity_code_present(self):
        mock_llm = AsyncMock()
        result = await evaluate_answer_v2(
            **BASE_KWARGS,
            student_answer="abc",
            llm_call=mock_llm,
            primary_client=MagicMock(),
            primary_model="test-model",
        )
        assert "sanity_code" in result
        assert result["sanity_code"] != "ok"


# ── Tests : succès LLM ──────────────────────────


class TestLLMSuccess:
    """Le pipeline appelle le LLM et parse correctement."""

    @pytest.mark.asyncio
    async def test_good_response(self):
        mock_llm = AsyncMock(return_value=_make_llm_response(_good_llm_json(5)))
        result = await evaluate_answer_v2(
            **BASE_KWARGS,
            student_answer="نلاحظ من خلال الوثيقة أن نسبة الغلوكوز تزداد بعد الوجبة ثم تنخفض تدريجياً",
            llm_call=mock_llm,
            primary_client=MagicMock(),
            primary_model="test-model",
        )
        assert result["source"] == "llm"
        assert result["score"] == 5
        assert result["score_max"] == 8
        assert result["percentage"] == 62  # round(5/8 * 100) = round(62.5) -> 62
        assert len(result["matched_criteria"]) == 2
        assert len(result["unmatched_criteria"]) == 1
        mock_llm.assert_called_once()

    @pytest.mark.asyncio
    async def test_highlights_in_response(self):
        mock_llm = AsyncMock(return_value=_make_llm_response(_good_llm_json()))
        student = "نلاحظ من خلال الوثيقة أن نسبة الغلوكوز تزداد بعد الوجبة ثم تنخفض"
        result = await evaluate_answer_v2(
            **BASE_KWARGS,
            student_answer=student,
            llm_call=mock_llm,
            primary_client=MagicMock(),
            primary_model="test-model",
        )
        assert isinstance(result["highlights"], list)

    @pytest.mark.asyncio
    async def test_score_clamped_to_max(self):
        """Un score LLM > score_max doit être clampé."""
        over_json = json.dumps({
            "score": 99,
            "matched_criteria": [],
            "unmatched_criteria": [],
            "highlights": [],
            "feedback_ar": "test",
            "advice_ar": "test",
            "confidence": 0.5,
        })
        mock_llm = AsyncMock(return_value=_make_llm_response(over_json))
        result = await evaluate_answer_v2(
            **BASE_KWARGS,
            student_answer="نلاحظ أن الوثيقة تُظهر تغيرات في نسبة الغلوكوز خلال مراحل مختلفة",
            llm_call=mock_llm,
            primary_client=MagicMock(),
            primary_model="test-model",
        )
        assert result["score"] == 8  # clampé à score_max
        assert result["score_max"] == 8

    @pytest.mark.asyncio
    async def test_negative_score_clamped_to_zero(self):
        """Un score négatif doit être clampé à 0."""
        neg_json = json.dumps({
            "score": -3,
            "matched_criteria": [],
            "unmatched_criteria": [],
            "highlights": [],
            "feedback_ar": "test",
            "advice_ar": "test",
            "confidence": 0.5,
        })
        mock_llm = AsyncMock(return_value=_make_llm_response(neg_json))
        result = await evaluate_answer_v2(
            **BASE_KWARGS,
            student_answer="نلاحظ أن الوثيقة تُظهر تغيرات في نسبة الغلوكوز خلال مراحل متعددة",
            llm_call=mock_llm,
            primary_client=MagicMock(),
            primary_model="test-model",
        )
        assert result["score"] == 0


# ── Tests : échec LLM ───────────────────────────


class TestLLMError:
    """Le pipeline gère les erreurs LLM gracieusement."""

    @pytest.mark.asyncio
    async def test_llm_exception_returns_error(self):
        mock_llm = AsyncMock(side_effect=RuntimeError("Timeout"))
        result = await evaluate_answer_v2(
            **BASE_KWARGS,
            student_answer="نلاحظ من خلال تحليل الوثيقة أن هناك تغيرات واضحة في المعطيات",
            llm_call=mock_llm,
            primary_client=MagicMock(),
            primary_model="test-model",
        )
        assert result["source"] == "llm_error"
        assert result["score"] == 0
        assert "error_message" in result

    @pytest.mark.asyncio
    async def test_unparseable_json_returns_error(self):
        mock_llm = AsyncMock(return_value=_make_llm_response("This is not JSON at all"))
        result = await evaluate_answer_v2(
            **BASE_KWARGS,
            student_answer="نلاحظ من خلال تحليل الوثيقة أن هناك تغيرات واضحة في القيم المقاسة",
            llm_call=mock_llm,
            primary_client=MagicMock(),
            primary_model="test-model",
        )
        assert result["source"] == "llm_error"
        assert result["llm_raw"] is not None


# ── Tests : parsing JSON tolérant ────────────────


class TestJSONParsing:
    """Vérifie le parsing JSON tolérant."""

    def test_plain_json(self):
        result = _extract_json_from_response('{"score": 5}')
        assert result == {"score": 5}

    def test_markdown_fence(self):
        raw = '```json\n{"score": 5}\n```'
        result = _extract_json_from_response(raw)
        assert result == {"score": 5}

    def test_text_before_json(self):
        raw = 'Here is the result:\n{"score": 5, "feedback_ar": "جيد"}'
        result = _extract_json_from_response(raw)
        assert result is not None
        assert result["score"] == 5

    def test_empty_returns_none(self):
        assert _extract_json_from_response("") is None
        assert _extract_json_from_response(None) is None


# ── Tests : post-validation ──────────────────────


class TestPostValidation:
    """Vérifie la post-validation des highlights et unmatched."""

    def test_validate_highlights_filters_invalid(self):
        highlights = [
            {"start": 0, "end": 5, "type": "good_element", "message_ar": "ok"},
            {"start": "a", "end": "b", "type": "good_element", "message_ar": "bad"},
            {"start": 10, "end": 5, "type": "good_element", "message_ar": "reversed"},
        ]
        result = _validate_highlights(highlights, "Hello World 123")
        assert len(result) == 1  # seul le premier est valide
        assert result[0]["start"] == 0
        assert result[0]["end"] == 5

    def test_validate_highlights_unknown_type(self):
        highlights = [
            {"start": 0, "end": 5, "type": "unknown_type", "message_ar": "ok"},
        ]
        result = _validate_highlights(highlights, "Hello World")
        assert result[0]["type"] == "irrelevant"  # normalisé

    def test_normalize_unmatched_strings(self):
        unmatched = ["critère 1", "critère 2"]
        result = _normalize_unmatched(unmatched)
        assert len(result) == 2
        assert result[0]["criterion"] == "critère 1"
        assert result[0]["why_ar"] == ""


# ── Tests : correcteur local sans clé API ────────


class TestLocalFallback:
    """Sans clé API (llm_guard actif), le correcteur doit évaluer localement."""

    @pytest.mark.asyncio
    async def test_local_fallback_when_llm_disabled(self):
        """LLM indisponible + local_fallback=True → source='local', pas llm_error."""
        from services.correction_v2 import evaluate_answer_v2

        async def mock_llm_disabled(**kwargs):
            from services.llm_guard import LLMDisabledError
            raise LLMDisabledError("chat.completions.create (external LLM disabled)")

        result = await evaluate_answer_v2(
            **BASE_KWARGS,
            student_answer="الاستنساخ يتم في النواة والترجمة في الهيولى",
            llm_call=mock_llm_disabled,
            primary_client=MagicMock(),
            primary_model="test",
            local_fallback=True,
        )
        assert result["source"] == "local"
        assert result["score"] >= 0
        assert result["score_max"] == BASE_KWARGS["score_max"]
        assert isinstance(result["feedback_ar"], str)
        assert result["percentage"] == round(result["score"] / result["score_max"] * 100)

    @pytest.mark.asyncio
    async def test_local_fallback_off_keeps_llm_error(self):
        """Sans local_fallback → comportement historique (llm_error)."""
        from services.correction_v2 import evaluate_answer_v2

        async def mock_llm_disabled(**kwargs):
            from services.llm_guard import LLMDisabledError
            raise LLMDisabledError("chat.completions.create (external LLM disabled)")

        result = await evaluate_answer_v2(
            **BASE_KWARGS,
            student_answer="الاستنساخ يتم في النواة والترجمة في الهيولى",
            llm_call=mock_llm_disabled,
            primary_client=MagicMock(),
            primary_model="test",
        )
        assert result["source"] == "llm_error"
