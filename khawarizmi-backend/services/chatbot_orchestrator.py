"""services/chatbot_orchestrator.py — Dispatcher du chatbot unifié (audit S2.2).

La logique métier vit dans services/chatbot_handlers.py (handlers async purs
et testables). Ce module classe le message et DISPATCHE vers le handler
approprié — l'ORDRE critique est conservé :
    refus/triche AVANT méthodologie/leçon (audit P0-4.4).

Point d'entrée public inchangé : handle_chatbot_message(message, context,
user_id, db, openai_client, mode).
"""

from __future__ import annotations

import logging

from sqlalchemy.ext.asyncio import AsyncSession

from services.chat_classifier import classify
from services.chatbot_handlers import (
    handle_default_explanation,
    handle_feedback,
    handle_illusion,
    handle_lesson,
    handle_methodology,
    handle_motivation,
    handle_navigation,
    handle_orientation,
    handle_procrastination,
    handle_refus,
    handle_smart_goal,
)
from services.metrics import MetricsCollector

logger = logging.getLogger("khawarizmi.chatbot_orchestrator")


async def handle_chatbot_message(
    message: str,
    context: dict,
    user_id: str | int,
    db: AsyncSession,
    openai_client=None,
    mode: str = "quick",
) -> dict:
    """Pipeline complet du chatbot unifié (dispatcher).

    Args:
        message: texte de l'élève (ou __init__)
        context: contexte (chapitre, fsrs, history, etc.)
        user_id: ID de l'élève
        db: session DB
        openai_client: client OpenAI/Gemini (optionnel)
        mode: "quick" | "tutor" | "bac"

    Returns:
        Dict aligné sur TuteurResponse.
    """
    mc = MetricsCollector(user_id=str(user_id), endpoint="/api/chatbot")
    mc.start("classification")

    # ── 1. Classification ──
    classification = classify(message)
    intent = classification["intent"]
    resp_type = classification["type"]
    is_init = classification["is_init"]

    mc.end("classification")
    mc.set("intent", intent)
    mc.set("resp_type", resp_type)

    # S2.3 : compteur Prometheus des messages classés (no-op si absent)
    from grading.observability import (
        observe_chatbot_step,
        record_chatbot_message,
    )

    record_chatbot_message(intent, resp_type)
    observe_chatbot_step("classification", mc._durations.get("classification", 0))

    logger.info(f"Chatbot | user={user_id} intent={intent} type={resp_type} mode={mode}")

    # ── 2. SAFETY / TRICHE AVANT toute réponse pédagogique (audit P0-4.4) ──
    if resp_type == "refus":
        return await handle_refus()

    # ── 3. Interception méthodologique locale (0 tokens) ──
    methodology = await handle_methodology(message, user_id)
    if methodology is not None:
        return methodology

    # ── 4. Mode explication de leçon (0 token) ──
    lesson = await handle_lesson(message, user_id)
    if lesson is not None:
        return lesson

    # ── 5. Dispatch par type ──
    if resp_type == "navigation":
        return await handle_navigation(context)

    if resp_type in ("orientation", "daily_plan") or is_init:
        return await handle_orientation(db, user_id, context, is_init=is_init)

    if resp_type == "procrastination":
        return await handle_procrastination(db, user_id, message, context, openai_client)

    if resp_type == "illusion":
        return await handle_illusion(db, user_id, context)

    if resp_type == "smart_goal":
        return await handle_smart_goal(db, user_id, message, context, openai_client)

    if resp_type == "motivation":
        return await handle_motivation(db, user_id, message, context, openai_client)

    if resp_type == "feedback":
        return await handle_feedback(db, user_id, message, context, openai_client)

    # ── 12. Cas par défaut : sos_concept / explication → RAG + LLM ──
    return await handle_default_explanation(
        db, user_id, message, context, openai_client, mode=mode, mc=mc,
    )
