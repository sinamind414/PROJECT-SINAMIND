import logging

from fastapi import APIRouter, Depends, Request
from openai import AsyncOpenAI
from sqlalchemy.ext.asyncio import AsyncSession

from config import get_settings
from deps import get_current_user, get_db, get_openai, get_tutor
from rate_limit import chat_limit, limiter
from schemas.ai_request import ChatOrchestratorRequest
from services.ai_orchestrator import get_orchestrator
from services.khawarizmi_engine import KhawarizmiTutor

logger = logging.getLogger("khawarizmi.ai_chat")
router = APIRouter(tags=["AI Chat"])


@router.post("/api/ai/chat")
@limiter.limit(chat_limit)
async def ai_chat_unified(
    request: Request,
    body: ChatOrchestratorRequest,
    current_user: dict = Depends(get_current_user),
    tutor: KhawarizmiTutor = Depends(get_tutor),
    openai_client: AsyncOpenAI = Depends(get_openai),
    db: AsyncSession = Depends(get_db),
):
    cfg = get_settings()
    return await get_orchestrator().handle_chat(
        body=body, user=current_user, db=db,
        openai_client=openai_client, cfg=cfg, tutor=tutor,
    )


@router.get("/api/ai/chat/health")
async def ai_chat_health():
    return {"status": "ok", "service": "ai_chat"}
