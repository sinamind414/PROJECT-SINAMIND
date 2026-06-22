"""Routes Bac Blanc immersif — 5 endpoints.

POST /api/bac-blanc/start    → démarre une session, retourne les 2 sujets
POST /api/bac-blanc/choose   → verrouille le choix du sujet
POST /api/bac-blanc/save     → sauvegarde auto une réponse
POST /api/bac-blanc/submit   → soumet définitivement + évaluation
GET  /api/bac-blanc/{sid}/correction → correction détaillée
"""

import json
import logging
from datetime import datetime, timezone
from typing import Dict, List

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession

from database import get_db
from deps import get_current_user
from schemas.bac_blanc import (
    StartBacRequest,
    StartBacResponse,
    BacSubjectSummary,
    ChooseSubjectRequest,
    ChooseSubjectResponse,
    BacSubjectDetail,
    BacExercise,
    SaveAnswerRequest,
    SubmitBacRequest,
    SubmitBacResponse,
    ExerciseScore,
    VerbScore,
    CorrectionResponse,
    CorrectionAnswer,
)
from services.document_analysis_service import evaluate_answer

logger = logging.getLogger("khawarizmi.api")
router = APIRouter(prefix="/api/bac-blanc", tags=["Bac Blanc"])


@router.post("/start", response_model=StartBacResponse)
async def start_bac(
    body: StartBacRequest,
    current_user: Dict = Depends(get_current_user),
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
        subjects.append(BacSubjectSummary(
            subject_number=m["subject_number"],
            title_ar=m["title_ar"],
            themes_ar=m["themes_ar"] if isinstance(m["themes_ar"], list) else json.loads(m["themes_ar"] or "[]"),
            estimated_minutes=m["estimated_minutes"],
            nb_exercises=len(exercises) if isinstance(exercises, list) else 0,
        ))

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
    current_user: Dict = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Verrouille le choix du sujet et retourne le détail."""
    sess = await db.execute(
        text("SELECT id, subject_choice, status FROM bac_sessions WHERE id = :sid"),
        {"sid": body.session_id},
    )
    sess_row = sess.fetchone()
    if not sess_row:
        raise HTTPException(404, "Session introuvable")

    if sess_row._mapping["subject_choice"] is not None:
        raise HTTPException(400, "Le choix est déjà verrouillé")

    result = await db.execute(
        text("""
            SELECT subject_number, title_ar, themes_ar, estimated_minutes, exercises
            FROM bac_subjects
            WHERE annale_slug = (
                SELECT annale_slug FROM bac_sessions WHERE id = :sid
            ) AND subject_number = :num
        """),
        {"sid": body.session_id, "num": body.subject_choice},
    )
    row = result.fetchone()
    if not row:
        raise HTTPException(404, "Sujet introuvable")

    await db.execute(
        text("UPDATE bac_sessions SET subject_choice = :choice WHERE id = :sid"),
        {"choice": body.subject_choice, "sid": body.session_id},
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
    current_user: Dict = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Sauvegarde automatique d'une réponse pendant l'épreuve."""
    sess = await db.execute(
        text("SELECT id FROM bac_sessions WHERE id = :sid AND status = 'in_progress'"),
        {"sid": body.session_id},
    )
    if not sess.fetchone():
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
    return {"status": "saved", "saved_at": datetime.now(timezone.utc).isoformat()}


@router.post("/submit", response_model=SubmitBacResponse)
async def submit_bac(
    body: SubmitBacRequest,
    current_user: Dict = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Soumet définitivement le bac blanc + évalue les réponses."""
    sess = await db.execute(
        text("""
            SELECT id, started_at, subject_choice, annale_slug, status
            FROM bac_sessions WHERE id = :sid
        """),
        {"sid": body.session_id},
    )
    sess_row = sess.fetchone()
    if not sess_row:
        raise HTTPException(404, "Session introuvable")

    if sess_row._mapping["status"] == "submitted":
        raise HTTPException(400, "Déjà soumis")

    sm = sess_row._mapping
    now = datetime.now(timezone.utc)
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

    exercise_scores: List[ExerciseScore] = []
    verb_scores_map: Dict[str, List[int]] = {}
    total_score = 0
    total_max = 0
    skipped_count = 0
    corrections: List[CorrectionAnswer] = []

    for ex in exercises_data:
        ex_id = ex["exercise_id"]
        verb = ex.get("verb_slug", "analyse")
        ans = answers_map.get(ex_id, {"answer_text": "", "skipped": True})
        answer_text = ans["answer_text"]
        is_skipped = ans["skipped"] or not answer_text.strip()

        if is_skipped:
            skipped_count += 1
            score = 0
            percentage = 0
            feedback = "تم تخطي هذا التمرين"
        else:
            evaluation = evaluate_answer(verb, answer_text, ex.get("model_answer_ar"))
            score = evaluation["score"]
            percentage = evaluation["percentage"]
            feedback = evaluation["advice"]

        score_max = ex.get("points", 5)
        total_score += score
        total_max += score_max

        exercise_scores.append(ExerciseScore(
            exercise_id=ex_id,
            title_ar=ex["title_ar"],
            score=score,
            score_max=score_max,
            percentage=percentage,
            skipped=is_skipped,
        ))

        verb_scores_map.setdefault(verb, [0, 0])
        verb_scores_map[verb][0] += score
        verb_scores_map[verb][1] += score_max

        corrections.append(CorrectionAnswer(
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
        ))

        await db.execute(
            text("""
                UPDATE bac_answers
                SET score = :score, feedback = :feedback
                WHERE session_id = :sid AND exercise_id = :eid
            """),
            {"score": score, "feedback": feedback, "sid": body.session_id, "eid": ex_id},
        )

    verb_scores = [
        VerbScore(verb_slug=v, score=s[0], score_max=s[1], percentage=round(s[0] / max(s[1], 1) * 100))
        for v, s in verb_scores_map.items()
    ]

    score_global = round(total_score / max(total_max, 1) * 100)

    if score_global >= 75:
        debrief = f"أحسنت! نتيجتك {score_global}%. أنت جاهز للبكالوريا. ركز على المراجعة الدورية."
    elif score_global >= 50:
        debrief = f"نتيجتك {score_global}%. تحتاج إلى مراجعة بعض النقاط. راجع التمارين التي تخطيتها."
    else:
        debrief = f"نتيجتك {score_global}%. لا تقلق، لديك وقت. ابدأ بمراجعة الدروس الأساسية."

    await db.execute(
        text("""
            UPDATE bac_sessions
            SET status = 'submitted', submitted_at = NOW(), time_used_sec = :time,
                score_global = :score,
                scores_by_exercise = :ex_scores,
                scores_by_verb = :verb_scores,
                debrief = :debrief
            WHERE id = :sid
        """),
        {
            "time": time_used,
            "score": score_global,
            "ex_scores": json.dumps([s.model_dump() for s in exercise_scores], ensure_ascii=False),
            "verb_scores": json.dumps([v.model_dump() for v in verb_scores], ensure_ascii=False),
            "debrief": json.dumps({"message": debrief, "skipped": skipped_count}, ensure_ascii=False),
            "sid": body.session_id,
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
    )


@router.get("/{session_id}/correction", response_model=CorrectionResponse)
async def get_correction(
    session_id: str,
    current_user: Dict = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Retourne la correction détaillée après soumission."""
    sess = await db.execute(
        text("SELECT status, annale_slug, subject_choice FROM bac_sessions WHERE id = :sid"),
        {"sid": session_id},
    )
    sess_row = sess.fetchone()
    if not sess_row:
        raise HTTPException(404, "Session introuvable")

    if sess_row._mapping["status"] != "submitted":
        raise HTTPException(400, "Session non soumise")

    sm = sess_row._mapping
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
        corrections.append(CorrectionAnswer(
            exercise_id=ex_id,
            question_id=ex_id,
            title_ar=ex["title_ar"],
            verb_slug=ex.get("verb_slug", ""),
            student_answer=ans.get("answer_text", ""),
            model_answer=ex.get("model_answer_ar", ""),
            score=ans.get("score", 0),
            score_max=ex.get("points", 5),
            percentage=round((ans.get("score", 0) / max(ex.get("points", 5), 1)) * 100),
            feedback=ans.get("feedback", ""),
            skipped=ans.get("skipped", False),
        ))

    return CorrectionResponse(session_id=session_id, corrections=corrections)
