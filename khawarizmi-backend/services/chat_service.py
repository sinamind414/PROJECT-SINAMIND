"""Service Tuteur Contextuel — pipeline complet.

Pipeline :
  1. Classification locale (0ms, 0 DA)
  2. RAG retrieval si concept (50ms, 0 DA)
  3. Orientation si motivation/init (interne, 0 DA)
  4. Construction du prompt (5ms, 0 DA)
  5. Gemini 2.5 Flash (1 call, 3-8s)
  6. Fallback 3 niveaux si échec
"""

import logging

from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession

from services.chat_classifier import classify
from services.chat_prompt import (
    build_explication_prompt,
    build_feedback_prompt,
    build_motivation_prompt,
    build_socratique_prompt,
)
from services.lesson_explanation import detect_lesson_request, get_lesson_explanation
from services.methodology_local_responses import detect_verb_from_message, get_local_methodology_response
from services.metrics import MetricsCollector, record_request
from services.orientation_service import calculer_orientation
from services.remediation import build_due_concept_question, get_due_concept_for_question
from services.reranker import rerank
from services.semantic_cache import get_semantic_cache, set_semantic_cache

logger = logging.getLogger("khawarizmi.chat")

# Types de questions qui méritent le cache sémantique (pas init/navigation/refus)
CACHEABLE_TYPES = {"sos_concept", "explication", "socratique", "feedback"}


