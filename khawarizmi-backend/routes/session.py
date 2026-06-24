import logging
from datetime import UTC, datetime

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession

from deps import get_current_user, get_db
from services.questions import get_all_question_ids, get_question

logger = logging.getLogger("khawarizmi.session")
router = APIRouter()


class SessionNextRequest(BaseModel):
    max_cards: int | None = 5
    lang: str | None = "fr"
    exclude: list[str] | None = []


@router.post("/api/session/next", tags=["Session"])
async def get_next_session(
    req: SessionNextRequest, current_user: dict = Depends(get_current_user), db: AsyncSession = Depends(get_db)
):
    """
    Construit la queue de révision pour la prochaine session d'Amina.
    Ordre absolu : PENDING > DUE > NEW
    """
    user_id = current_user["id"]
    max_cards = req.max_cards if req.max_cards else 5

    now = datetime.now(UTC)
    queue = []

    # 1. PENDING (Cartes en attente de vraie évaluation)
    exclude_set = set(req.exclude or [])
    res_pending = await db.execute(
        text("""
            SELECT concept_id
            FROM mastery_micro_concepts
            WHERE user_id = :uid
              AND pending_real_evaluation = TRUE
              AND concept_id != ALL(:excl)
            ORDER BY updated_at ASC
            LIMIT :lim
        """),
        {"uid": user_id, "lim": max_cards, "excl": list(exclude_set) if exclude_set else [""]},
    )
    for row in res_pending.fetchall():
        q_id = row[0]
        q_data = get_question(q_id)
        if q_data:
            queue.append(
                {
                    "question_id": q_id,
                    "texte": q_data.get("texte", ""),
                    "texte_ar": q_data.get("texte_ar", ""),
                    "concept_cle": q_data.get("concept_cle", ""),
                    "concept_cle_ar": q_data.get("concept_cle_ar", ""),
                    "tentative": 1,
                    "type": "PENDING",
                }
            )

    remaining = max_cards - len(queue)
    if remaining <= 0:
        return {"session_queue": queue}

    # 2. DUE (Cartes FSRS échues)
    # Exclure celles déjà dans la queue (même si théoriquement pending_real_evaluation gère l'exclusivité)
    res_due = await db.execute(
        text("""
            SELECT concept_id
            FROM mastery_micro_concepts
            WHERE user_id = :uid
              AND (pending_real_evaluation = FALSE OR pending_real_evaluation IS NULL)
              AND due_date <= :now
            ORDER BY due_date ASC
            LIMIT :lim
        """),
        {"uid": user_id, "now": now, "lim": remaining},
    )
    for row in res_due.fetchall():
        q_id = row[0]
        # Skip if already in queue (safety)
        if any(q["question_id"] == q_id for q in queue):
            continue

        q_data = get_question(q_id)
        if q_data:
            queue.append(
                {
                    "question_id": q_id,
                    "texte": q_data.get("texte", ""),
                    "texte_ar": q_data.get("texte_ar", ""),
                    "concept_cle": q_data.get("concept_cle", ""),
                    "concept_cle_ar": q_data.get("concept_cle_ar", ""),
                    "tentative": 1,
                    "type": "DUE",
                }
            )

    remaining = max_cards - len(queue)
    if remaining <= 0:
        return {"session_queue": queue}

    # 3. NEW (Cartes jamais vues - Cold Start)
    # On récupère les IDs des cartes qu'on a en mémoire (dans le JSON)
    # et on filtre celles déjà vues + celles déjà demandées (exclude)
    res_seen = await db.execute(
        text("SELECT concept_id FROM mastery_micro_concepts WHERE user_id = :uid"), {"uid": user_id}
    )
    seen_ids = {row[0] for row in res_seen.fetchall()}
    exclude_set = set(req.exclude or [])
    all_q_ids = get_all_question_ids()

    # Filtrer : ni déjà vues en DB, ni déjà posées dans cette session
    candidates = [qid for qid in all_q_ids if qid not in seen_ids and qid not in exclude_set]

    # Randomiser la sélection pour éviter l'ordre alphabétique
    import random

    selected = random.sample(candidates, min(remaining, len(candidates)))

    for q_id in selected:
        q_data = get_question(q_id)
        if q_data:
            queue.append(
                {
                    "question_id": q_id,
                    "texte": q_data.get("texte", ""),
                    "texte_ar": q_data.get("texte_ar", ""),
                    "concept_cle": q_data.get("concept_cle", ""),
                    "concept_cle_ar": q_data.get("concept_cle_ar", ""),
                    "tentative": 1,
                    "type": "NEW",
                }
            )

    logger.info(
        f"SESSION_QUEUE | user={user_id} | "
        f"pending={len([c for c in queue if c['type'] == 'PENDING'])} | "
        f"due={len([c for c in queue if c['type'] == 'DUE'])} | "
        f"new={len([c for c in queue if c['type'] == 'NEW'])} | "
        f"total={len(queue)}"
    )

    return {"session_queue": queue}


class SessionRandomRequest(BaseModel):
    max_cards: int | None = 5
    lang: str | None = "fr"
    exclude: list[str] | None = []


@router.post("/api/session/random", tags=["Session"])
async def get_random_questions(
    req: SessionRandomRequest, current_user: dict = Depends(get_current_user), db: AsyncSession = Depends(get_db)
):
    """
    Fallback : questions aléatoires quand la queue FSRS est épuisée.
    """
    from services.questions import get_all_question_ids, get_question

    all_ids = get_all_question_ids()
    exclude_set = set(req.exclude or [])
    candidates = [qid for qid in all_ids if qid not in exclude_set]

    import random

    selected = random.sample(candidates, min(req.max_cards, len(candidates)))

    queue = []
    for q_id in selected:
        q_data = get_question(q_id)
        if q_data:
            queue.append(
                {
                    "question_id": q_id,
                    "texte": q_data.get("texte", ""),
                    "texte_ar": q_data.get("texte_ar", ""),
                    "concept_cle": q_data.get("concept_cle", ""),
                    "concept_cle_ar": q_data.get("concept_cle_ar", ""),
                    "tentative": 1,
                    "type": "RANDOM_FALLBACK",
                }
            )

    return {"session_queue": queue, "source": "random"}


@router.post("/api/session/next-question", tags=["Session"])
async def get_next_question(current_user: dict = Depends(get_current_user), db: AsyncSession = Depends(get_db)):
    """
    Retourne la prochaine question optimale basée sur le scoring FSRS
    (poids_concept * 1 / stabilité) pour les concepts dus de l'élève.
    """
    from services.scheduler import KhawarizmiScheduler

    scheduler = KhawarizmiScheduler()
    result = await scheduler.select_next_question(current_user["id"], db)
    if not result:
        raise HTTPException(status_code=404, detail="Aucune question disponible")

    q_data = get_question(result["question_id"])
    if not q_data:
        # Fallback question standard
        return {
            "question_id": "q_test",
            "texte": "Quel est le rôle de l'ARN polymérase ?",
            "concept_id": "transcription",
            "type": "FALLBACK",
        }

    return {
        "question_id": result["question_id"],
        "texte": q_data.get("texte", ""),
        "concept_id": result["concept_id"],
        "type": result.get("type", "DUE"),
    }
