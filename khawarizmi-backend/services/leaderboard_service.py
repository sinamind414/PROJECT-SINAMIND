"""
Leaderboard Service — classements nationaux, wilaya, lycée, amis.
"""

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from models.user_stats import UserStats

WEIGHTS = {
    "schematic-functional": 3.0,
    "schematic-explanatory": 2.8,
    "summarize-diagram": 2.8,
    "comment": 2.5,
    "criticize": 2.5,
    "describe": 2.5,
    "distinguish": 2.3,
    "classify": 2.3,
    "extract": 2.0,
    "explain": 2.0,
    "determine": 2.0,
    "scientific-text": 1.8,
    "validate-hypothesis": 1.7,
    "discuss": 1.5,
    "hypothesis": 1.5,
    "compare": 1.3,
    "relationship": 1.2,
    "justify": 1.2,
    "interpret": 1.1,
    "define": 1.0,
    "analyse": 1.0,
    "deduce": 1.0,
    "cite": 0.9,
    "name": 0.8,
}


def calc_weighted_score(verb_slug: str, percentage: float) -> float:
    return WEIGHTS.get(verb_slug, 1.0) * (percentage / 100)


async def update_user_stats(db: AsyncSession, user_id: str) -> dict:
    # S3 finale : lecture via la vue consolidée (par-user, mastery-first)
    from services.fsrs_unified import get_user_memory

    memory = await get_user_memory(db, user_id, kinds=("verb_action",))
    rows = [
        {"verb_slug": i.item_id, "stability": i.stability, "attempts": i.attempts}
        for i in memory if i.attempts > 0
    ]

    total_eval = sum(r["attempts"] for r in rows)
    total_correct = sum(int(r["stability"] * r["attempts"]) for r in rows)
    precision = (total_correct / total_eval * 100) if total_eval > 0 else 0.0

    weighted = sum(
        calc_weighted_score(r["verb_slug"], r["stability"] * 100)
        for r in rows
    )

    stats_result = await db.execute(select(UserStats).where(UserStats.user_id == user_id))
    stats = stats_result.scalar_one_or_none()

    if not stats:
        stats = UserStats(user_id=user_id)
        db.add(stats)

    stats.total_evaluations = total_eval
    stats.total_correct = total_correct
    stats.precision_score = round(precision, 2)
    stats.weighted_score = round(weighted, 2)

    await db.commit()
    return {
        "total_evaluations": total_eval,
        "precision_score": round(precision, 2),
        "weighted_score": round(weighted, 2),
    }


async def get_leaderboard(db: AsyncSession, scope: str = "national", wilaya_code: str | None = None, school_name: str | None = None, limit: int = 20) -> list[dict]:
    query = select(UserStats).order_by(UserStats.weighted_score.desc())

    if scope == "wilaya" and wilaya_code:
        query = query.where(UserStats.wilaya_code == wilaya_code)
    elif scope == "school" and school_name:
        query = query.where(UserStats.school_name == school_name)

    query = query.limit(limit)
    result = await db.execute(query)

    return [
        {
            "user_id": str(s.user_id),
            "wilaya_code": s.wilaya_code,
            "school_name": s.school_name,
            "weighted_score": s.weighted_score,
            "precision_score": s.precision_score,
            "total_evaluations": s.total_evaluations,
        }
        for s in result.scalars().all()
    ]


async def get_user_rank(db: AsyncSession, user_id: str, scope: str = "national", wilaya_code: str | None = None) -> int:
    stats_result = await db.execute(select(UserStats).where(UserStats.user_id == user_id))
    stats = stats_result.scalar_one_or_none()
    if not stats:
        return 0

    query = select(func.count(UserStats.id)).where(UserStats.weighted_score > stats.weighted_score)

    if scope == "wilaya" and wilaya_code:
        query = query.where(UserStats.wilaya_code == wilaya_code)

    result = await db.execute(query)
    return (result.scalar() or 0) + 1
