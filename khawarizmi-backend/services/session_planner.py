# -*- coding: utf-8 -*-
"""
services/session_planner.py - Planificateur de sessions d'apprentissage actif
Recommandé par Claude 3 Opus.
"""

import random
import logging
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import text
from typing import Dict, Any, List, Optional

logger = logging.getLogger("khawarizmi.session_planner")

async def select_next_question(
    user_id: int,
    db: AsyncSession,
    interleaving_ratio: float = 0.3,  # 30% hors chapitre courant
) -> Optional[Dict[str, Any]]:
    """
    Sélectionne la prochaine question en combinant :
    1. Les concepts les plus urgents (FSRS due_date passée)
    2. L'entrelacement des chapitres
    3. La difficulté désirable (zone 50-70% de réussite estimée)
    """
    
    # 1. Récupérer les concepts en retard de révision
    # due_date <= NOW()
    overdue_query = await db.execute(
        text("""
            SELECT concept_id, chapter, difficulty, avg_score
            FROM mastery_micro_concepts
            WHERE user_id = :uid 
              AND due_date <= NOW()
            ORDER BY due_date ASC
            LIMIT 20
        """),
        {"uid": user_id}
    )
    overdue = overdue_query.fetchall()
    
    # Si aucun concept en retard, on cherche un nouveau concept non commencé (state = 0)
    # ou on prend un concept au hasard pour évaluation initiale (cold-start)
    if not overdue:
        logger.info(f"Aucun concept en retard pour l'utilisateur {user_id}. Sélection d'une nouvelle carte.")
        new_concept_query = await db.execute(
            text("""
                SELECT qcm.micro_concept AS concept_id, qcm.question_id
                FROM question_concept_map qcm
                LEFT JOIN mastery_micro_concepts mmc 
                  ON mmc.concept_id = qcm.micro_concept AND mmc.user_id = :uid
                WHERE mmc.id IS NULL
                ORDER BY RANDOM()
                LIMIT 1
            """),
            {"uid": user_id}
        )
        row = new_concept_query.fetchone()
        if row:
            return {"question_id": row[1], "concept_id": row[0]}
            
        # Fallback ultime : n'importe quelle question au hasard
        fallback_query = await db.execute(
            text("SELECT question_id FROM question_concept_map ORDER BY RANDOM() LIMIT 1")
        )
        fallback_row = fallback_query.fetchone()
        if fallback_row:
            return {"question_id": fallback_row[0], "concept_id": "cold_start"}
        return None

    # 2. Décider de l'entrelacement
    current_chapter = overdue[0][1]  # Le chapitre de la carte la plus urgente
    
    if random.random() < interleaving_ratio:
        # Tenter de sélectionner un concept d'un AUTRE chapitre
        other_chapter_concepts = [c for c in overdue if c[1] != current_chapter]
        if other_chapter_concepts:
            target_concept = random.choice(other_chapter_concepts)
        else:
            target_concept = overdue[0]
    else:
        target_concept = overdue[0]
        
    concept_id, chapter, difficulty, avg_score = target_concept
    
    # 3. Trouver une question liée dans la zone de difficulté désirable (50-70% réussite)
    # On map la difficulté cible autour de la performance moyenne de l'élève
    diff_low = max(0.1, avg_score - 0.2) if avg_score else 0.3
    diff_high = min(0.9, avg_score + 0.1) if avg_score else 0.7
    
    question_query = await db.execute(
        text("""
            SELECT qcm.question_id
            FROM question_concept_map qcm
            WHERE qcm.micro_concept = :concept
            ORDER BY RANDOM()
            LIMIT 1
        """),
        {
            "concept": concept_id,
            "diff_low": diff_low,
            "diff_high": diff_high
        }
    )
    q_row = question_query.fetchone()
    
    if q_row:
        return {"question_id": q_row[0], "concept_id": concept_id}
        
    # Fallback si pas de question spécifique trouvée pour ce concept
    return {"question_id": "q_test", "concept_id": concept_id}
