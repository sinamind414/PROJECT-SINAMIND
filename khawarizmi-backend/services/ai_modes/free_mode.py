"""Free Mode — wrapper mince qui délègue au chatbot orchestrator.

Préserve la signature handle_free_chat pour backward compatibility.
Les routes existantes qui importent ce module continuent de fonctionner.
"""

import logging

from openai import AsyncOpenAI
from sqlalchemy.ext.asyncio import AsyncSession

from services.chatbot_orchestrator import handle_chatbot_message

logger = logging.getLogger("khawarizmi.free_mode")


async def handle_free_chat(
    body,
    user: dict,
    db: AsyncSession,
    openai_client: AsyncOpenAI | None,
    cfg,
    tutor=None,
) -> dict:
    """Délègue au chatbot orchestrator unifié.

    Signature préservée pour backward compat.
    """
    message = body.message.strip() if hasattr(body, "message") else body.get("message", "")
    context = {
        "chapitre": body.chapitre.strip() if hasattr(body, "chapitre") and body.chapitre else None,
        "history": body.history if hasattr(body, "history") else body.get("history", []),
    }
    mode = body.mode if hasattr(body, "mode") else body.get("mode", "quick")

    result = await handle_chatbot_message(
        message=message,
        context=context,
        user_id=str(user["id"]),
        db=db,
        openai_client=openai_client,
        mode=mode,
    )

    # Mapper au format legacy free_mode
    return {
        "content": result.get("reponse", ""),
        "mode": mode,
        "lang": "ar",
        "tokens_used": result.get("tokens_used", 0),
        "from_cache": result.get("from_cache", False),
        "fallback_active": result.get("fallback_active", False),
        "cards": result.get("cartes", []),
    }
