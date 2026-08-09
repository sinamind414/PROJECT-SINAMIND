"""routes/memory.py — Endpoint mémoire FSRS unifié (audit S3).

Expose la vue consolidée de la mémoire FSRS (3 sources : concepts,
verb_chapter, verb_action) via services/fsrs_unified.py — la porte d'entrée
unique pour le dashboard et l'observabilité.

- GET /api/memory/summary : stats consolidées (nb items, dus, avg stability)
- GET /api/memory/due      : items dus (limit param)
"""

from __future__ import annotations

from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession

from database import get_db
from deps import get_current_user
from services.fsrs_unified import get_due_items, memory_summary

router = APIRouter(tags=["Mémoire"])


@router.get("/api/memory/summary")
async def memory_summary_endpoint(
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(get_current_user),
) -> dict:
    """Résumé consolidé de la mémoire FSRS de l'utilisateur."""
    return await memory_summary(db, current_user["id"])


@router.get("/api/memory/due")
async def memory_due_endpoint(
    limit: int = Query(50, ge=1, le=200),
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(get_current_user),
) -> dict:
    """Items dus (prochaine_revision <= maintenant), triés par date."""
    items = await get_due_items(db, current_user["id"], limit=limit)
    return {
        "count": len(items),
        "items": [
            {
                "kind": i.kind,
                "item_id": i.item_id,
                "chapter": i.chapter,
                "stability": i.stability,
                "difficulty": i.difficulty,
                "due": i.due.isoformat() if i.due else None,
                "interval_jours": i.interval_jours,
                "last_score": i.last_score,
                "attempts": i.attempts,
            }
            for i in items
        ],
    }
