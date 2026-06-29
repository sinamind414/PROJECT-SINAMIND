"""
services/drill_queue.py — Construction de la queue de drill (Phase 1).

PROBLÈME (avant) : la route /api/session/next lisait mastery_micro_concepts
directement et traitait chaque concept_id comme un question_id. Or cette table
est polluée par ~14 writers : nœuds mindmap (mm_*), concepts méthodologiques
sans texte, flashcards manuelles. Résultat : le drill servait des cartes vides
( ex. « Methodologie - منهجية - النص-العلمي » ).

SOLUTION (Phase 1) : ne servir QUE des questions qui existent VRAIMENT dans
questions_db avec un texte valide. L'état FSRS est filtré par question_id
( c'est la clé réelle que /api/drill/result utilise pour écrire ).

Auto-suffisant : ne dépend PAS de question_concept_map ( qui peut être vide
si l'import script n'a pas tourné ). Dérive le mapping depuis questions_db.

Couche ultérieure (Phase 2) : brancher l'évaluation réelle au lieu du self-rate.
"""

import logging
import random
from datetime import UTC, datetime

from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession

from services.questions import get_question, questions_db
from services.qcm_items import get_all_qcm_ids, qcm_db

logger = logging.getLogger("khawarizmi.drill_queue")

# Seuil minimal pour qu'un texte soit considéré comme une vraie question.
MIN_TEXT_LEN = 12

# Préfixes d'IDs à exclure du drill : ce ne sont pas des questions SVT
# drillables mais des méta-objets ( règles méthodologiques, etc. ).
_EXCLUDED_ID_PREFIXES = ("minhajiya_",)

# Textes placeholder qui ne sont pas de vraies questions ( règles méthodo ).
_PLACEHOLDER_TEXTS = {"règle méthodologique", "regle methodologique"}


def _is_valid_drill_question(qid: str, q: dict) -> bool:
    """True si la question est une vraie question SVT drillable.

    Exclut : texte vide/trop court, placeholders méthodologiques,
    et entrées méthodologiques ( préfixe minhajiya_ ).
    """
    if not q:
        return False
    if any(qid.startswith(p) for p in _EXCLUDED_ID_PREFIXES):
        return False
    texte = (q.get("texte_ar") or q.get("texte") or "").strip()
    if len(texte) < MIN_TEXT_LEN:
        return False
    if texte.lower() in _PLACEHOLDER_TEXTS:
        return False
    return True


