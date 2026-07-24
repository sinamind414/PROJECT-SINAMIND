import logging

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession

from database import get_db
from deps import get_current_user
from schemas.kunz_tunnel import (
    RecallDueItem,
    RecallResultRequest,
    RecallResultResponse,
    TunnelEventRequest,
    TunnelEventResponse,
)
from services.kunz_tunnel_service import (
    TunnelEventIn,
    append_event,
    apply_recall_result,
    list_due_recall,
)

logger = logging.getLogger("khawarizmi.api")
router = APIRouter(tags=["Kunz Tunnel"])


@router.post("/api/lesson/{lesson_id}/event", response_model=TunnelEventResponse)
async def post_lesson_event(
    lesson_id: str,
    body: TunnelEventRequest,
    current_user: dict = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    event_id = await append_event(
        db,
        user_id=current_user["id"],
        lesson_id=lesson_id,
        event=TunnelEventIn(
            session_id=body.session_id,
            event_type=body.type,
            payload=body.payload,
            client_event_id=body.client_event_id,
            client_ts=body.client_ts,
        ),
    )
    logger.info(
        f"Tunnel event: user={current_user['id']} lesson={lesson_id} "
        f"type={body.type} event_id={event_id}"
    )
    return TunnelEventResponse(event_id=event_id)


@router.get("/api/recall/due", response_model=list[RecallDueItem])
async def get_recall_due(
    current_user: dict = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
    limit: int = Query(default=50, ge=1, le=100),
):
    items = await list_due_recall(
        db,
        user_id=current_user["id"],
        limit=limit,
    )
    return [
        RecallDueItem(
            recall_item_id=i.recall_item_id,
            lesson_id=i.lesson_id,
            concept_id=i.concept_id,
            stage=i.stage,
            next_review_at=i.next_review_at,
            last_result=i.last_result,
        )
        for i in items
    ]


@router.post("/api/recall/{recall_item_id}/result", response_model=RecallResultResponse)
async def post_recall_result(
    recall_item_id: str,
    body: RecallResultRequest,
    current_user: dict = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    try:
        updated = await apply_recall_result(
            db,
            user_id=current_user["id"],
            recall_item_id=recall_item_id,
            success=body.success,
        )
    except LookupError:
        raise HTTPException(status_code=404, detail="Recall item not found")

    return RecallResultResponse(
        recall_item_id=updated.recall_item_id,
        stage=updated.stage,
        next_review_at=updated.next_review_at,
        last_result=updated.last_result or "",
    )
