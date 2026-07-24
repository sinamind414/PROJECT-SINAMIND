"""
Kunz Tunnel — append-only event log + recall result processor.

ATTENTION — RÈGLE ABSOLUE (P2.3) :
  append_event ne doit JAMAIS créer de recall_items.
  La création recall appartient exclusivement au FE (openRecallGateAndScheduleItem).
  Le BE tunnel est un journal passif ; recall_items est peuplé uniquement
  via un mécanisme externe (P2.3b: POST /api/recall).

  Voir docs/kunz-recall-fe-be.md pour la matrice d'ownership complète.
"""

from __future__ import annotations

import uuid
from dataclasses import dataclass
from datetime import datetime, timedelta, timezone
from typing import Any, Optional, Sequence

from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession

RECALL_DELAY_DAYS = {0: 1, 1: 3, 2: 7, 3: 14}
MAX_STAGE = 3


@dataclass(frozen=True)
class TunnelEventIn:
    session_id: str
    event_type: str
    payload: dict[str, Any]
    client_event_id: Optional[str] = None
    client_ts: Optional[datetime] = None


@dataclass(frozen=True)
class RecallDueDTO:
    recall_item_id: str
    lesson_id: str
    concept_id: Optional[str]
    stage: int
    next_review_at: datetime
    last_result: Optional[str]


async def append_event(
    db: AsyncSession,
    *,
    user_id: int,
    lesson_id: str,
    event: TunnelEventIn,
) -> str:
    if event.client_event_id:
        existing = await db.execute(
            text("""
                SELECT id FROM tunnel_events
                WHERE user_id = :uid AND client_event_id = :ceid
                LIMIT 1
            """),
            {"uid": user_id, "ceid": event.client_event_id},
        )
        row = existing.fetchone()
        if row is not None:
            return row[0]

    event_id = str(uuid.uuid4())
    await db.execute(
        text("""
            INSERT INTO tunnel_events
                (id, user_id, lesson_id, session_id, event_type, payload,
                 client_event_id, client_ts, created_at)
            VALUES
                (:id, :uid, :lid, :sid, :etype, CAST(:payload AS jsonb),
                 :ceid, :cts, NOW())
        """),
        {
            "id": event_id,
            "uid": user_id,
            "lid": lesson_id,
            "sid": event.session_id,
            "etype": event.event_type,
            "payload": event.payload,
            "ceid": event.client_event_id,
            "cts": event.client_ts,
        },
    )
    await db.commit()
    return event_id


async def list_due_recall(
    db: AsyncSession,
    *,
    user_id: int,
    now: Optional[datetime] = None,
    limit: int = 50,
) -> Sequence[RecallDueDTO]:
    now = now or datetime.now(timezone.utc)
    rows = await db.execute(
        text("""
            SELECT id, lesson_id, concept_id, stage, next_review_at, last_result
            FROM recall_items
            WHERE user_id = :uid
              AND (last_result IS NULL OR last_result != 'completed')
              AND next_review_at <= :now
            ORDER BY next_review_at ASC
            LIMIT :lim
        """),
        {"uid": user_id, "now": now, "lim": limit},
    )
    return [
        RecallDueDTO(
            recall_item_id=r[0],
            lesson_id=r[1],
            concept_id=r[2],
            stage=r[3],
            next_review_at=r[4],
            last_result=r[5],
        )
        for r in rows.fetchall()
    ]


async def apply_recall_result(
    db: AsyncSession,
    *,
    user_id: int,
    recall_item_id: str,
    success: bool,
    now: Optional[datetime] = None,
) -> RecallDueDTO:
    now = now or datetime.now(timezone.utc)
    row = await db.execute(
        text("""
            SELECT id, lesson_id, concept_id, stage, next_review_at, last_result
            FROM recall_items
            WHERE id = :rid AND user_id = :uid
            LIMIT 1
        """),
        {"rid": recall_item_id, "uid": user_id},
    )
    item = row.fetchone()
    if item is None:
        raise LookupError("recall_not_found")

    current_stage = int(item[3])
    if success:
        new_stage = min(current_stage + 1, MAX_STAGE)
        last_result = "success"
    else:
        new_stage = 0
        last_result = "fail"

    delay_days = RECALL_DELAY_DAYS.get(new_stage, 1)
    next_review = now + timedelta(days=delay_days)

    await db.execute(
        text("""
            UPDATE recall_items
            SET stage = :stage,
                last_result = :lr,
                next_review_at = :nra,
                updated_at = NOW()
            WHERE id = :rid AND user_id = :uid
        """),
        {
            "rid": recall_item_id,
            "uid": user_id,
            "stage": new_stage,
            "lr": last_result,
            "nra": next_review,
        },
    )
    await db.commit()

    return RecallDueDTO(
        recall_item_id=item[0],
        lesson_id=item[1],
        concept_id=item[2],
        stage=new_stage,
        next_review_at=next_review,
        last_result=last_result,
    )
