"""grading/post_validate.py — Post-validation et builders de résultats (S2.1e).

Extrait de correction_v2.py : les helpers de validation (highlights,
critères), les builders de résultats (sanity, llm_error) et la finalisation
du résultat v2 (percentage, success/missing/errors, dominant_error_code,
remédiation, hashes RGPD, parse_status).

Fidélité stricte à l'original (les tests de parité existants le garantissent) :
- validate_highlights : types autorisés = {gibberish, off_topic, missing_link,
  wrong_formulation, irrelevant, good_element} ; clamp aux bornes ; type
  inconnu → "irrelevant" ; start>=end → filtré.
- compute_dominant_error_code : sanity d'abord, all_correct si plein,
  scientific_error/off_topic/methodology_error selon highlights/unmatched.
- finalize_result : le dict final au contrat v2 — llm_raw JAMAIS exposé
  (uniquement son hash), parse_status "ok" si source=="llm" sinon "recovered".
"""

from __future__ import annotations

import logging
from typing import Any

from services.hashing import hash_answer
from services.remediation_service import get_generic_remediation, get_remediation

logger = logging.getLogger("khawarizmi.grading_post_validate")

_HIGHLIGHT_TYPES = {
    "gibberish",
    "off_topic",
    "missing_link",
    "wrong_formulation",
    "irrelevant",
    "good_element",
}


def clamp(value: int, min_val: int, max_val: int) -> int:
    """Clampe une valeur entre min et max."""
    return max(min_val, min(value, max_val))


def validate_highlights(
    highlights: list[dict],
    student_answer: str,
) -> list[dict]:
    """Valide et corrige les highlights retournés par le LLM.

    - Filtre les highlights avec start/end invalides
    - Clampe start/end dans les bornes du texte
    - S'assure que type est un type valide
    """
    valid_types = _HIGHLIGHT_TYPES
    text_len = len(student_answer)
    validated = []

    for h in highlights:
        if not isinstance(h, dict):
            continue

        start = h.get("start")
        end = h.get("end")
        h_type = h.get("type", "")
        message = h.get("message_ar", "")

        # Vérifier que start/end sont des entiers
        if not isinstance(start, int) or not isinstance(end, int):
            continue

        # Clamper dans les bornes
        start = clamp(start, 0, text_len)
        end = clamp(end, 0, text_len)

        # start doit être < end
        if start >= end:
            continue

        # Normaliser le type
        if h_type not in valid_types:
            h_type = "irrelevant"  # type par défaut

        validated.append({
            "start": start,
            "end": end,
            "type": h_type,
            "message_ar": str(message),
        })

    return validated


def normalize_unmatched(unmatched: list) -> list[dict]:
    """Normalise les critères non matchés retournés par le LLM."""
    result = []
    for item in unmatched:
        if isinstance(item, str):
            result.append({
                "criterion": item,
                "why_ar": "",
                "from_model_answer": "",
            })
        elif isinstance(item, dict):
            result.append({
                "criterion": item.get("criterion", str(item)),
                "why_ar": item.get("why_ar", ""),
                "from_model_answer": item.get("from_model_answer", ""),
            })
    return result


def build_sanity_result(
    *,
    sanity_code: str,
    message_ar: str,
    score_max: int,
    student_answer: str,
) -> dict[str, Any]:
    """Construit le résultat quand le sanity check rejette la réponse."""
    highlights = []
    if student_answer.strip():
        # Surligner tout le texte en rouge (charabia)
        highlights = [{
            "start": 0,
            "end": len(student_answer),
            "type": "gibberish",
            "message_ar": message_ar,
        }]

    return {
        "source": "sanity",
        "score": 0,
        "score_max": score_max,
        "percentage": 0,
        "highlights": highlights,
        "matched_criteria": [],
        "unmatched_criteria": [],
        "feedback_ar": message_ar,
        "advice_ar": "أعد كتابة إجابتك بشكل واضح ومنظم باللغة العربية.",
        "confidence": 1.0,
        "sanity_code": sanity_code,
        "provider": "none",
        "model": "none",
        "finish_reason": "sanity",
        "prompt_hash": None,
        "student_answer_hash": hash_answer(student_answer),
        "llm_raw_hash": None,
        "parse_status": "not_called",
        # Spec §3.1 — champs additionnels
        "missing": [],
        "dominant_error_code": sanity_code,
        "success": [],
        "errors": [],
        # Guide p.2 — remédiation automatique
        "remediation": None,
    }


