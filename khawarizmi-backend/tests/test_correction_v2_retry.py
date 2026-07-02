"""
tests/test_correction_v2_retry.py — 24 tests pour la couche retry LLM.

Couvre :
- Classification transitoire vs permanente (8 tests)
- Retry avec succès au 2e essai (4 tests)
- Retry épuisé (2 tests)
- Sanity court-circuit (2 tests)
- Succès direct sans retry (2 tests)
- Contrat de retour préservé (3 tests)
- Cas extrêmes (3 tests)
"""

from __future__ import annotations

from typing import Any
from unittest.mock import AsyncMock, MagicMock

import pytest

from services.correction_v2_retry import (
    _is_transient_error,
    evaluate_answer_v2_with_retry,
)

# ── Helpers ──────────────────────────────────────────────────────────


def _make_llm_response(content: str) -> MagicMock:
    response = MagicMock()
    response.choices = [MagicMock()]
    response.choices[0].message.content = content
    return response


BASE_KWARGS = {
    "scenario_context": "test",
    "documents": None,
    "question_prompt": "test?",
    "question_skill": "test",
    "verb_slug": "hypothesis",
    "model_answer": "test answer",
    "learning_focus": None,
    "score_max": 5,
}


def _success_result(score: int = 4, score_max: int = 5) -> dict:
    return {
        "source": "llm",
        "score": score,
        "score_max": score_max,
        "percentage": round((score / score_max) * 100) if score_max else 0,
        "highlights": [],
        "matched_criteria": ["test"],
        "unmatched_criteria": [],
        "feedback_ar": "إجابة جيدة",
        "advice_ar": "حاول إضافة تفاصيل",
        "confidence": 0.85,
        "sanity_code": "ok",
        "llm_raw": '{"score": ' + str(score) + "}",
        "error_message": None,
    }


def _error_result(error_msg: str) -> dict:
    return {
        "source": "llm_error",
        "score": 0,
        "score_max": 5,
        "percentage": 0,
        "highlights": [],
        "matched_criteria": [],
        "unmatched_criteria": [],
        "feedback_ar": "erreur",
        "advice_ar": "",
        "confidence": 0.0,
        "sanity_code": "ok",
        "llm_raw": None,
        "error_message": error_msg,
    }


def _sanity_result() -> dict:
    return {
        "source": "sanity",
        "score": 0,
        "score_max": 5,
        "percentage": 0,
        "highlights": [{"start": 0, "end": 5, "type": "gibberish", "message_ar": "غير مفهوم"}],
        "matched_criteria": [],
        "unmatched_criteria": [],
        "feedback_ar": "غير مفهوم",
        "advice_ar": "حاول مجدداً",
        "confidence": 1.0,
        "sanity_code": "gibberish",
        "llm_raw": None,
        "error_message": None,
    }


# ═══════════════════════════════════════════════════════════════════════
# Classification transitoire vs permanente (8 tests)
# ═══════════════════════════════════════════════════════════════════════


class TestTransientClassification:
    """_is_transient_error doit correctement classer les erreurs."""

    @pytest.mark.parametrize("error_msg", [
        "Error code: 503 - Service Unavailable",
        "Error code: 502 - Bad Gateway",
        "Error code: 504 - Gateway Timeout",
        "timeout of 30000ms exceeded",
        "connection reset by peer",
        "This model is currently experiencing high demand",
        "service temporarily unavailable",
        "rate limit exceeded, quota exhausted",
        "Deadline exceeded",
        "overloaded with requests",
        "try again later",
        "API is temporarily unavailable",
    ])
    def test_transient_errors_are_retryable(self, error_msg: str):
        result = _error_result(error_msg)
        assert _is_transient_error(result) is True, f"devrait être transitoire: {error_msg[:50]}"

    @pytest.mark.parametrize("error_msg", [
        "Error code: 401 - Invalid API key",
        "Error code: 403 - Forbidden",
        "Error code: 400 - Bad Request",
        "Error code: 404 - Not Found",
        "Invalid API key provided",
        "Unauthorized access",
        "Impossible de parser la réponse JSON",
        "json_parse_failed | raw_len=450",
        "le slug 'toto' ne correspond à aucun verbe",
    ])
    def test_permanent_errors_are_not_retryable(self, error_msg: str):
        result = _error_result(error_msg)
        assert _is_transient_error(result) is False, f"ne devrait PAS être transitoire: {error_msg[:50]}"

    def test_non_error_source_is_not_transient(self):
        result = _success_result()
        assert _is_transient_error(result) is False

    def test_empty_error_message_is_not_transient(self):
        result = _error_result("")
        assert _is_transient_error(result) is False


