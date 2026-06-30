"""Chatbot Orchestrator — Pipeline unifié du Chatbot Khawarizmi.

Ce service est le CERVEAU du chatbot. Il orchestre :
  1. Classification locale (0ms, 0 DA)
  2. RAG retrieval si concept (50ms, 0 DA)
  3. Orientation si motivation/init/procrastination (interne, 0 DA)
  4. FSRS due concept push (interne, 0 DA)
  5. Construction du prompt adaptatif (5ms, 0 DA)
  6. LLM call (Gemini/OpenAI, 3-8s)
  7. Fallback 3 niveaux si échec
  8. Engagement tracking (streak, daily mission)

Remplace :
  - services/chat_service.py (pipeline avancé mais débranché)
  - services/ai_modes/free_mode.py (pipeline basique mais branché)

Contrat de réponse : TuteurResponse (aligné avec le frontend)
  reponse, type, question_suivante, cartes, flashcards_suggerees,
  redirect, source_rag, sources, fallback_active, lang, tokens_used, from_cache
"""

import logging
import re

from sqlalchemy.ext.asyncio import AsyncSession

from services.chat_classifier import classify, detect_language
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
    KHAWARIZMI_IDENTITY,
)
from services.metrics import MetricsCollector, record_request
from services.orientation_service import calculer_orientation
from services.rag_service import format_rag_context, rag_search, source_cards
from services.remediation import build_due_concept_question, get_due_concept_for_question
from services.semantic_cache import get_semantic_cache, set_semantic_cache

logger = logging.getLogger("khawarizmi.chatbot_orchestrator")

