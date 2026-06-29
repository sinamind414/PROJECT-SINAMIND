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
    Construit la queue de révision pour la prochaine session ( drill ).

    Phase 1 : délègue à services.drill_queue.build_drill_queue qui ne sert QUE
    des questions valides ( texte présent ) — exclut les concepts
    méthodologiques sans texte, nœuds mindmap nus, flashcards manuelles.
    Gère le cold start ( nouveaux utilisateurs ) via questions jamais vues.
    """
    from services.drill_queue import build_drill_queue

    max_cards = req.max_cards if req.max_cards else 5
    queue = await build_drill_queue(
        user_id=current_user["id"],
        max_cards=max_cards,
        db=db,
        exclude=req.exclude,
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
        raise HTTPException(
            status_code=404,
            detail="QuestionFSRS introuvable dans la base"
        )

    return {
        "question_id": result["question_id"],
        "texte": q_data.get("texte", ""),
        "concept_id": result["concept_id"],
        "type": result.get("type", "DUE"),
    }
