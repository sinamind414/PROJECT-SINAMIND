"""Routes Action Verbs — 6 endpoints.

Permet à l'élève d'apprendre les techniques des verbes d'action
du BAC algérien via pratique guidée + répétition espacée FSRS.
"""

import json
import logging
from datetime import datetime, timezone
from typing import Dict
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession
from database import get_db
from deps import get_current_user, get_scheduler
from schemas.action_verb import (
    EvaluateRequest,
    EvaluateResponse,
    VerbReviewRequest,
    VerbProgressItem,
    VerbProgressResponse,
)
from services.action_verbs_service import evaluate_answer, score_to_fsrs_rating
from fsrs import Card, Rating as FsrsRating

logger = logging.getLogger("khawarizmi.api")
router = APIRouter(prefix="/api/action-verbs", tags=["Action Verbs"])


# ── 1. GET /api/action-verbs — liste des verbes ──

@router.get("")
async def lister_verbes(
    current_user: Dict = Depends(get_current_user),
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
    current_user: Dict = Depends(get_current_user),
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
    current_user: Dict = Depends(get_current_user),
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
    return [
        {**dict(r._mapping), "id": str(r._mapping["id"])}
        for r in rows
    ]


# ── 4. POST /api/action-verbs/evaluate — évaluer ──

@router.post("/evaluate", response_model=EvaluateResponse)
async def evaluer_reponse(
    body: EvaluateRequest,
    current_user: Dict = Depends(get_current_user),
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

    verb = dict(row._mapping)
    evaluation = evaluate_answer(verb, body.answer)

    # Enregistrer la tentative dans action_verb_progress
    await _enregistrer_tentative(
        db=db,
        user_id=current_user["id"],
        verb_slug=body.verb_slug,
        percentage=evaluation["percentage"],
    )

    logger.info(
        f"Action verb eval : user={current_user['id']} "
        f"verb={body.verb_slug} score={evaluation['percentage']}%"
    )

    return EvaluateResponse(**evaluation)


# ── 5. GET /api/action-verbs/progress — progression FSRS ──

@router.get("/progress", response_model=VerbProgressResponse)
async def progression_verbes(
    current_user: Dict = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Retourne la progression FSRS de l'élève sur tous les verbes."""
    result = await db.execute(
        text("""
            SELECT avp.verb_slug, avp.stability, avp.difficulty,
                   avp.last_score, avp.attempts,
                   avp.prochaine_revision, avp.interval_jours
            FROM action_verb_progress avp
            WHERE avp.user_id = :user_id
            ORDER BY avp.prochaine_revision ASC
        """),
        {"user_id": current_user["id"]},
    )
    rows = result.fetchall()

    now = datetime.now(timezone.utc)
    verbs: list[VerbProgressItem] = []
    dues = 0

    for r in rows:
        m = r._mapping
        est_due = (
            m["prochaine_revision"] is not None
            and m["prochaine_revision"] <= now
        ) or m["prochaine_revision"] is None
        if est_due:
            dues += 1
        verbs.append(VerbProgressItem(
            verb_slug=m["verb_slug"],
            stability=m["stability"] or 0.0,
            difficulty=m["difficulty"] or 0.0,
            last_score=m["last_score"] or 0,
            attempts=m["attempts"] or 0,
            est_due=est_due,
            prochaine_revision=m["prochaine_revision"].isoformat() if m["prochaine_revision"] else None,
            interval_jours=m["interval_jours"] or 0.0,
        ))

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
    current_user: Dict = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Marque une révision FSRS pour un verbe et programme la prochaine."""
    scheduler = get_scheduler()

    # Récupérer l'état FSRS existant
    result = await db.execute(
        text("""
            SELECT stability, difficulty, fsrs_state
            FROM action_verb_progress
            WHERE user_id = :user_id AND verb_slug = :slug
        """),
        {"user_id": current_user["id"], "slug": slug},
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

    # Déterminer le rating
    rating = body.rating
    if body.score_percentage is not None:
        rating = score_to_fsrs_rating(body.score_percentage)

    fsrs_rating = FsrsRating(rating)
    new_card = scheduler.review_card(card, fsrs_rating)

    now = datetime.now(timezone.utc)
    next_review = now + __import__("datetime").timedelta(days=new_card.scheduled_days)

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
            INSERT INTO action_verb_progress
                (user_id, verb_slug, stability, difficulty, fsrs_state,
                 prochaine_revision, interval_jours, last_score, attempts,
                 updated_at)
            VALUES
                (:user_id, :slug, :stability, :difficulty, :fsrs_state,
                 :next_review, :interval, :score, 1, NOW())
            ON CONFLICT (user_id, verb_slug) DO UPDATE SET
                stability = EXCLUDED.stability,
                difficulty = EXCLUDED.difficulty,
                fsrs_state = EXCLUDED.fsrs_state,
                prochaine_revision = EXCLUDED.prochaine_revision,
                interval_jours = EXCLUDED.interval_jours,
                last_score = EXCLUDED.last_score,
                attempts = action_verb_progress.attempts + 1,
                updated_at = NOW()
        """),
        {
            "user_id": current_user["id"],
            "slug": slug,
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
        f"Action verb review : user={current_user['id']} "
        f"verb={slug} rating={rating} next={next_review.isoformat()}"
    )

    return {
        "verb_slug": slug,
        "rating": rating,
        "next_review": next_review.isoformat(),
        "interval_days": float(new_card.scheduled_days),
        "stability": new_card.stability,
        "difficulty": new_card.difficulty,
    }


# ── Helper : enregistrer tentative ────────────────

async def _enregistrer_tentative(
    db: AsyncSession,
    user_id: str,
    verb_slug: str,
    percentage: int,
):
    """Enregistre une tentative (sans programmer FSRS — juste le score)."""
    await db.execute(
        text("""
            INSERT INTO action_verb_progress
                (user_id, verb_slug, last_score, attempts, updated_at)
            VALUES
                (:user_id, :slug, :score, 1, NOW())
            ON CONFLICT (user_id, verb_slug) DO UPDATE SET
                last_score = EXCLUDED.last_score,
                attempts = action_verb_progress.attempts + 1,
                updated_at = NOW()
        """),
        {"user_id": user_id, "slug": verb_slug, "score": percentage},
    )
    await db.commit()
