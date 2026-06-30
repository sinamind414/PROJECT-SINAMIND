"""routes/tuteur.py — Endpoint tuteur pédagogique.

POST /api/tuteur
Body : { message, context?: { chapitre?, history?, mode? } }
Auth : JWT Bearer requis

Délègue au chatbot_orchestrator unifié.
Préserve le format TuteurResponse (reponse, type, cartes, etc.).
"""

import logging

from fastapi import APIRouter, Depends, HTTPException, Request
from openai import AsyncOpenAI
from sqlalchemy.ext.asyncio import AsyncSession

from deps import get_current_user, get_openai_optional
from database import get_db
from rate_limit import chat_limit, limiter
from services.chatbot_orchestrator import handle_chatbot_message

logger = logging.getLogger("khawarizmi.tuteur")
router = APIRouter()


@router.post("/api/tuteur")
@limiter.limit(chat_limit)
async def tuteur(
    request: Request,
    body: dict,
    current_user: dict = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
    openai_client: AsyncOpenAI | None = Depends(get_openai_optional),
):
    message = (body.get("message") or "").strip()
    if not message:
        raise HTTPException(400, "Le champ 'message' est requis")

    context_raw = body.get("context") or {}
    context = {
        "chapitre": context_raw.get("chapitre") if isinstance(context_raw, dict) else None,
        "history": context_raw.get("history", []) if isinstance(context_raw, dict) else [],
        "mode": body.get("mode", "quick"),
    }

    # Déléguer à l'orchestrateur unifié
    result = await handle_chatbot_message(
        message=message,
        context=context,
        user_id=str(current_user["id"]),
        db=db,
        openai_client=openai_client,
        mode=context.get("mode", "quick"),
    )

    # Retourner le format TuteurResponse complet
    return {
        "reponse": result.get("reponse", ""),
        "type": result.get("type", "socratique"),
        "cartes": result.get("cartes", []),
        "flashcards_suggerees": result.get("flashcards_suggerees", []),
        "fallback_active": result.get("fallback_active", False),
        "source_rag": result.get("source_rag"),
        "sources": result.get("sources", []),
        "question_suivante": result.get("question_suivante"),
        "redirect": result.get("redirect"),
        "tokens_utilises": result.get("tokens_used", 0),
        "from_cache": result.get("from_cache", False),
        "due_concept": result.get("due_concept"),
        "due_chapter": result.get("due_chapter"),
        "lang": "ar",
    }
