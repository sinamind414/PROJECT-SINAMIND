"""tests/test_grading_pipeline.py — Pipeline complet (audit S2.1f).

Le pipeline appelle TOUTES les étapes directement (sanity → savoir → prompt
→ LLM → parser → mapping → post-validation) ; la façade correction_v2
délègue ici. Ces tests vérifient la logique réelle avec des mocks LLM :
- sanity court-circuit (aucun appel LLM)
- étage savoir (promotion, feature flag)
- LLM v1 / v2 (mapping), erreurs, JSON invalide, L2 fallback
- constances (LLM_MAX_TOKENS, VOLATILE_FIELDS) et assert_parity
"""

import json
from unittest.mock import MagicMock

import pytest

from grading.pipeline import (
    LLM_MAX_TOKENS,
    LLM_TEMPERATURE,
    LLM_TIMEOUT_SECONDS,
    VOLATILE_FIELDS,
    assert_parity,
    evaluate_answer_v2_pipeline,
)
from services.correction_v2 import evaluate_answer_v2

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


def _make_llm_response(content: str) -> MagicMock:
    resp = MagicMock()
    resp.choices = [MagicMock()]
    resp.choices[0].message.content = content
    resp.choices[0].finish_reason = "stop"
    resp._khawarizmi_json_mode = False
    resp._khawarizmi_provider = "primary"
    resp._khawarizmi_model = "test"
    return resp


def _v1_json(score: int = 6) -> str:
    return json.dumps({
        "score": score,
        "matched_criteria": ["a"],
        "unmatched_criteria": [],
        "highlights": [],
        "feedback_ar": "f",
        "advice_ar": "",
        "confidence": 0.8,
    }, ensure_ascii=False)


def _v2_json(score: int = 75) -> str:
    return json.dumps({
        "score": score,
        "errors": [],
        "feedback": "f",
        "grade": "acquis",
    }, ensure_ascii=False)


async def _run(llm_mock, *, answer: str = "الاستنساخ يتم في النواة والترجمة في الهيولى",
               **overrides) -> dict:
    kwargs = {k: v for k, v in BASE_KWARGS.items()
              if k not in ("verb_slug", "model_answer", "score_max")}
    kwargs.update(overrides)
    return await evaluate_answer_v2_pipeline(
        question_id=1,
        verb_slug="analyse",
        score_max=8,
        student_answer=answer,
        model_answer=BASE_KWARGS["model_answer"],
        llm_call=llm_mock,
        primary_client=MagicMock(),
        primary_model="test",
        **kwargs,
    )


class TestSanity:
    @pytest.mark.asyncio
    async def test_reject_circuit_breaks(self):
        """Copie invalide → sanity rejetée, AUCUN appel LLM."""
        llm_mock = MagicMock()
        result = await _run(llm_mock, answer="ZZZZZ")
        assert result["source"] == "sanity"
        assert result["sanity_code"] == "too_short"
        assert result["score"] == 0
        llm_mock.assert_not_called()

    @pytest.mark.asyncio
    async def test_empty_answer(self):
        llm_mock = MagicMock()
        result = await _run(llm_mock, answer="")
        assert result["source"] == "sanity"
        assert result["sanity_code"] == "empty"
        llm_mock.assert_not_called()

    @pytest.mark.asyncio
    async def test_precomputed_sanity_retrocompat(self):
        """precomputed_sanity (S2.1b) : résultat identique au calcul interne."""
        llm_mock = MagicMock()
        result = await _run(llm_mock, answer="", precomputed_sanity=(False, "empty", "msg"))
        assert result["source"] == "sanity"
        assert result["sanity_code"] == "empty"
        llm_mock.assert_not_called()


