import logging

from fsrs import Card
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession

logger = logging.getLogger("khawarizmi.fsrs")


async def get_concept_mapping(db: AsyncSession, question_id: str) -> dict[str, float]:
    """Charge les mappings concept → poids pour une question."""
    res = await db.execute(
        text("SELECT micro_concept AS concept_id, weight FROM question_concept_map WHERE question_id = :qid"),
        {"qid": question_id},
    )
    rows = res.fetchall()
    return {row[0]: row[1] for row in rows}


async def get_concept_states(db: AsyncSession, user_id: int, concept_ids: list[str]) -> dict[str, Card]:
    """Charge l'état FSRS de chaque concept — S3b : délègue à fsrs_unified."""
    from services.fsrs_unified import get_concept_states as _unified

    return await _unified(db, user_id, concept_ids)


async def save_concept_updates(
    db: AsyncSession,
    user_id: int,
    question: dict,
    updates: dict,
    eval_result: dict,
) -> str | None:
    """Persiste les mises à jour FSRS pour tous les concepts d'une question."""
    next_review_date: str | None = None
    chapter = question.get("chapitre_id", "ch_inconnu")

    for c_id, upd in updates.items():
        new_card = upd["card"]
        sched_days = getattr(new_card, "scheduled_days", 0)
        if not sched_days and new_card.due and new_card.last_review:
            sched_days = (new_card.due - new_card.last_review).days

        fsrs_json = {
            "stability": new_card.stability,
            "difficulty": new_card.difficulty,
            "scheduled_days": sched_days,
            "reps": getattr(new_card, "reps", 0),
            "lapses": getattr(new_card, "lapses", 0),
            "state": str(new_card.state),
            "last_review": new_card.last_review.isoformat() if new_card.last_review else None,
        }

        is_direct_eval = upd.get("rating_applied") is not None
        if is_direct_eval:
            pending = eval_result.get("needs_l1_review", False)
        else:
            pending = False
            forced_reason = upd.get("forced_review_reason")
            if forced_reason:
                logger.debug(
                    f"FSRS_PROPAGATION | user={user_id} | "
                    f"concept={c_id} | reason={forced_reason}"
                )

        # S3b : upsert via le service unifié (ON CONFLICT user_id+concept_id)
        from services.fsrs_unified import save_concept_update

        await save_concept_update(
            db, user_id, c_id,
            chapter=question.get("chapitre_id", "ch_inconnu"),
            due=upd["due"],
            interval_jours=sched_days,
            difficulty=new_card.difficulty,
            stability=new_card.stability,
            fsrs_state=fsrs_json,
            pending_eval=pending,
        )

        if c_id == question.get("concept_cle") and is_direct_eval:
            next_review_date = upd["due"].isoformat()

    await db.commit()
    return next_review_date
