"""POST /api/document-analysis/evaluate-v2 — GELÉ L2/LLM.

Même juge que DA v1 : grade(). Sans Rubric → ungraded. 0 OpenAI, 0 L2.
"""

from __future__ import annotations

import json
import logging

from fastapi import APIRouter, Depends, HTTPException, Request
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession

from deps import get_current_user, get_db
from rate_limit import evaluate_limit, limiter
from schemas.document_analysis import EvaluateRequest
from services.grade_adapter import (
    UNGRADED_AR,
    grade_or_none,
    may_write_fsrs,
    persist_grade_columns,
    resolve_question_id,
    to_verb_eval,
)
from services.hashing import hash_answer
from services.local_grader import TRAINING_BANNER_AR

logger = logging.getLogger("khawarizmi.document_analysis_v2")
router = APIRouter(prefix="/api/document-analysis", tags=["Document Analysis V2"])

_HINT_AR = "أرسل الإجابة للتصحيح المحلي — لا تلميح توليدي."


@router.post("/evaluate-v2")
@limiter.limit(evaluate_limit)
async def evaluer_reponses_v2(
    request: Request,
    body: EvaluateRequest,
    current_user: dict = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Note via grade(). ENABLE_EXTERNAL_LLM ignoré. Jamais L2 / LLM."""
    _ = request
    scenario = await db.execute(
        text("SELECT id FROM da_scenarios WHERE slug = :slug"),
        {"slug": body.scenario_id},
    )
    scenario_row = scenario.fetchone()
    if not scenario_row:
        raise HTTPException(404, f"Scénario introuvable : {body.scenario_id}")
    scenario_id = scenario_row._mapping["id"]

    if body.request_hint:
        return {
            "session_id": "",
            "score_global": 0,
            "score_max": 0,
            "percentage": 0,
            "evaluations": [
                {
                    "question_id": ans.question_id or "",
                    "verb_slug": ans.verb_slug,
                    "score": 0,
                    "score_max": 1,
                    "percentage": 0,
                    "highlights": [],
                    "matched_criteria": [],
                    "unmatched_criteria": [],
                    "feedback_ar": _HINT_AR,
                    "advice_ar": _HINT_AR,
                    "source": "ungraded",
                    "ungraded": True,
                    "banner_ar": TRAINING_BANNER_AR,
                }
                for ans in body.answers
            ],
            "technical_errors": 0,
        }

    session_result = await db.execute(
        text(
            """
            INSERT INTO da_sessions
                (user_id, scenario_id, chapter_slug, score_global, nb_questions)
            VALUES (:user_id, :scenario_id, :chapter_slug, 0, :nb)
            RETURNING id
            """
        ),
        {
            "user_id": current_user["id"],
            "scenario_id": scenario_id,
            "chapter_slug": body.chapter_slug,
            "nb": len(body.answers),
        },
    )
    session_id = session_result.fetchone()._mapping["id"]

    evaluations = []
    total_pct = 0
    graded_n = 0

    for ans in body.answers:
        if ans.question_id:
            q_result = await db.execute(
                text("SELECT id, verb_slug FROM da_questions WHERE id = :qid"),
                {"qid": ans.question_id},
            )
        else:
            q_result = await db.execute(
                text(
                    """
                    SELECT q.id, q.verb_slug
                    FROM da_questions q
                    JOIN da_scenarios s ON q.scenario_id = s.id
                    WHERE s.slug = :scenario_slug AND q.verb_slug = :verb_slug
                    """
                ),
                {"scenario_slug": body.scenario_id, "verb_slug": ans.verb_slug},
            )
        q_row = q_result.fetchone()
        if not q_row:
            continue

        verb_slug = q_row._mapping["verb_slug"]
        question_id = str(q_row._mapping["id"])
        qid = resolve_question_id(
            ans.question_id,
            question_id,
            f"{body.scenario_id}:{ans.question_id}" if ans.question_id else None,
            f"{body.scenario_id}:{question_id}",
        )
        graded = grade_or_none(qid, ans.answer)
        if graded is None:
            evaluation = {
                "question_id": question_id,
                "verb_slug": verb_slug,
                "score": 0,
                "score_max": 1,
                "percentage": 0,
                "highlights": [],
                "matched_criteria": [],
                "unmatched_criteria": [],
                "feedback_ar": f"{UNGRADED_AR} {TRAINING_BANNER_AR}",
                "advice_ar": UNGRADED_AR,
                "source": "ungraded",
                "ungraded": True,
                "success": [],
                "errors": [UNGRADED_AR],
                "dominant_error_code": "ungraded",
                "banner_ar": TRAINING_BANNER_AR,
            }
        else:
            mapped = to_verb_eval(graded)
            evaluation = {
                "question_id": question_id,
                "verb_slug": graded.verb_slug or verb_slug,
                "score": mapped["score"],
                "score_max": mapped["score_max"],
                "percentage": mapped["percentage"],
                "highlights": [],
                "matched_criteria": mapped["success"],
                "unmatched_criteria": [],
                "feedback_ar": mapped["advice"],
                "advice_ar": mapped["advice"],
                "source": "local_rubric",
                "ungraded": False,
                "success": mapped["success"],
                "errors": mapped["errors"],
                "dominant_error_code": mapped["dominant_error_code"],
                "banner_ar": TRAINING_BANNER_AR,
            }
            if may_write_fsrs(graded):
                from services.fsrs_unified import update_memory

                await update_memory(
                    db,
                    current_user["id"],
                    "verb_chapter",
                    item_id=f"{verb_slug}::{body.chapter_slug or 'general'}",
                    chapter=body.chapter_slug or "general",
                    last_score=mapped["percentage"],
                    attempts_delta=1,
                )
            total_pct += mapped["percentage"]
            graded_n += 1

        meta = persist_grade_columns(graded)
        await db.execute(
            text(
                """
                INSERT INTO da_answers
                    (session_id, question_id, verb_slug, chapter_slug,
                     answer_text, score, score_max, percentage, feedback_ar,
                     success, errors, missing_markers, forbidden_found,
                     rubric_version, grader_version, grading_engine,
                     science_status, stuffing_suspected, method_percent,
                     order_ok, diagnosis_code)
                VALUES
                    (:session_id, :question_id, :verb_slug, :chapter_slug,
                     :answer_text, :score, :score_max, :percentage, :feedback_ar,
                     :success, :errors, :missing_markers, :forbidden_found,
                     :rubric_version, :grader_version, :grading_engine,
                     :science_status, :stuffing_suspected, :method_percent,
                     :order_ok, :diagnosis_code)
                """
            ),
            {
                "session_id": session_id,
                "question_id": question_id,
                "verb_slug": verb_slug,
                "chapter_slug": body.chapter_slug or "",
                "answer_text": hash_answer(ans.answer),
                "score": evaluation["score"],
                "score_max": evaluation["score_max"],
                "percentage": evaluation["percentage"],
                "feedback_ar": evaluation["feedback_ar"],
                "success": json.dumps(evaluation.get("success") or [], ensure_ascii=False),
                "errors": json.dumps(evaluation.get("errors") or [], ensure_ascii=False),
                "missing_markers": json.dumps([], ensure_ascii=False),
                "forbidden_found": json.dumps([], ensure_ascii=False),
                **meta,
            },
        )
        evaluations.append(evaluation)

    global_pct = round(total_pct / graded_n) if graded_n else 0
    await db.execute(
        text("UPDATE da_sessions SET score_global = :pct WHERE id = :sid"),
        {"pct": global_pct, "sid": session_id},
    )
    await db.commit()

    logger.info(
        "eval_v2 | user=%s scenario=%s source=local_rubric pct=%s",
        current_user["id"],
        body.scenario_id,
        global_pct,
    )
    return {
        "session_id": str(session_id),
        "score_global": global_pct,
        "score_max": 100,
        "percentage": global_pct,
        "evaluations": evaluations,
        "technical_errors": 0,
    }
