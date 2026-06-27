import json
import logging
from datetime import UTC, datetime, timedelta

from fastapi import APIRouter, Depends
from fsrs import Card
from fsrs import Rating as FsrsRating
from fsrs import Scheduler as CardScheduler
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession

from deps import get_current_user, get_db, get_scheduler
from schemas.flashcard import DrillRequest, FlashcardCreateRequest, FlashcardReviewRequest, ScheduleRequest

logger = logging.getLogger("khawarizmi.api")
router = APIRouter()


def _rehydrate_fsrs_card(fsrs_state: dict | str | None) -> Card:
    """Reconstruit une Card FSRS depuis le JSON stocké en base."""
    card = Card()

    if not fsrs_state:
        return card

    try:
        state = fsrs_state if isinstance(fsrs_state, dict) else json.loads(fsrs_state)
    except Exception:
        logger.warning("FSRS state illisible, fallback sur Card() vierge")
        return card

    for field in ["stability", "difficulty", "scheduled_days", "reps", "lapses"]:
        if field in state and state[field] is not None:
            try:
                setattr(card, field, state[field])
            except Exception:
                logger.warning(f"Impossible de restaurer le champ FSRS {field}")

    return card


def _get_state():
    from main import state

    if state.interleaving is None:
        from services.interleaving import InterleavingSession

        state.interleaving = InterleavingSession()
    if state.scheduler is None:
        from services.scheduler import KhawarizmiScheduler

        state.scheduler = KhawarizmiScheduler()
    return state


_MATIERE_ALIASES = {
    "svt": "sciences_naturelles",
    "sciences": "sciences_naturelles",
    "sciences naturelles": "sciences_naturelles",
    "maths": "mathematiques",
    "mathematiques": "mathematiques",
    "physique": "physique",
    "physique chimie": "physique",
    "pc": "physique",
}


