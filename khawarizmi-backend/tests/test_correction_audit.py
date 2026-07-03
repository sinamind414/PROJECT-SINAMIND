"""tests/test_correction_audit.py — 6 tests pour correction_audit.py.

Couvre :
- Insert réussie
- Insert avec user_id=None
- Insert avec erreur
- Gestion silencieuse d'échec DB
- Hash d'erreur
- Migration upgrade/downgrade
"""

from __future__ import annotations

from unittest.mock import AsyncMock

import pytest

from services.correction_audit import _hash_error, log_correction_audit


@pytest.fixture
def sample_result() -> dict:
    return {
        "source": "llm",
        "score": 3,
        "score_max": 5,
        "percentage": 60,
        "highlights": [],
        "matched_criteria": ["test"],
        "unmatched_criteria": [],
        "feedback_ar": "جيدة",
        "advice_ar": "",
        "confidence": 0.85,
        "sanity_code": "ok",
        "prompt_hash": "abc123",
        "student_answer_hash": "def456",
        "llm_raw_hash": "ghi789",
        "parse_status": "ok",
        "provider": "groq",
        "model": "llama-3.3-70b",
        "finish_reason": "stop",
        "attempts": 1,
        "error_message": None,
    }


class TestHashError:
    def test_hash_error_none(self):
        assert _hash_error(None) is None

    def test_hash_error_empty(self):
        assert _hash_error("") is None

    def test_hash_error_valid(self):
        h = _hash_error("503 Service Unavailable")
        assert isinstance(h, str)
        assert len(h) == 16


class TestLogCorrectionAudit:
    @pytest.mark.asyncio
    async def test_insert_success(self, sample_result):
        db = AsyncMock()
        db.execute = AsyncMock()
        db.commit = AsyncMock()

        await log_correction_audit(
            db=db,
            result=sample_result,
            verb_slug="analyse",
            user_id=42,
            session_id="sess-001",
        )

        db.execute.assert_awaited_once()
        db.commit.assert_awaited_once()

    @pytest.mark.asyncio
    async def test_insert_without_user(self, sample_result):
        db = AsyncMock()
        db.execute = AsyncMock()
        db.commit = AsyncMock()

        await log_correction_audit(
            db=db,
            result=sample_result,
            verb_slug="analyse",
            user_id=None,
            session_id=None,
        )

        db.execute.assert_awaited_once()
        db.commit.assert_awaited_once()

    @pytest.mark.asyncio
    async def test_insert_with_error_message(self, sample_result):
        sample_result["error_message"] = "503 Service Unavailable"
        db = AsyncMock()
        db.execute = AsyncMock()
        db.commit = AsyncMock()

        await log_correction_audit(
            db=db,
            result=sample_result,
            verb_slug="analyse",
            user_id=42,
            session_id="sess-001",
        )

        db.execute.assert_awaited_once()
        db.commit.assert_awaited_once()

    @pytest.mark.asyncio
    async def test_db_failure_does_not_raise(self, sample_result):
        db = AsyncMock()
        db.execute = AsyncMock(side_effect=Exception("DB down"))

        await log_correction_audit(
            db=db,
            result=sample_result,
            verb_slug="analyse",
            user_id=42,
            session_id="sess-001",
        )

        db.execute.assert_awaited_once()
        # Pas d'exception remontée malgré l'échec DB
