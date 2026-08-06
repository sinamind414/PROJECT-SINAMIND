"""
routes/chatbot.py — Endpoint dédié pour le chatbot v2 (Q&A libre).

POST /api/chatbot/ask
POST /api/chatbot/ask/stream  (SSE : meta → token* → cartes → sources → done)
Body : { message, history?, lang?, chapitre?, mode? }
Auth : JWT Bearer requis

Délègue au chatbot_orchestrator unifié.
Maintient les endpoints legacy (state, feedback, daily-mission, etc.)
"""

import asyncio
import json
import logging

from fastapi import APIRouter, Depends, HTTPException, Request
from fastapi.responses import StreamingResponse
from openai import AsyncOpenAI
from sqlalchemy.ext.asyncio import AsyncSession

from cache import get_cache, make_cache_key, set_cache
from database import get_db
from deps import get_current_user, get_openai_optional
from rate_limit import chat_limit, limiter
from services.chatbot_orchestrator import handle_chatbot_message

logger = logging.getLogger("khawarizmi.chatbot")
router = APIRouter(prefix="/api/chatbot", tags=["Chatbot"])


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
            {"titre": "اشرح لي بسرعة", "raison": "فهم مباشر دون إطالة", "action": "اشرح الفكرة الأساسية فقط", "bouton": "⚡ سريع"},
            {"titre": "أعطني الأهم للبكالوريا", "raison": "تركيز على النقاط التي تربحك العلامة", "action": "ما المهم في البكالوريا هنا؟", "bouton": "🎯 BAC"},
        ],
        "tutor": [
            {"titre": "شرح خطوة بخطوة", "raison": "تعليم تدريجي حتى الفهم", "action": "اشرح لي خطوة بخطوة", "bouton": "📚 شرح"},
            {"titre": "ساعدني بدون الجواب", "raison": "توجيه سقراطي ذكي", "action": "ساعدني بدون أن تعطيني الجواب", "bouton": "🧠 فكر"},
        ],
        "bac": [
            {"titre": "ماذا ينتظر المصحح؟", "raison": "فهم المطلوب في صيغة البكالوريا", "action": "ماذا ينتظر المصحح في هذا السؤال؟", "bouton": "📝 مصحح"},
            {"titre": "أين أخطئ عادة؟", "raison": "تجنب الأخطاء الشائعة", "action": "ما هي الأخطاء الشائعة هنا؟", "bouton": "⚠️ أخطاء"},
        ],
    }
    return cards.get(mode, cards["quick"])


def _mode_instruction(mode: str) -> str:
    if mode == "tutor":
        return "أجب كمدرس شخصي: قصير، تدريجي، وادفع التلميذ إلى الفهم خطوة بخطوة."
    if mode == "bac":
        return "أجب بصيغة موجهة للبكالوريا: ركز على المطلوب، المنهجية، والنقطة التي تربح العلامة."
    return "أجب بسرعة ووضوح: الفكرة الأساسية أولاً ثم أهم نقطة تطبيقية."


# ── Endpoint principal ────────────────────────────