class TestSavoirIntegrated:
    # Contexte du golden couvert par le lexique (≥ 3 concepts dans la copie)
    _Q = "أين يحدث نسخ المعلومة الوراثية في الخلية حقيقية النواة؟"
    _MA = "يحدث نسخ المعلومة الوراثية في النواة حيث تتواجد جزيئة ADN"

    @pytest.mark.asyncio
    async def test_savoir_promoted_no_llm_call(self, monkeypatch):
        from config import get_settings
        monkeypatch.setattr(get_settings(), "savoir_enabled_verbs", ["analyse"])

        llm_mock = MagicMock()
        result = await evaluate_answer_v2_pipeline(
            question_id=1, verb_slug="analyse", score_max=2,
            student_answer=self._MA, model_answer=self._MA,
            question_prompt=self._Q, question_skill="restitution",
            llm_call=llm_mock, primary_client=MagicMock(), primary_model="test",
        )
        assert result["source"] == "local_savoir"
        assert result["parse_status"] == "local"
        assert result["remediation"] is None
        assert result["attempts"] == 0
        llm_mock.assert_not_called()

    @pytest.mark.asyncio
    async def test_savoir_disabled_by_default(self):
        """Défaut config : savoir_enabled_verbs=[] → jamais promu."""
        async def llm_mock(**kwargs):
            return _make_llm_response(_v1_json())

        result = await _run(llm_mock)
        assert result["source"] != "local_savoir"
        assert result["source"] == "llm"


class TestLLM:
    @pytest.mark.asyncio
    async def test_v1_success(self):
        async def llm_mock(**kwargs):
            return _make_llm_response(_v1_json(score=6))

        result = await _run(llm_mock)
        assert result["source"] == "llm"
        assert result["score"] == 6
        assert result["parse_status"] == "ok"
        assert result["percentage"] == 75

    @pytest.mark.asyncio
    async def test_v2_mapping(self):
        async def llm_mock(**kwargs):
            resp = _make_llm_response(_v2_json(score=75))
            resp._khawarizmi_json_mode = True
            return resp

        result = await _run(llm_mock, use_v2_prompt=True)
        assert result["source"] == "llm_v2"
        assert result["score"] == round(75 * 8 / 100)  # 6
        assert result["parse_status"] == "recovered"

    @pytest.mark.asyncio
    async def test_llm_error(self):
        async def llm_mock(**kwargs):
            raise RuntimeError("boom")

        result = await _run(llm_mock)
        assert result["source"] == "llm_error"
        assert result["error_message"] == "boom"
        assert result["parse_status"] == "failed"

    @pytest.mark.asyncio
    async def test_llm_error_with_local_fallback(self):
        async def llm_mock(**kwargs):
            raise RuntimeError("boom")

        result = await _run(llm_mock, local_fallback=True, local_fallback_db=None)
        assert result["source"] == "local"
        assert result["parse_status"] == "local_fallback"

    @pytest.mark.asyncio
    async def test_json_invalide_error(self):
        async def llm_mock(**kwargs):
            return _make_llm_response("pas de json ici {")

        result = await _run(llm_mock)
        assert result["source"] == "llm_error"
        assert "parser" in result["error_message"]

    @pytest.mark.asyncio
    async def test_json_invalide_local_fallback(self):
        async def llm_mock(**kwargs):
            return _make_llm_response("pas de json ici {")

        result = await _run(llm_mock, local_fallback=True, local_fallback_db=None)
        assert result["source"] == "local"

    @pytest.mark.asyncio
    async def test_llm_call_receives_expected_kwargs(self):
        captured = {}

        async def llm_mock(**kwargs):
            captured.update(kwargs)
            return _make_llm_response(_v1_json())

        await _run(llm_mock)
        assert captured["temperature"] == LLM_TEMPERATURE
        assert captured["max_tokens"] == LLM_MAX_TOKENS
        assert captured["timeout"] == LLM_TIMEOUT_SECONDS
        assert captured["json_schema"] is None  # json_mode_providers vide par défaut
        assert captured["response_validator"] is not None


class TestFacadeParity:
    @pytest.mark.asyncio
    async def test_facade_equals_pipeline(self):
        """La façade evaluate_answer_v2 délègue au pipeline (même résultat)."""
        async def llm_mock(**kwargs):
            return _make_llm_response(_v1_json(score=6))

        via_facade = await evaluate_answer_v2(
            **BASE_KWARGS,
            student_answer="الاستنساخ يتم في النواة والترجمة في الهيولى",
            llm_call=llm_mock, primary_client=MagicMock(), primary_model="test",
        )
        via_pipeline = await _run(llm_mock)
        assert_parity(via_facade, via_pipeline)


class TestConstants:
    def test_llm_constants(self):
        assert LLM_TEMPERATURE == 0.0
        assert LLM_MAX_TOKENS == 900
        assert LLM_TIMEOUT_SECONDS == 25.0

    def test_volatile_fields(self):
        assert "attempts" in VOLATILE_FIELDS
        assert "prompt_hash" in VOLATILE_FIELDS