async def handle_tuteur(
    message: str,
    context: dict,
    user_id: str,
    db: AsyncSession,
    openai_client=None,
) -> dict:
    """Pipeline complet du tuteur contextuel.

    Args:
        message: texte de l'élève (ou __init__)
        context: contexte (chapitre, fsrs, history, etc.)
        user_id: ID de l'élève
        db: session DB
        openai_client: client OpenAI/Gemini (optionnel)

    Returns:
        Dict avec reponse, type, cartes, etc.
    """
    mc = MetricsCollector(user_id=str(user_id), endpoint="/api/tuteur")
    mc.start("classification")

    # ── 1. Classification ──
    classification = classify(message)
    intent = classification["intent"]
    resp_type = classification["type"]
    is_init = classification["is_init"]

    mc.end("classification")
    mc.set("intent", intent)
    mc.set("resp_type", resp_type)

    logger.info(f"Tuteur : user={user_id} intent={intent} type={resp_type}")

    # ── 2. Interception méthodologique locale (0 tokens) ──
    verb = detect_verb_from_message(message)
    if verb:
        logger.info(f"Tuteur local methodology | user={user_id} verb={verb}")
        return get_local_methodology_response(verb)

    # ── 3. Mode explication de leçon (0 token) ──
    lesson_key = detect_lesson_request(message)
    if lesson_key:
        logger.info(f"Tuteur lesson explanation | user={user_id} lesson={lesson_key}")
        return get_lesson_explanation(lesson_key)

    # ── 5. Cas spécial : refus de triche (0 appel IA) ──
    if resp_type == "refus":
        return {
            "reponse": "لا أستطيع إعطاءك الحل جاهزا. لكن يمكنني مساعدتك على إيجاده بنفسك. ما الذي فهمته من الوثيقة؟",
            "type": "refus",
            "question_suivante": "ما الذي فهمته من الوثيقة؟",
            "cartes": [],
            "flashcards_suggerees": [],
            "redirect": None,
            "source_rag": None,
            "fallback_active": False,
        }

    # ── 6. Cas spécial : navigation (0 appel IA) ──
    if resp_type == "navigation":
        chapitre = context.get("chapitre", "")
        return {
            "reponse": "يمكنك الوصول للدرس مباشرة من هنا:",
            "type": "navigation",
            "question_suivante": None,
            "cartes": [
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
            "flashcards_suggerees": [],
            "redirect": None,
            "source_rag": None,
            "fallback_active": False,
        }

    # ── 7. Cas : orientation ou init → appeler le cerveau ──
    if resp_type == "orientation" or is_init:
        orientation = await calculer_orientation(db, user_id)
        cartes = _build_cartes_from_orientation(orientation)

        # Lien 1 (FSRS → Question auto) : si init, vérifier les concepts dus
        due_concept = await get_due_concept_for_question(db, user_id)
        if due_concept and is_init:
            due_push = build_due_concept_question(due_concept)
            greeting = "سلام! "
            if orientation["prediction_bac"] is not None:
                greeting += f"توقعك للبكالوريا: {orientation['prediction_bac']}/100. "
            # Combiner l'orientation + la question sur le concept dû
            msg = orientation["message"] + "\n\n" + due_push["reponse"]
            cartes = cartes + due_push["cartes"]
            mc.set("due_concept_pushed", due_concept["concept_id"])
            logger.info(
                f"Tuteur | Lien 1 FSRS push: concept={due_concept['concept_id']} stability={due_concept['stability']}"
            )
            return {
                "reponse": greeting + msg,
                "type": "orientation_with_due_push",
                "question_suivante": due_push["question_suivante"],
                "cartes": cartes,
                "flashcards_suggerees": [],
                "redirect": due_push.get("redirect"),
                "source_rag": None,
                "fallback_active": False,
                "due_concept": due_concept["concept_id"],
                "due_chapter": due_concept["chapter"],
            }

        if is_init:
            greeting = "سلام! "
            if orientation["prediction_bac"] is not None:
                greeting += f"توقعك للبكالوريا: {orientation['prediction_bac']}/100. "
            msg = orientation["message"]
        else:
            greeting = ""
            msg = orientation["message"]

        return {
            "reponse": greeting + msg,
            "type": "orientation",
            "question_suivante": "نبدأ؟",
            "cartes": cartes,
            "flashcards_suggerees": [],
            "redirect": None,
            "source_rag": None,
            "fallback_active": False,
        }

    # ── 8. Cas : motivation → appeler le cerveau + Gemini ──
    if resp_type == "motivation":
        chapitre = context.get("chapitre", "general")

        # Cache sémantique pour motivation
        cached = await get_semantic_cache(message, chapitre)
        if cached:
            logger.info(f"Tuteur cache HIT (motivation) | user={user_id}")
            return cached

        orientation = await calculer_orientation(db, user_id)
        prompt = build_motivation_prompt(message, context, orientation)

        reponse = await _call_gemini(prompt, openai_client)
        if reponse is None:
            reponse = _fallback_motivation(orientation)

        result = {
            "reponse": reponse,
            "type": "motivation",
            "question_suivante": None,
            "cartes": _build_cartes_from_orientation(orientation)[:1],
            "flashcards_suggerees": [],
            "redirect": None,
            "source_rag": None,
            "fallback_active": reponse is None,
        }

        await set_semantic_cache(message, result, chapitre)
        return result

    # ── 9. Cas : feedback → Gemini ──
    if resp_type == "feedback":
        chapitre = context.get("chapitre", "general")

        # Cache sémantique pour feedback
        cached = await get_semantic_cache(message, chapitre)
        if cached:
            logger.info(f"Tuteur cache HIT (feedback) | user={user_id}")
            return cached

        prompt = build_feedback_prompt(message, context, context.get("history", []))
        reponse = await _call_gemini(prompt, openai_client)
        if reponse is None:
            reponse = "أرسل إجابتك في صفحة التمرين وسأقيمها هناك. هنا يمكنني مساعدتك على فهم المنهجية."

        result = {
            "reponse": reponse,
            "type": "feedback",
            "question_suivante": None,
            "cartes": [],
            "flashcards_suggerees": [],
            "redirect": None,
            "source_rag": None,
            "fallback_active": reponse is None,
        }

        await set_semantic_cache(message, result, chapitre)
        return result

    # ── 10. Cas : sos_concept ou explication → RAG + Gemini ──
    stability = context.get("fsrs_stability", 0)
    is_explication = stability is not None and stability < 3.0
    chapitre = context.get("chapitre", "general")

    # Cache sémantique : vérifier si une question similaire a déjà été posée
    mc.start("cache_lookup")
    cached = await get_semantic_cache(message, chapitre)
    mc.end("cache_lookup")
    mc.set("cache_hit", cached is not None)

    if cached:
        logger.info(f"Tuteur cache HIT | user={user_id} type={cached.get('type')}")
        mc.set("fallback_active", cached.get("fallback_active", False))
        record_request("/api/tuteur", cache_hit=True, fallback=cached.get("fallback_active", False))
        mc.flush()
        return cached

    mc.start("rag")
    rag_chunks = await _rag_search(db, message, context.get("chapitre"))
    mc.end("rag")
    mc.set("rag_chunks_count", len(rag_chunks))

    if is_explication:
        prompt = build_explication_prompt(message, context, rag_chunks, context.get("history", []))
    else:
        prompt = build_socratique_prompt(message, context, rag_chunks, context.get("history", []))

    mc.start("llm")
    reponse = await _call_gemini(prompt, openai_client)
    mc.end("llm")

    if reponse is None:
        reponse = _fallback_socratique(message, rag_chunks)
        fallback = True
    else:
        fallback = False

    source_rag = rag_chunks[0]["source"] if rag_chunks else None

    result = {
        "reponse": reponse,
        "type": "explication" if is_explication else "socratique",
        "question_suivante": None,
        "cartes": [],
        "flashcards_suggerees": _extract_flashcard_suggestions(rag_chunks),
        "redirect": None,
        "source_rag": source_rag,
        "fallback_active": fallback,
    }

    # Stocker dans le cache sémantique (uniquement si pas fallback)
    mc.start("cache_store")
    await set_semantic_cache(message, result, chapitre)
    mc.end("cache_store")

    mc.set("fallback_active", fallback)
    record_request("/api/tuteur", cache_hit=False, fallback=fallback)
    mc.flush()

    return result


# ── Helpers ────────────────────────────────────────


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
        cartes.append(
            {
                "titre": rec.get("chapitre_ar") or rec.get("raison", "مهمة"),
                "raison": rec.get("raison", ""),
                "action": rec.get("action", "#"),
                "bouton": bouton_map.get(rec.get("type", "cours"), "ابدأ"),
            }
        )

    return cartes


async def _rag_search(
    db: AsyncSession,
    message: str,
    chapitre: str | None,
) -> list[dict]:
    """Recherche RAG dans pgvector + re-ranking hybride.

    Pipeline :
    1. pgvector récupère 20 chunks (bi-encoder, rapide)
    2. reranker.py re-score avec cosinus + BM25 + keyword coverage
    3. On garde les 5 meilleurs
    """
    if not chapitre:
        return []

    try:
        from services.embedder import embedder

        query_vector = embedder.encode([message])[0]
        query_emb = str(query_vector.tolist())
    except Exception as e:
        logger.warning(f"Embedding échec, fallback dummy: {e}")
        query_emb = _dummy_embedding()

    try:
        # Étape 1 : récupérer 20 chunks via pgvector (bi-encoder)
        result = await db.execute(
            text("""
                SELECT content, source, chapter,
                       1 - (embedding <=> CAST(:query_emb AS vector)) AS similarity
                FROM rag_chunks
                WHERE chapter ILIKE :chapter
                ORDER BY embedding <=> CAST(:query_emb AS vector)
                LIMIT 20
            """),
            {"chapter": f"%{chapitre}%", "query_emb": query_emb},
        )
        raw_chunks = [
            {
                "content": r._mapping["content"],
                "source": r._mapping["source"],
                "chapter": r._mapping["chapter"],
                "similarity": float(r._mapping["similarity"]) if r._mapping["similarity"] else 0.0,
            }
            for r in result.fetchall()
        ]

        if not raw_chunks:
            return []

        # Étape 2 : re-ranking hybride (cosinus + BM25 + keyword coverage)
        reranked = rerank(message, raw_chunks, top_k=5)

        # Retourner sans les scores internes
        return [
            {
                "content": c["content"],
                "source": c["source"],
                "chapter": c["chapter"],
                "score_rerank": c.get("score_rerank", 0),
            }
            for c in reranked
        ]

    except Exception as e:
        logger.warning(f"RAG search échec : {e}")
        return []


def _dummy_embedding() -> str:
    """Embedding vide pour fallback (RAG sans vectorisation)."""
    return "[" + ",".join(["0"] * 384) + "]"


async def _call_gemini(prompt: str, openai_client=None) -> str | None:
    """Appelle Gemini via OpenAI client. Retourne None si échec."""
    if not openai_client:
        return None

    try:
        from config import get_settings

        cfg = get_settings()

        response = await openai_client.chat.completions.create(
            model=cfg.openai_model,
            messages=[
                {"role": "system", "content": prompt},
                {"role": "user", "content": "Réponds."},
            ],
            temperature=0.7,
            max_tokens=300,
            timeout=15.0,
        )
        return response.choices[0].message.content.strip()
    except Exception as e:
        logger.error(f"Gemini échec : {e}")
        return None


def _fallback_motivation(orientation: dict) -> str:
    """Fallback motivation sans IA."""
    prediction = orientation.get("prediction_bac", "N/A")
    dues = orientation.get("dues_aujourd_hui", {})
    fc_dues = dues.get("flashcards", 0)

    if prediction != "N/A" and prediction is not None:
        return (
            f"طبيعي تشعر بالضغط. توقعك الحالي: {prediction}/100. عندك {fc_dues} بطاقة لمراجعة اليوم. نبدأ بواحدة فقط؟"
        )
    return f"طبيعي تشعر بالضغط. عندك {fc_dues} بطاقة لمراجعة اليوم. نبدأ بواحدة فقط؟"


def _fallback_socratique(message: str, rag_chunks: list[dict]) -> str:
    """Fallback socratique sans IA."""
    if rag_chunks:
        content = rag_chunks[0]["content"][:200]
        return f"حسب الدرس: {content}... ماذا تستنتج من هذا؟"
    return "سؤال مهم! حاول ربطه بما درسته في الدرس. ما هي المعلومات التي تذكرها حول هذا الموضوع؟"


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
