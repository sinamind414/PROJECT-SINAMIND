# -*- coding: utf-8 -*-
"""
services/reconciliation_queue.py - File de réconciliation asynchrone L1/L2
"""

import asyncio
import json
import logging
from datetime import datetime, timezone
from dataclasses import dataclass
from typing import Optional, Any
from sqlalchemy import text
# Import de state fait à l'intérieur des fonctions pour éviter les imports circulaires


logger = logging.getLogger("khawarizmi.reconciliation_queue")

@dataclass
class PendingReview:
    student_id:   str
    question_id:  str
    answer:       str
    l2_score:     float
    session_id:   str
    timestamp:    datetime

_review_queue: asyncio.Queue[PendingReview] = asyncio.Queue(maxsize=5000)

async def enque_for_l1_review(review: PendingReview) -> bool:
    """
    Enfile une évaluation L2 ambiguë pour re-évaluation L1 différée.
    Retourne False si la queue est pleine.
    """
    try:
        _review_queue.put_nowait(review)
        logger.info(f"Enfilé pour réévaluation L1 : user={review.student_id}, question={review.question_id}")
        return True
    except asyncio.QueueFull:
        logger.warning("La file de réconciliation L1/L2 est pleine, abandon du ticket.")
        return False

async def correct_fsrs_scores(student_id: str, question_id: str, corrected_scores: dict):
    """
    Corrige les scores FSRS en base de données suite à un arbitrage L1.
    """
    from main import state
    if not state.db_session:
        logger.error("DB Session non configurée dans state pour la correction FSRS.")
        return
        
    logger.info(f"Correction FSRS pour user={student_id}, question={question_id} | scores L1={corrected_scores}")
    
    async with state.db_session() as db:
        try:
            # 1. Charger la question
            from services.questions import get_question
            question = get_question(question_id)
            if not question:
                logger.error(f"Question {question_id} non trouvée lors de la correction.")
                return
                
            chapter = question.get("chapitre_id", "ch_inconnu")
            concept_ids = list(corrected_scores.keys())
            
            # 2. Charger l'état FSRS des concepts
            from fsrs import Card
            concept_states = {}
            if concept_ids:
                # ANY(:array) obligatoire — IN :tuple bug asyncpg (AGENTS.md §1.5)
                res_states = await db.execute(
                    text("SELECT concept_id, fsrs_state FROM mastery_micro_concepts WHERE user_id = :uid AND concept_id = ANY(:cids)"),
                    {"uid": int(student_id), "cids": list(concept_ids)}
                )
                for row in res_states.fetchall():
                    c_id = row[0]
                    fsrs_state_dict = row[1] if row[1] else {}
                    card = Card()
                    if fsrs_state_dict:
                        card.stability = fsrs_state_dict.get("stability", card.stability)
                        card.difficulty = fsrs_state_dict.get("difficulty", card.difficulty)
                        for attr in ["scheduled_days", "reps", "lapses"]:
                            if hasattr(card, attr) and attr in fsrs_state_dict:
                                setattr(card, attr, fsrs_state_dict[attr])
                    concept_states[c_id] = card
                    
            for c_id in concept_ids:
                if c_id not in concept_states:
                    concept_states[c_id] = Card()
                    
            # 3. Recalculer FSRS
            from services.fsrs_graph import QuestionConceptMapping, update_concept_graph
            mapping = QuestionConceptMapping(question_id=question_id, concepts={c: 1.0 for c in concept_ids})
            
            l1_eval_result = {
                "score": int(round(sum(corrected_scores.values()) / len(corrected_scores) * 10)) if corrected_scores else 0,
                "statut": "CORRECT" if any(s >= 0.6 for s in corrected_scores.values()) else "FAUX",
                "feedback": "Correction asynchrone.",
                "manquant": [],
                "scores_concepts": corrected_scores,
                "source": "GPT4O"
            }
            
            # Charger la config de l'élève
            res_config = await db.execute(
                text("SELECT fsrs_config FROM users WHERE id = :uid"),
                {"uid": int(student_id)}
            )
            config_row = res_config.fetchone()
            user_fsrs_config = config_row[0] if config_row else None
            
            # Charger le graphe de dépendances
            from services.fsrs_graph import load_concept_graph
            concept_graph = await load_concept_graph(db)

            updates = update_concept_graph(
                user_id=int(student_id),
                question_id=question_id,
                evaluation_result=l1_eval_result,
                mapping=mapping,
                concept_states=concept_states,
                now=datetime.now(timezone.utc),
                user_fsrs_config=user_fsrs_config,
                graph=concept_graph,
            )
            
            # 4. Enregistrer
            for c_id, upd in updates.items():
                new_card = upd["card"]
                sched_days = getattr(new_card, "scheduled_days", 0)
                if not sched_days and new_card.due and new_card.last_review:
                    sched_days = (new_card.due - new_card.last_review).days
                    
                fsrs_json = {
                    "stability":      new_card.stability,
                    "difficulty":     new_card.difficulty,
                    "scheduled_days": sched_days,
                    "reps":           getattr(new_card, "reps", 0),
                    "lapses":         getattr(new_card, "lapses", 0),
                    "state":          str(new_card.state),
                    "last_review":    new_card.last_review.isoformat() if new_card.last_review else None,
                }
                
                await db.execute(
                    text("""
                        UPDATE mastery_micro_concepts 
                        SET due_date = :due, interval_jours = :interval, difficulty = :difficulty,
                            stability = :stability, fsrs_state = :fsrs_state::jsonb, 
                            pending_real_evaluation = FALSE, updated_at = NOW()
                        WHERE user_id = :uid AND concept_id = :cid
                    """),
                    {
                        "due": upd["due"],
                        "interval": sched_days,
                        "difficulty": new_card.difficulty,
                        "stability": new_card.stability,
                        "fsrs_state": json.dumps(fsrs_json),
                        "uid": int(student_id),
                        "cid": c_id
                    }
                )
            await db.commit()
            logger.info(f"FSRS mis à jour avec succès après réévaluation pour user={student_id}, question={question_id}")
        except Exception as e:
            await db.rollback()
            logger.error(f"Erreur lors de la mise à jour FSRS après réévaluation: {e}")

