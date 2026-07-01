"""Helpers LLM — sanitize et appel avec fallback.


Extrait de chatbot_orchestrator.py pour alléger l'orchestrateur.
"""

import logging
import re

logger = logging.getLogger("khawarizmi.llm_helpers")


def sanitize_response(text: str) -> str:
    """Nettoie la réponse LLM : supprime les mentions de source, IA, fichiers. Tronque à 800 chars."""
    if not text:
        return text

    source_patterns = [
        r"(?i)selon\s+(?:le\s+)?(?:document|livre|fichier|source|manuel|wathi9a|ktab|milaff)\s*[^.]*\.\s*",
        r"(?i)d'après\s+(?:le\s+)?(?:document|livre|fichier|source|manuel|wathi9a|ktab|milaff)\s*[^.]*\.\s*",
        r"(?i)la\s+source\s+(?:indique|dit|mentionne|précise)\s*[^.]*\.\s*",
        r"(?i)le\s+document\s+(?:indique|dit|mentionne|précise)\s*[^.]*\.\s*",
        r"حسب\s+(?:الكتاب|الوثيقة|الملف|المصدر|الدرس|المستند|المنهج|البرنامج|الدليل|الدوسي)\s*[^.]*\.\s*",
        r"وفق\s+(?:الكتاب|الوثيقة|الملف|المصدر|الدرس|المستند|المنهج|البرنامج|الدليل)\s*[^.]*\.\s*",
        r"في\s+(?:الكتاب|الوثيقة|الملف|المصدر|الدرس|المستند|المنهج|البرنامج)\s*[^.]*\.\s*",
        r"(?:من|بناءً على|بناءا على)\s+(?:الكتاب|الوثيقة|الملف|المصدر|الدرس|المستند|المنهج|البرنامج|الدليل)\s*[^.]*\.\s*",
        r"(?:المصدر|الوثيقة|الكتاب|الملف|الدرس|المستند)\s*(?:يقول|تقول|يذكر|تذكر|يشير|تشير|يؤكد|تؤكد|يحدد|يشرح|تشرح|يوضح|توضح|يفسر|تفسر)\s*[^.]*\.\s*",
        r"(?:كما|وكما)\s*(?:ذكر|ورد|جاء|أشار)\s*(?:في|ب)\s*(?:الكتاب|الوثيقة|الملف|المصدر|الدرس|المستند|المنهج|البرنامج|الدليل)\s*[^.]*\.\s*",
    ]
    for pat in source_patterns:
        text = re.sub(pat, "", text)

    ia_patterns = [
        r"(?i)claude\b[^.]*\.\s*",
        r"(?i)openai\b[^.]*\.\s*",
        r"(?i)gemini\b[^.]*\.\s*",
        r"(?i)modèle\s+de\s+langage\b[^.]*\.\s*",
        r"(?i)intelligence\s+artificielle\b[^.]*\.\s*",
        r"(?i)je\s+suis\s+un\s+assistant\s+IA\b[^.]*\.\s*",
        r"(?i)je\s+suis\s+un\s+modèle\b[^.]*\.\s*",
    ]
    for pat in ia_patterns:
        text = re.sub(pat, "", text)

    meta_patterns = [
        r"(?i)je\s+vais\s+(?:analyser|examiner|regarder|consulter)\s*[^.]*\.\s*",
        r"(?i)en\s+analysant\s+(?:le\s+)?contexte\s*[^.]*\.\s*",
        r"(?i)d'après\s+(?:les\s+)?informations\s+(?:fournies|disponibles)\s*[^.]*\.\s*",
    ]
    for pat in meta_patterns:
        text = re.sub(pat, "", text)

    text = re.sub(r"\n{3,}", "\n\n", text).strip()

    if len(text) > 800:
        text = text[:800] + "..."

    return text


async def call_llm(prompt: str, openai_client=None, max_tokens: int = 350) -> str | None:
    """Appelle le LLM avec fallback. Sanitize la réponse avant retour."""
    if not openai_client:
        return None

    try:
        from config import get_settings
        cfg = get_settings()

        try:
            from services.llm import _call_with_fallback
            messages = [
                {"role": "system", "content": prompt},
                {"role": "user", "content": "أجب."},
            ]
            response = await _call_with_fallback(
                messages=messages,
                primary_client=openai_client,
                primary_model=cfg.openai_model,
                temperature=0.7,
                max_tokens=max_tokens,
                timeout=15.0,
            )
            ai_text = (response.choices[0].message.content or "").strip()
            if ai_text:
                return sanitize_response(ai_text)
        except Exception:
            pass

        response = await openai_client.chat.completions.create(
            model=cfg.openai_model,
            messages=[
                {"role": "system", "content": prompt},
                {"role": "user", "content": "أجب."},
            ],
            temperature=0.7,
            max_tokens=max_tokens,
            timeout=15.0,
        )
        return sanitize_response(response.choices[0].message.content.strip())
    except Exception as e:
        logger.error(f"LLM échec : {e}")
        return None