@router.post("/api/drill/session", tags=["Drill"])
async def generer_session_drill(
    body: DrillRequest,
    current_user: dict = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    s = _get_state()
    matiere = _MATIERE_ALIASES.get(body.matiere.lower().strip(), body.matiere)
    session = await s.interleaving.generer_session(
        user_id=current_user["id"],
        db=db,
        matiere=matiere,
        nb_questions=body.nb_questions,
    )

    if current_user["plan"] == "free":
        session["questions"] = session["questions"][:5]
        session["nb_questions"] = len(session["questions"])
        session["quota_atteint"] = len(session["questions"]) == 5

    logger.info(f"Drill : user={current_user['id']} matiere={body.matiere} questions={session['nb_questions']}")

    return session


@router.post("/api/drill/result", tags=["Drill"])
async def soumettre_resultat_drill(
    body: ScheduleRequest,
    current_user: dict = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    scheduler = get_scheduler()
    user_id = current_user["id"]

    existing = await db.execute(
        text("""
            SELECT fsrs_state FROM mastery_micro_concepts
            WHERE user_id = :user_id AND micro_concept_id = :mc_id
            LIMIT 1
        """),
        {"user_id": user_id, "mc_id": body.micro_concept_id},
    )
    row = existing.fetchone()
    existing_state = row[0] if row else None

    card = _rehydrate_fsrs_card(existing_state)
    result = scheduler.calculer_prochain_intervalle(card, body.score_percent)
    new_card = result["card"]

    now = datetime.now(UTC)
    fsrs_payload = {
        "stability": new_card.stability,
        "difficulty": new_card.difficulty,
        "scheduled_days": new_card.scheduled_days,
        "reps": new_card.reps,
        "lapses": new_card.lapses,
        "state": str(new_card.state),
        "last_review": now.isoformat(),
    }
    fsrs_json = json.dumps(fsrs_payload)

    await db.execute(
        text("""
            INSERT INTO mastery_micro_concepts
                (user_id, micro_concept_id, concept_id, prochaine_revision,
                 interval_jours, difficulty, stability, fsrs_state,
                 due_date, last_review, reps, lapses, state,
                 total_reviews, avg_score, updated_at)
            VALUES
                (:user_id, :mc_id, :concept_id, :next_rev,
                 :interval, :difficulty, :stability, :fsrs_state::jsonb,
                 :due_date, :last_review, :reps, :lapses, :state,
                 1, :avg_score, NOW())
            ON CONFLICT (user_id, micro_concept_id)
            DO UPDATE SET
                concept_id = COALESCE(mastery_micro_concepts.concept_id, EXCLUDED.concept_id),
                prochaine_revision = EXCLUDED.prochaine_revision,
                interval_jours = EXCLUDED.interval_jours,
                difficulty = EXCLUDED.difficulty,
                stability = EXCLUDED.stability,
                fsrs_state = EXCLUDED.fsrs_state,
                due_date = EXCLUDED.due_date,
                last_review = EXCLUDED.last_review,
                reps = EXCLUDED.reps,
                lapses = EXCLUDED.lapses,
                state = EXCLUDED.state,
                total_reviews = COALESCE(mastery_micro_concepts.total_reviews, 0) + 1,
                avg_score = (
                    (COALESCE(mastery_micro_concepts.avg_score, 0)
                     * COALESCE(mastery_micro_concepts.total_reviews, 0))
                    + :avg_score
                ) / NULLIF(COALESCE(mastery_micro_concepts.total_reviews, 0) + 1, 0),
                updated_at = NOW()
        """),
        {
            "user_id": user_id,
            "mc_id": body.micro_concept_id,
            "concept_id": body.micro_concept_id,
            "next_rev": result["prochaine_revision"],
            "interval": result["interval_jours"],
            "difficulty": result["difficulty"],
            "stability": result["stability"],
            "fsrs_state": fsrs_json,
            "due_date": result["prochaine_revision"],
            "last_review": now,
            "reps": new_card.reps,
            "lapses": new_card.lapses,
            "state": int(getattr(new_card.state, "value", 0)) if hasattr(new_card.state, "value") else 0,
            "avg_score": body.score_percent,
        },
    )
    await db.commit()

    logger.info(
        f"FSRS drill update: user={user_id} mc={body.micro_concept_id} "
        f"score={body.score_percent}% reps={new_card.reps} interval={result['interval_jours']}j"
    )

    return {
        "prochaine_revision": result["prochaine_revision"].isoformat(),
        "interval_jours": result["interval_jours"],
        "retrievability": result["retrievability"],
        "rating": result["rating"],
        "reps": new_card.reps,
        "lapses": new_card.lapses,
        "stability": new_card.stability,
        "difficulty": new_card.difficulty,
    }


# ── Frontend API — Flashcards ──────────────────────


@router.get("/api/flashcards/due", tags=["Flashcards"])
async def get_due_cards(
    current_user: dict = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    now = datetime.now(UTC)
    result = await db.execute(
        text("""
            SELECT id, micro_concept_id, concept_id, chapter,
                   difficulty, stability, state, due_date,
                   prochaine_revision, interval_jours
            FROM mastery_micro_concepts
            WHERE user_id = :uid
              AND due_date <= :now
              AND (state IS NULL OR state IN (0, 1))
            ORDER BY due_date ASC, stability ASC
            LIMIT 20
        """),
        {"uid": current_user["id"], "now": now},
    )
    rows = result.fetchall()

    cards = []
    for r in rows:
        cards.append(
            {
                "id": str(r[0]),
                "micro_concept_id": r[1],
                "concept_id": r[2],
                "chapter": r[3],
                "difficulty": r[4],
                "stability": r[5],
                "state": r[6],
                "due_date": r[7].isoformat() if r[7] else None,
                "next_review": r[8].isoformat() if r[8] else None,
                "interval_jours": r[9],
            }
        )

    return {"cards": cards, "total": len(cards)}


@router.post("/api/flashcards", tags=["Flashcards"])
async def create_flashcard(
    body: FlashcardCreateRequest,
    current_user: dict = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    card_id = f"fc_{current_user['id']}_{datetime.now(UTC).timestamp()}"
    mc_id = card_id

    await db.execute(
        text("""
            INSERT INTO mastery_micro_concepts
                (user_id, micro_concept_id, concept_id, chapter,
                 difficulty, stability, state, due_date,
                 prochaine_revision, interval_jours)
            VALUES
                (:uid, :mc_id, :concept_id, :chapter,
                 :difficulty, :stability, :state, :now,
                 :next_rev, :interval)
            ON CONFLICT (user_id, micro_concept_id)
            DO UPDATE SET
                chapter = EXCLUDED.chapter,
                difficulty = EXCLUDED.difficulty,
                updated_at = NOW()
        """),
        {
            "uid": current_user["id"],
            "mc_id": mc_id,
            "concept_id": card_id,
            "chapter": body.chapitre or "",
            "difficulty": {"critique": 7.0, "haute": 5.0, "moyenne": 3.0}[body.importance],
            "stability": 0.0,
            "state": 0,
            "now": datetime.now(UTC),
            "next_rev": datetime.now(UTC),
            "interval": 1,
        },
    )
    await db.commit()

    logger.info(f"Flashcard creee: {mc_id} user={current_user['id']}")

    return {
        "id": card_id,
        "micro_concept_id": mc_id,
        "recto": body.recto,
        "verso": body.verso,
        "type": body.type,
        "importance": body.importance,
        "matiere": body.matiere,
        "chapitre": body.chapitre,
    }


@router.post("/api/flashcards/{card_id}/review", tags=["Flashcards"])
async def review_flashcard(
    card_id: str,
    body: FlashcardReviewRequest,
    current_user: dict = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    rating_map = {1: FsrsRating.Again, 2: FsrsRating.Hard, 3: FsrsRating.Good, 4: FsrsRating.Easy}
    fsrs_rating = rating_map[body.rating]

    existing = await db.execute(
        text("""
            SELECT fsrs_state FROM mastery_micro_concepts
            WHERE user_id = :uid AND micro_concept_id = :mc_id
            LIMIT 1
        """),
        {"uid": current_user["id"], "mc_id": card_id},
    )
    row = existing.fetchone()
    card = _rehydrate_fsrs_card(row[0] if row else None)

    now = datetime.now(UTC)
    scheduler = CardScheduler()
    scheduling_cards = scheduler.repeat(card, now)
    new_card = scheduling_cards[fsrs_rating].card

    due_date = new_card.due if hasattr(new_card, "due") else now + timedelta(days=1)
    interval = new_card.scheduled_days if hasattr(new_card, "scheduled_days") else 1

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

    await db.execute(
        text("""
            INSERT INTO mastery_micro_concepts
                (user_id, micro_concept_id, prochaine_revision,
                 interval_jours, difficulty, stability, fsrs_state,
                 due_date, last_review)
            VALUES
                (:uid, :mc_id, :next_rev,
                 :interval, :difficulty, :stability, :fsrs_state::jsonb,
                 :due_date, :last_review)
            ON CONFLICT (user_id, micro_concept_id)
            DO UPDATE SET
                prochaine_revision = EXCLUDED.prochaine_revision,
                interval_jours = EXCLUDED.interval_jours,
                difficulty = EXCLUDED.difficulty,
                stability = EXCLUDED.stability,
                fsrs_state = EXCLUDED.fsrs_state,
                due_date = EXCLUDED.due_date,
                last_review = EXCLUDED.last_review,
                updated_at = NOW()
        """),
        {
            "uid": current_user["id"],
            "mc_id": card_id,
            "next_rev": due_date,
            "interval": interval,
            "difficulty": new_card.difficulty,
            "stability": new_card.stability,
            "fsrs_state": fsrs_json,
            "due_date": due_date,
            "last_review": now,
        },
    )
    await db.commit()

    return {
        "id": card_id,
        "stability": new_card.stability,
        "difficulty": new_card.difficulty,
        "due_date": due_date.isoformat() if hasattr(due_date, "isoformat") else str(due_date),
        "interval_jours": interval,
        "rating": body.rating,
    }
