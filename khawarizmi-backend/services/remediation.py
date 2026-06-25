"""Service de Remédiation — ferme la boucle des 3 cycles.

Implémente les 3 liens manquants du circuit d'apprentissage :

Lien 1 (FSRS → Question auto) :
    Quand l'élève ouvre le tuteur, détecte les concepts FSRS dus et
    génère une question guide sur le concept le plus critique.

Lien 2 (Eval → MindMap color) :
    Après évaluation, si le score est faible, met à jour automatiquement
    le nœud MindMap correspondant (maitrise_eleve=0 → couleur rouge).

Lien 3 (Eval → Verbe d'action) :
    Analyse le type d'erreur détecté par l'Eval Engine et suggère
    un verbe d'action spécifique pour la remédiation.
"""

import logging
from datetime import UTC, datetime

from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession

logger = logging.getLogger("khawarizmi.remediation")


# ── Lien 1 : FSRS → Question auto ────────────────────────────────────────────


async def get_due_concept_for_question(
    db: AsyncSession,
    user_id: str,
) -> dict | None:
    """Détecte le concept FSRS le plus critique dû aujourd'hui.

    Retourne le concept avec la plus faible stabilité parmi ceux dus.
    Utilisé par le tuteur pour pousser une question automatique.

    Returns:
        Dict avec chapter, concept_id, stability, difficulty, ou None.
    """
    now = datetime.now(UTC)
    try:
        result = await db.execute(
            text("""
                SELECT concept_id, chapter, stability, difficulty, micro_concept_id
                FROM mastery_micro_concepts
                WHERE user_id = :uid
                  AND due_date <= :now
                  AND (state IS NULL OR state IN (0, 1))
                ORDER BY stability ASC, difficulty DESC
                LIMIT 1
            """),
            {"uid": int(user_id), "now": now},
        )
        row = result.fetchone()
        if not row:
            return None

        return {
            "concept_id": row[0],
            "chapter": row[1],
            "stability": float(row[2]) if row[2] else 0.0,
            "difficulty": float(row[3]) if row[3] else 0.0,
            "micro_concept_id": row[4],
        }
    except Exception as e:
        logger.warning(f"REMEDIATION | get_due_concept error: {e}")
        return None


def build_due_concept_question(concept: dict) -> dict:
    """Construit une question guide sur le concept dû.

    Ne donne pas la réponse — guide l'élève vers la réflexion (Pilier 2: Rappel Actif).

    Returns:
        Dict avec reponse, type, question_suivante, cartes, redirect.
    """
    chapter = concept.get("chapter", "")
    concept_id = concept.get("concept_id", "")
    stability = concept.get("stability", 0)

    # Message adapté au niveau de stabilité
    if stability < 1.0:
        # Concept très fragile — question de restitution (L1)
        message = f"لديك مفهوم بحاجة لمراجعة عاجلة: {concept_id}. هل تذكر ما هو دوره الأساسي؟"
        question_type = "recall_urgent"
    elif stability < 3.0:
        # Concept fragile — question d'application (L2)
        message = f"مفهوم {concept_id} يحتاج لتثبيت. اشرح باختصار كيف يعمل في سياق {chapter}؟"
        question_type = "recall_stabilize"
    else:
        # Concept en déclin — question de type Bac (L3)
        message = f"مراجعة دورية: حلل دور {concept_id} في {chapter} كما في امتحان البكالوريا."
        question_type = "recall_maintenance"

    return {
        "reponse": message,
        "type": "fsrs_due_push",
        "question_suivante": f"ما الذي تعرفه عن {concept_id}؟",
        "cartes": [
            {
                "titre": f"راجع: {chapter}",
                "raison": "مفهوم مستحق للمراجعة (FSRS)",
                "action": f"/cours/{chapter}",
                "bouton": "راجع",
            },
            {
                "titre": "فلاش كارد",
                "raison": "تثبيت سريع",
                "action": "/flashcards",
                "bouton": "ابدأ",
            },
        ],
        "flashcards_suggerees": [],
        "redirect": f"/cours/{chapter}",
        "source_rag": None,
        "fallback_active": False,
        "due_concept": concept_id,
        "due_chapter": chapter,
    }


# ── Lien 2 : Eval → MindMap color ────────────────────────────────────────────


async def update_mindmap_after_eval(
    db: AsyncSession,
    user_id: str,
    concept_id: str,
    score: int,
    chapter: str = None,
) -> None:
    """Met à jour le nœud MindMap correspondant après évaluation.

    Si score faible (< 4/10) → maitrise_eleve = 0 (rouge #E74C3C)
    Si score moyen (4-7/10) → maitrise_eleve = 1 (en cours)
    Si score bon (>= 8/10) → maitrise_eleve = 2 (maîtrisé, vert)

    Le lien se fait via mindmap_nodes.fsrs_card_id qui contient
    le concept_id ou micro_concept_id du FSRS.
    """
    # Déterminer le niveau de maîtrise
    if score >= 8:
        maitrise = 2
    elif score >= 4:
        maitrise = 1
    else:
        maitrise = 0

    # Construire le fsrs_card_id (format: mm_{node_id} ou concept_id direct)
    possible_card_ids = [concept_id, f"mm_{concept_id}"]

    try:
        # Chercher le nœud MindMap lié à ce concept FSRS
        for card_id in possible_card_ids:
            result = await db.execute(
                text("""
                    UPDATE mindmap_nodes
                    SET maitrise_eleve = :maitrise,
                        updated_at = NOW()
                    WHERE fsrs_card_id = :card_id
                       OR id = :concept_id
                    RETURNING id, label
                """),
                {"maitrise": maitrise, "card_id": card_id, "concept_id": concept_id},
            )
            rows = result.fetchall()
            if rows:
                for row in rows:
                    logger.info(
                        f"REMEDIATION | MindMap node '{row[1]}' (id={row[0]}) "
                        f"mis à jour: maitrise={maitrise} (score={score}/10)"
                    )
                break  # Trouvé et mis à jour

    except Exception as e:
        logger.warning(f"REMEDIATION | update_mindmap error: {e}")


