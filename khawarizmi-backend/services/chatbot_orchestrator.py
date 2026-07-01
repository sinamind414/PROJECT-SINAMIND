"""Chatbot Orchestrator — Pipeline unifié du Chatbot Khawarizmi.

Ce service est le CERVEAU du chatbot. Il orchestre :
  1. Classification locale (0ms, 0 DA)
  2. Interception locale (méthodologie/leçon, 0 token)
  3. RAG retrieval si concept (50ms, 0 DA)
  4. Orientation si motivation/init/procrastination (interne, 0 DA)
  5. FSRS due concept push (interne, 0 DA)
  6. Construction du prompt adaptatif (5ms, 0 DA)
  7. LLM call (Gemini/OpenAI, 3-8s)
  8. Fallback 3 niveaux si échec
  9. Engagement tracking (streak, daily mission)

Contrat de réponse : TuteurResponse (aligné avec le frontend)
"""

import logging

from sqlalchemy.ext.asyncio import AsyncSession

from services.chat_classifier import classify
from services.chat_prompt import (
    build_daily_check_prompt,
    build_explication_prompt,
    build_feedback_prompt,
    build_motivation_prompt,
    build_navigation_prompt,
    build_orientation_prompt,
    build_procrastination_prompt,
    build_smart_goal_prompt,
    build_socratique_prompt,
)
from services.chatbot_fallbacks import (
    fallback_motivation,
    fallback_procrastination,
    fallback_smart_goal,
    fallback_socratique,
)
from services.chatbot_response import (
    build_action_cartes,
    build_cartes_from_orientation,
    build_sources,
    extract_flashcard_suggestions,
    make_response,
    normalize_cached,
    normalize_response,
)
from services.llm_helpers import sanitize_response, call_llm
from services.metrics import MetricsCollector, record_request
from services.orientation_service import calculer_orientation
from services.rag_service import format_rag_context, rag_search, source_cards
from services.remediation import build_due_concept_question, get_due_concept_for_question
from services.semantic_cache import get_semantic_cache, set_semantic_cache

logger = logging.getLogger("khawarizmi.chatbot_orchestrator")

CACHEABLE_TYPES = {
    "sos_concept", "explication", "socratique", "feedback",
    "procrastination", "smart_goal", "daily_plan",
}


