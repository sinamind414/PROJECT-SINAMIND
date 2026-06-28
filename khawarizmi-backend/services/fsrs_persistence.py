import json
import logging
from datetime import UTC, datetime

from fsrs import Card
from sqlalchemy import bindparam, text
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
    """Charge l'état FSRS de chaque concept pour cet utilisateur."""
    states: dict[str, Card] = {}
    if not concept_ids:
        return states

    cids_param = tuple(concept_ids) if len(concept_ids) > 1 else (concept_ids[0],)
    stmt = text(
        "SELECT concept_id, fsrs_state FROM mastery_micro_concepts WHERE user_id = :uid AND concept_id IN :cids"
    ).bindparams(bindparam("cids", expanding=True))

    try:
        res = await db.execute(stmt, {"uid": user_id, "cids": cids_param})
        for row in res.fetchall():
            c_id, fsrs_state_dict = row[0], row[1] or {}
            card = Card()
            if fsrs_state_dict:
                try:
                    card.stability = fsrs_state_dict.get("stability", card.stability)
                    card.difficulty = fsrs_state_dict.get("difficulty", card.difficulty)
                    for attr in ["scheduled_days", "reps", "lapses"]:
                        if hasattr(card, attr) and attr in fsrs_state_dict:
                            setattr(card, attr, fsrs_state_dict[attr])
                except Exception as e:
                    logger.error(f"Erreur hydratation FSRS: {e}")
            states[c_id] = card
    except Exception as e:
        logger.error(f"get_concept_states: {e}")

    for c_id in concept_ids:
        if c_id not in states:
            states[c_id] = Card()

    return states


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

        fsrs_json = json.dumps({
            "stability": new_card.stability,
            "difficulty": new_card.difficulty,
            "scheduled_days": sched_days,
            "reps": getattr(new_card, "reps", 0),
            "lapses": getattr(new_card, "lapses", 0),
            "state": str(new_card.state),
            "last_review": new_card.last_review.isoformat() if new_card.last_review else None,
        })

        is_direct_eval = upd.get("rating_applied") is not None
        forced_reason = upd.get("forced_review_reason")

        if is_direct_eval:
            pending = eval_result.get("needs_l1_review", False)
        else:
            pending = False
            if forced_reason:
                logger.debug(
                    f"FSRS_PROPAGATION | user={user_id} | "
                    f"concept={c_id} | reason={forced_reason}"
                )

        await db.execute(
            text("""
                INSERT INTO mastery_micro_concepts
                    (user_id, concept_id, chapter, due_date,
                     interval_jours, difficulty, stability, fsrs_state, pending_real_evaluation, updated_at)
                VALUES
                    (:user_id, :c_id, :chapter, :due,
                     :interval, :difficulty, :stability, CAST(:fsrs_state AS jsonb), :pending_eval, NOW())
                ON CONFLICT (user_id, concept_id)
                DO UPDATE SET
                    due_date           = EXCLUDED.due_date,
                    interval_jours     = EXCLUDED.interval_jours,
                    difficulty         = EXCLUDED.difficulty,
                    stability          = EXCLUDED.stability,
                    fsrs_state         = EXCLUDED.fsrs_state,
                    pending_real_evaluation = EXCLUDED.pending_real_evaluation,
                    updated_at         = NOW()
            """),
            {
                "user_id": user_id,
                "c_id": c_id,
                "chapter": chapter,
                "due": upd["due"],
                "interval": sched_days,
                "difficulty": new_card.difficulty,
                "stability": new_card.stability,
                "fsrs_state": fsrs_json,
                "pending_eval": pending,
            },
        )

        if c_id == question.get("concept_cle") and is_direct_eval:
            next_review_date = upd["due"].isoformat()

    await db.commit()
    return next_review_date