async def build_drill_queue(
    user_id: int,
    max_cards: int,
    db: AsyncSession,
    exclude: list[str] | None = None,
    unit_id: str | None = None,
) -> list[dict]:
    """Construit la queue de drill : DUE ( due ) → NEW ( cold start ).

    Ordre : 1. questions FSRS échues déjà vues
             2. questions jamais vues ( cold start )

    Si unit_id est fourni ( u1..u11 ), ne sert QUE les QCM de cette unité.

    Retourne une liste de dicts au contrat attendu par le frontend :
      { question_id, texte, texte_ar, concept_cle, concept_cle_ar, chapter,
        tentative, type }
    """
    exclude_set = set(exclude or [])
    now = datetime.now(UTC)
    queue: list[dict] = []

    # ── Source QCM : filtrer par unit_id si fourni ──
    all_qcm = get_all_qcm_ids() if qcm_db else []
    if unit_id:
        all_qcm = [qid for qid in all_qcm if qcm_db[qid].get("unit_id") == unit_id]
        if not all_qcm:
            logger.warning(f"DRILL_QUEUE | user={user_id} unit={unit_id} AUCUN QCM")
            return []
        logger.info(f"DRILL_QUEUE | user={user_id} filtrage unit={unit_id} ({len(all_qcm)} QCM)")

    # ── Source de vérité : les questions valides dans questions_db ──
    valid_qids = [
        qid for qid, q in questions_db.items()
        if _is_valid_drill_question(qid, q) and qid not in exclude_set
    ]
    if not valid_qids:
        logger.warning(f"DRILL_QUEUE | user={user_id} AUCUNE question valide dans questions_db")
        return []

    # ── État FSRS de l'utilisateur, filtré par question_id valide ──
    res_state = await db.execute(
        text("""
            SELECT micro_concept_id, due_date, stability, pending_real_evaluation
            FROM mastery_micro_concepts
            WHERE user_id = :uid
        """),
        {"uid": user_id},
    )
    fsrs_state: dict[str, dict] = {}
    for row in res_state.fetchall():
        mc_id = row[0]
        if mc_id in valid_qids:  # ne garder que les vraies questions
            fsrs_state[mc_id] = {
                "due_date": row[1],
                "stability": row[2] or 0.0,
                "pending": bool(row[3]),
            }

    seen_qids = set(fsrs_state.keys())

    # ── 1. DUE : questions échues, triées par stabilité ( + faible d'abord ) ──
    due_qids = [
        qid for qid, st in fsrs_state.items()
        if st["pending"] or (st["due_date"] and st["due_date"] <= now)
    ]
    due_qids.sort(key=lambda qid: fsrs_state[qid]["stability"])

    for qid in due_qids[:max_cards]:
        q = get_question(qid)
        if q:
            queue.append(_format_drill_item(qid, q, "DUE"))

    if len(queue) >= max_cards:
        logger.info(f"DRILL_QUEUE | user={user_id} due={len(queue)} total={len(queue)}")
        return queue[:max_cards]

    # ── 2. MIX NEW ( open ) + QCM — citoyens de premier rang ( Phase 3 ) ──
    # Le QCM n'est PAS un bouche-trou : il est la moitié de la session rapide.
    # Les QCM sont auto-corrigés ( zéro IA, instantané ) — idéaux pour densifier.
    # Si unit_id est fourni, ne servir QUE des QCM de cette unité.
    remaining = max_cards - len(queue)
    if remaining > 0:
        qcm_seen = set(fsrs_state.keys())
        qcm_candidates = [q for q in all_qcm if q not in qcm_seen and q not in exclude_set]

        if unit_id:
            n_qcm_target = min(remaining, len(qcm_candidates))
            n_open_target = 0
        else:
            n_qcm_target = min(remaining // 2, len(qcm_candidates)) if qcm_candidates else 0
            n_open_target = remaining - n_qcm_target

        if n_open_target > 0:
            new_candidates = [qid for qid in valid_qids if qid not in seen_qids]
            open_selected = random.sample(new_candidates, min(n_open_target, len(new_candidates)))
            for qid in open_selected:
                q = get_question(qid)
                if q:
                    queue.append(_format_drill_item(qid, q, "NEW"))

        qcm_selected = random.sample(qcm_candidates, n_qcm_target) if n_qcm_target else []
        for qid in qcm_selected:
            pub = {k: v for k, v in qcm_db[qid].items() if k != "correct_idx"}
            queue.append({
                "question_id": qid,
                "texte_ar": pub.get("question_ar", ""),
                "concept_cle": pub.get("unit", ""),
                "chapter": pub.get("domain_ar", ""),
                "unit_ar": pub.get("unit_ar", ""),
                "kind": "qcm",
                "options": pub.get("options", []),
                "explanation": pub.get("explanation", ""),
                "tentative": 1,
                "type": "QCM",
            })

        due_count = len([c for c in queue if c["type"] == "DUE"])
        tail = queue[due_count:]
        random.shuffle(tail)
        queue = queue[:due_count] + tail

    logger.info(
        f"DRILL_QUEUE | user={user_id} "
        f"due={len([c for c in queue if c['type'] == 'DUE'])} "
        f"new={len([c for c in queue if c['type'] == 'NEW'])} "
        f"qcm={len([c for c in queue if c.get('kind') == 'qcm'])} "
        f"definition={len([c for c in queue if c.get('kind') == 'definition'])} "
        f"total={len(queue)}"
    )
    return queue[:max_cards]


def _format_drill_item(qid: str, q: dict, item_type: str) -> dict:
    """Formate une question au contrat attendu par le frontend drill."""
    kind = q.get("kind", "open")
    return {
        "question_id": qid,
        "texte": q.get("texte", ""),
        "texte_ar": q.get("texte_ar") or q.get("texte", ""),
        "concept_cle": q.get("concept_cle", ""),
        "concept_cle_ar": q.get("concept_cle_ar", "") or q.get("micro_concept_id", ""),
        "chapter": q.get("chapitre_id", "") or q.get("chapitre", ""),
        "micro_concept_id": q.get("micro_concept_id", ""),
        "tentative": 1,
        "type": item_type,
        "kind": kind,
    }
