"""Helpers de réponse du chatbot — formatage et normalisation.


Extrait de chatbot_orchestrator.py pour alléger l'orchestrateur.
"""


def make_response(
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


def normalize_response(result: dict, intent: str = "unknown") -> dict:
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


def normalize_cached(cached: dict) -> dict:
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


def build_cartes_from_orientation(orientation: dict) -> list[dict]:
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


def build_action_cartes(orientation: dict | None) -> list[dict]:
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

    return build_cartes_from_orientation(orientation)[:2]


def build_sources(rag_chunks: list[dict]) -> list[dict]:
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


def extract_flashcard_suggestions(rag_chunks: list[dict]) -> list[str]:
    if not rag_chunks:
        return []
    suggestions = []
    for chunk in rag_chunks[:2]:
        source = chunk.get("source", "")
        if source:
            suggestions.append(f"flashcard:{source}")
    return suggestions
