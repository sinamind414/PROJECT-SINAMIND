"""
services/evaluation_fsrs.py — Application d'un résultat d'évaluation à FSRS.

Extrait du bloc inline de routes/evaluate.py pour être réutilisé par le drill
( Phase 2 ) SANS dupliquer la logique. Évite un troisième chemin FSRS
incohérent — le drill et /api/evaluate mettent à jour la mémoire de la
même façon.

Contrat :
  input  : db, user_id, question_id, reponse_eleve, question, eval_result
  output : next_review_date ( ISO str ) ou None
"""

import logging
from datetime import UTC, datetime

from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession

logger = logging.getLogger("khawarizmi.evaluate")


async def apply_evaluation_to_fsrs(
    db: AsyncSession,
    user_id,
    question_id: str,
    reponse_eleve: str,
    question: dict,
    eval_result: dict,
):
    """Met à jour FSRS à partir d'un résultat d'évaluation.

    Deux chemins selon la qualité de l'éval :
      - GPT4O / FALLBACK_L2 → graphe de concepts ( mise à jour riche )
      - sinon ( L3 / erreur ) → carte en attente ( pending_real_evaluation )
    """
    if eval_result["source"] in ["GPT4O", "FALLBACK_L2"]:
        from services.fsrs_graph import (
            QuestionConceptMapping,
            load_concept_graph,
            update_concept_graph,
        )
        from services.fsrs_persistence import (
            get_concept_mapping,
            get_concept_states,
            save_concept_updates,
        )

        concepts_dict = await get_concept_mapping(db, question_id)
        if not concepts_dict:
            concept_cle = question.get("concept_cle", "concept_general")
            concepts_dict = {concept_cle: 1.0}

        mapping = QuestionConceptMapping(question_id=question_id, concepts=concepts_dict)

        concept_graph = await load_concept_graph(db)

        all_concept_ids = list(concepts_dict.keys())
        for c_id in list(all_concept_ids):
            for prereq in concept_graph.get(c_id, []):
                if prereq not in all_concept_ids:
                    all_concept_ids.append(prereq)

        concept_states = await get_concept_states(db, user_id, all_concept_ids)

        res_config = await db.execute(
            text("SELECT fsrs_config FROM users WHERE id = :uid"), {"uid": user_id}
        )
        config_row = res_config.fetchone()
        user_fsrs_config = config_row[0] if config_row else None

        updates = update_concept_graph(
            user_id=user_id,
            question_id=question_id,
            evaluation_result=eval_result,
            mapping=mapping,
            concept_states=concept_states,
            now=datetime.now(UTC),
            user_fsrs_config=user_fsrs_config,
            graph=concept_graph,
        )

        next_review_date = await save_concept_updates(
            db, user_id, question, updates, eval_result
        )

        if eval_result.get("needs_l1_review"):
            from services.reconciliation_queue import PendingReview, enque_for_l1_review

            review = PendingReview(
                student_id=str(user_id),
                question_id=question_id,
                answer=reponse_eleve,
                l2_score=float(eval_result["score"]) / 10.0,
                session_id="",
                timestamp=datetime.now(UTC),
            )
            await enque_for_l1_review(review)

        logger.info(
            f"EVAL_OK | user={user_id} | q={question_id} | "
            f"score={eval_result['score']} | source={eval_result['source']} | "
            f"next_review={next_review_date}"
        )
        return next_review_date

    # Fallback L3 ou erreur totale : carte en attente ( Tag )
    await db.execute(
        text("""
            INSERT INTO mastery_micro_concepts
                (user_id, micro_concept_id, concept_id, chapter, pending_real_evaluation, updated_at)
            VALUES
                (:user_id, :mc_id, :mc_id, :chapter, TRUE, NOW())
            ON CONFLICT (user_id, concept_id)
            DO UPDATE SET pending_real_evaluation = TRUE, updated_at = NOW()
        """),
        {
            "user_id": user_id,
            "mc_id": question_id,
            "chapter": question.get("chapitre_id", "ch_inconnu"),
        },
    )
    await db.commit()

    logger.warning(
        f"PENDING_TAGGED | user={user_id} | q={question_id} | source={eval_result['source']}"
    )
    return None