async def process_review_queue():
    """
    Worker d'arrière-plan traitant les réévaluations.
    """
    from main import state
    logger.info("Démarrage du worker de réconciliation L1/L2...")
    
    BATCH_SIZE = 5
    BATCH_TIMEOUT_SECONDS = 15
    
    while True:
        batch = []
        deadline = asyncio.get_event_loop().time() + BATCH_TIMEOUT_SECONDS
        
        while len(batch) < BATCH_SIZE:
            timeout = deadline - asyncio.get_event_loop().time()
            if timeout <= 0:
                break
            try:
                item = await asyncio.wait_for(_review_queue.get(), timeout=timeout)
                batch.append(item)
            except asyncio.TimeoutError:
                break
                
        if not batch:
            continue
            
        logger.info(f"Traitement d'un lot de {len(batch)} réévaluations en attente...")
        
        for review in batch:
            try:
                if not state.openai:
                    logger.warning("Client OpenAI non disponible. Ré-enfilage de la réévaluation...")
                    await enque_for_l1_review(review)
                    await asyncio.sleep(5)
                    continue
                    
                from services.questions import get_question
                question = get_question(review.question_id)
                if not question:
                    continue
                    
                from services.llm import call_gpt4o_evaluator
                l1_result = await asyncio.wait_for(
                    call_gpt4o_evaluator(
                        client=state.openai,
                        question=question,
                        reponse=review.answer,
                        tentative=1
                    ),
                    timeout=15.0
                )
                
                l1_score_norm = float(l1_result["score"]) / 10.0
                # Si l'écart de score est supérieur à 0.20
                if abs(l1_score_norm - review.l2_score) > 0.20:
                    logger.warning(f"Écart de score détecté (L1: {l1_score_norm:.2f}, L2: {review.l2_score:.2f}). Correction FSRS requise.")
                    await correct_fsrs_scores(
                        student_id=review.student_id,
                        question_id=review.question_id,
                        corrected_scores=l1_result.get("scores_concepts", {})
                    )
                else:
                    # Le score L2 est validé, on désactive simplement le flag pending_real_evaluation
                    async with state.db_session() as db:
                        await db.execute(
                            text("""
                                UPDATE mastery_micro_concepts 
                                SET pending_real_evaluation = FALSE, updated_at = NOW()
                                WHERE user_id = :uid AND concept_id = :cid
                            """),
                            {"uid": int(review.student_id), "cid": review.question_id}
                        )
                        await db.commit()
                        logger.info(f"Score L2 confirmé (L1: {l1_score_norm:.2f}, L2: {review.l2_score:.2f}) pour user={review.student_id}, question={review.question_id}")
            except Exception as e:
                logger.error(f"Erreur lors du traitement de la réévaluation de q={review.question_id}: {e}")
                await asyncio.sleep(1)
