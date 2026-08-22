"""Correcteur local du Bac blanc : fond scientifique avant méthodologie."""
from __future__ import annotations

from typing import Any

from services.document_analysis_service import evaluate_answer as evaluate_methodology_markers
from services.savoir_corrector import deterministic_correct


def correct_bac_answer(exercise: dict[str, Any], student_answer: str) -> dict[str, Any]:
    """Note sur le barème déclaré, avec 70 % fond et 30 % méthodologie.

    Une erreur conceptuelle ou numérique grave plafonne la copie à 40 %.
    Le score retourné est toujours compris entre 0 et ``exercise.points``.
    """
    score_max = max(1, int(exercise.get("points", 1)))
    verb_slug = str(exercise.get("verb_slug") or "analyse")
    model_answer = str(exercise.get("model_answer_ar") or "")
    question = "\n".join(
        part for part in (
            str(exercise.get("context_ar") or ""),
            str(exercise.get("instruction_ar") or ""),
            str(exercise.get("title_ar") or ""),
        ) if part
    )

    scientific = deterministic_correct(
        question=question,
        student_answer=student_answer,
        points=score_max,
        language="ar",
        model_answer=model_answer,
    )
    scientific_ratio = float(scientific.get("score", 0.0)) / max(
        1.0, float(scientific.get("max_score", score_max))
    )

    methodology = evaluate_methodology_markers(
        verb_slug,
        student_answer,
        model_answer,
    )
    methodology_ratio = float(methodology.get("percentage", 0)) / 100.0

    # Sans référence scientifique, on refuse de fabriquer une précision : la
    # méthodologie reste formative mais ne peut pas valider le fond.
    if model_answer.strip():
        final_ratio = 0.70 * scientific_ratio + 0.30 * methodology_ratio
    else:
        final_ratio = min(methodology_ratio, 0.50)

    scientific_errors = [str(error) for error in scientific.get("erreurs", [])]
    grave = any(
        "خطأ مفاهيمي" in error or "قيمة عددية خاطئة" in error
        for error in scientific_errors
    )
    if grave:
        final_ratio = min(final_ratio, 0.40)

    final_ratio = max(0.0, min(1.0, final_ratio))
    score = max(0, min(score_max, int(round(final_ratio * score_max))))
    percentage = round(100 * score / score_max)

    feedback_parts: list[str] = []
    if scientific_errors:
        feedback_parts.append("علميا: " + " | ".join(scientific_errors[:3]))
    elif scientific.get("explication"):
        feedback_parts.append("علميا: " + str(scientific["explication"]))
    if methodology.get("advice"):
        feedback_parts.append("منهجيا: " + str(methodology["advice"]))
    if not model_answer.strip():
        feedback_parts.append("لا توجد إجابة مرجعية موثقة؛ العلامة محدودة إلى 50٪.")

    return {
        "score": score,
        "score_max": score_max,
        "percentage": percentage,
        "feedback": " | ".join(feedback_parts),
        "scientific_ratio": round(scientific_ratio, 3),
        "methodology_ratio": round(methodology_ratio, 3),
        "dominant_error_code": (
            "scientific_error" if grave
            else methodology.get("dominant_error_code") or "partial_correct"
        ),
    }
