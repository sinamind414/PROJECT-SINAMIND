"""Routes Active Lessons — apprentissage par blocs avec quick checks.

GET  /api/lessons/{chapter_slug}        → liste des blocs (sans réponses)
POST /api/lessons/{chapter_slug}/check  → vérifie une réponse + progression
"""

import logging

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession

from database import get_db
from deps import get_current_user
from schemas.lesson import (
    CheckAnswerRequest,
    CheckAnswerResponse,
    LessonBlock,
    LessonResponse,
    QuickCheck,
)

logger = logging.getLogger("khawarizmi.api")
router = APIRouter(prefix="/api/lessons", tags=["Active Lessons"])


@router.get("/{chapter_slug}", response_model=LessonResponse)
async def get_lesson(
    chapter_slug: str,
    current_user: dict = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Retourne les blocs d'une leçon active (sans les réponses)."""
    result = await db.execute(
        text("""
            SELECT id, block_type, sort_order, title_ar, body_ar,
                   visual_hint, quick_check
            FROM lesson_blocks
            WHERE chapter_slug = :slug
            ORDER BY sort_order
        """),
        {"slug": chapter_slug},
    )
    rows = result.fetchall()
    if not rows:
        raise HTTPException(404, f"Leçon introuvable : {chapter_slug}")

    blocks = []
    for r in rows:
        m = r._mapping
        qc_data = m["quick_check"]
        if isinstance(qc_data, str):
            import json

            qc_data = json.loads(qc_data)

        qc = QuickCheck(
            type=qc_data.get("type", "mcq"),
            question_ar=qc_data.get("question_ar", ""),
            options=qc_data.get("options", []),
            correct_index=qc_data.get("correct_index"),
            expected_keywords=qc_data.get("expected_keywords", []),
            explanation_ar=qc_data.get("explanation_ar", ""),
        )

        blocks.append(
            LessonBlock(
                id=str(m["id"]),
                block_type=m["block_type"],
                sort_order=m["sort_order"],
                title_ar=m["title_ar"],
                body_ar=m["body_ar"],
                visual_hint=m["visual_hint"],
                quick_check=qc,
            )
        )

    return LessonResponse(
        chapter_slug=chapter_slug,
        blocks=blocks,
        blocks_total=len(blocks),
    )


@router.post("/{chapter_slug}/check", response_model=CheckAnswerResponse)
async def check_answer(
    chapter_slug: str,
    body: CheckAnswerRequest,
    current_user: dict = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Vérifie la réponse à un quick check et met à jour la progression."""
    result = await db.execute(
        text("""
            SELECT id, quick_check FROM lesson_blocks
            WHERE chapter_slug = :slug AND id = :block_id
        """),
        {"slug": chapter_slug, "block_id": body.block_id},
    )
    row = result.fetchone()
    if not row:
        raise HTTPException(404, "Bloc introuvable")

    import json

    qc = row._mapping["quick_check"]
    if isinstance(qc, str):
        qc = json.loads(qc)

    is_correct = _evaluate_answer(qc, body.answer)
    explanation = qc.get("explanation_ar", "")

    total_result = await db.execute(
        text("SELECT COUNT(*) FROM lesson_blocks WHERE chapter_slug = :slug"),
        {"slug": chapter_slug},
    )
    blocks_total = total_result.scalar()

    progress_result = await db.execute(
        text("""
            SELECT blocks_completed FROM lesson_progress
            WHERE user_id = :uid AND chapter_slug = :slug
        """),
        {"uid": current_user["id"], "slug": chapter_slug},
    )
    progress_row = progress_result.fetchone()
    current_completed = progress_row._mapping["blocks_completed"] if progress_row else 0

    new_completed = current_completed + 1 if is_correct else current_completed
    score = round((new_completed / max(blocks_total, 1)) * 100)
    lesson_done = new_completed >= blocks_total

    await db.execute(
        text("""
            INSERT INTO lesson_progress
                (user_id, chapter_slug, blocks_completed, blocks_total,
                 score_percentage, completed, updated_at)
            VALUES
                (:uid, :slug, :completed, :total, :score, :done, NOW())
            ON CONFLICT (user_id, chapter_slug) DO UPDATE SET
                blocks_completed = EXCLUDED.blocks_completed,
                blocks_total = EXCLUDED.blocks_total,
                score_percentage = EXCLUDED.score_percentage,
                completed = EXCLUDED.completed,
                updated_at = NOW()
        """),
        {
            "uid": current_user["id"],
            "slug": chapter_slug,
            "completed": new_completed,
            "total": blocks_total,
            "score": score,
            "done": lesson_done,
        },
    )
    await db.commit()

    logger.info(
        f"Lesson check : user={current_user['id']} chapter={chapter_slug} "
        f"correct={is_correct} completed={new_completed}/{blocks_total}"
    )

    return CheckAnswerResponse(
        block_id=body.block_id,
        correct=is_correct,
        explanation_ar=explanation,
        score_percentage=score,
        blocks_completed=new_completed,
        blocks_total=blocks_total,
        lesson_completed=lesson_done,
    )


def _evaluate_answer(qc: dict, answer: str) -> bool:
    """Évalue la réponse selon le type de quick check."""
    qc_type = qc.get("type", "mcq")
    answer = answer.strip()

    if qc_type == "true-false" or qc_type == "mcq":
        try:
            idx = int(answer)
            return idx == qc.get("correct_index", -1)
        except (ValueError, TypeError):
            return False

    if qc_type == "short-answer":
        keywords = qc.get("expected_keywords", [])
        if not keywords:
            return len(answer) >= 10
        answer_lower = answer.lower()
        return any(kw.lower() in answer_lower for kw in keywords)

    return False
