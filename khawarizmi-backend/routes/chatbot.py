"""
routes/chatbot.py - Endpoint dédié pour le chatbot v2 (Q&A libre).

POST /api/chatbot/ask
Body : { message: str, history?: [{role, content}], lang?: "fr"|"ar", chapitre?: str }
Auth : JWT Bearer requis
Réponse : { response: str, sources?: [], source_rag?: str, from_cache: false }
"""

import logging

from fastapi import APIRouter, Depends, HTTPException, Request
from openai import AsyncOpenAI
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession

from config import get_settings
from database import get_db
from deps import get_current_user, get_openai
from rate_limit import chat_limit, limiter

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


# ── RAG hybride ──────────────────────────────────


async def _vector_rag_search(
    db: AsyncSession,
    message: str,
    chapter: str | None,
    limit: int = 20,
) -> list[dict]:
    """Recherche vectorielle via pgvector (bi-encoder MiniLM)."""
    try:
        from services.embedder import embedder

        query_vector = embedder.encode([message])[0]
        query_emb = str(query_vector.tolist())
    except Exception as e:
        logger.warning(f"Embedding échec, fallback keyword only: {e}")
        return []

    try:
        if chapter:
            result = await db.execute(
                text("""
                    SELECT content, source, chapter,
                           1 - (embedding <=> CAST(:query_emb AS vector)) AS similarity
                    FROM rag_chunks
                    WHERE LOWER(chapter) LIKE LOWER(:chapter)
                    ORDER BY embedding <=> CAST(:query_emb AS vector)
                    LIMIT :lim
                """),
                {"chapter": f"%{chapter}%", "query_emb": query_emb, "lim": limit},
            )
        else:
            result = await db.execute(
                text("""
                    SELECT content, source, chapter,
                           1 - (embedding <=> CAST(:query_emb AS vector)) AS similarity
                    FROM rag_chunks
                    ORDER BY embedding <=> CAST(:query_emb AS vector)
                    LIMIT :lim
                """),
                {"query_emb": query_emb, "lim": limit},
            )
        return [
            {
                "content": r._mapping["content"][:500],
                "source": r._mapping["source"],
                "chapter": r._mapping["chapter"],
                "similarity": float(r._mapping["similarity"]) if r._mapping["similarity"] else 0.0,
                "retrieval": "vector",
            }
            for r in result.fetchall()
        ]
    except Exception as e:
        logger.warning(f"Vector RAG search échec : {e}")
        return []


async def _keyword_rag_search(
    db: AsyncSession,
    message: str,
    chapter: str | None,
    limit: int = 20,
) -> list[dict]:
    """Recherche par mots-clés (ILIKE) avec score d'importance."""
    try:
        keywords = [w for w in message.split() if len(w) > 2][:5]
        if not keywords:
            return []

        if chapter:
            result = await db.execute(
                text("""
                    SELECT content, source, chapter, importance
                    FROM rag_chunks
                    WHERE LOWER(chapter) LIKE LOWER(:chapter)
                      AND LOWER(content) ILIKE ANY(:keywords)
                    ORDER BY chunk_index
                    LIMIT :lim
                """),
                {"chapter": f"%{chapter}%", "keywords": [f"%{k}%" for k in keywords], "lim": limit},
            )
        else:
            result = await db.execute(
                text("""
                    SELECT content, source, chapter, importance
                    FROM rag_chunks
                    WHERE LOWER(content) ILIKE ANY(:keywords)
                    ORDER BY chunk_index
                    LIMIT :lim
                """),
                {"keywords": [f"%{k}%" for k in keywords], "lim": limit},
            )

        importance_scores = {"critique": 0.95, "haute": 0.80, "moyenne": 0.60}
        return [
            {
                "content": r._mapping["content"][:500],
                "source": r._mapping["source"],
                "chapter": r._mapping["chapter"],
                "similarity": importance_scores.get(r._mapping.get("importance", "moyenne"), 0.60),
                "retrieval": "keyword",
            }
            for r in result.fetchall()
        ]
    except Exception as e:
        logger.warning(f"Keyword RAG search échec : {e}")
        return []