# ═══════════════════════════════════════════════════════════════════════
# Retry avec succès au 2e essai (4 tests)
# ═══════════════════════════════════════════════════════════════════════


class TestRetrySuccessful:
    """Sur erreur transitoire, le retry doit réussir."""

    @pytest.mark.asyncio
    async def test_retry_succeeds_on_second_attempt(self):
        call_count = 0

        async def mock_llm(**kwargs):
            nonlocal call_count
            call_count += 1
            if call_count == 1:
                raise Exception("503 - Service Unavailable")
            return _make_llm_response('{"score": 4, "matched_criteria": ["test"], "unmatched_criteria": [], "highlights": [], "feedback_ar": "ok", "advice_ar": "ok"}')

        result = await evaluate_answer_v2_with_retry(
            **BASE_KWARGS,
            student_answer="فرضية جيدة",
            llm_call=mock_llm,
            primary_client=MagicMock(),
            primary_model="test",
            max_attempts=2,
            backoff_base_seconds=0.01,
        )

        assert result["source"] == "llm_retried"
        assert result["score"] == 4
        assert result["attempts"] == 2

    @pytest.mark.asyncio
    async def test_retry_succeeds_on_third_attempt_with_max_3(self):
        call_count = 0

        async def mock_llm(**kwargs):
            nonlocal call_count
            call_count += 1
            if call_count <= 2:
                raise Exception("503 - Service Unavailable")
            return _make_llm_response('{"score": 3, "matched_criteria": ["test"], "unmatched_criteria": [], "highlights": [], "feedback_ar": "ok", "advice_ar": "ok"}')

        result = await evaluate_answer_v2_with_retry(
            **BASE_KWARGS,
            student_answer="فرضية جيدة",
            llm_call=mock_llm,
            primary_client=MagicMock(),
            primary_model="test",
            max_attempts=3,
            backoff_base_seconds=0.01,
        )

        assert result["source"] == "llm_retried"
        assert result["score"] == 3
        assert result["attempts"] == 3

    @pytest.mark.asyncio
    async def test_retry_with_timeout_error(self):
        call_count = 0

        async def mock_llm(**kwargs):
            nonlocal call_count
            call_count += 1
            if call_count == 1:
                raise Exception("timeout of 25000ms exceeded")
            return _make_llm_response('{"score": 5, "matched_criteria": ["test"], "unmatched_criteria": [], "highlights": [], "feedback_ar": "ok", "advice_ar": "ok"}')

        result = await evaluate_answer_v2_with_retry(
            **BASE_KWARGS,
            student_answer="فرضية سليمة",
            llm_call=mock_llm,
            primary_client=MagicMock(),
            primary_model="test",
            max_attempts=2,
            backoff_base_seconds=0.01,
        )

        assert result["source"] == "llm_retried"
        assert result["attempts"] == 2

    @pytest.mark.asyncio
    async def test_retry_with_high_demand_error(self):
        call_count = 0

        async def mock_llm(**kwargs):
            nonlocal call_count
            call_count += 1
            if call_count == 1:
                raise Exception("This model is currently experiencing high demand")
            return _make_llm_response('{"score": 4, "matched_criteria": ["test"], "unmatched_criteria": [], "highlights": [], "feedback_ar": "ok", "advice_ar": "ok"}')

        result = await evaluate_answer_v2_with_retry(
            **BASE_KWARGS,
            student_answer="فرضية جيدة",
            llm_call=mock_llm,
            primary_client=MagicMock(),
            primary_model="test",
            max_attempts=2,
            backoff_base_seconds=0.01,
        )

        assert result["source"] == "llm_retried"
        assert result["attempts"] == 2


# ═══════════════════════════════════════════════════════════════════════
# Retry épuisé (2 tests)
# ═══════════════════════════════════════════════════════════════════════


