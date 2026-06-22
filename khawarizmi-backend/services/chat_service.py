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
from typing import Dict, List, Optional

from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession

from services.chat_classifier import classify
from services.chat_prompt import (
    build_socratique_prompt,
    build_explication_prompt,
    build_feedback_prompt,
    build_motivation_prompt,
)
from services.orientation_service import calculer_orientation

logger = logging.getLogger("khawarizmi.chat")


async def handle_tuteur(
    message: str,
    context: Dict,
    user_id: str,
    db: AsyncSession,
    openai_client=None,
) -> Dict:
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
    # ── 1. Classification ──
    classification = classify(message)
    intent = classification["intent"]
    resp_type = classification["type"]
    is_init = classification["is_init"]

    logger.info(f"Tuteur : user={user_id} intent={intent} type={resp_type}")

    # ── 2. Cas spécial : refus de triche (0 appel IA) ──
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

    # ── 3. Cas spécial : navigation (0 appel IA) ──
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

    # ── 4. Cas : orientation ou init → appeler le cerveau ──
    if resp_type == "orientation" or is_init:
        orientation = await calculer_orientation(db, user_id)
        cartes = _build_cartes_from_orientation(orientation)

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

    # ── 5. Cas : motivation → appeler le cerveau + Gemini ──
    if resp_type == "motivation":
        orientation = await calculer_orientation(db, user_id)
        prompt = build_motivation_prompt(message, context, orientation)

        reponse = await _call_gemini(prompt, openai_client)
        if reponse is None:
            reponse = _fallback_motivation(orientation)

        return {
            "reponse": reponse,
            "type": "motivation",
            "question_suivante": None,
            "cartes": _build_cartes_from_orientation(orientation)[:1],
            "flashcards_suggerees": [],
            "redirect": None,
            "source_rag": None,
            "fallback_active": reponse is None,
        }

    # ── 6. Cas : feedback → Gemini ──
    if resp_type == "feedback":
        prompt = build_feedback_prompt(message, context, context.get("history", []))
        reponse = await _call_gemini(prompt, openai_client)
        if reponse is None:
            reponse = "أرسل إجابتك في صفحة التمرين وسأقيمها هناك. هنا يمكنني مساعدتك على فهم المنهجية."

        return {
            "reponse": reponse,
            "type": "feedback",
            "question_suivante": None,
            "cartes": [],
            "flashcards_suggerees": [],
            "redirect": None,
            "source_rag": None,
            "fallback_active": reponse is None,
        }

    # ── 7. Cas : sos_concept ou explication → RAG + Gemini ──
    stability = context.get("fsrs_stability", 0)
    is_explication = stability is not None and stability < 3.0

    rag_chunks = await _rag_search(db, message, context.get("chapitre"))

    if is_explication:
        prompt = build_explication_prompt(message, context, rag_chunks, context.get("history", []))
    else:
        prompt = build_socratique_prompt(message, context, rag_chunks, context.get("history", []))

    reponse = await _call_gemini(prompt, openai_client)

    if reponse is None:
        reponse = _fallback_socratique(message, rag_chunks)
        fallback = True
    else:
        fallback = False

    source_rag = rag_chunks[0]["source"] if rag_chunks else None

    return {
        "reponse": reponse,
        "type": "explication" if is_explication else "socratique",
        "question_suivante": None,
        "cartes": [],
        "flashcards_suggerees": _extract_flashcard_suggestions(rag_chunks),
        "redirect": None,
        "source_rag": source_rag,
        "fallback_active": fallback,
    }


# ── Helpers ────────────────────────────────────────

def _build_cartes_from_orientation(orientation: Dict) -> List[Dict]:
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


async def _rag_search(
    db: AsyncSession,
    message: str,
    chapitre: Optional[str],
) -> List[Dict]:
    """Recherche RAG dans pgvector."""
    if not chapitre:
        return []

    try:
        result = await db.execute(
            text("""
                SELECT content, source, chapter,
                       1 - (embedding <=> :query_emb) AS similarity
                FROM rag_chunks
                WHERE chapter ILIKE :chapter
                ORDER BY embedding <=> :query_emb
                LIMIT 3
            """),
            {"chapter": f"%{chapitre}%", "query_emb": _dummy_embedding()},
        )
        return [
            {
                "content": r._mapping["content"],
                "source": r._mapping["source"],
                "chapter": r._mapping["chapter"],
            }
            for r in result.fetchall()
        ]
    except Exception as e:
        logger.warning(f"RAG search échec : {e}")
        return []


def _dummy_embedding() -> str:
    """Embedding vide pour fallback (RAG sans vectorisation)."""
    return "[" + ",".join(["0"] * 384) + "]"


async def _call_gemini(prompt: str, openai_client=None) -> Optional[str]:
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


def _fallback_motivation(orientation: Dict) -> str:
    """Fallback motivation sans IA."""
    prediction = orientation.get("prediction_bac", "N/A")
    dues = orientation.get("dues_aujourd_hui", {})
    fc_dues = dues.get("flashcards", 0)

    if prediction != "N/A" and prediction is not None:
        return f"طبيعي تشعر بالضغط. توقعك الحالي: {prediction}/100. عندك {fc_dues} بطاقة لمراجعة اليوم. نبدأ بواحدة فقط؟"
    return f"طبيعي تشعر بالضغط. عندك {fc_dues} بطاقة لمراجعة اليوم. نبدأ بواحدة فقط؟"


def _fallback_socratique(message: str, rag_chunks: List[Dict]) -> str:
    """Fallback socratique sans IA."""
    if rag_chunks:
        content = rag_chunks[0]["content"][:200]
        return f"حسب الدرس: {content}... ماذا تستنتج من هذا؟"
    return "سؤال مهم! حاول ربطه بما درسته في الدرس. ما هي المعلومات التي تذكرها حول هذا الموضوع؟"


def _extract_flashcard_suggestions(rag_chunks: List[Dict]) -> List[str]:
    """Extrait des suggestions de flashcards depuis le RAG."""
    if not rag_chunks:
        return []
    suggestions = []
    for chunk in rag_chunks[:2]:
        source = chunk.get("source", "")
        if source:
            suggestions.append(f"flashcard:{source}")
    return suggestions
