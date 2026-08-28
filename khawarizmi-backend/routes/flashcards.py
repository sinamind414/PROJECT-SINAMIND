import json
import logging
from datetime import UTC, datetime, timedelta

from fastapi import APIRouter, Depends, HTTPException
from fsrs import Card
from fsrs import Rating as FsrsRating
from fsrs import Scheduler as CardScheduler
from sqlalchemy.ext.asyncio import AsyncSession

from fastapi.responses import JSONResponse

from deps import get_current_user, get_db, get_scheduler
from schemas.flashcard import (
    DrillRequest,
    DrillSubmitRequest,
    FlashcardCreateRequest,
    FlashcardReviewRequest,
    QcmSubmitRequest,
    ScheduleRequest,
)

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

    # S3b : lecture via le service FSRS unifié (même SELECT qu'avant)
    from services.fsrs_unified import get_concept_state, save_concept_review

    existing_state = await get_concept_state(db, user_id, body.micro_concept_id)

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
    # S3b : upsert riche via le service unifié (total_reviews/avg_score)
    ok = await save_concept_review(
        db, user_id, body.micro_concept_id,
        concept_id_alias=body.micro_concept_id,
        prochaine_revision=result["prochaine_revision"],
        interval_jours=result["interval_jours"],
        difficulty=result["difficulty"],
        stability=result["stability"],
        fsrs_state=fsrs_payload,
        due_date=result["prochaine_revision"],
        last_review=now,
        reps=new_card.reps,
        lapses=new_card.lapses,
        state=int(getattr(new_card.state, "value", 0)) if hasattr(new_card.state, "value") else 0,
        avg_score=body.score_percent,
    )
    await db.commit()
    if not ok:
        logger.warning(f"FSRS drill update non persisté (table indisponible): {body.micro_concept_id}")

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


# ── Phase 2 : drill copie libre → grade() (S10). 0 GPT / 0 L2.
# Sans Rubric L0 → 422 ungraded. QCM local inchangé.


