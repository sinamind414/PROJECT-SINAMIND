from __future__ import annotations

from datetime import UTC, datetime, timedelta
from typing import Any

from fsrs import Card
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession

from services.scheduler import KhawarizmiScheduler


async def get_progress_snapshot(
    db: AsyncSession,
    user_id: int | str,
    scheduler: KhawarizmiScheduler,
) -> dict[str, Any]:
    result = await db.execute(
        text("""
            SELECT
                mc.matiere,
                mc.chapitre_id,
                mmc.difficulty,
                mmc.stability,
                mmc.prochaine_revision,
                mmc.interval_jours
            FROM mastery_micro_concepts mmc
            JOIN micro_concepts mc ON mc.id = mmc.micro_concept_id
            WHERE mmc.user_id = :user_id
            ORDER BY mc.matiere, mc.chapitre_id
        """),
        {"user_id": user_id},
    )
    rows = result.fetchall()

    concepts: list[dict[str, Any]] = []
    cards_par_matiere: dict[str, list] = {}

    for row in rows:
        matiere, chapitre_id, difficulty, stability, next_rev, interval = row
        card = Card()
        card.stability = stability or 0.0
        card.difficulty = difficulty or 0.0
        cards_par_matiere.setdefault(matiere, []).append(card)
        retrievability = scheduler._get_retrievability(card)
        est_due = next_rev <= datetime.now(UTC) if next_rev else True
        concepts.append(
            {
                "matiere": matiere,
                "chapitre_id": chapitre_id,
                "stability": round(stability or 0.0, 3),
                "difficulty": round(difficulty or 0.0, 3),
                "retrievability": retrievability,
                "prochaine_revision": next_rev.isoformat() if next_rev else None,
                "interval_jours": interval,
                "est_due": est_due,
                "statut_revision": scheduler._review_status_label(next_rev),
                "priority": scheduler._priority_label(stability or 0.0),
            }
        )

    prediction = await scheduler.predire_score_bac(cards_par_matiere)

    return {
        "nb_concepts": len(concepts),
        "dues_aujourd_hui": sum(1 for c in concepts if c["est_due"]),
        "prediction_bac": prediction,
        "concepts": concepts,
    }


async def get_week_activity_snapshot(
    db: AsyncSession,
    user_id: int | str,
) -> dict[str, Any]:
    now = datetime.now(UTC)
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
            "user_id": user_id,
            "week_start": week_start,
            "week_end": week_start + timedelta(days=7),
        },
    )
    rows = result.fetchall()

    days = []
    total_dues = 0
    total_reviewed = 0
    for i in range(7):
        day_date = week_start + timedelta(days=i)
        day_dues = sum(1 for r in rows if r.due_date and r.due_date.date() == day_date.date())
        day_reviewed = sum(1 for r in rows if r.reviewed_at and r.reviewed_at.date() == day_date.date())
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

        days.append(
            {
                "date": day_date.isoformat(),
                "day_index": i,
                "dues_count": day_dues,
                "reviewed_count": day_reviewed,
                "status": status,
                "primary_task": None,
                "primary_chapter": None,
                "load": load,
            }
        )

    return {
        "week_start": week_start.isoformat(),
        "days": days,
        "streak_days": total_dues,
        "total_dues_this_week": total_dues,
        "total_reviewed_this_week": total_reviewed,
    }


async def get_due_cards_snapshot(
    db: AsyncSession,
    user_id: int | str,
) -> dict[str, Any]:
    now = datetime.now(UTC)
    result = await db.execute(
        text("""
            SELECT id, micro_concept_id, concept_id, chapter,
                   difficulty, stability, state, due_date,
                   prochaine_revision, interval_jours
            FROM mastery_micro_concepts
            WHERE user_id = :uid
              AND due_date <= :now
              AND (state IS NULL OR state IN (0, 1))
            ORDER BY due_date ASC, stability ASC
            LIMIT 20
        """),
        {"uid": user_id, "now": now},
    )
    rows = result.fetchall()
    cards = [
        {
            "id": str(r[0]),
            "micro_concept_id": r[1],
            "concept_id": r[2],
            "chapter": r[3],
            "difficulty": r[4],
            "stability": r[5],
            "state": r[6],
            "due_date": r[7].isoformat() if r[7] else None,
            "next_review": r[8].isoformat() if r[8] else None,
            "interval_jours": r[9],
        }
        for r in rows
    ]
    return {"cards": cards, "total": len(cards)}