# Types de questions qui méritent le cache sémantique
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
            return _normalize_response(result, intent="methodology")
    except ImportError:
        pass

    # ── 3. Mode explication de leçon (0 token) ──
    try:
        from services.lesson_explanation import detect_lesson_request, get_lesson_explanation
        lesson_key = detect_lesson_request(message)
        if lesson_key:
            logger.info(f"Chatbot lesson explanation | user={user_id} lesson={lesson_key}")
            result = get_lesson_explanation(lesson_key)
            return _normalize_response(result, intent="lesson")
    except ImportError:
        pass

    # ── 4. Cas spécial : refus de triche (0 appel IA) ──
    if resp_type == "refus":
        return _make_response(
            reponse="لا أستطيع إعطاءك الحل جاهزاً. الحل الجاهز ما يربحك نقطة في البكالوريا — الفهم هو اللي يربح. ما الذي فهمته من الوثيقة؟",
            type_="refus",
            question_suivante="ما الذي فهمته من الوثيقة؟",
        )

    # ── 5. Cas spécial : navigation (0 appel IA) ──
    if resp_type == "navigation":
        chapitre = context.get("chapitre", "")
        return _make_response(
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
        cartes = _build_cartes_from_orientation(orientation)

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
            return _make_response(
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

        return _make_response(
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
            return _normalize_cached(cached)

        prompt = build_procrastination_prompt(message, orientation)
        reponse = await _call_llm(prompt, openai_client)
        if reponse is None:
            reponse = _fallback_procrastination(orientation)

        result = _make_response(
            reponse=reponse,
            type_="procrastination",
            cartes=_build_action_cartes(orientation)[:1],
        )

        await _safe_semantic_cache_set(message, result, chapitre)
        return result

    # ── 8. Cas : illusion → vérifier par question ──
    if resp_type == "illusion":
        orientation = await _safe_orientation(db, user_id)
        due_concept = await _safe_get_due_concept(db, user_id)

        if due_concept:
            due_push = build_due_concept_question(due_concept)
            return _make_response(
                reponse=f"ممتاز! شرحلي بكلماتك: كيف يحدث {due_concept.get('concept_id', 'هذا المفهوم')}؟\n\n{due_push['reponse']}",
                type_="illusion_check",
                question_suivante=due_push.get("question_suivante"),
                cartes=due_push.get("cartes", []),
            )

        chapitre = context.get("chapitre", "")
        if chapitre:
            return _make_response(
                reponse=f"رائع! بما إنك فاهم، شرحلي بكلماتك كيف يحدث {chapitre}؟ اللي يشرح فهِم حقيقة.",
                type_="illusion_check",
                question_suivante="شرحلي بكلماتك...",
            )

        return _make_response(
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
            return _normalize_cached(cached)

        prompt = build_smart_goal_prompt(message, context, orientation)
        reponse = await _call_llm(prompt, openai_client)
        if reponse is None:
            reponse = _fallback_smart_goal(orientation)

        result = _make_response(
            reponse=reponse,
            type_="smart_goal",
            cartes=_build_action_cartes(orientation),
        )

        await _safe_semantic_cache_set(message, result, chapitre)
        return result

    # ── 10. Cas : motivation → posture soutenante + Gemini ──
    if resp_type == "motivation":
        chapitre = context.get("chapitre", "general")

        cached = await _safe_semantic_cache_get(message, chapitre)
        if cached:
            logger.info(f"Chatbot cache HIT (motivation) | user={user_id}")
            return _normalize_cached(cached)

        orientation = await calculer_orientation(db, user_id)
        prompt = build_motivation_prompt(message, context, orientation)
        reponse = await _call_llm(prompt, openai_client)
        if reponse is None:
            reponse = _fallback_motivation(orientation)

        result = _make_response(
            reponse=reponse,
            type_="motivation",
            cartes=_build_cartes_from_orientation(orientation)[:1],
        )

        await _safe_semantic_cache_set(message, result, chapitre)
        return result

    # ── 11. Cas : feedback → Gemini ──
    if resp_type == "feedback":
        chapitre = context.get("chapitre", "general")

        cached = await _safe_semantic_cache_get(message, chapitre)
        if cached:
            logger.info(f"Chatbot cache HIT (feedback) | user={user_id}")
            return _normalize_cached(cached)

        prompt = build_feedback_prompt(message, context, context.get("history", []))
        reponse = await _call_llm(prompt, openai_client)
        if reponse is None:
            reponse = "أرسل إجابتك في صفحة التمرين وسأقيمها هناك. هنا يمكنني مساعدتك على فهم المنهجية."

        result = _make_response(
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
        return _normalize_cached(cached)

    # RAG
    mc.start("rag")
    rag_chunks = await _rag_search(db, message, chapitre)
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
    reponse = await _call_llm(prompt, openai_client)
    mc.end("llm")

    if reponse is None:
        reponse = _fallback_socratique(message, rag_chunks)
        fallback = True
    else:
        fallback = False

    # Sources RAG
    source_rag = rag_chunks[0]["source"] if rag_chunks else None
    sources = _build_sources(rag_chunks)

    result = _make_response(
        reponse=reponse,
        type_="explication" if is_explication else "socratique",
        source_rag=source_rag,
        sources=sources,
        flashcards_suggerees=_extract_flashcard_suggestions(rag_chunks),
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
# HELPERS — Formatage réponse
# ═══════════════════════════════════════════════════════════════

def _make_response(
    reponse: str,
    type_: str = "socratique",
    question_suivante: str | None = None,
    cartes: list | None = None,
    flashcards_suggerees: list | None = None,
    redirect: str | None = None,
    source_rag: str | None = None,
    sources: list | None = None,
    fallback: bool = False,
    due_concept: str | None = None,
    due_chapter: str | None = None,
) -> dict:
    """Construit une réponse au format TuteurResponse."""
    return {
        "reponse": reponse,
        "type": type_,
        "question_suivante": question_suivante,
        "cartes": cartes or [],
        "flashcards_suggerees": flashcards_suggerees or [],
        "redirect": redirect,
        "source_rag": source_rag,
        "sources": sources or [],
        "fallback_active": fallback,
        "lang": "ar",
        "tokens_used": 0,
        "from_cache": False,
        "due_concept": due_concept,
        "due_chapter": due_chapter,
    }


def _normalize_response(result: dict, intent: str = "unknown") -> dict:
    """Normalise une réponse locale (méthodologie/leçon) au format TuteurResponse."""
    return {
        "reponse": result.get("reponse", ""),
        "type": result.get("type", intent),
        "question_suivante": result.get("question_suivante"),
        "cartes": result.get("cartes", []),
        "flashcards_suggerees": result.get("flashcards_suggerees", []),
        "redirect": result.get("redirect"),
        "source_rag": result.get("source_rag"),
        "sources": result.get("sources", []),
        "fallback_active": result.get("fallback_active", False),
        "lang": "ar",
        "tokens_used": 0,
        "from_cache": False,
    }


def _normalize_cached(cached: dict) -> dict:
    """Normalise une réponse du cache sémantique."""
    return {
        "reponse": cached.get("reponse", ""),
        "type": cached.get("type", "socratique"),
        "question_suivante": cached.get("question_suivante"),
        "cartes": cached.get("cartes", []),
        "flashcards_suggerees": cached.get("flashcards_suggerees", []),
        "redirect": cached.get("redirect"),
        "source_rag": cached.get("source_rag"),
        "sources": cached.get("sources", []),
        "fallback_active": cached.get("fallback_active", False),
        "lang": "ar",
        "tokens_used": 0,
        "from_cache": True,
    }


# ═══════════════════════════════════════════════════════════════
# HELPERS — Orientation / Cartes
# ═══════════════════════════════════════════════════════════════

def _build_cartes_from_orientation(orientation: dict) -> list[dict]:
    """Convertit les recommandations d'orientation en cartes cliquables."""
    cartes = []
    bouton_map = {
        "cours": "ابدأ",
        "action_verb": "تدرب",
        "document_analysis": "حلل",
        "flashcards": "راجع",
        "mindmap": "شاهد",
        "annales": "حل",
    }

    for rec in orientation.get("recommendations", []):
        cartes.append({
            "titre": rec.get("chapitre_ar") or rec.get("raison", "مهمة"),
            "raison": rec.get("raison", ""),
            "action": rec.get("action", "#"),
            "bouton": bouton_map.get(rec.get("type", "cours"), "ابدأ"),
        })

    return cartes


def _build_action_cartes(orientation: dict | None) -> list[dict]:
    """Cartes d'action pour procrastination/SMART — max 2."""
    if not orientation:
        return [
            {"titre": "مراجعة الآن", "raison": "5 بطاقات فقط", "action": "/flashcards", "bouton": "ابدأ"},
        ]

    recs = orientation.get("recommendations", [])
    if not recs:
        dues = orientation.get("dues_aujourd_hui", {})
        fc = dues.get("flashcards", 0) if isinstance(dues, dict) else 0
        return [
            {"titre": f"مراجعة {fc} بطاقة", "raison": "مستحقة اليوم", "action": "/flashcards", "bouton": "راجع"},
        ]

    cartes = _build_cartes_from_orientation(orientation)[:2]
    return cartes


def _build_sources(rag_chunks: list[dict]) -> list[dict]:
    """Construit les sources RAG pour le frontend."""
    if not rag_chunks:
        return []
    sources = []
    for c in rag_chunks[:3]:
        sources.append({
            "source": c.get("source", ""),
            "chapter": c.get("chapter", ""),
            "excerpt": c.get("content", "")[:200],
        })
    return sources


def _extract_flashcard_suggestions(rag_chunks: list[dict]) -> list[str]:
    """Extrait des suggestions de flashcards depuis le RAG."""
    if not rag_chunks:
        return []
    suggestions = []
    for chunk in rag_chunks[:2]:
        source = chunk.get("source", "")
        if source:
            suggestions.append(f"flashcard:{source}")
    return suggestions


# ═══════════════════════════════════════════════════════════════
# HELPERS — RAG
# ═══════════════════════════════════════════════════════════════

async def _rag_search(
    db: AsyncSession,
    message: str,
    chapitre: str | None,
) -> list[dict]:
    """Recherche RAG via le service central."""
    try:
        chunks = await rag_search(db, message, chapitre)
        return chunks[:5] if chunks else []
    except Exception as e:
        logger.warning(f"RAG search échec : {e}")
        return []


# ═══════════════════════════════════════════════════════════════
# HELPERS — LLM
# ═══════════════════════════════════════════════════════════════

def _sanitize_response(text: str) -> str:
    """Nettoie la réponse LLM : supprime les mentions de source, IA, fichiers."""
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

    text = re.sub(r"\n{3,}", "\n\n", text)
    text = text.strip()

    if len(text) > 800:
        text = text[:800] + "..."

    return text


async def _call_llm(prompt: str, openai_client=None) -> str | None:
    """Appelle le LLM. Sanitize la réponse avant retour."""
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
                max_tokens=400,
                timeout=15.0,
            )
            ai_text = (response.choices[0].message.content or "").strip()
            if ai_text:
                return _sanitize_response(ai_text)
        except Exception:
            pass

        response = await openai_client.chat.completions.create(
            model=cfg.openai_model,
            messages=[
                {"role": "system", "content": prompt},
                {"role": "user", "content": "أجب."},
            ],
            temperature=0.7,
            max_tokens=400,
            timeout=15.0,
        )
        return _sanitize_response(response.choices[0].message.content.strip())
    except Exception as e:
        logger.error(f"LLM échec : {e}")
        return None


# ═══════════════════════════════════════════════════════════════
# HELPERS — Fallbacks (0 token)
# ═══════════════════════════════════════════════════════════════

def _fallback_motivation(orientation: dict) -> str:
    """Fallback motivation sans IA."""
    prediction = orientation.get("prediction_bac", "N/A")
    dues = orientation.get("dues_aujourd_hui", {})
    fc_dues = dues.get("flashcards", 0) if isinstance(dues, dict) else 0

    if prediction != "N/A" and prediction is not None:
        return f"طبيعي تحس بالضغط — توقعك الحالي: {prediction}/100. عندك {fc_dues} بطاقة لمراجعة اليوم. نبدأ بواحدة فقط؟"
    return f"طبيعي تحس بالضغط. عندك {fc_dues} بطاقة لمراجعة اليوم. نبدأ بواحدة فقط؟"


def _fallback_procrastination(orientation: dict | None) -> str:
    """Fallback procrastination sans IA."""
    dues = {}
    if orientation:
        dues = orientation.get("dues_aujourd_hui", {})
    fc = dues.get("flashcards", 0) if isinstance(dues, dict) else 0

    if fc > 0:
        return f"البكالوريا قريبة — عندك {fc} بطاقة مستحقة اليوم. حتى 5 دقائق مراجعة أفضل من لا شيء. نبدأ؟"
    return "البكالوريا قريبة — كل يوم تأخير يكلّف. خلّينا نبدأ بفصل واحد فقط، 5 دقائق. نبدأ؟"


def _fallback_socratique(message: str, rag_chunks: list[dict]) -> str:
    """Fallback socratique sans IA."""
    if rag_chunks:
        content = rag_chunks[0]["content"][:200]
        return f"حسب الدرس: {content}... ماذا تستنتج من هذا؟"
    return "سؤال مهم! حاول ربطه بما درسته في الدرس. ما هي المعلومات التي تذكرها حول هذا الموضوع؟"


def _fallback_smart_goal(orientation: dict | None) -> str:
    """Fallback SMART goal sans IA."""
    if not orientation:
        return "هدف اليوم: راجع 10 بطاقات FSRS. خذها واحدة واحدة. نبدأ؟"

    pred = orientation.get("prediction_bac")
    dues = orientation.get("dues_aujourd_hui", {})
    fc = dues.get("flashcards", 0) if isinstance(dues, dict) else 0
    recs = orientation.get("recommendations", [])

    if recs:
        chap = recs[0].get("chapitre_ar", "الفصل الأول")
        return f"🎯 هدف SMART اليوم:\n• محدد: راجع {chap}\n• قابل للقياس: {fc} بطاقة\n• قابل للتحقيق: 15 دقيقة\n• محدد زمنياً: اليوم\nنبدأ؟"

    return f"🎯 هدف اليوم: راجع {fc} بطاقة مراجعة في 15 دقيقة. نبدأ؟"


# ═══════════════════════════════════════════════════════════════
# HELPERS — Safe wrappers (non-bloquants)
# ═══════════════════════════════════════════════════════════════

async def _safe_orientation(db: AsyncSession, user_id) -> dict | None:
    """Récupère l'orientation sans crasher."""
    try:
        return await calculer_orientation(db, user_id)
    except Exception as e:
        logger.warning(f"Orientation échec (non bloquant): {e}")
        return None


async def _safe_get_due_concept(db: AsyncSession, user_id) -> dict | None:
    """Récupère un concept dû FSRS sans crasher."""
    try:
        return await get_due_concept_for_question(db, user_id)
    except Exception as e:
        logger.warning(f"Due concept échec (non bloquant): {e}")
        return None


async def _safe_semantic_cache_get(message: str, chapitre: str) -> dict | None:
    """Récupère du cache sémantique sans crasher."""
    try:
        return await get_semantic_cache(message, chapitre)
    except Exception:
        return None


async def _safe_semantic_cache_set(message: str, result: dict, chapitre: str) -> None:
    """Stocke dans le cache sémantique sans crasher."""
    try:
        await set_semantic_cache(message, result, chapitre)
    except Exception:
        pass


async def _safe_record_engagement(db: AsyncSession, user_id, message: str, chapter: str | None, mode: str) -> None:
    """Enregistre l'engagement sans crasher."""
    try:
        from services.chatbot_engagement_service import record_chat_interaction
        await record_chat_interaction(db, user_id, message, chapter=chapter, mode=mode)
    except Exception:
        pass
