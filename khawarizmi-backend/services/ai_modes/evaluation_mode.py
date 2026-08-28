"""S11 — plus de GPT/L2 ici. grade() ou ungraded. Route /api/ai/evaluate hors registre."""

from __future__ import annotations

import logging

from sqlalchemy.ext.asyncio import AsyncSession

from services.grade_adapter import (
    UNGRADED_AR,
    grade_or_none,
    may_write_fsrs,
    resolve_question_id,
    to_verb_eval,
)
from services.local_grader import TRAINING_BANNER_AR

logger = logging.getLogger("khawarizmi.evaluation_mode")


async def handle_evaluation(req, user: dict, db: AsyncSession, openai_client):
    """0 LLM. ENABLE_EXTERNAL_LLM ignoré. Sans Rubric L0 → ungraded."""
    _ = openai_client
    qid = resolve_question_id(getattr(req, "question_id", None))
    answer = getattr(req, "reponse_eleve", "") or ""
    graded = grade_or_none(qid, answer)
    if graded is None:
        logger.info(
            "eval_mode ungraded | user=%s q=%s",
            user.get("id"),
            getattr(req, "question_id", None),
        )
        return {
            "mode": "evaluation",
            "score": 0,
            "statut": "ungraded",
            "feedback": f"{UNGRADED_AR} {TRAINING_BANNER_AR}",
            "manquant": [],
            "next_review_date": None,
            "source": "ungraded",
            "ungraded": True,
            "banner_ar": TRAINING_BANNER_AR,
            "methodology": None,
        }

    mapped = to_verb_eval(graded)
    if may_write_fsrs(graded):
        from services.fsrs_unified import update_memory

        await update_memory(
            db,
            user["id"],
            "verb_chapter",
            item_id=str(qid),
            last_score=mapped["percentage"],
            attempts_delta=1,
        )
        await db.commit()

    return {
        "mode": "evaluation",
        "score": mapped["percentage"],
        "statut": mapped["method_label_ar"],
        "feedback": mapped["advice"],
        "manquant": [],
        "next_review_date": None,
        "source": "local_rubric",
        "ungraded": False,
        "banner_ar": TRAINING_BANNER_AR,
        "methodology": None,
        "method_percent": mapped["method_percent"],
        "science_status": mapped["science_status"],
    }
