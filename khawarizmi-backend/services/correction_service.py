"""Correction locale des exercices — même référentiel scientifique que le Bac blanc."""
from __future__ import annotations

from typing import Any

from services.savoir_corrector import deterministic_correct


async def correct_student_answer(
    question: str,
    student_answer: str,
    points: int = 4,
    language: str = "ar",
    model_answer: str = "",
) -> dict[str, Any]:
    """Corrige sans appel direct à un provider externe.

    Le résultat conserve le contrat historique de la route exercices tout en
    utilisant la question, la correction de référence et le barème réel.
    """
    result = deterministic_correct(
        question=question,
        student_answer=student_answer,
        points=points,
        language=language,
        model_answer=model_answer,
    )
    score = max(0.0, min(float(points), float(result.get("score", 0.0))))
    return {
        "score": score,
        "max_score": points,
        "points_forts": list(result.get("points_forts", [])),
        "erreurs": list(result.get("erreurs", [])),
        "reponse_correcte": model_answer or result.get("reponse_correcte", ""),
        "explication": result.get("explication", ""),
        "conseils": result.get("conseils", ""),
        "source": "deterministic-savoir",
    }
