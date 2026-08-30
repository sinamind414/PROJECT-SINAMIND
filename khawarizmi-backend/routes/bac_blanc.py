"""Routes Bac Blanc immersif — 5 endpoints.

POST /api/bac-blanc/start    → démarre une session, retourne les 2 sujets
POST /api/bac-blanc/choose   → verrouille le choix du sujet
POST /api/bac-blanc/save     → sauvegarde auto une réponse
POST /api/bac-blanc/submit   → soumet définitivement + évaluation
GET  /api/bac-blanc/{sid}/correction → correction détaillée
"""

import json
import logging
from datetime import UTC, datetime

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession

from database import get_db
from deps import get_current_user
from schemas.bac_blanc import (
    BacExercise,
    BacSubjectDetail,
    BacSubjectSummary,
    ChooseSubjectRequest,
    ChooseSubjectResponse,
    CorrectionAnswer,
    CorrectionResponse,
    ExerciseScore,
    SaveAnswerRequest,
    StartBacRequest,
    StartBacResponse,
    SubmitBacRequest,
    SubmitBacResponse,
    VerbScore,
)
from services.grade_adapter import UNGRADED_AR, grade_or_none, resolve_question_id
from services.hashing import hash_answer
from services.local_grader import TRAINING_BANNER_AR

logger = logging.getLogger("khawarizmi.api")
router = APIRouter(prefix="/api/bac-blanc", tags=["Bac Blanc"])


async def _require_own_session(db: AsyncSession, session_id: str, user_id: int):
    """Session de CET élève. 404 si absente, 403 si elle appartient à un autre (G9)."""
    owned = await db.execute(
        text(
            """
            SELECT id, user_id, subject_choice, status, started_at, annale_slug
            FROM bac_sessions
            WHERE id = :sid AND user_id = :uid
            """
        ),
        {"sid": session_id, "uid": user_id},
    )
    row = owned.fetchone()
    if row:
        return row._mapping
    exists = await db.execute(
        text("SELECT 1 FROM bac_sessions WHERE id = :sid"),
        {"sid": session_id},
    )
    if exists.fetchone():
        raise HTTPException(status_code=403, detail="Session d'un autre élève")
    raise HTTPException(status_code=404, detail="Session introuvable")


