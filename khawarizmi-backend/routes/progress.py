import logging
from datetime import datetime, timezone
from typing import Dict, List
from fastapi import APIRouter, Depends
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession
from deps import get_current_user, get_db, get_scheduler
from fsrs import Card

logger = logging.getLogger("khawarizmi.api")
router = APIRouter()


@router.get("/api/progress", tags=["Progression"])
async def get_progression(
    current_user: Dict         = Depends(get_current_user),
    db:           AsyncSession = Depends(get_db),
):
    result = await db.execute(
        text("""
            SELECT
                mc.matiere,
                mc.chapitre_id,
                mmc.difficulty,
                mmc.stability,
                mmc.fsrs_state,
                mmc.prochaine_revision,
                mmc.interval_jours
            FROM mastery_micro_concepts mmc
            JOIN micro_concepts mc ON mc.id = mmc.micro_concept_id
            WHERE mmc.user_id = :user_id
            ORDER BY mc.matiere, mc.chapitre_id
        """),
        {"user_id": current_user["id"]}
    )
    rows = result.fetchall()

    if not rows:
        return {
            "message":   "Aucune progression enregistrée",
            "concepts":  [],
            "prediction_bac": None,
        }

    scheduler = get_scheduler()
    cards_par_matiere: Dict[str, List] = {}

    concepts = []
    for row in rows:
        matiere, chapitre_id, difficulty, stability, fsrs_state_json, next_rev, interval = row

        card = Card()
        card.stability  = stability  or 0.0
        card.difficulty = difficulty or 0.0

        cards_par_matiere.setdefault(matiere, []).append(card)
        retrievability = scheduler._get_retrievability(card)

        concepts.append({
            "matiere":           matiere,
            "chapitre_id":       chapitre_id,
            "stability":         round(stability or 0.0, 3),
            "difficulty":        round(difficulty or 0.0, 3),
            "retrievability":    retrievability,
            "prochaine_revision": next_rev.isoformat() if next_rev else None,
            "interval_jours":    interval,
            "est_due":           next_rev <= datetime.now(timezone.utc) if next_rev else True,
        })

    prediction = scheduler.predire_score_bac(cards_par_matiere)
    dues_auj = sum(1 for c in concepts if c["est_due"])

    return {
        "user_id":          current_user["id"],
        "nb_concepts":      len(concepts),
        "dues_aujourd_hui": dues_auj,
        "prediction_bac":   prediction,
        "concepts":         concepts,
    }
