"""Correction formative de la banque 55 chapitres, sans appel LLM direct."""
from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Literal

from services.bac_blanc_corrector import correct_bac_answer
from services.pedagogical_validation import grading_validation_status

BANK_PATH = Path(__file__).resolve().parents[1] / "data" / "chapter_exercise_bank.json"


def _load_bank() -> dict[str, Any]:
    with BANK_PATH.open(encoding="utf-8") as stream:
        payload = json.load(stream)
    return {
        chapter["chapterSlug"]: chapter
        for chapter in payload.get("chapters", [])
    }


CHAPTER_EXERCISES = _load_bank()


def get_chapter_activity(
    chapter_slug: str,
    activity_kind: Literal["restitution", "document"],
) -> tuple[dict[str, Any], dict[str, Any]] | None:
    chapter = CHAPTER_EXERCISES.get(chapter_slug)
    if not chapter:
        return None
    activity = next(
        (item for item in chapter.get("activities", []) if item.get("kind") == activity_kind),
        None,
    )
    return (chapter, activity) if activity else None


def _safe_internal_feedback(value: str) -> str:
    return (
        value
        .replace("البرنامج الرسمي ONEC", "المرجع العلمي الداخلي")
        .replace("حسب البرنامج الرسمي", "حسب المرجع العلمي الداخلي")
        .replace("ONEC", "المرجع الداخلي")
    )


def _documents_context(activity: dict[str, Any]) -> str:
    lines: list[str] = []
    for document in activity.get("documents", []):
        lines.append(str(document.get("titleAr") or ""))
        lines.extend(str(item) for item in document.get("dataAr", []))
    return "\n".join(line for line in lines if line)


def _build_priorities(
    *,
    chapter: dict[str, Any],
    activity: dict[str, Any],
    error_types: list[str],
) -> list[dict[str, str]]:
    priorities: list[dict[str, str]] = []
    retry_href = f"/exercices/{chapter['chapterSlug']}#activity-{activity['id']}"

    if "scientific_error" in error_types:
        priorities.append({
            "type": "scientific",
            "title_ar": "صحّح المحتوى العلمي أولا",
            "detail_ar": "راجع مفاهيم الفصل ثم أعد صياغة الإجابة دون نسخ المرجع.",
            "href": chapter["courseHref"],
            "label_ar": "راجع الفصل العلمي",
        })
    elif "off_topic" in error_types:
        priorities.append({
            "type": "off_topic",
            "title_ar": "أعد قراءة التعليمة والمعطيات",
            "detail_ar": "استخرج المطلوب من الوثيقة أو السؤال قبل استعمال المعارف.",
            "href": chapter["practiceHref"],
            "label_ar": "تدريب وثائقي للفصل",
        })

    if "methodology_error" in error_types and len(priorities) < 2:
        priorities.append({
            "type": "methodology",
            "title_ar": "أصلح منهجية فعل التعليمة",
            "detail_ar": f"تدرّب على الفعل «{activity['verbSlug']}» ثم عد إلى نفس السؤال.",
            "href": f"/action-verbs/{activity['verbSlug']}",
            "label_ar": "افتح ورشة الفعل",
        })

    if error_types and len(priorities) < 2:
        priorities.append({
            "type": "retry",
            "title_ar": "أعد المحاولة مباشرة",
            "detail_ar": "طبّق التصحيح على السؤال نفسه لتثبيت التعلم.",
            "href": retry_href,
            "label_ar": "ارجع إلى المحاولة",
        })

    return priorities[:2]


def evaluate_chapter_activity(
    *,
    chapter_slug: str,
    activity_kind: Literal["restitution", "document"],
    student_answer: str,
) -> dict[str, Any] | None:
    """Évalue le fond avant la méthode et retourne deux priorités maximum."""
    selected = get_chapter_activity(chapter_slug, activity_kind)
    if not selected:
        return None
    chapter, activity = selected
    reference = str(activity.get("referenceAnswerAr") or "")
    result = correct_bac_answer(
        {
            "points": activity.get("scoreMax", 4),
            "verb_slug": activity.get("verbSlug", "analyse"),
            "model_answer_ar": reference,
            "context_ar": _documents_context(activity),
            "instruction_ar": activity.get("promptAr", ""),
            "title_ar": activity.get("titleAr", ""),
        },
        student_answer,
    )

    # Invariant de calibration : la réponse de référence doit obtenir le
    # barème complet. Cela neutralise les faux négatifs regex sur ses propres
    # formulations sans élargir ce traitement aux autres copies.
    normalized_answer = " ".join(student_answer.casefold().split())
    normalized_reference = " ".join(reference.casefold().split())
    if normalized_reference and normalized_answer == normalized_reference:
        result.update({
            "score": result["score_max"],
            "percentage": 100,
            "scientific_ratio": 1.0,
            "methodology_ratio": 1.0,
            "scientific_errors": [],
            "methodology_error_code": "all_correct",
            "dominant_error_code": "all_correct",
        })

    scientific_percentage = round(float(result["scientific_ratio"]) * 100)
    methodology_percentage = round(float(result["methodology_ratio"]) * 100)
    answer_words = [word for word in student_answer.strip().split() if word]
    severe_scientific = result.get("dominant_error_code") == "scientific_error"
    reference_missing = not reference.strip()

    if scientific_percentage == 0 and len(answer_words) >= 4 and not severe_scientific:
        error_types = ["off_topic"]
    else:
        error_types = []
        if scientific_percentage < 70 or reference_missing:
            error_types.append("scientific_error")
        if methodology_percentage < 70:
            error_types.append("methodology_error")

    passed = (
        int(result["percentage"]) >= 70
        and scientific_percentage >= 70
        and not reference_missing
        and not error_types
    )
    priorities = _build_priorities(
        chapter=chapter,
        activity=activity,
        error_types=error_types,
    )

    warning_ar = ""
    if reference_missing:
        warning_ar = "لا توجد إجابة مرجعية موثقة؛ النتيجة محدودة إلى 50٪."

    return {
        "chapter_slug": chapter_slug,
        "activity_id": activity["id"],
        "activity_kind": activity_kind,
        "verb_slug": activity["verbSlug"],
        "score": result["score"],
        "score_max": result["score_max"],
        "percentage": result["percentage"],
        "passed": passed,
        "scientific": {
            "percentage": scientific_percentage,
            "errors": [
                _safe_internal_feedback(str(error))
                for error in result.get("scientific_errors", [])
            ][:3],
            "strengths": list(result.get("scientific_strengths", []))[:3],
        },
        "methodology": {
            "percentage": methodology_percentage,
            "dominant_error_code": result.get("methodology_error_code", "partial_correct"),
            "advice_ar": result.get("methodology_advice", ""),
        },
        "error_types": error_types,
        "priorities": priorities,
        "reference_answer_ar": reference,
        "reference_missing": reference_missing,
        "warning_ar": warning_ar,
        "allow_second_attempt": not passed or int(result["percentage"]) < 85,
        "source": "deterministic-science-first",
        "grading_validation": grading_validation_status(),
    }
