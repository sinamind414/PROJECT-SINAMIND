import logging
from datetime import UTC, datetime

from sqlalchemy import text as sa_text
from sqlalchemy.ext.asyncio import AsyncSession

from services.fsrs_persistence import get_concept_states, save_concept_updates
from services.fsrs_graph import QuestionConceptMapping, update_concept_graph
from services.questions import get_question

logger = logging.getLogger("khawarizmi.evaluation_mode")


async def handle_evaluation(req, user: dict, db: AsyncSession, openai_client):
    from routes.evaluate import evaluate_with_fallback, normalize_result

    user_id = user["id"]
    question = get_question(req.question_id)
    if not question:
        from fastapi import HTTPException
        raise HTTPException(404, f"Question {req.question_id} introuvable")

    eval_result = await evaluate_with_fallback(question, req, openai_client, user_id, db)

    next_review_date = None

    if eval_result["source"] in ("GPT4O", "FALLBACK_L2"):
        res = await db.execute(
            sa_text("""
                SELECT micro_concept AS concept_id, weight
                FROM question_concept_map
                WHERE question_id = :qid
            """),
            {"qid": req.question_id},
        )
        rows = res.fetchall()

        if not rows:
            concept_cle = question.get("concept_cle", "concept_general")
            concepts_dict = {concept_cle: 1.0}
        else:
            concepts_dict = {r[0]: r[1] for r in rows}

        from services.fsrs_graph import load_concept_graph

        concept_ids = list(concepts_dict.keys())
        concept_graph = await load_concept_graph(db)

        for c_id in list(concept_ids):
            for prereq in concept_graph.get(c_id, []):
                if prereq not in concept_ids:
                    concept_ids.append(prereq)
            for dep, prereqs in concept_graph.items():
                if c_id in prereqs and dep not in concept_ids:
                    concept_ids.append(dep)

        concept_states = await get_concept_states(db, user_id, concept_ids)

        res_cfg = await db.execute(
            sa_text("SELECT fsrs_config FROM users WHERE id = :uid"),
            {"uid": user_id},
        )
        cfg_row = res_cfg.fetchone()
        user_fsrs_config = cfg_row[0] if cfg_row else None

        mapping = QuestionConceptMapping(question_id=req.question_id, concepts=concepts_dict)
        updates = update_concept_graph(
            user_id=user_id,
            question_id=req.question_id,
            evaluation_result=eval_result,
            mapping=mapping,
            concept_states=concept_states,
            now=datetime.now(UTC),
            user_fsrs_config=user_fsrs_config,
            graph=concept_graph,
        )

        next_review_date = await save_concept_updates(db, user_id, question, updates, eval_result)

        if eval_result.get("needs_l1_review"):
            from services.reconciliation_queue import PendingReview, enque_for_l1_review
            await enque_for_l1_review(PendingReview(
                student_id=str(user_id),
                question_id=req.question_id,
                answer=req.reponse_eleve,
                l2_score=float(eval_result["score"]) / 10.0,
                session_id="",
                timestamp=datetime.now(UTC),
            ))

    else:
        await db.execute(
            sa_text("""
                INSERT INTO mastery_micro_concepts
                    (user_id, concept_id, chapter, pending_real_evaluation, updated_at)
                VALUES (:uid, :mc_id, :chapter, TRUE, NOW())
                ON CONFLICT (user_id, concept_id)
                DO UPDATE SET pending_real_evaluation = TRUE, updated_at = NOW()
            """),
            {
                "uid": user_id,
                "mc_id": req.question_id,
                "chapter": question.get("chapitre_id", "ch_inconnu"),
            },
        )
        await db.commit()

    eval_result = normalize_result(eval_result)

    if req.lang == "ar":
        from services.feedback_translator import translate_feedback
        eval_result["feedback"] = translate_feedback(eval_result.get("feedback", ""))

    methodology_result = None
    if req.include_methodology:
        try:
            from methodology.evaluator import evaluate_methodology
            question_texte = question.get("texte", "") or question.get("texte_ar", "")
            methodo = await evaluate_methodology(
                instruction=question_texte,
                student_answer=req.reponse_eleve,
            )
            methodology_result = methodo
        except Exception as e:
            logger.warning(f"Methodology skipped: {e}")

    return {
        "mode": "evaluation",
        "score": eval_result["score"],
        "statut": eval_result["statut"],
        "feedback": eval_result["feedback"],
        "manquant": eval_result["manquant"],
        "next_review_date": next_review_date,
        "source": eval_result["source"],
        "methodology": methodology_result,
    }
