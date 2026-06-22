# -*- coding: utf-8 -*-
"""
services/fsrs_scheduler.py - Planificateur FSRS de questions par score d'urgence conceptuelle.
"""

import logging
from datetime import datetime, timezone, timedelta
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import text
from typing import Dict, Any, List, Optional

from services.questions import get_question

logger = logging.getLogger("khawarizmi.fsrs_scheduler")

async def get_due_concepts(student_id: int, db: AsyncSession) -> List[Dict[str, Any]]:
    """
    Récupère les concepts dus ou presque dus (due_date <= NOW() + 1 jour),
    triés par urgence.
    """
    now = datetime.now(timezone.utc)
    target_date = now + timedelta(days=1)
    
    # Tri par urgence : due_date la plus ancienne en premier,
    # et pondéré par la stabilité (plus la stabilité est faible, plus c'est urgent)
    query = text("""
        SELECT concept_id, stability, due_date, state
        FROM mastery_micro_concepts
        WHERE user_id = :uid
          AND due_date <= :target_date
        ORDER BY due_date ASC, stability ASC
    """)
    
    result = await db.execute(query, {"uid": student_id, "target_date": target_date})
    rows = result.fetchall()
    
    due_concepts = []
    for row in rows:
        due_concepts.append({
            "concept_id": row[0],
            "stability": row[1] if row[1] is not None else 0.0,
            "due_date": row[2],
            "state": row[3]
        })
        
    logger.info(f"FSRS_SCHEDULER | {len(due_concepts)} concepts dus pour l'élève {student_id}")
    return due_concepts

async def select_next_question(student_id: int, db: AsyncSession) -> Optional[Dict[str, Any]]:
    """
    Sélectionne la prochaine question optimale pour l'élève.
    Scoring des questions disponibles par (poids_concept * 1 / stabilité) pour les concepts dus.
    """
    due_concepts = await get_due_concepts(student_id, db)
    
    # 1. Pas de concept dû -> Cold start / Explorer un concept non commencé
    if not due_concepts:
        logger.info("FSRS_SCHEDULER | Aucun concept dû. Recherche d'un concept non commencé (Cold Start).")
        query_new = text("""
            SELECT qcm.question_id, qcm.micro_concept
            FROM question_concept_map qcm
            LEFT JOIN mastery_micro_concepts mmc 
              ON mmc.concept_id = qcm.micro_concept AND mmc.user_id = :uid
            WHERE mmc.id IS NULL
            ORDER BY RANDOM()
            LIMIT 1
        """)
        res_new = await db.execute(query_new, {"uid": student_id})
        row = res_new.fetchone()
        if row:
            return {"question_id": row[0], "concept_id": row[1], "type": "NEW"}
            
        # Fallback 2 : N'importe quelle question non répondue récemment ou hasard
        query_fallback = text("""
            SELECT question_id, micro_concept 
            FROM question_concept_map 
            ORDER BY RANDOM() 
            LIMIT 1
        """)
        res_fallback = await db.execute(query_fallback)
        row_fb = res_fallback.fetchone()
        if row_fb:
            return {"question_id": row_fb[0], "concept_id": row_fb[1], "type": "NEW_FALLBACK"}
            
        return {"question_id": "q_test", "concept_id": "transcription", "type": "DEFAULT"}

    # 2. Des concepts sont dus -> Scoring des questions qui couvrent ces concepts
    concept_ids = [c["concept_id"] for c in due_concepts]
    concept_stability = {c["concept_id"]: c["stability"] for c in due_concepts}
    
    # Récupérer les mappings questions <-> concepts pour les concepts dus
    # ANY(:array) obligatoire — IN :tuple bug asyncpg (AGENTS.md §1.5)
    query_mappings = text("""
        SELECT question_id, micro_concept, weight
        FROM question_concept_map
        WHERE micro_concept = ANY(:cids)
    """)

    res_mappings = await db.execute(query_mappings, {"cids": list(concept_ids)})
    mappings = res_mappings.fetchall()
    
    if not mappings:
        # Si aucun mapping en base, faire un fallback sur la première question liée à un concept dû
        logger.warning("FSRS_SCHEDULER | Aucun mapping trouvé pour les concepts dus dans question_concept_map.")
        concept_fb = concept_ids[0]
        return {"question_id": "q_test", "concept_id": concept_fb, "type": "DUE_FALLBACK"}
        
    # Calculer le score de chaque question
    question_scores = {}
    question_concept_assoc = {}
    
    for q_id, concept_id, weight in mappings:
        stability = concept_stability.get(concept_id, 0.0)
        # Éviter la division par zéro et pénaliser les stabilités proches de zéro (les rendre très prioritaires)
        inv_stability = 1.0 / max(stability, 0.1)
        
        score_contrib = weight * inv_stability
        
        if q_id not in question_scores:
            question_scores[q_id] = 0.0
            question_concept_assoc[q_id] = concept_id
            
        question_scores[q_id] += score_contrib
        
    # Trier les questions par score décroissant
    sorted_questions = sorted(question_scores.items(), key=lambda x: x[1], reverse=True)
    
    best_q_id, best_score = sorted_questions[0]
    best_concept_id = question_concept_assoc[best_q_id]
    
    logger.info(f"FSRS_SCHEDULER | Sélectionné question={best_q_id} (score={best_score:.3f}) pour concept={best_concept_id}")
    
    return {
        "question_id": best_q_id,
        "concept_id": best_concept_id,
        "score": best_score,
        "type": "DUE"
    }