class TestRetryExhausted:
    """Quand tous les essais échouent, source=llm_error est préservé."""

    @pytest.mark.asyncio
    async def test_all_attempts_fail_returns_llm_error(self):
        call_count = 0

        async def mock_llm(**kwargs):
            nonlocal call_count
            call_count += 1
            raise Exception("503 - Service Unavailable")

        result = await evaluate_answer_v2_with_retry(
            **BASE_KWARGS,
            student_answer="فرضية سليمة",
            llm_call=mock_llm,
            primary_client=MagicMock(),
            primary_model="test",
            max_attempts=2,
            backoff_base_seconds=0.01,
        )

        assert result["source"] == "llm_error"
        assert result["score"] == 0
        assert result["attempts"] == 2
        assert call_count == 2

    @pytest.mark.asyncio
    async def test_all_attempts_fail_with_error_message_present(self):
        async def mock_llm(**kwargs):
            raise Exception("high demand spikes are usually temporary")

        result = await evaluate_answer_v2_with_retry(
            **BASE_KWARGS,
            student_answer="فرضية سليمة",
            llm_call=mock_llm,
            primary_client=MagicMock(),
            primary_model="test",
            max_attempts=2,
            backoff_base_seconds=0.01,
        )

        assert result["source"] == "llm_error"
        assert "high demand" in result.get("error_message", "").lower()


# ═══════════════════════════════════════════════════════════════════════
# Sanity court-circuit (2 tests)
# ═══════════════════════════════════════════════════════════════════════


class TestSanityCourtCircuit:
    """Sanity check ne doit JAMAIS déclencher de retry."""

    @pytest.mark.asyncio
    async def test_gibberish_no_retry(self):
        mock_llm = AsyncMock()
        result = await evaluate_answer_v2_with_retry(
            **BASE_KWARGS,
            student_answer="ERRETREZR",
            llm_call=mock_llm,
            primary_client=MagicMock(),
            primary_model="test",
            max_attempts=3,
            backoff_base_seconds=0.01,
        )

        assert result["source"] == "sanity"
        assert result["score"] == 0
        assert result["attempts"] == 1
        mock_llm.assert_not_called()

    @pytest.mark.asyncio
    async def test_empty_answer_no_retry(self):
        mock_llm = AsyncMock()
        result = await evaluate_answer_v2_with_retry(
            **BASE_KWARGS,
            student_answer="",
            llm_call=mock_llm,
            primary_client=MagicMock(),
            primary_model="test",
            max_attempts=3,
            backoff_base_seconds=0.01,
        )

        assert result["source"] == "sanity"
        assert result["attempts"] == 1
        mock_llm.assert_not_called()


# ═══════════════════════════════════════════════════════════════════════
# Succès direct (2 tests)
# ═══════════════════════════════════════════════════════════════════════


class TestDirectSuccess:
    """Premier essai réussi → source llm, attempts=1."""

    @pytest.mark.asyncio
    async def test_first_attempt_success_llm_source(self):
        async def mock_llm(**kwargs):
            return _make_llm_response('{"score": 5, "matched_criteria": ["test"], "unmatched_criteria": [], "highlights": [], "feedback_ar": "ok", "advice_ar": "ok"}')

        result = await evaluate_answer_v2_with_retry(
            **BASE_KWARGS,
            student_answer="فرضية ممتازة",
            llm_call=mock_llm,
            primary_client=MagicMock(),
            primary_model="test",
            max_attempts=2,
            backoff_base_seconds=0.01,
        )

        assert result["source"] == "llm"
        assert result["attempts"] == 1
        assert result["score"] == 5

    @pytest.mark.asyncio
    async def test_first_attempt_success_llm_recovered_source(self):
        async def mock_llm(**kwargs):
            return _make_llm_response('{"score": null, "matched_criteria": [], "unmatched_criteria": [], "highlights": []}')

        result = await evaluate_answer_v2_with_retry(
            **BASE_KWARGS,
            student_answer="فرضية سليمة",
            llm_call=mock_llm,
            primary_client=MagicMock(),
            primary_model="test",
        )

        assert result["source"] == "llm_recovered"
        assert result["attempts"] == 1


# ═══════════════════════════════════════════════════════════════════════
# Contrat de retour préservé (3 tests)
# ═══════════════════════════════════════════════════════════════════════


