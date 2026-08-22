import json
import logging
import re
from pathlib import Path

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession

from database import get_db
from deps import get_current_user
from routes.cours import COURSE_FILE, extract_unit_scope

logger = logging.getLogger("khawarizmi.api")
router = APIRouter(prefix="/api/exercices", tags=["Exercices"])

MAPPING_PATH = Path(__file__).resolve().parent.parent / "data" / "chapter_mapping.json"
try:
    with open(MAPPING_PATH, encoding="utf-8") as f:
        CHAPTER_MAPPING = json.load(f)
    logger.info(f"✅ Exercices chapter mapping chargé ({len(CHAPTER_MAPPING)} entrées)")
except FileNotFoundError:
    logger.warning(f"⚠️ chapter_mapping.json introuvable ({MAPPING_PATH}), fallback vide")
    CHAPTER_MAPPING = {}
except Exception as e:
    logger.error(f"❌ Erreur exercices chapter_mapping: {e}")
    CHAPTER_MAPPING = {}


def get_keywords(chapitre: str) -> list[str]:
    if chapitre in CHAPTER_MAPPING:
        return CHAPTER_MAPPING[chapitre]
    for key, keywords in CHAPTER_MAPPING.items():
        if key.lower() in chapitre.lower() or chapitre.lower() in key.lower():
            return keywords
    return [chapitre]


def _fallback_unit_exercises(domain_num: int | None, unit_num: int | None) -> str | None:
    """Retourne les exercices corrigés de l'unité lorsque le RAG est vide."""
    if domain_num is None or unit_num is None or not COURSE_FILE.exists():
        return None
    unit_content = extract_unit_scope(
        COURSE_FILE.read_text(encoding="utf-8"),
        domain_num,
        unit_num,
    )
    if not unit_content:
        return None

    start_match = re.search(r"^##\s+✅\s+التمارين التطبيقية", unit_content, re.MULTILINE)
    if not start_match:
        return None
    end_match = re.search(
        r"^##\s+(?:🎓\s+نصائح|🏆\s+اختبار|#)|^#\s+",
        unit_content[start_match.end():],
        re.MULTILINE,
    )
    end = start_match.end() + end_match.start() if end_match else len(unit_content)
    return unit_content[start_match.start():end].strip()


@router.get("/{chapitre}")
async def get_exercices(
    chapitre: str,
    domain_num: int | None = Query(None, ge=1, le=3),
    unit_num: int | None = Query(None, ge=1, le=5),
    current_user: dict = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    decoded = chapitre.replace("%20", " ").replace("+", " ")
    keywords = get_keywords(decoded)

    conditions = " OR ".join(f"LOWER(chapitre) LIKE LOWER(:kw{i})" for i in range(len(keywords)))
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
        content = _fallback_unit_exercises(domain_num, unit_num)
        if not content:
            raise HTTPException(
                status_code=404,
                detail=f"Aucun exercice trouve pour : {decoded}",
            )
        source_sections = 1
    else:
        content = "\n\n".join(r.content for r in rows)
        source_sections = len(rows)

    nb_exercices = content.count("التمرين") + content.count("Exercice")
    nb_corrections = content.count("إجابة") + content.count("Correction")

    return {
        "chapitre": decoded,
        "contenu": content,
        "nb_exercices": nb_exercices,
        "nb_corrections": nb_corrections,
        "nb_sections": source_sections,
    }


from pydantic import BaseModel

from models.exercise import Exercise, UserExerciseResponse
from services.correction_service import correct_student_answer
from services.language_service import ensure_arabic_version


class CorrectionRequest(BaseModel):
    answer: str
    language: str = "ar"


@router.post("/{exercise_id}/correct")
async def correct_exercise(
    exercise_id: int,
    request: CorrectionRequest,
    current_user: dict = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    exercise = await db.get(Exercise, exercise_id)
    if not exercise:
        raise HTTPException(status_code=404, detail="Exercice non trouvé")

    question = exercise.get_question(request.language)

    result = await correct_student_answer(
        question=question,
        student_answer=request.answer,
        points=exercise.points,
        language=request.language,
        model_answer=exercise.get_corrige(request.language),
    )

    user_response = UserExerciseResponse(
        exercise_id=exercise_id,
        user_id=current_user["id"],
        answer=request.answer,
        language=request.language,
        score=result["score"],
        feedback=result["explication"],
        corrected_answer=result["reponse_correcte"],
    )
    db.add(user_response)
    await db.commit()

    return result


@router.post("/{exercise_id}/ensure-arabic")
async def ensure_arabic(exercise_id: int, db: AsyncSession = Depends(get_db)):
    exercise = await db.get(Exercise, exercise_id)
    if not exercise:
        raise HTTPException(status_code=404, detail="Exercice non trouvé")

    success = await ensure_arabic_version(exercise, db)
    return {"generated_arabic": success}
