"""services/chatbot_handlers.py — Handlers du chatbot unifié (audit S2.2).

Chaque handler est une fonction ASYNC PUR et testable : elle reçoit ses
dépendances (db, openai_client, message, context…) en paramètres et retourne
un dict aligné sur TuteurResponse (via make_response). Aucun état global,
aucun import de chatbot_orchestrator (pas de cycle).

Le dispatcher (chatbot_orchestrator.handle_chatbot_message) classe le message
et appelle le handler correspondant — l'ORDRE critique est conservé :
refus/triche AVANT méthodologie/leçon (audit P0-4.4).

Handlers :
- refus (triche) — statique, 0 token
- methodology — détection verbe locale (0 token)
- lesson — explication de leçon (0 token)
- navigation — statique
- orientation / daily_plan / init (+ FSRS push)
- procrastination — cache + LLM + fallback
- illusion — vérification par question
- smart_goal — LLM + cache
- motivation — LLM + cache
- feedback — LLM + cache
- default (sos_concept / explication) — RAG + LLM + cache + engagement
"""

from __future__ import annotations

import logging
from typing import Any

from sqlalchemy.ext.asyncio import AsyncSession

from services.chat_prompt import (
    build_explication_prompt,
    build_feedback_prompt,
    build_motivation_prompt,
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
from services.llm_helpers import call_llm
from services.metrics import record_request
from services.orientation_service import calculer_orientation
from services.pedagogical import pedagogical_bucket
from services.rag_service import rag_search
from services.remediation import build_due_concept_question, get_due_concept_for_question
from services.semantic_cache import get_semantic_cache, set_semantic_cache

logger = logging.getLogger("khawarizmi.chatbot_handlers")

# ── Safe wrappers (non-bloquants) ────────────────────────────────────


async def safe_rag_search(db: AsyncSession, message: str, chapitre: str | None) -> list[dict]:
    try:
        chunks = await rag_search(db, message, chapitre)
        return chunks[:5] if chunks else []
    except Exception as e:
        logger.warning(f"RAG search échec : {e}")
        return []


async def safe_orientation(db: AsyncSession, user_id) -> dict | None:
    try:
        return await calculer_orientation(db, user_id)
    except Exception as e:
        logger.warning(f"Orientation échec (non bloquant): {e}")
        return None


async def safe_get_due_concept(db: AsyncSession, user_id) -> dict | None:
    try:
        return await get_due_concept_for_question(db, user_id)
    except Exception as e:
        logger.warning(f"Due concept échec (non bloquant): {e}")
        return None


async def safe_semantic_cache_get(message: str, chapitre: str) -> dict | None:
    try:
        return await get_semantic_cache(message, chapitre)
    except Exception:
        return None


async def safe_semantic_cache_set(message: str, result: dict, chapitre: str) -> None:
    try:
        await set_semantic_cache(message, result, chapitre)
    except Exception:
        pass


async def safe_record_engagement(db: AsyncSession, user_id, message: str, chapter: str | None, mode: str) -> None:
    try:
        from services.chatbot_engagement_service import record_chat_interaction
        await record_chat_interaction(db, user_id, message, chapter=chapter, mode=mode)
    except Exception:
        pass


# ── Handlers ─────────────────────────────────────────────────────────

async def handle_refus() -> dict:
    """Triche — refus ferme (0 token, 0 LLM)."""
    return make_response(
        reponse="لا أستطيع إعطاءك الحل جاهزاً. الحل الجاهز ما يربحك نقطة في البكالوريا — الفهم هو اللي يربح. ما الذي فهمته من الوثيقة؟",
        type_="refus",
        question_suivante="ما الذي فهمته من الوثيقة؟",
    )


async def handle_methodology(message: str, user_id) -> dict | None:
    """Méthodologie locale par verbe (0 token). None si aucun verbe détecté."""
    try:
        from services.methodology_local_responses import detect_verb_from_message, get_local_methodology_response
        verb = detect_verb_from_message(message)
        if verb:
            logger.info(f"Chatbot local methodology | user={user_id} verb={verb}")
            result = get_local_methodology_response(verb)
            return normalize_response(result, intent="methodology")
    except ImportError:
        pass
    return None


async def handle_lesson(message: str, user_id) -> dict | None:
    """Explication de leçon locale (0 token). None si aucune leçon détectée."""
    try:
        from services.lesson_explanation import detect_lesson_request, get_lesson_explanation
        lesson_key = detect_lesson_request(message)
        if lesson_key:
            logger.info(f"Chatbot lesson explanation | user={user_id} lesson={lesson_key}")
            result = get_lesson_explanation(lesson_key)
            return normalize_response(result, intent="lesson")
    except ImportError:
        pass
    return None


async def handle_navigation(context: dict | None) -> dict:
    """Navigation (0 appel IA) — cartes vers les cours / flashcards."""
    context = context or {}
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


async def handle_orientation(
    db: AsyncSession,
    user_id,
    context: dict | None,
    is_init: bool = False,
) -> dict:
    """Orientation / daily_plan / init — orientation + boussole FSRS."""
    context = context or {}
    orientation = await calculer_orientation(db, user_id)
    cartes = build_cartes_from_orientation(orientation)

    # Boussole unité par unité : best effort pour ne jamais bloquer le coach.
    boussole = None
    try:
        from services.orientation_roadmap import calculer_roadmap

        roadmap = await calculer_roadmap(db, user_id)
        boussole = roadmap["coach"]["ar"]
        weakest = roadmap["prochain_objectif"].get("chapitre_faible")
        if weakest and weakest.get("nom_ar"):
            boussole += (
                f"\n📚 ابدأ بـ: {weakest['nom_ar']} "
                f"(إتقان {weakest['maitrise']}٪)."
            )
    except Exception as exc:
        logger.warning("Chatbot boussole indisponible : %s", exc)

    # FSRS push : si init, vérifier les concepts dus
    due_concept = await safe_get_due_concept(db, user_id)
    if due_concept and is_init:
        due_push = build_due_concept_question(due_concept)
        greeting = "سلام! "
        if orientation.get("prediction_bac") is not None:
            greeting += f"توقعك للبكالوريا: {orientation['prediction_bac']}/100. "
        msg = orientation["message"] + "\n\n" + due_push["reponse"]
        if boussole:
            msg += "\n\n🧭 " + boussole
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

    greeting = "سلام! " if is_init else ""
    if is_init and orientation.get("prediction_bac") is not None:
        greeting += f"توقعك للبكالوريا: {orientation['prediction_bac']}/100. "

    response_text = greeting + orientation["message"]
    if boussole:
        response_text += "\n\n🧭 " + boussole

    return make_response(
        reponse=response_text,
        type_="orientation",
        question_suivante="نبدأ؟",
        cartes=cartes,
    )


async def handle_procrastination(
    db: AsyncSession,
    user_id,
    message: str,
    context: dict | None,
    openai_client=None,
) -> dict:
    """Procrastination — posture ferme, cache + LLM + fallback."""
    context = context or {}
    orientation = await safe_orientation(db, user_id)
    chapitre = context.get("chapitre", "general")

    cached = await safe_semantic_cache_get(message, chapitre)
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

    await safe_semantic_cache_set(message, result, chapitre)
    return result


async def handle_illusion(
    db: AsyncSession,
    user_id,
    context: dict | None,
) -> dict:
    """Illusion — vérifier par question (due concept / chapitre / cartes)."""
    context = context or {}
    orientation = await safe_orientation(db, user_id)
    due_concept = await safe_get_due_concept(db, user_id)

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


async def handle_smart_goal(
    db: AsyncSession,
    user_id,
    message: str,
    context: dict | None,
    openai_client=None,
) -> dict:
    """SMART goal — construire objectif (cache + LLM + fallback)."""
    context = context or {}
    orientation = await safe_orientation(db, user_id)
    chapitre = context.get("chapitre", "general")

    cached = await safe_semantic_cache_get(message, chapitre)
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

    await safe_semantic_cache_set(message, result, chapitre)
    return result


async def handle_motivation(
    db: AsyncSession,
    user_id,
    message: str,
    context: dict | None,
    openai_client=None,
) -> dict:
    """Motivation — posture soutenante (cache + LLM + fallback)."""
    context = context or {}
    chapitre = context.get("chapitre", "general")

    cached = await safe_semantic_cache_get(message, chapitre)
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

    await safe_semantic_cache_set(message, result, chapitre)
    return result


async def handle_feedback(
    db: AsyncSession,
    user_id,
    message: str,
    context: dict | None,
    openai_client=None,
) -> dict:
    """Feedback de correction (cache + LLM + fallback)."""
    context = context or {}
    chapitre = context.get("chapitre", "general")

    cached = await safe_semantic_cache_get(message, chapitre)
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

    await safe_semantic_cache_set(message, result, chapitre)
    return result


async def handle_default_explanation(
    db: AsyncSession,
    user_id,
    message: str,
    context: dict | None,
    openai_client=None,
    mode: str = "quick",
    mc: Any | None = None,
) -> dict:
    """Cas par défaut : sos_concept / explication → RAG + LLM + cache.

    Prompt adaptatif (explication si stabilité faible, socratique sinon) +
    injection du mode (tutor/bac) + fallback local + engagement tracking.
    """
    context = context or {}
    # Seuil unique partagé avec la clé de cache chatbot (services/pedagogical.py)
    is_explication = pedagogical_bucket(context) == "low"
    chapitre = context.get("chapitre", "general")

    # Cache sémantique
    if mc:
        mc.start("cache_lookup")
    cached = await safe_semantic_cache_get(message, chapitre)
    if mc:
        mc.end("cache_lookup")
        mc.set("cache_hit", cached is not None)

    if cached:
        logger.info(f"Chatbot cache HIT | user={user_id} type={cached.get('type')}")
        if mc:
            mc.set("fallback_active", cached.get("fallback_active", False))
            record_request("/api/chatbot", cache_hit=True, fallback=cached.get("fallback_active", False))
            mc.flush()
        return normalize_cached(cached)

    # RAG
    if mc:
        mc.start("rag")
    rag_chunks = await safe_rag_search(db, message, chapitre)
    if mc:
        mc.end("rag")
        mc.set("rag_chunks_count", len(rag_chunks))

    # Orientation context pour enrichir le prompt
    orientation = await safe_orientation(db, user_id)

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

    if mc:
        mc.start("llm")
    reponse = await call_llm(prompt, openai_client)
    if mc:
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
        if mc:
            mc.start("cache_store")
        await safe_semantic_cache_set(message, result, chapitre)
        if mc:
            mc.end("cache_store")

    # Engagement tracking
    await safe_record_engagement(db, user_id, message, context.get("chapitre"), mode)

    if mc:
        mc.set("fallback_active", fallback)
        record_request("/api/chatbot", cache_hit=False, fallback=fallback)
        mc.flush()

    return result