@router.post("/api/drill/submit", tags=["Drill"])
async def soumettre_reponse_drill(
    body: DrillSubmitRequest,
    current_user: dict = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Note une copie drill via grade(). ENABLE_EXTERNAL_LLM ignoré."""
    from services.grade_adapter import (
        grade_or_none,
        may_write_fsrs,
        resolve_question_id,
        to_verb_eval,
        ungraded_http,
    )
    from services.local_grader import TRAINING_BANNER_AR

    user_id = current_user["id"]
    qid = resolve_question_id(body.question_id)
    graded = grade_or_none(qid, body.reponse_eleve)
    if graded is None:
        return JSONResponse(
            status_code=422,
            content=ungraded_http(body.question_id),
        )

    mapped = to_verb_eval(graded)
    next_review_date = None
    if may_write_fsrs(graded):
        from services.fsrs_unified import update_memory

        await update_memory(
            db,
            user_id,
            "verb_chapter",
            item_id=body.question_id,
            last_score=mapped["percentage"],
            attempts_delta=1,
        )
        await db.commit()

    logger.info(
        "DRILL_SUBMIT | user=%s | q=%s | score=%s | source=local_rubric",
        user_id,
        body.question_id,
        mapped["percentage"],
    )
    return {
        "score": mapped["percentage"],
        "statut": mapped["method_label_ar"],
        "feedback": mapped["advice"],
        "manquant": [],
        "next_review_date": next_review_date,
        "source": "local_rubric",
        "ungraded": False,
        "banner_ar": TRAINING_BANNER_AR,
        "method_percent": mapped["method_percent"],
        "overall_training_percent": mapped["overall_training_percent"],
        "science_status": mapped["science_status"],
    }


# ── Phase 3 : drill QCM ( auto-correction locale, zéro IA, instantané ) ──


@router.post("/api/drill/qcm/submit", tags=["Drill"])
async def soumettre_qcm_drill(
    body: QcmSubmitRequest,
    current_user: dict = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Corrige une réponse QCM localement et met à jour FSRS.

    Pas d'appel IA : la bonne réponse est connue ( extraite du programme ).
    Conversion correct/incorrect → score FSRS ( 10 ou 2 ).
    """
    from services.evaluation_fsrs import apply_evaluation_to_fsrs
    from services.qcm_items import get_qcm

    user_id = current_user["id"]

    qcm = get_qcm(body.qcm_id)
    if not qcm:
        raise HTTPException(status_code=404, detail=f"QCM {body.qcm_id} introuvable")

    correct_idx = qcm.get("correct_idx", -1)
    is_correct = body.selected_idx == correct_idx

    score = 10 if is_correct else 2
    statut = "CORRECT" if is_correct else "FAUX"
    eval_result = {
        "score": score,
        "statut": statut,
        "source": "QCM_LOCAL",
        "feedback": qcm.get("explanation", ""),
        "manquant": [] if is_correct else [
            qcm["options"][correct_idx] if correct_idx in (0, 1, 2, 3) else "—"
        ],
        "needs_l1_review": not is_correct,
    }

    next_review_date = await apply_evaluation_to_fsrs(
        db=db,
        user_id=user_id,
        question_id=body.qcm_id,
        reponse_eleve=str(body.selected_idx),
        question={
            "concept_cle": qcm.get("unit_slug", "qcm_general"),
            "chapitre_id": qcm.get("unit_slug", ""),
        },
        eval_result=eval_result,
    )

    logger.info(
        f"DRILL_QCM | user={user_id} | qcm={body.qcm_id} | "
        f"correct={is_correct} | next_review={next_review_date}"
    )

    return {
        "correct": is_correct,
        "correct_idx": correct_idx,
        "correct_option": qcm["options"][correct_idx] if correct_idx in (0, 1, 2, 3) else "",
        "explanation": qcm.get("explanation", ""),
        "selected_idx": body.selected_idx,
        "score": score,
        "statut": statut,
        "next_review_date": next_review_date,
    }


# ── Frontend API — Flashcards ──────────────────────


@router.get("/api/flashcards/due", tags=["Flashcards"])
async def get_due_cards(
    current_user: dict = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    from services.progress_snapshots import get_due_cards_snapshot

    return await get_due_cards_snapshot(db, current_user["id"])


@router.post("/api/flashcards", tags=["Flashcards"])
async def create_flashcard(
    body: FlashcardCreateRequest,
    current_user: dict = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    card_id = f"fc_{current_user['id']}_{datetime.now(UTC).timestamp()}"
    mc_id = card_id

    # S3b : création via le service FSRS unifié (même upsert qu'avant)
    from services.fsrs_unified import save_concept_card

    ok = await save_concept_card(
        db, current_user["id"], mc_id,
        concept_id_alias=card_id,
        chapter=body.chapitre or "",
        difficulty={"critique": 7.0, "haute": 5.0, "moyenne": 3.0}[body.importance],
        stability=0.0, state=0,
        due_date=datetime.now(UTC),
        prochaine_revision=datetime.now(UTC),
        interval_jours=1,
    )
    await db.commit()
    if not ok:
        logger.warning(f"Flashcard non persistée (table indisponible): {mc_id}")

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

    # S3b : lecture via le service FSRS unifié
    from services.fsrs_unified import get_concept_state, save_concept_review

    existing_state = await get_concept_state(db, current_user["id"], card_id)
    card = _rehydrate_fsrs_card(existing_state)

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
    # S3b : upsert via le service unifié (review simple)
    ok = await save_concept_review(
        db, current_user["id"], card_id,
        concept_id_alias=card_id,
        prochaine_revision=due_date,
        interval_jours=interval,
        difficulty=new_card.difficulty,
        stability=new_card.stability,
        fsrs_state={
            "stability": new_card.stability,
            "difficulty": new_card.difficulty,
            "scheduled_days": new_card.scheduled_days,
            "reps": new_card.reps,
            "lapses": new_card.lapses,
            "state": str(new_card.state),
            "last_review": now.isoformat(),
        },
        due_date=due_date,
        last_review=now,
    )
    await db.commit()
    if not ok:
        logger.warning(f"Review non persistée (table indisponible): {card_id}")

    await db.commit()

    return {
        "id": card_id,
        "stability": new_card.stability,
        "difficulty": new_card.difficulty,
        "due_date": due_date.isoformat() if hasattr(due_date, "isoformat") else str(due_date),
        "interval_jours": interval,
        "rating": body.rating,
    }
