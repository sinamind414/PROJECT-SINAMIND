"""Routes Action Verbs — 6 endpoints.

Permet à l'élève d'apprendre les techniques des verbes d'action
du BAC algérien via pratique guidée + répétition espacée FSRS.
"""

import json
import logging
from datetime import UTC, datetime, timedelta
from typing import Any

from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import JSONResponse
from fsrs import Card
from fsrs import Rating as FsrsRating
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession

from app_state import state
from database import get_db
from deps import get_current_user, get_scheduler
from schemas.action_verb import (
    EvaluateRequest,
    EvaluateResponse,
    VerbProgressItem,
    VerbProgressResponse,
    VerbReviewRequest,
)
from services.action_verbs_service import score_to_fsrs_rating
from services.grade_adapter import (
    grade_or_none,
    may_write_fsrs,
    resolve_question_id,
    to_verb_eval,
    ungraded_http,
)

logger = logging.getLogger("khawarizmi.api")
router = APIRouter(prefix="/api/action-verbs", tags=["Action Verbs"])


# ── 1. GET /api/action-verbs — liste des verbes ──


@router.get("")
async def lister_verbes(
    current_user: dict = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Retourne la liste de tous les verbes d'action (résumé)."""
    result = await db.execute(
        text("""
            SELECT slug, ar, fr, category, priority
            FROM action_verbs
            ORDER BY
                CASE priority WHEN 'high' THEN 0 WHEN 'medium' THEN 1 ELSE 2 END,
                slug
        """)
    )
    rows = result.fetchall()
    return [dict(r._mapping) for r in rows]


# ── 2. GET /api/action-verbs/{slug} — détail ──


@router.get("/{slug}")
async def detail_verbe(
    slug: str,
    current_user: dict = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Retourne le détail complet d'un verbe (méthodologie, marqueurs, exemples)."""
    result = await db.execute(
        text("""
            SELECT slug, ar, fr, category, priority,
                   definition_ar, objective_ar, formula_ar,
                   steps, required_markers, forbidden_markers,
                   common_errors, scoring_rules,
                   bad_example, good_example, feedback_template_ar
            FROM action_verbs
            WHERE slug = :slug
        """),
        {"slug": slug},
    )
    row = result.fetchone()
    if not row:
        raise HTTPException(404, f"Verbe introuvable : {slug}")
    return dict(row._mapping)


# ── 3. GET /api/action-verbs/{slug}/exercises — exercices ──


@router.get("/{slug}/exercises")
async def exercices_verbe(
    slug: str,
    current_user: dict = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Retourne les exercices d'un verbe."""
    result = await db.execute(
        text("""
            SELECT id, verb_slug, type, question_ar, context_ar,
                   model_answer_ar, difficulty
            FROM action_verb_exercises
            WHERE verb_slug = :slug
            ORDER BY difficulty ASC
        """),
        {"slug": slug},
    )
    rows = result.fetchall()
    if not rows:
        return []
    return [{**dict(r._mapping), "id": str(r._mapping["id"])} for r in rows]


# ── 4. POST /api/action-verbs/evaluate — évaluer ──


@router.post("/evaluate", response_model=EvaluateResponse)
async def evaluer_reponse(
    body: EvaluateRequest,
    current_user: dict = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Évalue la réponse d'un élève pour un verbe donné."""
    result = await db.execute(
        text("""
            SELECT slug, ar, fr, definition_ar, objective_ar, formula_ar,
                   steps, required_markers, forbidden_markers,
                   common_errors, scoring_rules, feedback_template_ar
            FROM action_verbs
            WHERE slug = :slug
        """),
        {"slug": body.verb_slug},
    )
    row = result.fetchone()
    if not row:
        raise HTTPException(404, f"Verbe introuvable : {body.verb_slug}")

    qid = resolve_question_id(body.exercise_id, f"verb:{body.verb_slug}")
    result = grade_or_none(qid, body.answer)
    if result is None:
        return JSONResponse(
            status_code=422,
            content=ungraded_http(body.exercise_id or f"verb:{body.verb_slug}"),
        )

    evaluation = to_verb_eval(result)
    if may_write_fsrs(result):
        await _enregistrer_tentative(
            db=db,
            user_id=current_user["id"],
            verb_slug=body.verb_slug,
            percentage=evaluation["percentage"],
        )

    logger.info(
        f"Action verb eval : user={current_user['id']} verb={body.verb_slug} "
        f"score={evaluation['percentage']}% source=local_rubric"
    )

    return EvaluateResponse(**evaluation)


# ── 5. GET /api/action-verbs/progress — progression FSRS ──


@router.get("/progress", response_model=VerbProgressResponse)
async def progression_verbes(
    current_user: dict = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Retourne la progression FSRS de l'élève sur tous les verbes."""
    # S3 finale : lecture via la vue consolidée (mastery-first, fallback avp)
    from services.fsrs_unified import get_user_memory

    memory = await get_user_memory(db, current_user["id"], kinds=("verb_action",))
    memory.sort(key=lambda i: i.due or datetime.max.replace(tzinfo=UTC))

    now = datetime.now(UTC)
    verbs: list[VerbProgressItem] = []
    dues = 0

    for item in memory:
        m = {
            "verb_slug": item.item_id,
            "stability": item.stability,
            "difficulty": item.difficulty,
            "last_score": item.last_score,
            "attempts": item.attempts,
            "prochaine_revision": item.due,
            "interval_jours": item.interval_jours,
        }
        est_due = (m["prochaine_revision"] is not None and m["prochaine_revision"] <= now) or m[
            "prochaine_revision"
        ] is None
        if est_due:
            dues += 1
        verbs.append(
            VerbProgressItem(
                verb_slug=m["verb_slug"],
                stability=m["stability"] or 0.0,
                difficulty=m["difficulty"] or 0.0,
                last_score=m["last_score"] or 0,
                attempts=m["attempts"] or 0,
                est_due=est_due,
                prochaine_revision=m["prochaine_revision"].isoformat() if m["prochaine_revision"] else None,
                interval_jours=m["interval_jours"] or 0.0,
            )
        )

    return VerbProgressResponse(
        user_id=str(current_user["id"]),
        nb_verbs=len(verbs),
        dues_aujourd_hui=dues,
        verbs=verbs,
    )


# ── 6. POST /api/action-verbs/{slug}/review — révision FSRS ──


@router.post("/{slug}/review")
async def reviser_verbe(
    slug: str,
    body: VerbReviewRequest,
    current_user: dict = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Marque une révision FSRS pour un verbe et programme la prochaine."""
    scheduler = get_scheduler()

    # S3 finale : lecture via la vue consolidée (mastery-first, fallback avp)
    from services.fsrs_unified import get_user_memory, update_memory

    memory = await get_user_memory(db, current_user["id"], kinds=("verb_action",))
    av_item = next((i for i in memory if i.item_id == slug), None)

    card = Card()
    if av_item and av_item.fsrs_state:
        state = av_item.fsrs_state
        card.stability = state.get("stability", 0.0)
        card.difficulty = state.get("difficulty", 0.0)
        card.reps = state.get("reps", 0)
        card.lapses = state.get("lapses", 0)

    # Déterminer le rating
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
        db, current_user["id"], "verb_action",
        item_id=slug,
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
        f"Action verb review : user={current_user['id']} verb={slug} rating={rating} next={next_review.isoformat()}"
    )

    return {
        "verb_slug": slug,
        "rating": rating,
        "next_review": next_review.isoformat(),
        "interval_days": float(new_card.scheduled_days),
        "stability": new_card.stability,
        "difficulty": new_card.difficulty,
    }


# ── 7. POST /api/action-verbs/feedback/hardest — sondage « verbe le plus difficile » ──
# Le frontend (HardestVerbPoll, page /action-verbs) postait vers cet endpoint
# depuis toujours, mais il n'existait PAS au backend : 404 avalé par le catch
# silencieux du composant → aucun vote jamais collecté. Fix 2026-08-21.


@router.post("/feedback/hardest")
async def feedback_verbe_difficile(body: dict[str, Any] | None = None):
    """Enregistre un vote anonyme « ce verbe est le plus difficile pour moi ».

    Public (pas de JWT — le sondage est anonyme). Persistance Redis INCR
    quand Redis est disponible (production), sinon log structuré seul
    (preview) — dégradation gracieuse, jamais de 500.
    """
    verb_slug = str((body or {}).get("verb_slug", "")).strip()
    if not verb_slug:
        raise HTTPException(400, "verb_slug requis")
    if len(verb_slug) > 80:
        raise HTTPException(400, "verb_slug trop long")

    count: int | None = None
    if state.redis is not None:
        try:
            count = await state.redis.incr(f"khawarizmi:hardest_verb_feedback:{verb_slug}")
        except Exception as exc:
            logger.warning(f"Hardest-verb feedback Redis indisponible : {exc}")

    logger.info("hardest_verb_feedback verb=%s count=%s", verb_slug, count)
    return {"status": "ok", "verb_slug": verb_slug, "count": count}


# ── Helper : enregistrer tentative ────────────────


async def _enregistrer_tentative(
    db: AsyncSession,
    user_id: str,
    verb_slug: str,
    percentage: int,
):
    """Enregistre une tentative (sans programmer FSRS — juste le score)."""
    # S3 finale : écriture via le service unifié
    from services.fsrs_unified import update_memory

    await update_memory(
        db, user_id, "verb_action",
        item_id=verb_slug,
        last_score=percentage,
        attempts_delta=1,
    )
    await db.commit()
