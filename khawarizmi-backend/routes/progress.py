import logging
from datetime import datetime, timezone, timedelta
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


@router.get("/api/week-activity", tags=["Progression"])
async def get_week_activity(
    current_user: Dict         = Depends(get_current_user),
    db:           AsyncSession = Depends(get_db),
):
    now = datetime.now(timezone.utc)
    week_start = now - timedelta(days=now.weekday())
    week_start = week_start.replace(hour=0, minute=0, second=0, microsecond=0)

    result = await db.execute(
        text("""
            SELECT
                mmc.prochaine_revision as due_date,
                mmc.last_review as reviewed_at
            FROM mastery_micro_concepts mmc
            WHERE mmc.user_id = :user_id
              AND mmc.prochaine_revision >= :week_start
              AND mmc.prochaine_revision < :week_end
        """),
        {
            "user_id": current_user["id"],
            "week_start": week_start,
            "week_end": week_start + timedelta(days=7),
        }
    )
    rows = result.fetchall()

    days = []
    total_dues = 0
    total_reviewed = 0
    for i in range(7):
        day_date = week_start + timedelta(days=i)
        day_dues = sum(1 for r in rows if r.due_date and r.due_date.date() == day_date.date())
        day_reviewed = sum(1 for r in rows if r.reviewed_at and r.reviewed_at.date() == day_date.date())  # noqa
        total_dues += day_dues
        total_reviewed += day_reviewed

        today = now.date()
        if day_date.date() == today:
            status = "active"
        elif day_date.date() < today:
            status = "done" if day_reviewed >= day_dues else "missed"
        else:
            status = "planned"

        load = 0
        if day_dues > 10:
            load = 3
        elif day_dues > 5:
            load = 2
        elif day_dues > 0:
            load = 1

        days.append({
            "date": day_date.isoformat(),
            "day_index": i,
            "dues_count": day_dues,
            "reviewed_count": day_reviewed,
            "status": status,
            "primary_task": None,
            "primary_chapter": None,
            "load": load,
        })

    return {
        "user_id": current_user["id"],
        "week_start": week_start.isoformat(),
        "days": days,
        "streak_days": total_dues,
        "total_dues_this_week": total_dues,
        "total_reviewed_this_week": total_reviewed,
    }