async def handle_chatbot_message(
    message: str,
    context: dict,
    user_id: str | int,
    db: AsyncSession,
    openai_client=None,
    mode: str = "quick",
) -> dict:
    """Pipeline complet du chatbot unifié.

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

    logger.info(f"Chatbot | user={user_id} intent={intent} type={resp_type} mode={mode}")

    # ── 2. Interception méthodologique locale (0 tokens) ──
    try:
        from services.methodology_local_responses import detect_verb_from_message, get_local_methodology_response
        verb = detect_verb_from_message(message)
        if verb:
            logger.info(f"Chatbot local methodology | user={user_id} verb={verb}")
            result = get_local_methodology_response(verb)
            return normalize_response(result, intent="methodology")
    except ImportError:
        pass

    # ── 3. Mode explication de leçon (0 token) ──
    try:
        from services.lesson_explanation import detect_lesson_request, get_lesson_explanation
        lesson_key = detect_lesson_request(message)
        if lesson_key:
            logger.info(f"Chatbot lesson explanation | user={user_id} lesson={lesson_key}")
            result = get_lesson_explanation(lesson_key)
            return normalize_response(result, intent="lesson")
    except ImportError:
        pass

    # ── 4. Cas spécial : refus de triche (0 appel IA) ──
    if resp_type == "refus":
        return make_response(
            reponse="لا أستطيع إعطاءك الحل جاهزاً. الحل الجاهز ما يربحك نقطة في البكالوريا — الفهم هو اللي يربح. ما الذي فهمته من الوثيقة؟",
            type_="refus",
            question_suivante="ما الذي فهمته من الوثيقة؟",
        )

    # ── 5. Cas spécial : navigation (0 appel IA) ──
    if resp_type == "navigation":
        chapitre = context.get("chapitre", "")
        return make_response(
            reponse="يمكنك الوصول للدرس مباشرة من هنا:",
            type_="navigation",
            cartes=[
                {
                    "titre": "الدروس",
                    "raison": f"درس {chapitre}" if chapitre else "كل الدروس",
                    "action": f"/cours/{chapitre}" if chapitre else "/cours",
                    "bouton": "افتح",
                },
                {
                    "titre": "الفلاش كارد",
                    "raison": "مراجعة FSRS",
                    "action": "/flashcards",
                    "bouton": "راجع",
                },
            ],
        )

    # ── 6. Cas : orientation ou init → appeler l'orientation + FSRS push ──
    if resp_type in ("orientation", "daily_plan") or is_init:
        orientation = await calculer_orientation(db, user_id)
        cartes = build_cartes_from_orientation(orientation)

        # FSRS push : si init, vérifier les concepts dus
        due_concept = await _safe_get_due_concept(db, user_id)
        if due_concept and is_init:
            due_push = build_due_concept_question(due_concept)
            greeting = "سلام! "
            if orientation.get("prediction_bac") is not None:
                greeting += f"توقعك للبكالوريا: {orientation['prediction_bac']}/100. "
            msg = orientation["message"] + "\n\n" + due_push["reponse"]
            cartes = cartes + due_push.get("cartes", [])

            logger.info(
                f"Chatbot | FSRS push: concept={due_concept.get('concept_id')} stability={due_concept.get('stability')}"
            )
            return make_response(
                reponse=greeting + msg,
                type_="orientation_with_due_push",
                question_suivante=due_push.get("question_suivante"),
                cartes=cartes,
                due_concept=due_concept.get("concept_id"),
                due_chapter=due_concept.get("chapter"),
            )

        if is_init:
            greeting = "سلام! "
            if orientation.get("prediction_bac") is not None:
                greeting += f"توقعك للبكالوريا: {orientation['prediction_bac']}/100. "
            msg = orientation["message"]
        else:
            greeting = ""
            msg = orientation["message"]

        return make_response(
            reponse=greeting + msg,
            type_="orientation",
            question_suivante="نبدأ؟",
            cartes=cartes,
        )

    # ── 7. Cas : procrastination → posture ferme ──
    if resp_type == "procrastination":
        orientation = await _safe_orientation(db, user_id)

        chapitre = context.get("chapitre", "general")
        cached = await _safe_semantic_cache_get(message, chapitre)
        if cached:
            logger.info(f"Chatbot cache HIT (procrastination) | user={user_id}")
            return normalize_cached(cached)

        prompt = build_procrastination_prompt(message, orientation)
        reponse = await call_llm(prompt, openai_client)
        if reponse is None:
            reponse = fallback_procrastination(orientation)

        result = make_response(
            reponse=reponse,
            type_="procrastination",
            cartes=build_action_cartes(orientation)[:1],
        )

        await _safe_semantic_cache_set(message, result, chapitre)
        return result

    # ── 8. Cas : illusion → vérifier par question ──
    if resp_type == "illusion":
        orientation = await _safe_orientation(db, user_id)
        due_concept = await _safe_get_due_concept(db, user_id)

        if due_concept:
            due_push = build_due_concept_question(due_concept)
            return make_response(
                reponse=f"ممتاز! شرحلي بكلماتك: كيف يحدث {due_concept.get('concept_id', 'هذا المفهوم')}؟\n\n{due_push['reponse']}",
                type_="illusion_check",
                question_suivante=due_push.get("question_suivante"),
                cartes=due_push.get("cartes", []),
            )

        chapitre = context.get("chapitre", "")
        if chapitre:
            return make_response(
                reponse=f"رائع! بما إنك فاهم، شرحلي بكلماتك كيف يحدث {chapitre}؟ اللي يشرح فهِم حقيقة.",
                type_="illusion_check",
                question_suivante="شرحلي بكلماتك...",
            )

        return make_response(
            reponse="ممتاز! بما إنك فاهم، خذ 3 بطاقات مراجعة الآن — إذا تجاوب صح، يعني فعلاً فاهم.",
            type_="illusion_check",
            cartes=[{"titre": "مراجعة الآن", "raison": "تأكد إنك فاهم فعلاً", "action": "/flashcards", "bouton": "راجع"}],
        )

    # ── 9. Cas : SMART goal → construire objectif ──
    if resp_type == "smart_goal":
        orientation = await _safe_orientation(db, user_id)
        chapitre = context.get("chapitre", "general")

        cached = await _safe_semantic_cache_get(message, chapitre)
        if cached:
            logger.info(f"Chatbot cache HIT (smart_goal) | user={user_id}")
            return normalize_cached(cached)

        prompt = build_smart_goal_prompt(message, context, orientation)
        reponse = await call_llm(prompt, openai_client)
        if reponse is None:
            reponse = fallback_smart_goal(orientation)

        result = make_response(
            reponse=reponse,
            type_="smart_goal",
            cartes=build_action_cartes(orientation),
        )

        await _safe_semantic_cache_set(message, result, chapitre)
        return result

    # ── 10. Cas : motivation → posture soutenante + Gemini ──
    if resp_type == "motivation":
        chapitre = context.get("chapitre", "general")

        cached = await _safe_semantic_cache_get(message, chapitre)
        if cached:
            logger.info(f"Chatbot cache HIT (motivation) | user={user_id}")
            return normalize_cached(cached)

        orientation = await calculer_orientation(db, user_id)
        prompt = build_motivation_prompt(message, context, orientation)
        reponse = await call_llm(prompt, openai_client)
        if reponse is None:
            reponse = fallback_motivation(orientation)

        result = make_response(
            reponse=reponse,
            type_="motivation",
            cartes=build_cartes_from_orientation(orientation)[:1],
        )

        await _safe_semantic_cache_set(message, result, chapitre)
        return result

    # ── 11. Cas : feedback → Gemini ──
    if resp_type == "feedback":
        chapitre = context.get("chapitre", "general")

        cached = await _safe_semantic_cache_get(message, chapitre)
        if cached:
            logger.info(f"Chatbot cache HIT (feedback) | user={user_id}")
            return normalize_cached(cached)

        prompt = build_feedback_prompt(message, context, context.get("history", []))
        reponse = await call_llm(prompt, openai_client)
        if reponse is None:
            reponse = "أرسل إجابتك في صفحة التمرين وسأقيمها هناك. هنا يمكنني مساعدتك على فهم المنهجية."

        result = make_response(
            reponse=reponse,
            type_="feedback",
        )

        await _safe_semantic_cache_set(message, result, chapitre)
        return result

    # ── 12. Cas par défaut : sos_concept ou explication → RAG + LLM ──
    stability = context.get("fsrs_stability", 0)
    is_explication = stability is not None and stability < 3.0
    chapitre = context.get("chapitre", "general")

    # Cache sémantique
    mc.start("cache_lookup")
    cached = await _safe_semantic_cache_get(message, chapitre)
    mc.end("cache_lookup")
    mc.set("cache_hit", cached is not None)

    if cached:
        logger.info(f"Chatbot cache HIT | user={user_id} type={cached.get('type')}")
        mc.set("fallback_active", cached.get("fallback_active", False))
        record_request("/api/chatbot", cache_hit=True, fallback=cached.get("fallback_active", False))
        mc.flush()
        return normalize_cached(cached)

    # RAG
    mc.start("rag")
    rag_chunks = await _safe_rag_search(db, message, chapitre)
    mc.end("rag")
    mc.set("rag_chunks_count", len(rag_chunks))

    # Orientation context pour enrichir le prompt
    orientation = await _safe_orientation(db, user_id)

    # Prompt adaptatif
    if is_explication:
        prompt = build_explication_prompt(message, context, rag_chunks, context.get("history", []), orientation)
    else:
        prompt = build_socratique_prompt(message, context, rag_chunks, context.get("history", []), orientation)

    # Mode injection (quick/tutor/bac)
    if mode == "tutor":
        prompt += "\n\n⚠️ وضع المدرّس الشخصي مفعّل: علّم خطوة بخطوة، لا تعطِ الجواب. كل رسالة 3-5 أسطر."
    elif mode == "bac":
        prompt += "\n\n⚠️ وضع البكالوريا مفعّل: ركز على المطلوب في البكالوريا، المنهجية، والنقاط اللي تربح العلامة."

    mc.start("llm")
    reponse = await call_llm(prompt, openai_client)
    mc.end("llm")

    if reponse is None:
        reponse = fallback_socratique(message, rag_chunks)
        fallback = True
    else:
        fallback = False

    # Sources RAG
    source_rag = rag_chunks[0]["source"] if rag_chunks else None
    sources = build_sources(rag_chunks)

    result = make_response(
        reponse=reponse,
        type_="explication" if is_explication else "socratique",
        source_rag=source_rag,
        sources=sources,
        flashcards_suggerees=extract_flashcard_suggestions(rag_chunks),
        fallback=fallback,
    )

    # Cache store
    if not fallback:
        mc.start("cache_store")
        await _safe_semantic_cache_set(message, result, chapitre)
        mc.end("cache_store")

    # Engagement tracking
    await _safe_record_engagement(db, user_id, message, context.get("chapitre"), mode)

    mc.set("fallback_active", fallback)
    record_request("/api/chatbot", cache_hit=False, fallback=fallback)
    mc.flush()

    return result


# ═══════════════════════════════════════════════════════════════
# HELPERS — Safe wrappers (non-bloquants)
# ═══════════════════════════════════════════════════════════════

async def _safe_rag_search(db: AsyncSession, message: str, chapitre: str | None) -> list[dict]:
    try:
        chunks = await rag_search(db, message, chapitre)
        return chunks[:5] if chunks else []
    except Exception as e:
        logger.warning(f"RAG search échec : {e}")
        return []


async def _safe_orientation(db: AsyncSession, user_id) -> dict | None:
    try:
        return await calculer_orientation(db, user_id)
    except Exception as e:
        logger.warning(f"Orientation échec (non bloquant): {e}")
        return None


async def _safe_get_due_concept(db: AsyncSession, user_id) -> dict | None:
    try:
        return await get_due_concept_for_question(db, user_id)
    except Exception as e:
        logger.warning(f"Due concept échec (non bloquant): {e}")
        return None


async def _safe_semantic_cache_get(message: str, chapitre: str) -> dict | None:
    try:
        return await get_semantic_cache(message, chapitre)
    except Exception:
        return None


async def _safe_semantic_cache_set(message: str, result: dict, chapitre: str) -> None:
    try:
        await set_semantic_cache(message, result, chapitre)
    except Exception:
        pass


async def _safe_record_engagement(db: AsyncSession, user_id, message: str, chapter: str | None, mode: str) -> None:
    try:
        from services.chatbot_engagement_service import record_chat_interaction
        await record_chat_interaction(db, user_id, message, chapter=chapter, mode=mode)
    except Exception:
        pass
