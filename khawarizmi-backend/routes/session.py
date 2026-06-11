import logging
from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import text
from typing import Dict, Any, List, Optional
from datetime import datetime, timezone

from main import get_current_user, get_db
from services.questions import get_question, get_all_question_ids

logger = logging.getLogger("khawarizmi.session")
router = APIRouter()

class SessionNextRequest(BaseModel):
    max_cards: Optional[int] = 5

@router.post("/api/session/next", tags=["Session"])
async def get_next_session(
    req:          SessionNextRequest,
    current_user: Dict         = Depends(get_current_user),
    db:           AsyncSession = Depends(get_db)
):
    """
    Construit la queue de révision pour la prochaine session d'Amina.
    Ordre absolu : PENDING > DUE > NEW
    """
    user_id = current_user["id"]
    max_cards = req.max_cards if req.max_cards else 5

    now = datetime.now(timezone.utc)
    queue = []
    
    # 1. PENDING (Cartes en attente de vraie évaluation)
    res_pending = await db.execute(
        text("""
            SELECT micro_concept_id 
            FROM mastery_micro_concepts
            WHERE user_id = :uid 
              AND pending_real_evaluation = TRUE
            ORDER BY updated_at ASC
            LIMIT :lim
        """),
        {"uid": user_id, "lim": max_cards}
    )
    for row in res_pending.fetchall():
        q_id = row[0]
        q_data = get_question(q_id)
        if q_data:
            queue.append({
                "question_id": q_id,
                "texte": q_data.get("texte", ""),
                "tentative": 1, # Toujours 1 pour une carte pending !
                "type": "PENDING"
            })
            
    remaining = max_cards - len(queue)
    if remaining <= 0:
        return {"session_queue": queue}

    # 2. DUE (Cartes FSRS échues)
    # Exclure celles déjà dans la queue (même si théoriquement pending_real_evaluation gère l'exclusivité)
    res_due = await db.execute(
        text("""
            SELECT micro_concept_id
            FROM mastery_micro_concepts
            WHERE user_id = :uid
              AND (pending_real_evaluation = FALSE OR pending_real_evaluation IS NULL)
              AND prochaine_revision <= :now
            ORDER BY prochaine_revision ASC
            LIMIT :lim
        """),
        {"uid": user_id, "now": now, "lim": remaining}
    )
    for row in res_due.fetchall():
        q_id = row[0]
        # Skip if already in queue (safety)
        if any(q["question_id"] == q_id for q in queue):
            continue
            
        q_data = get_question(q_id)
        if q_data:
            queue.append({
                "question_id": q_id,
                "texte": q_data.get("texte", ""),
                "tentative": 1, # TODO: Récupérer le vrai nombre de tentatives depuis l'historique si on veut
                "type": "DUE"
            })
            
    remaining = max_cards - len(queue)
    if remaining <= 0:
        return {"session_queue": queue}

    # 3. NEW (Cartes jamais vues - Cold Start)
    # On récupère les IDs des cartes qu'on a en mémoire (dans le JSON) 
    # et on filtre celles que l'utilisateur a déjà dans mastery_micro_concepts
    res_seen = await db.execute(
        text("SELECT micro_concept_id FROM mastery_micro_concepts WHERE user_id = :uid"),
        {"uid": user_id}
    )
    seen_ids = set(row[0] for row in res_seen.fetchall())
    
    all_q_ids = get_all_question_ids()
    new_ids = [qid for qid in all_q_ids if qid not in seen_ids]
    
    # On en prend autant qu'il en manque
    for q_id in new_ids[:remaining]:
        q_data = get_question(q_id)
        if q_data:
            queue.append({
                "question_id": q_id,
                "texte": q_data.get("texte", ""),
                "tentative": 1,
                "type": "NEW"
            })

    return {"session_queue": queue}
