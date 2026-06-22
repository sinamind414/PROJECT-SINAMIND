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


@router.get("/api/progress/week", tags=["Progression"])
async def get_week_activity(
    current_user: Dict         = Depends(get_current_user),
    db:           AsyncSession = Depends(get_db),
):
    """Activité réelle de la semaine basée sur FSRS.

    Pour chaque jour de la semaine (7 jours), retourne :
    - dues_count : nombre de concepts dus ce jour
    - reviewed_count : nombre de concepts révisés ce jour
    - status : "done" (tout révisé) | "active" (aujourd'hui) | "missed" (passé non révisé) | "planned" (futur)
    - primary_task : tâche prioritaire du jour (chapitre le plus critique dû)
    - load : intensité de charge (0-3) basée sur dues_count
    """
    now = datetime.now(timezone.utc)
    today = now.date()
    week_start = today - timedelta(days=today.weekday() + 1 if today.weekday() < 6 else 0)  # Dimanche = début

    # Ajuster pour commencer le dimanche (getDay() == 0 en JS)
    days_since_sunday = today.weekday() + 1 if today.weekday() < 6 else 0
    week_start = today - timedelta(days=days_since_sunday)

    days_data = []

    for i in range(7):
        day = week_start + timedelta(days=i)
        day_start = datetime(day.year, day.month, day.day, tzinfo=timezone.utc)
        day_end = day_start + timedelta(days=1)

        # Concepts dus ce jour (due_date entre début et fin du jour)
        dues_result = await db.execute(
            text("""
                SELECT chapter, stability, difficulty
                FROM mastery_micro_concepts
                WHERE user_id = :uid
                  AND due_date >= :day_start
                  AND due_date < :day_end
                ORDER BY stability ASC
            """),
            {"uid": current_user["id"], "day_start": day_start, "day_end": day_end}
        )
        dues_rows = dues_result.fetchall()
        dues_count = len(dues_rows)

        # Concepts révisés ce jour (last_review entre début et fin du jour)
        reviewed_result = await db.execute(
            text("""
                SELECT COUNT(*) FROM mastery_micro_concepts
                WHERE user_id = :uid
                  AND last_review >= :day_start
                  AND last_review < :day_end
            """),
            {"uid": current_user["id"], "day_start": day_start, "day_end": day_end}
        )
        reviewed_count = reviewed_result.fetchone()[0]

        # Déterminer le statut réel
        is_today = day == today
        is_past = day < today
        is_future = day > today

        if is_today:
            status = "active"
        elif is_past:
            # Passé : "done" si tous les dus ont été révisés, sinon "missed"
            if dues_count == 0:
                status = "done"  # Pas de dues = rien à faire = considéré fait
            elif reviewed_count >= dues_count:
                status = "done"
            else:
                status = "missed"
        else:
            status = "planned"

        # Tâche prioritaire : chapitre avec la plus faible stabilité
        primary_task = None
        primary_chapter = None
        if dues_rows:
            primary_chapter = dues_rows[0][0]  # chapter du concept le moins stable
            primary_task = f"راجع: {primary_chapter}"

        # Niveau de charge (0-3)
        if dues_count == 0:
            load = 0
        elif dues_count <= 3:
            load = 1
        elif dues_count <= 7:
            load = 2
        else:
            load = 3

        days_data.append({
            "date": day.isoformat(),
            "day_index": day.weekday(),
            "dues_count": dues_count,
            "reviewed_count": reviewed_count,
            "status": status,
            "primary_task": primary_task,
            "primary_chapter": primary_chapter,
            "load": load,
        })

    # Calculer le streak réel (jours consécutifs "done" jusqu'à aujourd'hui)
    streak = 0
    for d in reversed(days_data):
        if d["status"] == "done":
            streak += 1
        elif d["status"] == "active":
            continue  # Aujourd'hui ne casse pas le streak
        else:
            break

    return {
        "user_id": current_user["id"],
        "week_start": week_start.isoformat(),
        "days": days_data,
        "streak_days": streak,
        "total_dues_this_week": sum(d["dues_count"] for d in days_data),
        "total_reviewed_this_week": sum(d["reviewed_count"] for d in days_data),
    }