@router.post("/start", response_model=StartBacResponse)
async def start_bac(
    body: StartBacRequest,
    current_user: dict = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Démarre une session de bac blanc et retourne les 2 sujets au choix."""
    result = await db.execute(
        text("""
            SELECT subject_number, title_ar, themes_ar, estimated_minutes, exercises
            FROM bac_subjects
            WHERE annale_slug = :slug
            ORDER BY subject_number
        """),
        {"slug": body.annale_slug},
    )
    rows = result.fetchall()
    if not rows:
        raise HTTPException(404, f"Sujets introuvables pour : {body.annale_slug}")

    subjects = []
    for r in rows:
        m = r._mapping
        exercises = m["exercises"]
        if isinstance(exercises, str):
            exercises = json.loads(exercises)
        subjects.append(
            BacSubjectSummary(
                subject_number=m["subject_number"],
                title_ar=m["title_ar"],
                themes_ar=m["themes_ar"] if isinstance(m["themes_ar"], list) else json.loads(m["themes_ar"] or "[]"),
                estimated_minutes=m["estimated_minutes"],
                nb_exercises=len(exercises) if isinstance(exercises, list) else 0,
            )
        )

    session_result = await db.execute(
        text("""
            INSERT INTO bac_sessions (user_id, annale_slug, status)
            VALUES (:uid, :slug, 'in_progress')
            RETURNING id
        """),
        {"uid": current_user["id"], "slug": body.annale_slug},
    )
    session_id = session_result.fetchone()._mapping["id"]
    await db.commit()

    logger.info(f"Bac blanc start : user={current_user['id']} session={session_id}")

    return StartBacResponse(
        session_id=str(session_id),
        subjects=subjects,
    )


@router.post("/choose", response_model=ChooseSubjectResponse)
async def choose_subject(
    body: ChooseSubjectRequest,
    current_user: dict = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Verrouille le choix du sujet et retourne le détail."""
    sess_map = await _require_own_session(db, body.session_id, current_user["id"])

    if sess_map["subject_choice"] is not None:
        raise HTTPException(400, "Le choix est déjà verrouillé")

    result = await db.execute(
        text("""
            SELECT subject_number, title_ar, themes_ar, estimated_minutes, exercises
            FROM bac_subjects
            WHERE annale_slug = :slug AND subject_number = :num
        """),
        {"slug": sess_map["annale_slug"], "num": body.subject_choice},
    )
    row = result.fetchone()
    if not row:
        raise HTTPException(404, "Sujet introuvable")

    await db.execute(
        text(
            "UPDATE bac_sessions SET subject_choice = :choice "
            "WHERE id = :sid AND user_id = :uid"
        ),
        {
            "choice": body.subject_choice,
            "sid": body.session_id,
            "uid": current_user["id"],
        },
    )
    await db.commit()

    m = row._mapping
    exercises_data = m["exercises"]
    if isinstance(exercises_data, str):
        exercises_data = json.loads(exercises_data)

    exercises = [BacExercise(**ex) for ex in exercises_data]
    themes = m["themes_ar"] if isinstance(m["themes_ar"], list) else json.loads(m["themes_ar"] or "[]")

    subject = BacSubjectDetail(
        subject_number=m["subject_number"],
        title_ar=m["title_ar"],
        themes_ar=themes,
        estimated_minutes=m["estimated_minutes"],
        exercises=exercises,
    )

    logger.info(f"Bac blanc choose : user={current_user['id']} subject={body.subject_choice}")

    return ChooseSubjectResponse(
        session_id=body.session_id,
        subject=subject,
        time_limit_sec=m["estimated_minutes"] * 60,
    )


@router.post("/save")
async def save_answer(
    body: SaveAnswerRequest,
    current_user: dict = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Sauvegarde automatique d'une réponse pendant l'épreuve."""
    sess_map = await _require_own_session(db, body.session_id, current_user["id"])
    if sess_map["status"] != "in_progress":
        raise HTTPException(400, "Session non active")

    existing = await db.execute(
        text("""
            SELECT id FROM bac_answers
            WHERE session_id = :sid AND exercise_id = :eid AND question_id = :qid
        """),
        {"sid": body.session_id, "eid": body.exercise_id, "qid": body.question_id},
    )
    existing_row = existing.fetchone()

    if existing_row:
        await db.execute(
            text("""
                UPDATE bac_answers
                SET answer_text = :answer, skipped = :skipped, saved_at = NOW()
                WHERE id = :aid
            """),
            {"answer": body.answer_text, "skipped": body.skipped, "aid": existing_row._mapping["id"]},
        )
    else:
        await db.execute(
            text("""
                INSERT INTO bac_answers (session_id, exercise_id, question_id, answer_text, skipped)
                VALUES (:sid, :eid, :qid, :answer, :skipped)
            """),
            {
                "sid": body.session_id,
                "eid": body.exercise_id,
                "qid": body.question_id,
                "answer": body.answer_text,
                "skipped": body.skipped,
            },
        )

    await db.commit()
    return {"status": "saved", "saved_at": datetime.now(UTC).isoformat()}


@router.post("/submit", response_model=SubmitBacResponse)
async def submit_bac(
    body: SubmitBacRequest,
    current_user: dict = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Soumet définitivement le bac blanc + évalue les réponses."""
    sm = await _require_own_session(db, body.session_id, current_user["id"])

    if sm["status"] == "submitted":
        raise HTTPException(400, "Déjà soumis")
    now = datetime.now(UTC)
    started = sm["started_at"]
    time_used = int((now - started).total_seconds()) if started else 0

    subj_result = await db.execute(
        text("""
            SELECT exercises FROM bac_subjects
            WHERE annale_slug = :slug AND subject_number = :num
        """),
        {"slug": sm["annale_slug"], "num": sm["subject_choice"]},
    )
    subj_row = subj_result.fetchone()
    if not subj_row:
        raise HTTPException(404, "Sujet introuvable")

    exercises_data = subj_row._mapping["exercises"]
    if isinstance(exercises_data, str):
        exercises_data = json.loads(exercises_data)

    answers_result = await db.execute(
        text("SELECT exercise_id, question_id, answer_text, skipped FROM bac_answers WHERE session_id = :sid"),
        {"sid": body.session_id},
    )
    answers_map = {}
    for r in answers_result.fetchall():
        am = r._mapping
        answers_map[am["exercise_id"]] = {
            "answer_text": am["answer_text"] or "",
            "skipped": am["skipped"],
        }

    exercise_scores: list[ExerciseScore] = []
    verb_scores_map: dict[str, list[int]] = {}
    skipped_count = 0
    ungraded_count = 0
    graded_percents: list[int] = []
    corrections: list[CorrectionAnswer] = []
    annale = sm["annale_slug"]

    for ex in exercises_data:
        ex_id = ex["exercise_id"]
        verb = ex.get("verb_slug", "analyse")
        ans = answers_map.get(ex_id, {"answer_text": "", "skipped": True})
        answer_text = ans["answer_text"]
        is_skipped = ans["skipped"] or not answer_text.strip()
        score_max = ex.get("points", 5)
        is_ungraded = False

        if is_skipped:
            skipped_count += 1
            score = 0
            percentage = 0
            feedback = "تم تخطي هذا التمرين"
        else:
            qid = resolve_question_id(
                ex_id,
                f"bac:{annale}:{ex_id}",
            )
            graded = grade_or_none(qid, answer_text)
            if graded is None:
                is_ungraded = True
                ungraded_count += 1
                score = 0
                percentage = 0
                feedback = f"{UNGRADED_AR} {TRAINING_BANNER_AR}"
            else:
                percentage = int(graded.overall_training_percent)
                score = round(percentage / 100 * score_max)
                feedback = graded.phrase_ar or TRAINING_BANNER_AR
                if graded.science_flags:
                    feedback = (feedback + " | " + " · ".join(graded.science_flags)).strip(" |")
                graded_percents.append(percentage)

        exercise_scores.append(
            ExerciseScore(
                exercise_id=ex_id,
                title_ar=ex["title_ar"],
                score=score,
                score_max=score_max,
                percentage=percentage,
                skipped=is_skipped,
                ungraded=is_ungraded,
            )
        )

        verb_scores_map.setdefault(verb, [0, 0])
        verb_scores_map[verb][0] += score
        verb_scores_map[verb][1] += score_max

        corrections.append(
            CorrectionAnswer(
                exercise_id=ex_id,
                question_id=ex_id,
                title_ar=ex["title_ar"],
                verb_slug=verb,
                student_answer=answer_text,
                model_answer=ex.get("model_answer_ar", ""),
                score=score,
                score_max=score_max,
                percentage=percentage,
                feedback=feedback,
                skipped=is_skipped,
                ungraded=is_ungraded,
            )
        )

        await db.execute(
            text("""
                UPDATE bac_answers
                SET score = :score, feedback = :feedback, answer_text = :hashed
                WHERE session_id = :sid AND exercise_id = :eid
            """),
            {
                "score": score,
                "feedback": feedback,
                "hashed": hash_answer(answer_text) if answer_text else "",
                "sid": body.session_id,
                "eid": ex_id,
            },
        )

    verb_scores = [
        VerbScore(verb_slug=v, score=s[0], score_max=s[1], percentage=round(s[0] / max(s[1], 1) * 100))
        for v, s in verb_scores_map.items()
    ]

    score_global = round(sum(graded_percents) / len(graded_percents)) if graded_percents else 0

    if ungraded_count and not graded_percents:
        debrief = f"{TRAINING_BANNER_AR} {UNGRADED_AR}"
    else:
        debrief = f"درجة التدريب {score_global}%. {TRAINING_BANNER_AR}"

    await db.execute(
        text("""
            UPDATE bac_sessions
            SET status = 'submitted', submitted_at = NOW(), time_used_sec = :time,
                score_global = :score,
                scores_by_exercise = :ex_scores,
                scores_by_verb = :verb_scores,
                debrief = :debrief
            WHERE id = :sid AND user_id = :uid
        """),
        {
            "time": time_used,
            "score": score_global,
            "ex_scores": json.dumps([s.model_dump() for s in exercise_scores], ensure_ascii=False),
            "verb_scores": json.dumps([v.model_dump() for v in verb_scores], ensure_ascii=False),
            "debrief": json.dumps(
                {
                    "message": debrief,
                    "skipped": skipped_count,
                    "ungraded": ungraded_count,
                    "banner_ar": TRAINING_BANNER_AR,
                },
                ensure_ascii=False,
            ),
            "sid": body.session_id,
            "uid": current_user["id"],
        },
    )
    await db.commit()

    logger.info(
        f"Bac blanc submit : user={current_user['id']} session={body.session_id} "
        f"score={score_global}% time={time_used}s skipped={skipped_count}"
    )

    return SubmitBacResponse(
        session_id=body.session_id,
        score_global=score_global,
        time_used_sec=time_used,
        scores_by_exercise=exercise_scores,
        scores_by_verb=verb_scores,
        exercises_skipped=skipped_count,
        debrief_message=debrief,
        ungraded_count=ungraded_count,
        banner_ar=TRAINING_BANNER_AR,
    )


@router.get("/{session_id}/correction", response_model=CorrectionResponse)
async def get_correction(
    session_id: str,
    current_user: dict = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Retourne la correction détaillée après soumission."""
    sm = await _require_own_session(db, session_id, current_user["id"])

    if sm["status"] != "submitted":
        raise HTTPException(400, "Session non soumise")

    subj_result = await db.execute(
        text("SELECT exercises FROM bac_subjects WHERE annale_slug = :slug AND subject_number = :num"),
        {"slug": sm["annale_slug"], "num": sm["subject_choice"]},
    )
    subj_row = subj_result.fetchone()
    exercises_data = subj_row._mapping["exercises"]
    if isinstance(exercises_data, str):
        exercises_data = json.loads(exercises_data)

    answers_result = await db.execute(
        text("SELECT exercise_id, answer_text, skipped, score, feedback FROM bac_answers WHERE session_id = :sid"),
        {"sid": session_id},
    )
    answers_map = {}
    for r in answers_result.fetchall():
        am = r._mapping
        answers_map[am["exercise_id"]] = am

    corrections = []
    for ex in exercises_data:
        ex_id = ex["exercise_id"]
        ans = answers_map.get(ex_id, {})
        feedback = ans.get("feedback", "") or ""
        is_ungraded = UNGRADED_AR in feedback
        score_max = ex.get("points", 5)
        score = ans.get("score", 0) or 0
        percentage = 0 if is_ungraded else round((score / max(score_max, 1)) * 100)
        corrections.append(
            CorrectionAnswer(
                exercise_id=ex_id,
                question_id=ex_id,
                title_ar=ex["title_ar"],
                verb_slug=ex.get("verb_slug", ""),
                student_answer="",
                model_answer="" if is_ungraded else ex.get("model_answer_ar", ""),
                score=score,
                score_max=score_max,
                percentage=percentage,
                feedback=feedback,
                skipped=ans.get("skipped", False),
                ungraded=is_ungraded,
            )
        )

    return CorrectionResponse(session_id=session_id, corrections=corrections)