async def _resolve_ask(
    body: dict,
    current_user: dict,
    db: AsyncSession,
    openai_client: AsyncOpenAI | None,
) -> tuple[dict, str | None]:
    """Logique commune à /ask et /ask/stream.

    Retourne (response_data, cache_key) — le cache_key permet de stocker
    la réponse après succès (et de servir le cache sur /ask et /ask/stream).
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

    cache_key = make_cache_key("chatbot", lang, mode, chapter or "-", message.strip().lower())
    cached = await get_cache(cache_key)
    if cached:
        try:
            payload = json.loads(cached)
            payload["from_cache"] = True
            return payload, cache_key
        except json.JSONDecodeError:
            pass

    context = {
        "chapitre": chapter,
        "history": history,
        "mode": mode,
    }

    result = await handle_chatbot_message(
        message=message,
        context=context,
        user_id=str(current_user["id"]),
        db=db,
        openai_client=openai_client,
        mode=mode,
    )

    response_data = {
        "response": result.get("reponse", ""),
        "lang": "ar",
        "tokens_utilises": result.get("tokens_used", 0),
        "from_cache": result.get("from_cache", False),
        "fallback_active": result.get("fallback_active", False),
        "cartes": result.get("cartes", []),
        "sources": result.get("sources", []),
        "source_rag": result.get("source_rag"),
        "type": result.get("type", "socratique"),
        "question_suivante": result.get("question_suivante"),
        "flashcards_suggerees": result.get("flashcards_suggerees", []),
    }

    try:
        await set_cache(cache_key, json.dumps(response_data, ensure_ascii=False), ttl=900)
    except Exception:
        pass

    return response_data, cache_key


def _sse(event: str, data: dict) -> str:
    """Sérialise un événement SSE (contrat frontend : `event:` + `data:` + \\n\\n)."""
    return f"event: {event}\ndata: {json.dumps(data, ensure_ascii=False)}\n\n"


def _tokenize_stream(text: str, chunk_size: int = 40) -> list[str]:
    """Découpe la réponse en chunks lisibles (limites de mots) pour l'effet streaming."""
    if not text:
        return []
    words = text.split(" ")
    chunks: list[str] = []
    current = ""
    for w in words:
        candidate = (current + " " + w).strip()
        if len(candidate) > chunk_size and current:
            chunks.append(current)
            current = w
        else:
            current = candidate
    if current:
        chunks.append(current)
    return chunks


async def _stream_events(
    response_data: dict,
) -> object:
    """Générateur SSE : meta → token* → cartes → sources → done."""
    yield _sse("meta", {
        "waiting": False,
        "mode": response_data.get("type", "quick"),
        "chapitre": response_data.get("source_rag"),
    })

    text = response_data.get("response", "")
    for chunk in _tokenize_stream(text):
        yield _sse("token", {"d": chunk})
        await asyncio.sleep(0.015)

    cartes = response_data.get("cartes", [])
    if cartes:
        yield _sse("cartes", {"cartes": cartes})

    sources = response_data.get("sources", [])
    yield _sse("sources", {
        "sources": sources,
        "rag_found": bool(sources),
    })

    yield _sse("done", {
        "text": text,
        "fallback": bool(response_data.get("fallback_active", False)),
    })


@router.post("/ask")
@limiter.limit(chat_limit)
async def ask_chatbot(
    request: Request,
    body: dict,
    current_user: dict = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
    openai_client: AsyncOpenAI | None = Depends(get_openai_optional),
):
    response_data, _ = await _resolve_ask(body, current_user, db, openai_client)
    return response_data


@router.post("/ask/stream")
@limiter.limit(chat_limit)
async def ask_chatbot_stream(
    request: Request,
    body: dict,
    current_user: dict = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
    openai_client: AsyncOpenAI | None = Depends(get_openai_optional),
):
    """Version SSE du chatbot (contrat frontend : meta/token/cartes/sources/done)."""
    try:
        response_data, _ = await _resolve_ask(body, current_user, db, openai_client)
    except HTTPException as exc:
        return StreamingResponse(
            iter([_sse("error", {
                "message_fr": exc.detail,
                "message_ar": "تعذر الاتصال بالمدرس.",
            })]),
            media_type="text/event-stream",
            headers={"Cache-Control": "no-cache", "X-Accel-Buffering": "no"},
        )
    except Exception as exc:  # pragma: no cover — filet de sécurité
        logger.exception("ask_stream_failed")
        return StreamingResponse(
            iter([_sse("error", {
                "message_fr": "Erreur technique du tuteur.",
                "message_ar": "حدث خطأ تقني في المدرس.",
            })]),
            media_type="text/event-stream",
            headers={"Cache-Control": "no-cache", "X-Accel-Buffering": "no"},
        )

    return StreamingResponse(
        _stream_events(response_data),
        media_type="text/event-stream",
        headers={"Cache-Control": "no-cache", "X-Accel-Buffering": "no"},
    )


@router.get("/health")
async def chatbot_health():
    """Endpoint de santé pour le chatbot (pas d'auth requise)."""
    return {"status": "ok", "service": "chatbot-v2"}
