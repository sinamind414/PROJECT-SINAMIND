"""admin_analytics.py — Dashboard santé méthodologique pour le professeur.

Endpoints :
  GET /api/admin/analytics/global            → performance moyenne par verbe
  GET /api/admin/analytics/methodology-gaps  → distribution des dominant_error_code
  GET /api/admin/analytics/students-at-risk  → élèves < 50 % avec ≥ 3 tentatives
"""

from __future__ import annotations

import logging

from fastapi import APIRouter, Depends
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession

from deps import get_current_user, get_db

logger = logging.getLogger("khawarizmi.admin_analytics")
router = APIRouter(prefix="/api/admin/analytics", tags=["Admin Analytics"])


@router.get("/global")
async def analytics_global(
    current_user: dict = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    rows = await db.execute(
        text("""
            SELECT
                verb_slug,
                ROUND(AVG(percentage))::int AS avg_score,
                COUNT(*) AS total_attempts
            FROM da_answers
            GROUP BY verb_slug
            ORDER BY avg_score ASC
        """)
    )
    verbs = [dict(r._mapping) for r in rows.fetchall()]

    total_row = await db.execute(
        text("""
            SELECT
                ROUND(AVG(percentage))::int AS global_avg,
                COUNT(*) AS total_evaluations,
                COUNT(DISTINCT user_id) AS total_students
            FROM da_answers
        """)
    )
    total = dict(total_row.fetchone()._mapping)

    most_critical = verbs[0] if verbs else None

    return {
        "verbs": verbs,
        "global_avg": total["global_avg"] or 0,
        "total_evaluations": total["total_evaluations"],
        "total_students": total["total_students"],
        "most_critical_verb": most_critical,
    }


@router.get("/methodology-gaps")
async def analytics_methodology_gaps(
    current_user: dict = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    rows = await db.execute(
        text("""
            SELECT
                COALESCE(errors->>0, 'unknown') AS error_type,
                COUNT(*) AS occurrences
            FROM da_answers
            WHERE errors IS NOT NULL AND errors != '[]'::jsonb
            GROUP BY error_type
            ORDER BY occurrences DESC
        """)
    )
    gaps = [dict(r._mapping) for r in rows.fetchall()]
    total = sum(g["occurrences"] for g in gaps)

    insight_ar = ""
    if gaps:
        top = gaps[0]["error_type"]
        if "methodology" in top:
            insight_ar = "تنبيه: تعاني الفئة من صعوبات في البنية المنهجية. راجع المنهجية (Manhadjiya)."
        elif "scientific" in top:
            insight_ar = "تنبيه: المفاهيم العلمية غير مستوعبة. راجع الأمثلة التطبيقية."
        elif "off_topic" in top:
            insight_ar = "تنبيه: الإجابات خارجة عن الموضوع. راجع استخراج الهدف من السياق."

    return {
        "gaps": gaps,
        "total": total,
        "insight_ar": insight_ar,
    }


@router.get("/students-at-risk")
async def analytics_students_at_risk(
    current_user: dict = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    rows = await db.execute(
        text("""
            SELECT
                a.user_id,
                u.prenom,
                ROUND(AVG(a.percentage))::int AS avg_score,
                COUNT(*) AS attempts
            FROM da_answers a
            JOIN users u ON u.id = a.user_id
            GROUP BY a.user_id, u.prenom
            HAVING AVG(a.percentage) < 50 AND COUNT(*) >= 3
            ORDER BY avg_score ASC
        """)
    )
    students = [dict(r._mapping) for r in rows.fetchall()]

    return {"students": students}
