"""Calibrage du moteur Eval sur corpus ONEC.

Injecte des exemples few-shot du Golden Set dans le prompt d'évaluation
pour aligner le LLM sur les barèmes réels de l'ONEC.

Principe :
  - Le Golden Set contient 50 Q/R corrigées officielles
  - Pour chaque évaluation, on sélectionne 2-3 exemples pertinents
    (même chapitre, même niveau) et on les injecte dans le prompt
  - Le LLM "voit" comment un correcteur officiel note

Gain attendu :
  - Réduction des faux positifs (IA trop indulgente)
  - Réduction des faux négatifs (IA trop stricte)
  - Alignement sur la terminologie officielle ONEC
"""

import json
import logging
import pathlib

logger = logging.getLogger("khawarizmi.eval_calibration")

# Cache du Golden Set en mémoire
_golden_set_cache: dict | None = None


def _load_golden_set() -> dict:
    """Charge le Golden Set en mémoire (avec cache)."""
    global _golden_set_cache
    if _golden_set_cache is not None:
        return _golden_set_cache

    golden_path = pathlib.Path(__file__).parent.parent / "data" / "golden_set_onec.json"
    if not golden_path.exists():
        logger.warning(f"Golden Set introuvable: {golden_path}")
        return {"questions": []}

    with open(golden_path, encoding="utf-8") as f:
        _golden_set_cache = json.load(f)
    logger.info(f"Golden Set chargé: {len(_golden_set_cache.get('questions', []))} questions")
    return _golden_set_cache


def select_few_shot_examples(
    chapitre: str,
    niveau: str = None,
    question_text: str = "",
    max_examples: int = 3,
) -> list[dict]:
    """Sélectionne les exemples few-shot les plus pertinents.

    Stratégie de sélection :
    1. Même chapitre (priorité absolue)
    2. Même niveau (L1/L2/L3) si possible
    3. Similarité textuelle avec la question (fallback)

    Args:
        chapitre: chapitre de la question à évaluer
        niveau: niveau de difficulté (L1/L2/L3) optionnel
        question_text: texte de la question pour similarité
        max_examples: nombre max d'exemples à retourner

    Returns:
        Liste d'exemples few-shot formatés
    """
    golden = _load_golden_set()
    questions = golden.get("questions", [])

    if not questions:
        return []

    # Filtrer par chapitre (match souple)
    chapitre_lower = chapitre.lower() if chapitre else ""
    same_chapter = [q for q in questions if chapitre_lower and chapitre_lower in q.get("chapitre", "").lower()]

    if not same_chapter:
        # Pas d'exemples du même chapitre → prendre des exemples variés
        same_chapter = questions

    # Filtrer par niveau si spécifié
    if niveau:
        same_level = [q for q in same_chapter if q.get("niveau") == niveau]
        if same_level:
            same_chapter = same_level

    # Si on a plus d'exemples que nécessaire, sélectionner les plus pertinents
    if len(same_chapter) > max_examples:
        # Simple : prendre les premiers (ils sont déjà triés par chapitre)
        # Amélioration future : similarité cosinus avec question_text
        selected = same_chapter[:max_examples]
    else:
        selected = same_chapter

    return selected


def format_few_shot_prompt(examples: list[dict]) -> str:
    """Formate les exemples few-shot pour injection dans le prompt d'évaluation.

    Format :
        EXEMPLE 1 (Niveau L1, Barème 3 points):
        Question: ...
        Réponse officielle attendue: ...
        Score attendu: 3/3 (CORRECT)
        Mots-clés obligatoires: ...

        EXEMPLE 2 ...
    """
    if not examples:
        return ""

    parts = [
        "═══════════════════════════════════════════════\nEXEMLES DE CORRECTION OFFICIELLE ONEC (FEW-SHOT)\n═══════════════════════════════════════════════"
    ]

    for i, ex in enumerate(examples, 1):
        niveau = ex.get("niveau", "?")
        bareme = ex.get("bareme", "?")
        question = ex.get("question", "")
        reponse = ex.get("reponse_attendue", "")
        mots_cles = ex.get("mots_cles_attendus", [])
        q_type = ex.get("type", "restitution")

        parts.append(f"""
EXEMPLE {i} (Niveau {niveau}, Type: {q_type}, Barème: {bareme} points):
Question: {question}
Réponse officielle attendue: {reponse}
Mots-clés obligatoires: {", ".join(mots_cles)}
Score attendu pour une réponse complète: {bareme}/{bareme} (CORRECT)
Note: Une réponse qui omet un mot-clé obligatoire perd au minimum 1 point.
""")

    parts.append("═══════════════════════════════════════════════\n")
    return "\n".join(parts)


def build_calibrated_prompt(
    chapitre: str,
    question_text: str = "",
    niveau: str = None,
    max_examples: int = 3,
) -> str:
    """Construit le bloc few-shot à injecter dans le SYSTEM_PROMPT d'évaluation.

    Args:
        chapitre: chapitre de la question
        question_text: texte de la question
        niveau: niveau de difficulté
        max_examples: nombre d'exemples

    Returns:
        Texte à ajouter au prompt d'évaluation
    """
    examples = select_few_shot_examples(
        chapitre=chapitre,
        niveau=niveau,
        question_text=question_text,
        max_examples=max_examples,
    )

    if not examples:
        logger.debug(f"EVAL_CALIBRATION | Aucun exemple trouvé pour chapitre='{chapitre}'")
        return ""

    few_shot_block = format_few_shot_prompt(examples)
    logger.info(
        f"EVAL_CALIBRATION | {len(examples)} exemples few-shot injectés "
        f"pour chapitre='{chapitre}' niveau={niveau or 'N/A'}"
    )
    return few_shot_block


def get_calibration_stats() -> dict:
    """Retourne les statistiques du Golden Set pour monitoring."""
    golden = _load_golden_set()
    questions = golden.get("questions", [])

    by_chapter = {}
    by_level = {"L1": 0, "L2": 0, "L3": 0}
    by_type = {}

    for q in questions:
        ch = q.get("chapitre", "?")
        by_chapter[ch] = by_chapter.get(ch, 0) + 1

        niveau = q.get("niveau", "?")
        if niveau in by_level:
            by_level[niveau] += 1

        q_type = q.get("type", "?")
        by_type[q_type] = by_type.get(q_type, 0) + 1

    return {
        "total_questions": len(questions),
        "by_chapter": by_chapter,
        "by_level": by_level,
        "by_type": by_type,
    }