def _merge_chunks(
    vector_chunks: list[dict],
    keyword_chunks: list[dict],
) -> list[dict]:
    """Fusionne et déduplique les résultats vectoriels + keyword."""
    seen: dict[str, dict] = {}

    for c in vector_chunks:
        key = (c.get("source", ""), c.get("content", "")[:160])
        if key not in seen:
            seen[key] = c

    for c in keyword_chunks:
        key = (c.get("source", ""), c.get("content", "")[:160])
        if key in seen:
            seen[key]["retrieval"] = "hybrid"
        else:
            seen[key] = c

    return list(seen.values())


async def _rag_search(
    db: AsyncSession,
    message: str,
    chapter: str | None = None,
    limit: int = 3,
) -> list[dict]:
    """RAG hybride : vector search + keyword search + fusion + reranking."""
    vector_chunks = await _vector_rag_search(db, message, chapter)
    keyword_chunks = await _keyword_rag_search(db, message, chapter)
    candidates = _merge_chunks(vector_chunks, keyword_chunks)

    if not candidates:
        return []

    # Reranking hybride (cosinus + BM25 + keyword coverage)
    try:
        from services.reranker import rerank

        reranked = rerank(message, candidates, top_k=limit)
    except Exception as e:
        logger.warning(f"Reranker indisponible, fallback tri par similarité : {e}")
        reranked = sorted(candidates, key=lambda c: c.get("similarity", 0), reverse=True)[:limit]

    return reranked


def _format_rag_context(chunks: list[dict]) -> str:
    """Formate les chunks RAG pour injection dans le prompt système."""
    if not chunks:
        return ""
    parts = []
    for c in chunks:
        src = c.get("source", "manuel")
        chap = c.get("chapter", "")
        parts.append(f"[{src}/{chap}] {c['content'][:300]}")
    return "\n\n".join(parts)


def _source_cards(chunks: list[dict]) -> list[dict]:
    """Extrait les sources RAG pour la réponse."""
    seen = set()
    sources = []
    for c in chunks:
        key = (c.get("source", ""), c.get("chapter", ""))
        if key not in seen:
            seen.add(key)
            sources.append({
                "source": c.get("source", "manuel_svt"),
                "chapter": c.get("chapter"),
                "excerpt": c["content"][:200],
            })
    return sources


# ── Helpers ─────────────────────────────────────


def _response(
    reponse: str,
    type_: str = "socratique",
    fallback: bool = False,
    cartes: list | None = None,
    sources: list | None = None,
    source_rag: str | None = None,
) -> dict:
    return {
        "response": reponse,
        "lang": "ar",
        "tokens_utilises": 0,
        "from_cache": False,
        "fallback_active": fallback,
        "cartes": cartes or [],
        "sources": sources or [],
        "source_rag": source_rag,
    }


def _cards_for_mode(mode: str) -> list[dict]:
    cards = {
        "quick": [
            {"titre": "شرح مفهوم", "raison": "فهم أفضل للدرس", "action": "اطلب شرح أي مفهوم في SVT", "bouton": "📖 شرح"},
            {"titre": "حل تمرين", "raison": "تطبيق مباشر", "action": "حل تمارين البكالوريا", "bouton": "✍️ تمرين"},
        ],
        "tutor": [
            {"titre": "شرح خطوة بخطوة", "raison": "تعليم تدريجي", "action": "اطلب شرح المفهوم بالتفصيل", "bouton": "📚 شرح"},
            {"titre": "سؤال تفاعلي", "raison": "تقييم الفهم", "action": "اسألني سؤالاً", "bouton": "❓ سؤال"},
        ],
    }
    return cards.get(mode, cards["quick"])


# ── Endpoint ─────────────────────────────────────