# ── Lien 3 : Eval → Verbe d'action ───────────────────────────────────────────

# Mapping error_type → verbe d'action recommandé
ERROR_TO_VERB = {
    # Erreurs méthodologiques
    "missing_deduction": {"verb_slug": "استنتاج", "verb_fr": "déduire", "reason_ar": "تفتقد خطوة الاستنتاج"},
    "missing_description": {"verb_slug": "صف", "verb_fr": "décrire", "reason_ar": "تفتقد وصف الوثيقة"},
    "missing_results": {"verb_slug": "استخرج", "verb_fr": "extraire", "reason_ar": "تفتقد استخراج النتائج"},
    "missing_comparison": {"verb_slug": "قارن", "verb_fr": "comparer", "reason_ar": "تفتقد المقارنة"},
    "missing_causality": {"verb_slug": "فسر", "verb_fr": "expliquer", "reason_ar": "تفتقد التفسير السببي"},
    "missing_relation": {"verb_slug": "حدد", "verb_fr": "identifier", "reason_ar": "تفتقد تحديد العلاقة"},
    # Erreurs conceptuelles
    "wrong_terminology": {"verb_slug": "عرف", "verb_fr": "définir", "reason_ar": "مصطلحات غير دقيقة"},
    "conceptual_error": {"verb_slug": "وضح", "verb_fr": "expliquer", "reason_ar": "خطأ مفاهيمي"},
    "incomplete_answer": {"verb_slug": "اذكر", "verb_fr": "citer", "reason_ar": "إجابة غير كاملة"},
    # Erreurs de structure
    "no_structure": {"verb_slug": "حلل", "verb_fr": "analyser", "reason_ar": "تفتقد البنية المنهجية"},
    "off_topic": {"verb_slug": "حدد", "verb_fr": "identifier", "reason_ar": "إجابة خارج الموضوع"},
}

# Mapping par chapitre (si pas d'error_type spécifique)
CHAPTER_TO_VERB = {
    "ch1_proteines": {"verb_slug": "صف", "verb_fr": "décrire", "reason_ar": "مراجعة تركيب البروتينات"},
    "ch2_enzymes": {"verb_slug": "حلل", "verb_fr": "analyser", "reason_ar": "تحليل النشاط الإنزيمي"},
    "ch3_immunite": {"verb_slug": "فسر", "verb_fr": "expliquer", "reason_ar": "تفسير الاستجابة المناعية"},
    "ch4_nerveux": {"verb_slug": "حلل", "verb_fr": "analyser", "reason_ar": "تحليل النقل العصبي"},
    "ch5_photosynthese": {"verb_slug": "صف", "verb_fr": "décrire", "reason_ar": "وصف البناء الضوئي"},
    "ch6_genetique": {"verb_slug": "فسر", "verb_fr": "expliquer", "reason_ar": "تفسير الوراثة"},
    "ch7_geologie": {"verb_slug": "حلل", "verb_fr": "analyser", "reason_ar": "تحليل الظواهر الجيولوجية"},
}


def suggest_action_verb(
    error_type: str = None,
    chapter: str = None,
    score: int = 0,
    missing_concepts: list[str] = None,
) -> dict | None:
    """Suggère un verbe d'action pour la remédiation.

    Priorité :
    1. error_type explicite (depuis common_mistakes ou Eval LLM)
    2. chapter du concept évalué
    3. missing_concepts (analyse des concepts manquants)

    Returns:
        Dict avec verb_slug, verb_fr, reason_ar, href, ou None.
    """
    # 1. Error type explicite
    if error_type and error_type in ERROR_TO_VERB:
        suggestion = ERROR_TO_VERB[error_type]
        return {
            "verb_slug": suggestion["verb_slug"],
            "verb_fr": suggestion["verb_fr"],
            "reason_ar": suggestion["reason_ar"],
            "href": f"/action-verbs/{suggestion['verb_slug']}",
            "priority": "high" if score < 4 else "medium",
        }

    # 2. Chapitre
    if chapter and chapter in CHAPTER_TO_VERB:
        suggestion = CHAPTER_TO_VERB[chapter]
        return {
            "verb_slug": suggestion["verb_slug"],
            "verb_fr": suggestion["verb_fr"],
            "reason_ar": suggestion["reason_ar"],
            "href": f"/action-verbs/{suggestion['verb_slug']}",
            "priority": "high" if score < 4 else "medium",
        }

    # 3. Analyse des concepts manquants
    if missing_concepts:
        # Si beaucoup de concepts manquants → verbe "citer" (restitution)
        if len(missing_concepts) >= 3:
            return {
                "verb_slug": "اذكر",
                "verb_fr": "citer",
                "reason_ar": f"تفتقد {len(missing_concepts)} مفاهيم — ابدأ بالحفظ",
                "href": "/action-verbs/اذكر",
                "priority": "high",
            }
        # Si peu de concepts manquants → verbe "expliquer" (compréhension)
        return {
            "verb_slug": "وضح",
            "verb_fr": "expliquer",
            "reason_ar": "وضح المفاهيم الناقصة",
            "href": "/action-verbs/وضح",
            "priority": "medium",
        }

    # 4. Fallback : score bas → verbe général
    if score < 4:
        return {
            "verb_slug": "عرف",
            "verb_fr": "définir",
            "reason_ar": "راجع التعاريف الأساسية",
            "href": "/action-verbs",
            "priority": "high",
        }

    return None
