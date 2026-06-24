"""
routes/chatbot.py - Endpoint dédié pour le chatbot v2 (Q&A libre).

POST /api/chatbot/ask
Body : { message: str, history?: [{role, content}], lang?: "fr"|"ar" }
Auth : JWT Bearer requis
Réponse : { response: str, sources?: [], from_cache: false }
"""
import json
import logging
from typing import Dict, List, Optional
from fastapi import APIRouter, Depends, HTTPException, Request
from openai import AsyncOpenAI

from config import get_settings
from deps import get_current_user, get_openai
from rate_limit import limiter, chat_limit

logger = logging.getLogger("khawarizmi.chatbot")
router = APIRouter(prefix="/api/chatbot", tags=["Chatbot"])


SYSTEM_PROMPT_AR = """أنت "الأستاذ خوارزمي"، أستاذ ذكي لمادة علوم الطبيعة والحياة (SVT) في البكالوريا الجزائرية.

🎯 **دورك**:
- الإجابة بالعربية فقط (لا فرنسية، لا إنجليزية)
- الإجابة على أسئلة SVT فقط (إذا كان السؤال خارج النطاق، قل: "عذراً، أنا أستاذ علوم الحياة فقط")
- استخدام أسلوب علمي بسيط + أمثلة من الحياة اليومية
- ذكر المفهوم، التعريف، الآلية، مثال، استنتاج

📚 **التنسيق**:
- استخدم emoji لتسهيل القراءة
- استخدم نقاط (•) للقوائم
- استخدم **bold** للمفاهيم المهمة
- اجعل الإجابة مختصرة (300-500 كلمة)

⚠️ **لا تستعمل**:
- لا معلومات بدون source
- لا تخرج عن نطاق SVT
- لا ترد على أسئلة رياضيات، فيزياء، فلسفة، تاريخ، إلخ."""

SYSTEM_PROMPT_FR = """Tu es "Professeur Khawarizmi", assistant intelligent pour la matière SVT du Baccalauréat algérien.

🎯 **Ton rôle**:
- Répondre en ARABE uniquement (même si la question est en français)
- Répondre aux questions SVT uniquement (sinon: "عذراً، أنا أستاذ علوم الحياة فقط")
- Utiliser un style scientifique simple + exemples du quotidien
- Mentionner : concept, définition, mécanisme, exemple, conclusion

📚 **Format**:
- Utiliser des emojis pour faciliter la lecture
- Utiliser des puces (•) pour les listes
- **bold** pour les concepts importants
- Réponse concise (300-500 mots)"""


@router.post("/ask")
@limiter.limit(chat_limit)
async def ask_chatbot(
    request: Request,
    body: Dict,
    current_user: Dict = Depends(get_current_user),
    openai_client: AsyncOpenAI = Depends(get_openai),
):
    """
    Réponse libre à une question SVT en arabe.
    Body :
      - message: str (question de l'utilisateur)
      - history?: list[{role, content}] (historique de conversation)
      - lang?: "fr" | "ar" (défaut: "ar")
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

    cfg = get_settings()
    system_prompt = SYSTEM_PROMPT_AR if lang == "ar" else SYSTEM_PROMPT_FR

    # Construire les messages
    messages = [{"role": "system", "content": system_prompt}]
    # Limiter l'historique aux 6 derniers échanges (économie de tokens)
    for h in history[-6:]:
        if isinstance(h, dict) and h.get("role") in ("user", "assistant") and h.get("content"):
            messages.append({"role": h["role"], "content": h["content"][:500]})
    messages.append({"role": "user", "content": message[:1000]})  # limite message

    try:
        response = await openai_client.chat.completions.create(
            model=cfg.openai_model,
            messages=messages,
            temperature=0.7,
            max_tokens=800,
            timeout=30.0,
        )
        ai_text = (response.choices[0].message.content or "").strip()
        tokens_used = response.usage.total_tokens if response.usage else 0

        # Garantir que la réponse est en arabe (même si query en FR)
        if lang == "fr" and not any("\u0600" <= c <= "\u06FF" for c in ai_text[:50]):
            # Pas d'arabe → forcer
            ai_text = "عذراً، أعد صياغة سؤالك بالعربية من فضلك. 🇩🇿"

        return {
            "response": ai_text,
            "lang": "ar",
            "tokens_utilises": tokens_used,
            "from_cache": False,
        }

    except Exception as e:
        logger.error(f"Erreur chatbot : {e}")
        # Fallback : message de sécurité en arabe
        return {
            "response": "عذراً، أواجه صعوبة في الاتصال حالياً. حاول مرة أخرى بعد قليل 🙏",
            "lang": "ar",
            "tokens_utilises": 0,
            "from_cache": False,
            "error": str(e),
        }


@router.get("/health")
async def chatbot_health():
    """Endpoint de santé pour le chatbot (pas d'auth requise)."""
    return {"status": "ok", "service": "chatbot-v2"}
