"""grading/sanity.py — Étape 1 du pipeline : sanity check (audit S2.1b).

Wrapper PUR autour de services/answer_sanity.check_answer_sanity — aucun
état, aucune dépendance externe. Le résultat standardisé (dict) est porté
par le PipelineContext (ctx.sanity_result) et passé à l'ancien moteur via
`precomputed_sanity` pour qu'il ne refasse pas le calcul (S2.1b : la sanity
sort du monolithe, tout le reste reste dans le legacy).

Codes de rejet (answer_sanity) : empty, too_short, gibberish, not_arabic,
repeated_chars. Succès : (True, "ok", "").
"""

from __future__ import annotations

from typing import Any

from services.answer_sanity import check_answer_sanity


def run_sanity(student_answer: str) -> dict[str, Any]:
    """Exécute le sanity check et retourne un résultat standardisé.

    Retourne {"is_valid": bool, "sanity_code": str, "message_ar": str} —
    compatible avec le tuple (bool, str, str) attendu par l'ancien moteur
    via precomputed_sanity.
    """
    is_valid, sanity_code, message_ar = check_answer_sanity(student_answer)
    return {
        "is_valid": is_valid,
        "sanity_code": sanity_code,
        "message_ar": message_ar,
    }


def sanity_tuple(sanity: dict[str, Any]) -> tuple[bool, str, str]:
    """Convertit le dict standardisé vers le tuple attendu par le legacy."""
    return (
        bool(sanity["is_valid"]),
        str(sanity["sanity_code"]),
        str(sanity["message_ar"]),
    )
