"""correction_audit.py — Audit logging asynchrone pour corrections LLM v2.

Règles (Section 1.2 / AGENTS.md) :
- Aucune donnée personnelle en clair
- Contenu élève = hash uniquement
- Insert async sans impacter le flux de correction
"""

from __future__ import annotations

import logging
from typing import Any

from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession

logger = logging.getLogger("khawarizmi.correction_audit")


async def log_correction_audit(
    db: AsyncSession,
    result: dict[str, Any],
    verb_slug: str,
    user_id: int | None = None,
    session_id: str | None = None,
) -> None:
    """Insère une ligne d'audit dans correction_audit.

    Stocke UNIQUEMENT des hash SHA256 — jamais le contenu brut.
    """
    try:
        stmt = text("""
            INSERT INTO correction_audit
                (user_id, session_id, question_hash, student_answer_hash,
                 prompt_hash, verb_slug, sanity_code, source,
                 provider, model, finish_reason, score, score_max,
                 percentage, confidence, parse_status, attempts,
                 error_message_hash)
            VALUES
                (:user_id, :session_id, :question_hash, :student_answer_hash,
                 :prompt_hash, :verb_slug, :sanity_code, :source,
                 :provider, :model, :finish_reason, :score, :score_max,
                 :percentage, :confidence, :parse_status, :attempts,
                 :error_message_hash)
        """)
        await db.execute(stmt, {
            "user_id": user_id,
            "session_id": session_id,
            "question_hash": result.get("prompt_hash"),
            "student_answer_hash": result.get("student_answer_hash"),
            "prompt_hash": result.get("prompt_hash"),
            "verb_slug": verb_slug,
            "sanity_code": result.get("sanity_code"),
            "source": result.get("source"),
            "provider": result.get("provider"),
            "model": result.get("model"),
            "finish_reason": result.get("finish_reason"),
            "score": result.get("score"),
            "score_max": result.get("score_max"),
            "percentage": result.get("percentage"),
            "confidence": result.get("confidence"),
            "parse_status": result.get("parse_status"),
            "attempts": result.get("attempts"),
            "error_message_hash": _hash_error(
                result.get("error_message")
            ),
        })
        await db.commit()
    except Exception:
        logger.exception(
            "correction_audit_insert_failed — audit ignoré"
        )


def _hash_error(error_message: str | None) -> str | None:
    if not error_message:
        return None
    import hashlib
    return hashlib.sha256(error_message.encode()).hexdigest()[:16]
