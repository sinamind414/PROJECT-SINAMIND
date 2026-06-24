"""Translation du feedback pédagogique via LLM (Gemini/OpenAI).

Remplace l'ancien dictionnaire de mots-clés par une traduction
contextuelle intelligente qui préserve le sens pédagogique.
"""

import logging

logger = logging.getLogger("khawarizmi.feedback_translator")


def translate_feedback(text_fr: str, lang: str = "ar") -> str:
    """Traduit un feedback du français vers l'arabe via LLM."""
    if not text_fr or lang != "ar":
        return text_fr

    from routes.lifespan import state

    llm = state.openai or state.tutor
    if not llm:
        return text_fr

    try:
        prompt = (
            "Tu es un traducteur pédagogique. Traduis le feedback suivant "
            "du français vers l'arabe académique (arabe standard). "
            "Conserve le ton encourageant et la terminologie scientifique. "
            "Ne réponds QUE par la traduction, sans commentaire.\n\n"
            f"Feedback : {text_fr}"
        )
        if hasattr(llm, "generate_content"):
            resp = llm.generate_content(prompt)
            return resp.text.strip() if hasattr(resp, "text") else text_fr
        elif hasattr(llm, "chat"):
            resp = llm.chat.completions.create(
                model="gpt-4o-mini",
                messages=[{"role": "user", "content": prompt}],
                temperature=0.1,
                max_tokens=500,
            )
            return resp.choices[0].message.content.strip()
        else:
            return text_fr
    except Exception as e:
        logger.warning(f"Translation LLM échouée, fallback texte original : {e}")
        return text_fr
