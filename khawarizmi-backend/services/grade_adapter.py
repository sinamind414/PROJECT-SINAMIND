"""Adaptateurs S3 — 0 logique de note. grade() seul juge. Sans grille → None.

Pas d'alias inventé : on ne charge que des question_id déjà dans index.json.
"""

from __future__ import annotations

from services.local_grader import TRAINING_BANNER_AR, UngradedError, grade_question
from services.rubric_store import load

UNGRADED_AR = "تعذر التصحيح — لا شبكة تقييم لهذه السؤال."


def resolve_question_id(*candidates: str | None) -> str | None:
    """Premier id qui a une Rubric. Pas d'alias, pas de verbe générique."""
    seen: set[str] = set()
    for c in candidates:
        if not c or c in seen:
            continue
        seen.add(c)
        if load(c) is not None:
            return c
    return None


def grade_or_none(question_id: str | None, answer: str):
    if not question_id:
        return None
    try:
        return grade_question(question_id, answer)
    except UngradedError:
        return None


def ungraded_http(question_id: str) -> dict:
    return {
        "code": "ungraded",
        "erreur": "ungraded",
        "question_id": question_id,
        "status": 422,
        "banner_ar": TRAINING_BANNER_AR,
    }


def may_write_fsrs(result) -> bool:
    if result.sanity_code != "ok":
        return False
    if result.method_percent < 10:
        return False
    if result.science_status == "error" and result.method_percent >= 85:
        return False
    return True


def persist_grade_columns(result) -> dict:
    """Colonnes 035 — métadonnées de note, jamais la copie."""
    if result is None:
        return {
            "rubric_version": "",
            "grader_version": "",
            "grading_engine": "ungraded",
            "science_status": "not_applicable",
            "stuffing_suspected": False,
            "method_percent": 0,
            "order_ok": None,
            "diagnosis_code": "ungraded",
        }
    diag = result.diagnosis
    return {
        "rubric_version": result.rubric_version,
        "grader_version": result.grader_version,
        "grading_engine": "local_rubric",
        "science_status": result.science_status,
        "stuffing_suspected": bool(result.stuffing_suspected),
        "method_percent": int(result.method_percent),
        "order_ok": result.order_ok,
        "diagnosis_code": diag.code if diag else None,
    }


def to_verb_eval(result) -> dict:
    """percentage = overall (cap science). method_percent reste l'axe منهج."""
    return {
        "verb_slug": result.verb_slug,
        "score": int(round(result.method_points)),
        "score_max": int(round(result.method_points_max)) or 1,
        "percentage": int(result.overall_training_percent),
        "method_percent": int(result.method_percent),
        "overall_training_percent": int(result.overall_training_percent),
        "success": [c.label_ar for c in result.criteria if c.status == "full"],
        "errors": list(result.science_flags)
        + ([result.next_step_ar] if result.next_step_ar else []),
        "missing_markers": [],
        "forbidden_found": [],
        "advice": result.phrase_ar or TRAINING_BANNER_AR,
        "dominant_error_code": result.diagnosis.code if result.diagnosis else None,
        "allow_second_attempt": result.overall_training_percent < 85,
        "source": "local_rubric",
        "banner_ar": TRAINING_BANNER_AR,
        "ungraded": False,
        "method_label_ar": result.method_label_ar,
        "science_status": result.science_status,
        "science_capped": bool(result.science_capped),
        "science_flags": list(result.science_flags),
        "order_ok": result.order_ok,
        "praise_ar": result.praise_ar,
        "next_step_ar": result.next_step_ar,
    }
