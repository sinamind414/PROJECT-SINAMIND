import logging

from openai import AsyncOpenAI
from sqlalchemy.ext.asyncio import AsyncSession

from config import get_settings
from prompts.free_chat_prompt import build_free_prompt, cards_for_mode
from services.rag_service import rag_search, format_rag_context
from services.llm import _call_with_fallback

logger = logging.getLogger("khawarizmi.free_mode")


def _fallback_response(text: str, mode: str, fallback: bool = False) -> dict:
    return {
        "content": text,
        "mode": "free",
        "lang": "ar",
        "tokens_used": 0,
        "from_cache": False,
        "fallback_active": fallback,
        "cards": cards_for_mode(mode),
    }


def _is_greeting_or_meta(message: str) -> bool:
    """True si c'est une salutation / remerciement / question d'identité,
    PAS une demande de contenu SVT.

    Exception AGENTS.md §3 : les messages de navigation/politesse restent
    autorisés sans RAG ( le LLM sait se présenter / saluer ).
    Une vraie question SVT sans contexte RAG → refus ( consulte le manuel ).
    """
    m = (message or "").lower().strip()
    if not m:
        return False
    meta_triggers = [
        "مرحبا", "السلام عليكم", "اهلا", "أهلا", "صباح الخير", "مساء الخير",
        "شكرا", "شكراً", "مشكور", "بارك الله",
        "من أنت", "من انت", "ما اسمك", "كيف حالك", "عرف بنفسك",
        "hi", "hello", "bonjour", "salut", "merci", "thanks", "qui es",
    ]
    return any(k in m for k in meta_triggers)


async def handle_free_chat(
    body,
    user: dict,
    db: AsyncSession,
    openai_client: AsyncOpenAI,
    cfg,
    tutor=None,
) -> dict:
    message = body.message.strip()
    lang = body.lang or "ar"
    history = body.history or []
    chapter = body.chapitre or None
    mode = body.mode or "quick"

    rag_chunks = await rag_search(db, message, chapter)
    rag_context = format_rag_context(rag_chunks)

    if openai_client is None:
        if rag_chunks:
            excerpt = rag_chunks[0]["content"][:250]
            return _fallback_response(
                f"أنا في وضع احتياطي، لكن وجدت في القاعدة الرسمية ما يلي:\n\n• {excerpt}\n\nاكتب لي أي جزء لم تفهمه.",
                mode, fallback=True,
            )
        return _fallback_response(
            "أنا متاح في وضع احتياطي. خدمة الذكاء الاصطناعي غير مفعلة.",
            mode, fallback=True,
        )

    # P2 — RAG vide → refus ( AGENTS.md §3 : l'IA répond UNIQUEMENT à partir
    # du contexte RAG fourni ). Avant : on appelait le LLM sans contexte cours
    # → l'IA inventait des faits hors manuel ( hallucination ).
    # Exception : salutations / questions d'identité laissées au LLM.
    if not rag_chunks and not _is_greeting_or_meta(message):
        logger.info(f"free | user={user['id']} RAG vide → refus AGENTS.md §3")
        return _fallback_response(
            "لم أجد هذه المعلومة في قاعدة الدروس الرسمية. "
            "راجع الكتاب المدرسي، أو أعد صياغة السؤال بشكل أدق. 📖",
            mode, fallback=True,
        )

    system_prompt = build_free_prompt(lang, rag_context, user_message=message, tutor=(mode == "tutor"))
    messages = [{"role": "system", "content": system_prompt}]

    for h in history[-6:]:
        if isinstance(h, dict) and h.get("role") in ("user", "assistant") and h.get("content"):
            messages.append({"role": h["role"], "content": str(h["content"])[:500]})

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
        tokens = response.usage.total_tokens if response.usage else 0

        # P1 — Garde-fou langue : le chatbot est arabophone. Si la réponse de
        # l'IA ne contient quasi aucun caractère arabe, c'est qu'elle a ignoré
        # la consigne ( Groq/llama répond parfois en français ) → reformulation.
        # Avant : la condition dépendait de lang=="fr", or le frontend envoie
        # TOUJOURS lang="ar" → le garde-fou ne se déclenchait jamais.
        arabic_chars = sum(1 for c in ai_text if "\u0600" <= c <= "\u06ff")
        if ai_text and arabic_chars / len(ai_text) < 0.15:
            ai_text = "عذراً، أُجيب دائماً بالعربية. أعد صياغة سؤالك من فضلك. 🇩🇿"

        try:
            from services.chatbot_engagement_service import record_chat_interaction
            await record_chat_interaction(db, user["id"], message, chapter=chapter, mode=mode)
        except Exception:
            pass

        logger.info(f"free | user={user['id']} chapter={chapter} tokens={tokens}")

        return {
            "content": ai_text,
            "mode": "free",
            "lang": "ar",
            "tokens_used": tokens,
            "from_cache": False,
            "fallback_active": False,
            "cards": cards_for_mode(mode),
        }

    except Exception as e:
        logger.error(f"Erreur free_mode : {e}")
        fallback_text = (
            f"حسب الدرس: {rag_chunks[0]['content'][:200]}...\nماذا تستنتج؟ 💡"
            if rag_chunks
            else "عذراً، أواجه صعوبة. حاول مرة أخرى 🙏"
        )
        return _fallback_response(fallback_text, mode, fallback=True)
