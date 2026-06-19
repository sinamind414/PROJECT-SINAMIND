import json
import logging
from pathlib import Path
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession
from database import get_db
from deps import get_current_user

logger = logging.getLogger("khawarizmi.api")
router = APIRouter(prefix="/api/exercices", tags=["Exercices"])

MAPPING_PATH = Path(__file__).resolve().parent.parent / "data" / "chapter_mapping.json"
with open(MAPPING_PATH, "r", encoding="utf-8") as f:
    CHAPTER_MAPPING = json.load(f)


def get_keywords(chapitre: str) -> list[str]:
    if chapitre in CHAPTER_MAPPING:
        return CHAPTER_MAPPING[chapitre]
    for key, keywords in CHAPTER_MAPPING.items():
        if key.lower() in chapitre.lower() or chapitre.lower() in key.lower():
            return keywords
    return [chapitre]


@router.get("/{chapitre}")
async def get_exercices(
    chapitre: str,
    current_user: dict = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    decoded = chapitre.replace("%20", " ").replace("+", " ")
    keywords = get_keywords(decoded)

    conditions = " OR ".join(
        f"LOWER(chapitre) LIKE LOWER(:kw{i})" for i in range(len(keywords))
    )
    params = {f"kw{i}": f"%{k}%" for i, k in enumerate(keywords)}
    params["source"] = "svt_bac_complet.md"

    result = await db.execute(
        text(f"""
            SELECT content, chunk_index, importance, chapitre
            FROM rag_chunks
            WHERE source = :source
            AND ({conditions})
            AND LENGTH(content) > 100
            AND (
                content LIKE '%تمارين%'
                OR content LIKE '%التمرين%'
                OR content LIKE '%إجابة%'
                OR content LIKE '%Exercice%'
                OR content LIKE '%Correction%'
                OR content LIKE '%منهجية%'
                OR content LIKE '%سلّم%'
            )
            ORDER BY chunk_index ASC
            LIMIT 30
        """),
        params,
    )
    rows = result.fetchall()

    if not rows:
        result = await db.execute(
            text(f"""
                SELECT content, chunk_index, importance, chapitre
                FROM rag_chunks
                WHERE ({conditions})
                AND LENGTH(content) > 100
                AND (
                    content LIKE '%تمارين%'
                    OR content LIKE '%التمرين%'
                    OR content LIKE '%إجابة%'
                    OR content LIKE '%Exercice%'
                    OR content LIKE '%Correction%'
                    OR content LIKE '%منهجية%'
                    OR content LIKE '%سلّم%'
                )
                ORDER BY chunk_index ASC
                LIMIT 30
            """),
            {k: v for k, v in params.items() if k != "source"},
        )
        rows = result.fetchall()

    if not rows:
        raise HTTPException(
            status_code=404,
            detail=f"Aucun exercice trouve pour : {decoded}",
        )

    content = "\n\n".join(r.content for r in rows)
    nb_exercices = content.count("التمرين") + content.count("Exercice")
    nb_corrections = content.count("إجابة") + content.count("Correction")

    return {
        "chapitre": decoded,
        "contenu": content,
        "nb_exercices": nb_exercices,
        "nb_corrections": nb_corrections,
        "nb_sections": len(rows),
    }

from pydantic import BaseModel
from models.exercise import Exercise, UserExerciseResponse
from services.language_service import ensure_arabic_version
from services.correction_service import correct_student_answer

class CorrectionRequest(BaseModel):
    answer: str
    language: str = "ar"

@router.post("/{exercise_id}/correct")
async def correct_exercise(
    exercise_id: int,
    request: CorrectionRequest,
    current_user: dict = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    exercise = await db.get(Exercise, exercise_id)
    if not exercise:
        raise HTTPException(status_code=404, detail="Exercice non trouvé")

    question = exercise.get_question(request.language)

    result = await correct_student_answer(
        question=question,
        student_answer=request.answer,
        points=exercise.points,
        language=request.language
    )

    user_response = UserExerciseResponse(
        exercise_id=exercise_id,
        user_id=current_user["id"],
        answer=request.answer,
        language=request.language,
        score=result["score"],
        feedback=result["explication"],
        corrected_answer=result["reponse_correcte"]
    )
    db.add(user_response)
    await db.commit()

    return result


@router.post("/{exercise_id}/ensure-arabic")
async def ensure_arabic(
    exercise_id: int,
    db: AsyncSession = Depends(get_db)
):
    exercise = await db.get(Exercise, exercise_id)
    if not exercise:
        raise HTTPException(status_code=404, detail="Exercice non trouvé")

    success = await ensure_arabic_version(exercise, db)
    return {"generated_arabic": success}
