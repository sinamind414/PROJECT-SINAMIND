"""
routes/chatbot.py - Endpoint dédié pour le chatbot v2 (Q&A libre).

POST /api/chatbot/ask
Body : { message: str, history?: [{role, content}], lang?: "fr"|"ar", chapitre?: str }
Auth : JWT Bearer requis
Réponse : { response: str, sources?: [], source_rag?: str, from_cache: false }
"""

import logging

from fastapi import APIRouter, Depends, HTTPException, Request
from openai import AsyncOpenAI
from sqlalchemy.ext.asyncio import AsyncSession

from config import get_settings
from database import get_db
from deps import get_current_user, get_openai_optional
from rate_limit import chat_limit, limiter
from services.llm import _call_with_fallback

logger = logging.getLogger("khawarizmi.chatbot")
router = APIRouter(prefix="/api/chatbot", tags=["Chatbot"])


from prompts.free_chat_prompt import SYSTEM_PROMPT_AR, SYSTEM_PROMPT_FR


from services.rag_service import format_rag_context, rag_search, source_cards


# ── Helpers ─────────────────────────────────────


def _response(
    reponse: str,
    type_: str = "socratique",
    fallback: bool = False,
    cartes: list | None = None,
    sources: list | None = None,
    source_rag: str | None = None,
) -> dict:
    return {
        "response": reponse,
        "lang": "ar",
        "tokens_utilises": 0,
        "from_cache": False,
        "fallback_active": fallback,
        "cartes": cartes or [],
        "sources": sources or [],
        "source_rag": source_rag,
    }


def _cards_for_mode(mode: str) -> list[dict]:
    cards = {
        "quick": [
            {"titre": "شرح مفهوم", "raison": "فهم أفضل للدرس", "action": "اطلب شرح أي مفهوم في SVT", "bouton": "📖 شرح"},
            {"titre": "حل تمرين", "raison": "تطبيق مباشر", "action": "حل تمارين البكالوريا", "bouton": "✍️ تمرين"},
        ],
        "tutor": [
            {"titre": "شرح خطوة بخطوة", "raison": "تعليم تدريجي", "action": "اطلب شرح المفهوم بالتفصيل", "bouton": "📚 شرح"},
            {"titre": "سؤال تفاعلي", "raison": "تقييم الفهم", "action": "اسألني سؤالاً", "bouton": "❓ سؤال"},
        ],
    }
    return cards.get(mode, cards["quick"])


# ── Endpoint ─────────────────────────────────────


@router.post("/ask")
@limiter.limit(chat_limit)
async def ask_chatbot(
    request: Request,
    body: dict,
    current_user: dict = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
    openai_client: AsyncOpenAI | None = Depends(get_openai_optional),
):
    """
    Réponse libre à une question SVT en arabe.
    Body :
      - message: str (question de l'utilisateur)
      - history?: list[{role, content}] (historique de conversation)
      - lang?: "fr" | "ar" (défaut: "ar")
      - chapitre?: str (chapitre optionnel pour filtrer le RAG)
      - mode?: "quick" | "tutor" (défaut: "quick")
    """
    message = body.get("message", "").strip()
    if not message:
        raise HTTPException(status_code=400, detail="Le champ 'message' est requis")

    lang = body.get("lang", "ar")
    if lang not in ("fr", "ar"):
        lang = "ar"

    history = body.get("history", []) or []
    if not isinstance(history, list):
        history = []

    chapter = body.get("chapitre") or None
    mode = body.get("mode", "quick")

    cfg = get_settings()
    system_prompt = SYSTEM_PROMPT_AR if lang == "ar" else SYSTEM_PROMPT_FR

    rag_chunks = await rag_search(db, message, chapter)
    rag_context = format_rag_context(rag_chunks)
    sources = source_cards(rag_chunks)
    source_rag = rag_chunks[0]["source"] if rag_chunks else None

    if openai_client is None:
        if rag_chunks:
            excerpt = rag_chunks[0]["content"][:250]
            return _response(
                f"أنا في وضع احتياطي، لكن وجدت في القاعدة الرسمية ما يلي:\n\n• {excerpt}\n\nاكتب لي أي جزء لم تفهمه وسأبسطه خطوة بخطوة.",
                type_="orientation",
                fallback=True,
                cartes=_cards_for_mode(mode),
                sources=sources,
                source_rag=source_rag,
            )
        return _response(
            "أنا متاح الآن في وضع احتياطي. اكتب المفهوم الذي تريد فهمه وسأرشدك بخطوات قصيرة، لكن خدمة الذكاء الاصطناعي غير مفعلة حالياً.",
            type_="orientation",
            fallback=True,
            cartes=_cards_for_mode(mode),
            sources=sources,
            source_rag=source_rag,
        )

    # Injecter le contexte RAG dans le prompt système
    messages = [{"role": "system", "content": system_prompt}]
    if rag_context:
        messages.append({
            "role": "system",
            "content": f"Contexte du manuel officiel :\n{rag_context}",
        })

    # Limiter l'historique aux 6 derniers échanges (économie de tokens)
    for h in history[-6:]:
        if isinstance(h, dict) and h.get("role") in ("user", "assistant") and h.get("content"):
            messages.append({"role": h["role"], "content": h["content"][:500]})
    messages.append({"role": "user", "content": message[:1000]})

    try:
        response = await _call_with_fallback(
            messages=messages,
            primary_client=openai_client,
            primary_model=cfg.openai_model,
            temperature=0.7,
            max_tokens=800,
            timeout=30.0,
        )
        ai_text = (response.choices[0].message.content or "").strip()
        tokens_used = response.usage.total_tokens if response.usage else 0

        if lang == "fr" and not any("\u0600" <= c <= "\u06ff" for c in ai_text[:50]):
            ai_text = "عذراً، أعد صياغة سؤالك بالعربية من فضلك. 🇩🇿"

        # Enregistrer l'interaction (non bloquant)
        try:
            from services.chatbot_engagement_service import record_chat_interaction
            await record_chat_interaction(
                db, current_user["id"], message,
                chapter=chapter, mode=mode,
            )
        except Exception:
            logger.warning("Échec record_chat_interaction (non bloquant)")

        return {
            "response": ai_text,
            "lang": "ar",
            "tokens_utilises": tokens_used,
            "from_cache": False,
            "fallback_active": False,
            "cartes": _cards_for_mode(mode),
            "sources": sources,
            "source_rag": source_rag,
        }

    except Exception as e:
        logger.error(f"Erreur chatbot : {e}")
        if rag_chunks:
            fallback_text = (
                f"حسب الدرس: {rag_chunks[0]['content'][:200]}...\n"
                "ماذا تستنتج من هذا؟ 💡"
            )
        else:
            fallback_text = "عذراً، أواجه صعوبة في الاتصال حالياً. حاول مرة أخرى بعد قليل 🙏"

        return {
            "response": fallback_text,
            "lang": "ar",
            "tokens_utilises": 0,
            "from_cache": False,
            "fallback_active": True,
            "cartes": _cards_for_mode(mode),
            "sources": sources,
            "source_rag": source_rag,
        }


@router.get("/health")
async def chatbot_health():
    """Endpoint de santé pour le chatbot (pas d'auth requise)."""
    return {"status": "ok", "service": "chatbot-v2"}
