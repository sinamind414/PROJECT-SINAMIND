import logging

from fastapi import APIRouter, Depends, HTTPException, Request
from openai import AsyncOpenAI

from config import get_settings
from deps import get_current_user, get_openai
from rate_limit import chat_limit, limiter

logger = logging.getLogger("khawarizmi.tuteur")
router = APIRouter()

SYSTEM_PROMPT = """أنت "الأستاذ خوارزمي"، أستاذ SVT للبكالوريا الجزائرية.

قواعد صارمة:
- الرد بالعربية فقط
- أسلوب تربوي +
- استخدم أمثلة من الحياة اليومية
- أسلوب السقراطي (اسأل الطالب بدل إعطاء الإجابة مباشرة)
- ابق ضمن SVT فقط"""


@router.post("/api/tuteur")
@limiter.limit(chat_limit)
async def tuteur(
    request: Request,
    body: dict,
    current_user: dict = Depends(get_current_user),
    openai_client: AsyncOpenAI = Depends(get_openai),
):
    message = (body.get("message") or "").strip()
    if not message:
        raise HTTPException(400, "Le champ 'message' est requis")

    context = body.get("context") or {}
    history = context.get("history", []) if isinstance(context, dict) else []

    if message == "__init__":
        return {
            "reponse": "مرحبا بك يا طالب البكالوريا! كيف يمكنني مساعدتك اليوم في مادة SVT؟ 😊",
            "type": "orientation",
            "cartes": [
                {"titre": "شرح مفهوم", "raison": "فهم أفضل للدرس", "action": "اطلب شرح أي مفهوم في SVT", "bouton": "📖 شرح"},
                {"titre": "حل تمرين", "raison": "تطبيق مباشر", "action": "حل تمارين البكالوريا", "bouton": "✍️ تمرين"},
            ],
            "flashcards_suggerees": [],
            "fallback_active": False,
        }

    try:
        messages = [{"role": "system", "content": SYSTEM_PROMPT}]
        for h in (history or [])[-6:]:
            if isinstance(h, dict) and h.get("role") in ("user", "assistant") and h.get("content"):
                messages.append({"role": h["role"], "content": str(h["content"])[:500]})
        messages.append({"role": "user", "content": message[:1000]})

        cfg = get_settings()
        response = await openai_client.chat.completions.create(
            model=cfg.openai_model,
            messages=messages,
            temperature=0.5,
            max_tokens=600,
            timeout=30.0,
        )
        ai_text = (response.choices[0].message.content or "").strip()
        tokens_used = response.usage.total_tokens if response.usage else 0

        return {
            "reponse": ai_text,
            "type": "socratique",
            "cartes": [],
            "flashcards_suggerees": [],
            "fallback_active": False,
            "source_rag": None,
            "tokens_utilises": tokens_used,
        }

    except Exception as e:
        logger.error(f"Erreur tuteur: {e}")
        return {
            "reponse": "عذراً، أواجه صعوبة في الاتصال حالياً. حاول مرة أخرى 🙏",
            "type": "refus",
            "cartes": [],
            "flashcards_suggerees": [],
            "fallback_active": True,
        }