class TestReturnContract:
    """Les champs existants de evaluate_answer_v2 sont préservés."""

    @pytest.mark.asyncio
    async def test_all_expected_fields_present_on_success(self):
        async def mock_llm(**kwargs):
            return _make_llm_response('{"score": 4, "matched_criteria": ["test"], "unmatched_criteria": [], "highlights": [], "feedback_ar": "ok", "advice_ar": "ok", "confidence": 0.9}')

        result = await evaluate_answer_v2_with_retry(
            **BASE_KWARGS,
            student_answer="فرضية سليمة",
            llm_call=mock_llm,
            primary_client=MagicMock(),
            primary_model="test",
        )

        expected_fields = {"source", "score", "score_max", "percentage", "highlights",
                           "matched_criteria", "unmatched_criteria", "feedback_ar",
                           "advice_ar", "confidence", "sanity_code", "attempts"}
        assert expected_fields.issubset(result.keys())

    @pytest.mark.asyncio
    async def test_all_expected_fields_present_on_error(self):
        async def mock_llm(**kwargs):
            raise Exception("This model is currently experiencing high demand")

        result = await evaluate_answer_v2_with_retry(
            **BASE_KWARGS,
            student_answer="فرضية سليمة",
            llm_call=mock_llm,
            primary_client=MagicMock(),
            primary_model="test",
            max_attempts=2,
            backoff_base_seconds=0.01,
        )

        expected_fields = {"source", "score", "score_max", "percentage", "highlights",
                           "matched_criteria", "unmatched_criteria", "feedback_ar",
                           "advice_ar", "confidence", "sanity_code", "attempts"}
        assert expected_fields.issubset(result.keys())

    @pytest.mark.asyncio
    async def test_all_expected_fields_present_on_sanity(self):
        mock_llm = AsyncMock()
        result = await evaluate_answer_v2_with_retry(
            **BASE_KWARGS,
            student_answer="BVCGGCVUVUY",
            llm_call=mock_llm,
            primary_client=MagicMock(),
            primary_model="test",
        )

        expected_fields = {"source", "score", "score_max", "percentage", "highlights",
                           "matched_criteria", "unmatched_criteria", "feedback_ar",
                           "advice_ar", "confidence", "sanity_code", "attempts"}
        assert expected_fields.issubset(result.keys())


# ═══════════════════════════════════════════════════════════════════════
# Cas extrêmes (3 tests)
# ═══════════════════════════════════════════════════════════════════════


class TestEdgeCases:
    """Comportement sur erreurs inclassables et timeouts réels."""

    @pytest.mark.asyncio
    async def test_max_attempts_1_disables_retry(self):
        call_count = 0

        async def mock_llm(**kwargs):
            nonlocal call_count
            call_count += 1
            raise Exception("503 - Service Unavailable")

        result = await evaluate_answer_v2_with_retry(
            **BASE_KWARGS,
            student_answer="فرضية سليمة",
            llm_call=mock_llm,
            primary_client=MagicMock(),
            primary_model="test",
            max_attempts=1,
            backoff_base_seconds=0.01,
        )

        assert result["source"] == "llm_error"
        assert result["attempts"] == 1
        assert call_count == 1

    @pytest.mark.asyncio
    async def test_unknown_error_no_retry(self):
        call_count = 0

        async def mock_llm(**kwargs):
            nonlocal call_count
            call_count += 1
            raise Exception("Weird cryptic error that nobody expects")

        result = await evaluate_answer_v2_with_retry(
            **BASE_KWARGS,
            student_answer="فرضية سليمة",
            llm_call=mock_llm,
            primary_client=MagicMock(),
            primary_model="test",
            max_attempts=3,
            backoff_base_seconds=0.01,
        )

        assert result["source"] == "llm_error"
        assert result["attempts"] == 1
        assert call_count == 1

    @pytest.mark.asyncio
    async def test_backoff_respected_between_attempts(self):
        import time

        call_count = 0

        async def mock_llm(**kwargs):
            nonlocal call_count
            call_count += 1
            if call_count == 1:
                raise Exception("503 - Service Unavailable")
            return _make_llm_response('{"score": 4, "matched_criteria": ["test"], "unmatched_criteria": [], "highlights": [], "feedback_ar": "ok", "advice_ar": "ok"}')

        t0 = time.monotonic()
        result = await evaluate_answer_v2_with_retry(
            **BASE_KWARGS,
            student_answer="فرضية سليمة",
            llm_call=mock_llm,
            primary_client=MagicMock(),
            primary_model="test",
            max_attempts=2,
            backoff_base_seconds=0.1,
        )
        elapsed = time.monotonic() - t0

        assert result["source"] == "llm_retried"
        assert elapsed >= 0.08, f"backoff trop court: {elapsed:.3f}s (attendu ≥0.08s)"
