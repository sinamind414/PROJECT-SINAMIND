"""Routes Document Analysis — 7 endpoints.

Permet à l'élève de pratiquer l'analyse de documents SVT
avec évaluation regex + répétition espacée FSRS.
"""

import json
import logging
from datetime import datetime, timezone, timedelta
from typing import Dict, List

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession

from database import get_db
from deps import get_current_user, get_scheduler
from schemas.document_analysis import (
    EvaluateRequest,
    EvaluateResponse,
    AnswerEvaluation,
    DaReviewRequest,
    DaFsrsItem,
    DaProgressResponse,
    WeakSpotsResponse,
    WeakSpot,
)
from services.document_analysis_service import evaluate_answer, score_to_fsrs_rating
from fsrs import Card, Rating as FsrsRating

logger = logging.getLogger("khawarizmi.api")
router = APIRouter(prefix="/api/document-analysis", tags=["Document Analysis"])


# ── 1. GET /api/document-analysis/scenarios — liste ──

@router.get("/scenarios")
async def lister_scenarios(
    current_user: Dict = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Retourne la liste de tous les scénarios d'analyse de documents."""
    result = await db.execute(
        text("""
            SELECT s.id, s.slug, s.chapter_slug, s.unit_key,
                   s.title_ar, s.subtitle_ar, s.context_ar,
                   s.dominant_skills,
                   (SELECT COUNT(*) FROM da_documents d WHERE d.scenario_id = s.id) AS nb_documents,
                   (SELECT COUNT(*) FROM da_questions q WHERE q.scenario_id = s.id) AS nb_questions
            FROM da_scenarios s
            ORDER BY s.unit_key, s.slug
        """)
    )
    rows = result.fetchall()
    return [
        {**dict(r._mapping), "id": str(r._mapping["id"])}
        for r in rows
    ]


# ── 2. GET /api/document-analysis/scenarios/{slug} — détail ──

@router.get("/scenarios/{slug}")
async def detail_scenario(
    slug: str,
    current_user: Dict = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Retourne un scénario complet avec documents et questions (SANS model answers)."""
    result = await db.execute(
        text("""
            SELECT id, slug, chapter_slug, unit_key, title_ar, subtitle_ar,
                   context_ar, mindmap_node_id, dominant_skills
            FROM da_scenarios
            WHERE slug = :slug
        """),
        {"slug": slug},
    )
    row = result.fetchone()
    if not row:
        raise HTTPException(404, f"Scénario introuvable : {slug}")

    scenario = dict(row._mapping)
    scenario_id = scenario["id"]

    docs_result = await db.execute(
        text("""
            SELECT doc_type, title_ar, caption_ar, data, sort_order
            FROM da_documents
            WHERE scenario_id = :sid
            ORDER BY sort_order
        """),
        {"sid": scenario_id},
    )
    documents = [
        {
            "type": r._mapping["doc_type"],
            "title_ar": r._mapping["title_ar"],
            "caption_ar": r._mapping["caption_ar"],
            "data": r._mapping["data"],
        }
        for r in docs_result.fetchall()
    ]

    questions_result = await db.execute(
        text("""
            SELECT id, verb_slug, level, n, title_ar, skill_ar,
                   doc_ref, prompt_ar, placeholder_ar
            FROM da_questions
            WHERE scenario_id = :sid
            ORDER BY n
        """),
        {"sid": scenario_id},
    )
    questions = [
        {
            "id": str(r._mapping["id"]),
            "verb_slug": r._mapping["verb_slug"],
            "level": r._mapping["level"],
            "n": r._mapping["n"],
            "title_ar": r._mapping["title_ar"],
            "skill_ar": r._mapping["skill_ar"],
            "doc_ref": r._mapping["doc_ref"],
            "prompt_ar": r._mapping["prompt_ar"],
            "placeholder_ar": r._mapping["placeholder_ar"],
        }
        for r in questions_result.fetchall()
    ]

    return {
        **{k: v for k, v in scenario.items() if k != "id"},
        "id": str(scenario_id),
        "documents": documents,
        "questions": questions,
    }


# ── 3. POST /api/document-analysis/evaluate — évaluer ──

@router.post("/evaluate", response_model=EvaluateResponse)
async def evaluer_reponses(
    body: EvaluateRequest,
    current_user: Dict = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Évalue les réponses d'un élève pour un scénario donné."""
    result = await db.execute(
        text("SELECT id FROM da_scenarios WHERE slug = :slug"),
        {"slug": body.scenario_id},
    )
    row = result.fetchone()
    if not row:
        raise HTTPException(404, f"Scénario introuvable : {body.scenario_id}")
    scenario_id = row._mapping["id"]

    session_result = await db.execute(
        text("""
            INSERT INTO da_sessions (user_id, scenario_id, chapter_slug, score_global, nb_questions)
            VALUES (:user_id, :scenario_id, :chapter_slug, 0, :nb)
            RETURNING id
        """),
        {
            "user_id": current_user["id"],
            "scenario_id": scenario_id,
            "chapter_slug": body.chapter_slug,
            "nb": len(body.answers),
        },
    )
    session_id = session_result.fetchone()._mapping["id"]

    evaluations: List[AnswerEvaluation] = []
    total_score = 0
    fsrs_count = 0

    for ans in body.answers:
        if ans.question_id:
            q_result = await db.execute(
                text("SELECT id, verb_slug, model_answer_ar FROM da_questions WHERE id = :qid"),
                {"qid": ans.question_id},
            )
        else:
            q_result = await db.execute(
                text("""
                    SELECT q.id, q.verb_slug, q.model_answer_ar
                    FROM da_questions q
                    JOIN da_scenarios s ON q.scenario_id = s.id
                    WHERE s.slug = :scenario_slug AND q.verb_slug = :verb_slug
                """),
                {"scenario_slug": body.scenario_id, "verb_slug": ans.verb_slug},
            )
        q_row = q_result.fetchone()
        if not q_row:
            continue

        verb_slug = q_row._mapping["verb_slug"]
        model_answer = q_row._mapping["model_answer_ar"]
        question_id = str(q_row._mapping["id"])

        evaluation = evaluate_answer(verb_slug, ans.answer, model_answer)
        evaluation["question_id"] = question_id

        await db.execute(
            text("""
                INSERT INTO da_answers
                    (session_id, question_id, verb_slug, chapter_slug,
                     answer_text, score, score_max, percentage, feedback_ar,
                     success, errors, missing_markers, forbidden_found)
                VALUES
                    (:session_id, :question_id, :verb_slug, :chapter_slug,
                     :answer_text, :score, :score_max, :percentage, :feedback_ar,
                     :success, :errors, :missing_markers, :forbidden_found)
            """),
            {
                "session_id": session_id,
                "question_id": question_id,
                "verb_slug": verb_slug,
                "chapter_slug": body.chapter_slug or "",
                "answer_text": ans.answer,
                "score": evaluation["score"],
                "score_max": evaluation["score_max"],
                "percentage": evaluation["percentage"],
                "feedback_ar": evaluation["advice"],
                "success": json.dumps(evaluation["success"], ensure_ascii=False),
                "errors": json.dumps(evaluation["errors"], ensure_ascii=False),
                "missing_markers": json.dumps(evaluation["missing_markers"], ensure_ascii=False),
                "forbidden_found": json.dumps(evaluation["forbidden_found"], ensure_ascii=False),
            },
        )

        await _update_fsrs(
            db=db,
            user_id=current_user["id"],
            verb_slug=verb_slug,
            chapter_slug=body.chapter_slug or "general",
            percentage=evaluation["percentage"],
        )
        fsrs_count += 1
        total_score += evaluation["percentage"]

        evaluations.append(AnswerEvaluation(**evaluation))

    score_global = round(total_score / max(len(evaluations), 1))
    await db.execute(
        text("UPDATE da_sessions SET score_global = :score WHERE id = :sid"),
        {"score": score_global, "sid": session_id},
    )
    await db.commit()

    logger.info(
        f"DA evaluate : user={current_user['id']} scenario={body.scenario_id} "
        f"score={score_global}% questions={len(evaluations)}"
    )

    return EvaluateResponse(
        scenario_id=body.scenario_id,
        session_id=str(session_id),
        score_global=score_global,
        nb_questions=len(evaluations),
        evaluations=evaluations,
        fsrs_updated=fsrs_count,
    )


# ── 4. GET /api/document-analysis/scenarios/{slug}/correction ──

@router.get("/scenarios/{slug}/correction")
async def correction_scenario(
    slug: str,
    current_user: Dict = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Retourne les model answers d'un scénario (après évaluation)."""
    result = await db.execute(
        text("SELECT id FROM da_scenarios WHERE slug = :slug"),
        {"slug": slug},
    )
    row = result.fetchone()
    if not row:
        raise HTTPException(404, f"Scénario introuvable : {slug}")

    q_result = await db.execute(
        text("""
            SELECT id, verb_slug, level, n, title_ar, skill_ar,
                   doc_ref, prompt_ar, placeholder_ar,
                   model_answer_ar, learning_focus_ar
            FROM da_questions
            WHERE scenario_id = :sid
            ORDER BY n
        """),
        {"sid": row._mapping["id"]},
    )
    questions = [
        {
            "id": str(r._mapping["id"]),
            "verb_slug": r._mapping["verb_slug"],
            "level": r._mapping["level"],
            "n": r._mapping["n"],
            "title_ar": r._mapping["title_ar"],
            "skill_ar": r._mapping["skill_ar"],
            "doc_ref": r._mapping["doc_ref"],
            "prompt_ar": r._mapping["prompt_ar"],
            "placeholder_ar": r._mapping["placeholder_ar"],
            "model_answer_ar": r._mapping["model_answer_ar"],
            "learning_focus_ar": r._mapping["learning_focus_ar"],
        }
        for r in q_result.fetchall()
    ]
    return {"scenario_id": slug, "questions": questions}


# ── 5. GET /api/document-analysis/progress — progression FSRS ──

@router.get("/progress", response_model=DaProgressResponse)
async def progression_da(
    current_user: Dict = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Retourne la progression FSRS de l'élève sur l'analyse de documents."""
    result = await db.execute(
        text("""
            SELECT verb_slug, chapter_slug, stability, difficulty,
                   last_score, attempts, prochaine_revision, interval_jours
            FROM da_fsrs
            WHERE user_id = :user_id
            ORDER BY prochaine_revision ASC
        """),
        {"user_id": current_user["id"]},
    )
    rows = result.fetchall()

    now = datetime.now(timezone.utc)
    skills: List[DaFsrsItem] = []
    dues = 0

    for r in rows:
        m = r._mapping
        est_due = (
            m["prochaine_revision"] is not None
            and m["prochaine_revision"] <= now
        ) or m["prochaine_revision"] is None
        if est_due:
            dues += 1
        skills.append(DaFsrsItem(
            verb_slug=m["verb_slug"],
            chapter_slug=m["chapter_slug"],
            stability=m["stability"] or 0.0,
            difficulty=m["difficulty"] or 0.0,
            last_score=m["last_score"] or 0,
            attempts=m["attempts"] or 0,
            est_due=est_due,
            prochaine_revision=m["prochaine_revision"].isoformat() if m["prochaine_revision"] else None,
            interval_jours=m["interval_jours"] or 0.0,
        ))

    return DaProgressResponse(
        user_id=str(current_user["id"]),
        nb_skills=len(skills),
        dues_aujourd_hui=dues,
        skills=skills,
    )


# ── 6. POST /api/document-analysis/review — révision FSRS ──

@router.post("/review")
async def reviser_da(
    body: DaReviewRequest,
    current_user: Dict = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Marque une révision FSRS pour un verbe×chapitre et programme la prochaine."""
    scheduler = get_scheduler()

    result = await db.execute(
        text("""
            SELECT stability, difficulty, fsrs_state
            FROM da_fsrs
            WHERE user_id = :user_id AND verb_slug = :verb AND chapter_slug = :chapter
        """),
        {
            "user_id": current_user["id"],
            "verb": body.verb_slug,
            "chapter": body.chapter_slug,
        },
    )
    row = result.fetchone()

    card = Card()
    if row and row._mapping["fsrs_state"]:
        state = row._mapping["fsrs_state"]
        if isinstance(state, str):
            state = json.loads(state)
        card.stability = state.get("stability", 0.0)
        card.difficulty = state.get("difficulty", 0.0)
        card.reps = state.get("reps", 0)
        card.lapses = state.get("lapses", 0)

    rating = body.rating
    if body.score_percentage is not None:
        rating = score_to_fsrs_rating(body.score_percentage)

    fsrs_rating = FsrsRating(rating)
    new_card = scheduler.review_card(card, fsrs_rating)

    now = datetime.now(timezone.utc)
    next_review = now + timedelta(days=new_card.scheduled_days)

    fsrs_json = json.dumps({
        "stability": new_card.stability,
        "difficulty": new_card.difficulty,
        "scheduled_days": new_card.scheduled_days,
        "reps": new_card.reps,
        "lapses": new_card.lapses,
        "state": str(new_card.state),
        "last_review": now.isoformat(),
    })

    await db.execute(
        text("""
            INSERT INTO da_fsrs
                (user_id, verb_slug, chapter_slug, stability, difficulty,
                 fsrs_state, prochaine_revision, interval_jours, last_score,
                 attempts, updated_at)
            VALUES
                (:user_id, :verb, :chapter, :stability, :difficulty,
                 :fsrs_state, :next_review, :interval, :score, 1, NOW())
            ON CONFLICT (user_id, verb_slug, chapter_slug) DO UPDATE SET
                stability = EXCLUDED.stability,
                difficulty = EXCLUDED.difficulty,
                fsrs_state = EXCLUDED.fsrs_state,
                prochaine_revision = EXCLUDED.prochaine_revision,
                interval_jours = EXCLUDED.interval_jours,
                last_score = EXCLUDED.last_score,
                attempts = da_fsrs.attempts + 1,
                updated_at = NOW()
        """),
        {
            "user_id": current_user["id"],
            "verb": body.verb_slug,
            "chapter": body.chapter_slug,
            "stability": new_card.stability,
            "difficulty": new_card.difficulty,
            "fsrs_state": fsrs_json,
            "next_review": next_review,
            "interval": float(new_card.scheduled_days),
            "score": body.score_percentage or 0,
        },
    )
    await db.commit()

    logger.info(
        f"DA review : user={current_user['id']} verb={body.verb_slug} "
        f"chapter={body.chapter_slug} rating={rating} next={next_review.isoformat()}"
    )

    return {
        "verb_slug": body.verb_slug,
        "chapter_slug": body.chapter_slug,
        "rating": rating,
        "next_review": next_review.isoformat(),
        "interval_days": float(new_card.scheduled_days),
        "stability": new_card.stability,
        "difficulty": new_card.difficulty,
    }


# ── 7. GET /api/document-analysis/weak-spots — faiblesses ──

@router.get("/weak-spots", response_model=WeakSpotsResponse)
async def faiblesses_da(
    current_user: Dict = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Retourne les faiblesses de l'élève (compétences dues + scores faibles)."""
    now = datetime.now(timezone.utc)
    result = await db.execute(
        text("""
            SELECT verb_slug, chapter_slug, last_score, attempts,
                   prochaine_revision
            FROM da_fsrs
            WHERE user_id = :user_id
              AND (last_score < 75 OR prochaine_revision IS NULL OR prochaine_revision <= :now)
            ORDER BY last_score ASC, prochaine_revision ASC
            LIMIT 20
        """),
        {"user_id": current_user["id"], "now": now},
    )
    rows = result.fetchall()

    weak_spots = []
    for r in rows:
        m = r._mapping
        est_due = (
            m["prochaine_revision"] is not None
            and m["prochaine_revision"] <= now
        ) or m["prochaine_revision"] is None
        weak_spots.append(WeakSpot(
            verb_slug=m["verb_slug"],
            chapter_slug=m["chapter_slug"],
            last_score=m["last_score"] or 0,
            attempts=m["attempts"] or 0,
            est_due=est_due,
        ))

    return WeakSpotsResponse(
        user_id=str(current_user["id"]),
        total=len(weak_spots),
        weak_spots=weak_spots,
    )


# ── Helper : update FSRS après évaluation ─────────

async def _update_fsrs(
    db: AsyncSession,
    user_id: str,
    verb_slug: str,
    chapter_slug: str,
    percentage: int,
):
    """Met à jour le score et le compteur FSRS (sans programmer la prochaine révision)."""
    await db.execute(
        text("""
            INSERT INTO da_fsrs
                (user_id, verb_slug, chapter_slug, last_score, attempts, updated_at)
            VALUES
                (:user_id, :verb, :chapter, :score, 1, NOW())
            ON CONFLICT (user_id, verb_slug, chapter_slug) DO UPDATE SET
                last_score = EXCLUDED.last_score,
                attempts = da_fsrs.attempts + 1,
                updated_at = NOW()
        """),
        {"user_id": user_id, "verb": verb_slug, "chapter": chapter_slug, "score": percentage},
    )
