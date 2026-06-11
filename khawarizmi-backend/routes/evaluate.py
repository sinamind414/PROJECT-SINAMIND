import json
import logging
import os
from datetime import datetime, timezone
from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import text
from typing import Dict, Any, Optional

from main import get_current_user, get_db, get_openai, get_scheduler
from services.llm import call_gpt4o_evaluator
from services.fallback import fallback_evaluate, fallback_safe_json

logger = logging.getLogger("khawarizmi.evaluate")
router = APIRouter()

from services.questions import get_question

# ═══════════════════════════════
# SCHMAS
# ═══════════════════════════════

class EvaluateRequest(BaseModel):
    question_id: str
    reponse_eleve: str
    tentative: int = 1

class EvaluateResponse(BaseModel):
    score: int
    statut: str
    feedback: str
    manquant: list[str]
    next_review_date: Optional[str] = None
    source: str

# ═══════════════════════════════
# ENDPOINT PRINCIPAL
# ═══════════════════════════════

@router.post("/api/evaluate", response_model=EvaluateResponse)
async def evaluate(
    req:          EvaluateRequest,
    current_user: Dict           = Depends(get_current_user),
    db:           AsyncSession   = Depends(get_db),
    openai_client                = Depends(get_openai)
):
    user_id = current_user["id"]
    
    # 1. Charger la question
    question = get_question(req.question_id)
    if not question:
        raise HTTPException(status_code=404, detail=f"Question {req.question_id} introuvable")

    # 2. Charger l'tat FSRS (Cold Start gr : si inexistant, fsrs_state_db reste None)
    result_card = await db.execute(
        text("SELECT fsrs_state FROM mastery_micro_concepts WHERE user_id = :u AND micro_concept_id = :q"),
        {"u": user_id, "q": req.question_id}
    )
    row = result_card.fetchone()
    fsrs_state_dict = row[0] if row and row[0] else {}

    # 3. Tentative d'valuation GPT-4o (avec fallbacks)
    eval_result = await evaluate_with_fallback(question, req, openai_client, user_id)

    # 4. Mise  jour FSRS  OPTION B
    next_review_date = None

    if eval_result["source"] == "GPT4O":
        scheduler = get_scheduler()
        from fsrs import Card
        card = Card()
        
        # Hydrater la carte si on a dj un tat
        if fsrs_state_dict:
            try:
                card.stability = fsrs_state_dict.get("stability", card.stability)
                card.difficulty = fsrs_state_dict.get("difficulty", card.difficulty)
                card.scheduled_days = fsrs_state_dict.get("scheduled_days", card.scheduled_days)
                card.reps = fsrs_state_dict.get("reps", card.reps)
                card.lapses = fsrs_state_dict.get("lapses", card.lapses)
                # Le state enum FSFS ncessite un parsing, mais on utilise calculer_prochain_intervalle de notre scheduler
            except Exception as e:
                logger.error(f"Erreur hydratation FSRS: {e}")

        # Map Score (0-10) to FSRS Rating percentage (0-100)
        score_percent = eval_result["score"] * 10
        
        fsrs_calc = scheduler.calculer_prochain_intervalle(card, score_percent)
        new_card = fsrs_calc["card"]
        
        fsrs_json = json.dumps({
            "stability":     new_card.stability,
            "difficulty":    new_card.difficulty,
            "scheduled_days":new_card.scheduled_days,
            "reps":          new_card.reps,
            "lapses":        new_card.lapses,
            "state":         str(new_card.state),
            "last_review":   datetime.now(timezone.utc).isoformat(),
        })

        # Sauvegarde DB
        await db.execute(
            text("""
                INSERT INTO mastery_micro_concepts
                    (user_id, micro_concept_id, prochaine_revision,
                     interval_jours, difficulty, stability, fsrs_state, pending_real_evaluation)
                VALUES
                    (:user_id, :mc_id, :next_rev,
                     :interval, :difficulty, :stability, :fsrs_state::jsonb, FALSE)
                ON CONFLICT (user_id, micro_concept_id)
                DO UPDATE SET
                    prochaine_revision = EXCLUDED.prochaine_revision,
                    interval_jours     = EXCLUDED.interval_jours,
                    difficulty         = EXCLUDED.difficulty,
                    stability          = EXCLUDED.stability,
                    fsrs_state         = EXCLUDED.fsrs_state,
                    pending_real_evaluation = FALSE,
                    updated_at         = NOW()
            """),
            {
                "user_id":    user_id,
                "mc_id":      req.question_id,
                "next_rev":   fsrs_calc["prochaine_revision"],
                "interval":   fsrs_calc["interval_jours"],
                "difficulty": fsrs_calc["difficulty"],
                "stability":  fsrs_calc["stability"],
                "fsrs_state": fsrs_json,
            }
        )
        await db.commit()
        next_review_date = fsrs_calc["prochaine_revision"].isoformat() if fsrs_calc["prochaine_revision"] else None

        logger.info(
            f"EVAL_OK | user={user_id} | q={req.question_id} | "
            f"score={eval_result['score']} | "
            f"next_review={next_review_date}"
        )

    else:
        # Fallback L2 ou L3  Option B : carte en attente (Tag)
        # On insre ou on update juste la colonne pending_real_evaluation
        await db.execute(
            text("""
                INSERT INTO mastery_micro_concepts (user_id, micro_concept_id, pending_real_evaluation)
                VALUES (:user_id, :mc_id, TRUE)
                ON CONFLICT (user_id, micro_concept_id)
                DO UPDATE SET pending_real_evaluation = TRUE
            """),
            {"user_id": user_id, "mc_id": req.question_id}
        )
        await db.commit()
        
        logger.warning(
            f"PENDING_TAGGED | user={user_id} | "
            f"q={req.question_id} | source={eval_result['source']}"
        )

    return EvaluateResponse(
        score            = eval_result["score"],
        statut           = eval_result["statut"],
        feedback         = eval_result["feedback"],
        manquant         = eval_result["manquant"],
        next_review_date = next_review_date,
        source           = eval_result["source"]
    )

# ═══════════════════════════════
# LOGIQUE DE FALLBACK
# ═══════════════════════════════

async def evaluate_with_fallback(question: dict, req: EvaluateRequest, openai_client, user_id: str) -> dict:
    
    # NIVEAU 1  GPT-4o avec retry
    try:
        result = await call_gpt4o_evaluator(
            client      = openai_client,
            question    = question,
            reponse     = req.reponse_eleve,
            tentative   = req.tentative
        )
        result["source"] = "GPT4O"
        return result

    except Exception as e:
        logger.warning(f"FALLBACK_L2 | user={user_id} | q={req.question_id} | reason={str(e)}")

    # NIVEAU 2  Pattern matching local
    try:
        result = fallback_evaluate(
            pattern  = question.get("pattern_recherche", ""),
            reponse  = req.reponse_eleve
        )
        result["source"] = "FALLBACK_L2"
        return result

    except Exception as e:
        logger.error(f"FALLBACK_L3 | user={user_id} | q={req.question_id} | reason={str(e)}")

    # NIVEAU 3  JSON de scurit
    result = fallback_safe_json()
    result["source"] = "FALLBACK_L3"
    return result