@router.post("/ask")
@limiter.limit(chat_limit)
async def ask_chatbot(
    request: Request,
    body: dict,
    current_user: dict = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """
    Réponse libre à une question SVT en arabe.
    Body :
      - message: str (question de l'utilisateur)
      - history?: list[{role, content}] (historique de conversation)
      - lang?: "fr" | "ar" (défaut: "ar")
      - chapitre?: str (chapitre optionnel pour filtrer le RAG)
      - mode?: "quick" | "tutor" (défaut: "quick")
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

    chapter = body.get("chapitre") or None
    mode = body.get("mode", "quick")

    cfg = get_settings()
    system_prompt = SYSTEM_PROMPT_AR if lang == "ar" else SYSTEM_PROMPT_FR

    # Recherche RAG hybride (toujours, même sans IA)
    rag_chunks = await _rag_search(db, message, chapter)
    rag_context = _format_rag_context(rag_chunks)
    sources = _source_cards(rag_chunks)
    source_rag = rag_chunks[0]["source"] if rag_chunks else None

    # Appel IA dans le corps avec fallback propre
    try:
        openai_client: AsyncOpenAI | None = get_openai()
    except HTTPException:
        openai_client = None

    if openai_client is None:
        if rag_chunks:
            excerpt = rag_chunks[0]["content"][:250]
            return _response(
                f"أنا في وضع احتياطي، لكن وجدت في القاعدة الرسمية ما يلي:\n\n• {excerpt}\n\nاكتب لي أي جزء لم تفهمه وسأبسطه خطوة بخطوة.",
                type_="orientation",
                fallback=True,
                cartes=_cards_for_mode(mode),
                sources=sources,
                source_rag=source_rag,
            )
        return _response(
            "أنا متاح الآن في وضع احتياطي. اكتب المفهوم الذي تريد فهمه وسأرشدك بخطوات قصيرة، لكن خدمة الذكاء الاصطناعي غير مفعلة حالياً.",
            type_="orientation",
            fallback=True,
            cartes=_cards_for_mode(mode),
            sources=sources,
            source_rag=source_rag,
        )

    # Injecter le contexte RAG dans le prompt système
    messages = [{"role": "system", "content": system_prompt}]
    if rag_context:
        messages.append({
            "role": "system",
            "content": f"Contexte du manuel officiel :\n{rag_context}",
        })

    # Limiter l'historique aux 6 derniers échanges (économie de tokens)
    for h in history[-6:]:
        if isinstance(h, dict) and h.get("role") in ("user", "assistant") and h.get("content"):
            messages.append({"role": h["role"], "content": h["content"][:500]})
    messages.append({"role": "user", "content": message[:1000]})

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

        if lang == "fr" and not any("\u0600" <= c <= "\u06ff" for c in ai_text[:50]):
            ai_text = "عذراً، أعد صياغة سؤالك بالعربية من فضلك. 🇩🇿"

        # Enregistrer l'interaction (non bloquant)
        try:
            from services.chatbot_engagement_service import record_chat_interaction
            await record_chat_interaction(
                db, current_user["id"], message,
                chapter=chapter, mode=mode,
            )
        except Exception:
            logger.warning("Échec record_chat_interaction (non bloquant)")

        return {
            "response": ai_text,
            "lang": "ar",
            "tokens_utilises": tokens_used,
            "from_cache": False,
            "fallback_active": False,
            "cartes": _cards_for_mode(mode),
            "sources": sources,
            "source_rag": source_rag,
        }

    except Exception as e:
        logger.error(f"Erreur chatbot : {e}")
        if rag_chunks:
            fallback_text = (
                f"حسب الدرس: {rag_chunks[0]['content'][:200]}...\n"
                "ماذا تستنتج من هذا؟ 💡"
            )
        else:
            fallback_text = "عذراً، أواجه صعوبة في الاتصال حالياً. حاول مرة أخرى بعد قليل 🙏"

        return {
            "response": fallback_text,
            "lang": "ar",
            "tokens_utilises": 0,
            "from_cache": False,
            "fallback_active": True,
            "cartes": _cards_for_mode(mode),
            "sources": sources,
            "source_rag": source_rag,
        }


@router.get("/state")
async def get_state(
    current_user: dict = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Retourne l'état chatbot : mémoire, streak, concepts faibles, mission."""
    from services.chatbot_engagement_service import get_chatbot_state
    state = await get_chatbot_state(db, current_user["id"])
    return {"status": "ok", **state}


@router.post("/feedback")
async def post_feedback(
    body: dict,
    current_user: dict = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Enregistre un feedback utilisateur et met à jour les concepts faibles."""
    feedback = body.get("feedback", "")
    chapter = body.get("chapitre") or None
    if feedback not in ("understood", "partial", "confused", "example", "quiz"):
        raise HTTPException(status_code=400, detail="Feedback invalide")

    from services.chatbot_engagement_service import record_chat_feedback
    await record_chat_feedback(db, current_user["id"], feedback, chapter)
    return {"status": "ok", "feedback": feedback}


@router.post("/daily-mission/complete")
async def complete_mission(
    body: dict,
    current_user: dict = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Marque la mission quotidienne comme complétée."""
    mission_id = body.get("mission_id")
    if not mission_id:
        raise HTTPException(status_code=400, detail="mission_id requis")

    from services.chatbot_engagement_service import complete_daily_mission
    result = await complete_daily_mission(db, current_user["id"], mission_id)
    return result


@router.post("/confusion/detect")
async def detect_confusion_endpoint(
    body: dict,
    current_user: dict = Depends(get_current_user),
):
    """Détecte le type de confusion à partir du texte de l'élève."""
    text = (body.get("text") or "").strip()
    feedback_type = body.get("feedback_type", "confused")
    if not text:
        raise HTTPException(status_code=400, detail="text requis")

    from services.chatbot_engagement_service import detect_confusion
    result = await detect_confusion(text, feedback_type)
    return result


@router.post("/explain-back")
async def explain_back(
    body: dict,
    current_user: dict = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Évalue la réponse d'un élève en mode explain-back."""
    concept = (body.get("concept") or "").strip()
    answer = (body.get("answer") or "").strip()
    if not concept or not answer:
        raise HTTPException(status_code=400, detail="concept et answer requis")

    from services.chatbot_engagement_service import evaluate_explain_back
    result = await evaluate_explain_back(db, current_user["id"], concept, answer)
    return result


@router.post("/boss-fight/start")
async def start_boss_fight_endpoint(
    body: dict,
    current_user: dict = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Démarre un boss fight Bac sur un chapitre donné."""
    chapter = (body.get("chapter") or "").strip()
    if not chapter:
        raise HTTPException(status_code=400, detail="chapter requis")

    from services.chatbot_engagement_service import start_boss_fight
    result = await start_boss_fight(db, current_user["id"], chapter)
    if "error" in result:
        raise HTTPException(status_code=500, detail=result["error"])
    return result


@router.post("/boss-fight/{boss_fight_id}/submit")
async def submit_boss_fight_endpoint(
    boss_fight_id: str,
    body: dict,
    current_user: dict = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Soumet les réponses d'un boss fight."""
    answers = body.get("answers", {})
    if not answers:
        raise HTTPException(status_code=400, detail="answers requis")

    from services.chatbot_engagement_service import submit_boss_fight
    result = await submit_boss_fight(db, current_user["id"], boss_fight_id, answers)
    if "error" in result:
        raise HTTPException(status_code=404 if "non trouvé" in result["error"] else 400, detail=result["error"])
    return result


@router.post("/mystery-box/open")
async def open_mystery_box_endpoint(
    current_user: dict = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Ouvre une mystery box chatbot."""
    from services.chatbot_engagement_service import open_chatbot_mystery_box
    result = await open_chatbot_mystery_box(db, current_user["id"])
    return result


@router.get("/health")
async def chatbot_health():
    """Endpoint de santé pour le chatbot (pas d'auth requise)."""
    return {"status": "ok", "service": "chatbot-v2"}