def build_error_result(
    *,
    score_max: int,
    error_message: str,
    llm_raw: str | None = None,
    prompt_hash: str | None = None,
    student_answer: str = "",
    provider: str = "unknown",
    model: str = "unknown",
    finish_reason: str = "unknown",
) -> dict[str, Any]:
    """Construit le résultat quand l'appel LLM échoue."""
    return {
        "source": "llm_error",
        "score": 0,
        "score_max": score_max,
        "percentage": 0,
        "highlights": [],
        "matched_criteria": [],
        "unmatched_criteria": [],
        "feedback_ar": "حدث خطأ تقني أثناء التصحيح. يرجى المحاولة لاحقاً.",
        "advice_ar": "",
        "confidence": 0.0,
        "sanity_code": "ok",
        "llm_raw": llm_raw,  # debug interne — jamais exposé publiquement
        "error_message": error_message,
        "provider": provider,
        "model": model,
        "finish_reason": finish_reason,
        "prompt_hash": prompt_hash,
        "student_answer_hash": hash_answer(student_answer),
        "llm_raw_hash": hash_answer(llm_raw) if llm_raw is not None else None,
        "parse_status": "failed",
        # Spec §3.1 — champs additionnels
        "missing": [],
        "dominant_error_code": "server_error",
        "success": [],
        "errors": [],
        "remediation": None,
    }


def compute_dominant_error_code(
    highlights: list[dict],
    unmatched: list[dict],
    sanity_code: str,
    score: int,
    score_max: int,
) -> str:
    """Détermine le code d'erreur dominant pour le retour API (Spec §3.1)."""
    if sanity_code != "ok":
        return sanity_code  # gibberish, too_short, empty, etc.

    if score == score_max:
        return "all_correct"

    highlight_types = {h.get("type") for h in highlights if isinstance(h, dict)}

    if "scientific_error" in highlight_types:
        return "scientific_error"
    if "off_topic" in highlight_types:
        return "off_topic"
    if "missing_link" in highlight_types:
        return "methodology_error"
    if unmatched:
        return "methodology_error"
    if score < score_max:
        return "partial_correct"

    return "unknown"


def finalize_result(
    *,
    source: str,
    score: int,
    score_max: int,
    highlights: list[dict],
    matched: list,
    unmatched: list[dict],
    feedback_ar: str,
    advice_ar: str,
    confidence: float,
    provider: str,
    model: str,
    finish_reason: str,
    prompt_hash: str | None,
    student_answer: str,
    llm_raw: str | None,
    verb_slug: str,
    dominant_error_code: str | None = None,
    log_prefix: str = "",
) -> dict[str, Any]:
    """Finalise le résultat v2 : pourcentage, champs spec, code dominant,
    remédiation, hashes RGPD, parse_status. Fidèle au bloc final original."""
    percentage = round((score / score_max) * 100) if score_max > 0 else 0

    logger.info(
        f"{log_prefix}eval_v2_done | verb={verb_slug} source={source} "
        f"score={score}/{score_max} ({percentage}%) highlights={len(highlights)}"
    )

    # Spec §3.1 — mapping des champs
    success = [str(m) for m in matched]
    missing = [
        {
            "expected": u["criterion"],
            "why_ar": u.get("why_ar", ""),
            "from_model_answer": u.get("from_model_answer", ""),
        }
        for u in unmatched if isinstance(u, dict)
    ]
    errors = list(unmatched)  # alias spec-compatible

    if dominant_error_code is None:
        dominant_error_code = compute_dominant_error_code(
            highlights=highlights,
            unmatched=unmatched,
            sanity_code="ok",
            score=score,
            score_max=score_max,
        )

    # Guide p.2 — remédiation automatique
    remediation = get_remediation(verb_slug, dominant_error_code)
    if remediation is None:
        remediation = get_generic_remediation(dominant_error_code)

    return {
        "source": source,
        "score": score,
        "score_max": score_max,
        "percentage": percentage,
        "highlights": highlights,
        "matched_criteria": success,
        "unmatched_criteria": unmatched,
        "feedback_ar": feedback_ar,
        "advice_ar": advice_ar,
        "confidence": confidence,
        "sanity_code": "ok",
        # NOTE : llm_raw volontairement absent du contrat public (fuite potentielle).
        # Conservé uniquement dans le résultat llm_error (debug interne, jamais exposé).
        "provider": provider,
        "model": model,
        "finish_reason": finish_reason,
        "prompt_hash": prompt_hash,
        "student_answer_hash": hash_answer(student_answer),
        "llm_raw_hash": hash_answer(llm_raw) if llm_raw is not None else None,
        "parse_status": "ok" if source == "llm" else "recovered",
        # Spec §3.1 — champs additionnels
        "missing": missing,
        "dominant_error_code": dominant_error_code,
        "success": success,
        "errors": errors,
        "remediation": remediation,
    }
