"""Routes Document Analysis — 7 endpoints.

Permet à l'élève de pratiquer l'analyse de documents SVT
avec grade() local (0 LLM) + répétition espacée FSRS.
"""

import json
import logging
from datetime import UTC, datetime, timedelta

from fastapi import APIRouter, Depends, HTTPException
from fsrs import Card
from fsrs import Rating as FsrsRating
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession

from database import get_db
from deps import get_current_user, get_scheduler
from schemas.document_analysis import (
    AnswerEvaluation,
    DaFsrsItem,
    DaProgressResponse,
    DaReviewRequest,
    EvaluateRequest,
    EvaluateResponse,
    WeakSpot,
    WeakSpotsResponse,
)
from services.document_analysis_service import score_to_fsrs_rating
from services.hashing import hash_answer
from services.grade_adapter import (
    UNGRADED_AR,
    grade_or_none,
    may_write_fsrs,
    persist_grade_columns,
    resolve_question_id,
    to_verb_eval,
)
from services.local_grader import TRAINING_BANNER_AR

logger = logging.getLogger("khawarizmi.api")
router = APIRouter(prefix="/api/document-analysis", tags=["Document Analysis"])


# ── 1. GET /api/document-analysis/scenarios — liste ──


@router.get("/scenarios")
async def lister_scenarios(
    current_user: dict = Depends(get_current_user),
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
    return [{**dict(r._mapping), "id": str(r._mapping["id"])} for r in rows]


# ── 2. GET /api/document-analysis/scenarios/{slug} — détail ──


@router.get("/scenarios/{slug}")
async def detail_scenario(
    slug: str,
    current_user: dict = Depends(get_current_user),
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
    current_user: dict = Depends(get_current_user),
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

    evaluations: list[AnswerEvaluation] = []
    total_score = 0
    fsrs_count = 0

    for ans in body.answers:
        if ans.question_id:
            q_result = await db.execute(
                text("SELECT id, verb_slug FROM da_questions WHERE id = :qid"),
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
                "success": [],
                "errors": [UNGRADED_AR],
                "missing_markers": [],
                "forbidden_found": [],
                "advice": f"{UNGRADED_AR} {TRAINING_BANNER_AR}",
                "dominant_error_code": "ungraded",
                "ungraded": True,
            }
        else:
            mapped = to_verb_eval(graded)
            evaluation = {
                "question_id": question_id,
                "verb_slug": graded.verb_slug or verb_slug,
                "score": mapped["score"],
                "score_max": mapped["score_max"],
                "percentage": mapped["percentage"],
                "success": mapped["success"],
                "errors": mapped["errors"],
                "missing_markers": [],
                "forbidden_found": [],
                "advice": mapped["advice"],
                "dominant_error_code": mapped["dominant_error_code"],
                "ungraded": False,
            }

        meta = persist_grade_columns(graded)
        await db.execute(
            text("""
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
            """),
            {
                "session_id": session_id,
                "question_id": question_id,
                "verb_slug": verb_slug,
                "chapter_slug": body.chapter_slug or "",
                "answer_text": hash_answer(ans.answer),
                "score": evaluation["score"],
                "score_max": evaluation["score_max"],
                "percentage": evaluation["percentage"],
                "feedback_ar": evaluation["advice"],
                "success": json.dumps(evaluation["success"], ensure_ascii=False),
                "errors": json.dumps(evaluation["errors"], ensure_ascii=False),
                "missing_markers": json.dumps(evaluation["missing_markers"], ensure_ascii=False),
                "forbidden_found": json.dumps(evaluation["forbidden_found"], ensure_ascii=False),
                **meta,
            },
        )

        if graded is not None and may_write_fsrs(graded):
            await _update_fsrs(
                db=db,
                user_id=current_user["id"],
                verb_slug=verb_slug,
                chapter_slug=body.chapter_slug or "general",
                percentage=evaluation["percentage"],
            )
            fsrs_count += 1
        if not evaluation["ungraded"]:
            total_score += evaluation["percentage"]

        evaluations.append(AnswerEvaluation(**evaluation))

    graded_n = sum(1 for e in evaluations if not e.ungraded)
    score_global = round(total_score / graded_n) if graded_n else 0
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
    current_user: dict = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Model answers seulement après une eval persistée de CET élève (G11)."""
    result = await db.execute(
        text("SELECT id FROM da_scenarios WHERE slug = :slug"),
        {"slug": slug},
    )
    row = result.fetchone()
    if not row:
        raise HTTPException(404, "Correction indisponible")

    proof = await db.execute(
        text(
            """
            SELECT 1
            FROM da_sessions sess
            JOIN da_answers a ON a.session_id = sess.id
            WHERE sess.user_id = :uid AND sess.scenario_id = :sid
            LIMIT 1
            """
        ),
        {"uid": current_user["id"], "sid": row._mapping["id"]},
    )
    if not proof.fetchone():
        raise HTTPException(404, "Correction indisponible")

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
    current_user: dict = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Retourne la progression FSRS de l'élève sur l'analyse de documents."""
    # S3 finale : lecture via la vue consolidée (mastery-first) — les tables
    # héritées da_fsrs / action_verb_progress sont supprimées (migration 034).
    from services.fsrs_unified import get_user_memory

    memory = await get_user_memory(db, current_user["id"], kinds=("verb_chapter",))
    memory.sort(key=lambda i: i.due or datetime.max.replace(tzinfo=UTC))

    now = datetime.now(UTC)
    skills: list[DaFsrsItem] = []
    dues = 0

    for item in memory:
        verb, _, chapter = item.item_id.partition("::")
        est_due = item.due is None or item.due <= now
        if est_due:
            dues += 1
        skills.append(
            DaFsrsItem(
                verb_slug=verb or item.extra.get("verb_slug", ""),
                chapter_slug=item.chapter or chapter,
                stability=item.stability,
                difficulty=item.difficulty,
                last_score=item.last_score or 0,
                attempts=item.attempts,
                est_due=est_due,
                prochaine_revision=item.due.isoformat() if item.due else None,
                interval_jours=item.interval_jours,
            )
        )

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
    current_user: dict = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Marque une révision FSRS pour un verbe×chapitre et programme la prochaine."""
    scheduler = get_scheduler()

    # S3 finale : lecture via la vue consolidée (mastery-first) — plus de
    # SELECT direct sur da_fsrs (table supprimée en 034).
    from services.fsrs_unified import get_user_memory, update_memory

    vc_id = f"{body.verb_slug}::{body.chapter_slug}"
    memory = await get_user_memory(db, current_user["id"], kinds=("verb_chapter",))
    vc_item = next((i for i in memory if i.item_id == vc_id), None)

    card = Card()
    if vc_item and vc_item.fsrs_state:
        state = vc_item.fsrs_state
        card.stability = state.get("stability", 0.0)
        card.difficulty = state.get("difficulty", 0.0)
        card.reps = state.get("reps", 0)
        card.lapses = state.get("lapses", 0)

    rating = body.rating
    if body.score_percentage is not None:
        rating = score_to_fsrs_rating(body.score_percentage)

    fsrs_rating = FsrsRating(rating)
    new_card = scheduler.review_card(card, fsrs_rating)

    now = datetime.now(UTC)
    next_review = now + timedelta(days=new_card.scheduled_days)

    fsrs_json = json.dumps(
        {
            "stability": new_card.stability,
            "difficulty": new_card.difficulty,
            "scheduled_days": new_card.scheduled_days,
            "reps": new_card.reps,
            "lapses": new_card.lapses,
            "state": str(new_card.state),
            "last_review": now.isoformat(),
        }
    )

    await update_memory(
        db, current_user["id"], "verb_chapter",
        item_id=vc_id,
        chapter=body.chapter_slug,
        stability=new_card.stability,
        difficulty=new_card.difficulty,
        fsrs_state={
            "stability": new_card.stability,
            "difficulty": new_card.difficulty,
            "scheduled_days": new_card.scheduled_days,
            "reps": new_card.reps,
            "lapses": new_card.lapses,
            "state": str(new_card.state),
            "last_review": now.isoformat(),
        },
        due=next_review,
        interval_jours=float(new_card.scheduled_days),
        last_score=body.score_percentage or 0,
        attempts_delta=1,
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
    current_user: dict = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Retourne les faiblesses de l'élève (compétences dues + scores faibles).

    S3 finale : lecture via la vue consolidée (mastery-first) — plus de
    SELECT direct sur da_fsrs (table supprimée en 034).
    """
    from services.fsrs_unified import get_user_memory

    now = datetime.now(UTC)
    memory = await get_user_memory(db, current_user["id"], kinds=("verb_chapter",))

    # Filtre : score < 75 OU due (prochaine_revision NULL ou passée)
    candidates = [
        i for i in memory
        if (i.last_score is None or i.last_score < 75)
        or i.due is None or i.due <= now
    ]
    candidates.sort(key=lambda i: (i.last_score if i.last_score is not None else 0,
                                   i.due or datetime.max.replace(tzinfo=UTC)))

    weak_spots = []
    for item in candidates[:20]:
        verb, _, chapter = item.item_id.partition("::")
        est_due = item.due is None or item.due <= now
        weak_spots.append(
            WeakSpot(
                verb_slug=verb or item.extra.get("verb_slug", ""),
                chapter_slug=item.chapter or chapter,
                last_score=item.last_score or 0,
                attempts=item.attempts,
                est_due=est_due,
            )
        )

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
    """Met à jour le score et le compteur FSRS (sans programmer la prochaine révision).

    S3 finale : écriture via le service unifié — la table da_fsrs n'est plus
    écrite directement (table supprimée en 034).
    """
    from services.fsrs_unified import update_memory

    await update_memory(
        db, user_id, "verb_chapter",
        item_id=f"{verb_slug}::{chapter_slug}",
        chapter=chapter_slug,
        last_score=percentage,
        attempts_delta=1,
    )
