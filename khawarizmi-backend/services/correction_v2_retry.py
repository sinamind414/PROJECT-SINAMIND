"""
services/correction_v2_retry.py — Wrapper résilient avec retry.

Ajoute un retry ciblé sur erreurs LLM transitoires (503, timeout, etc.)
sans modifier le contrat de evaluate_answer_v2.

Erreurs transitoires → jusqu'à max_attempts tentatives avec backoff.
Erreurs permanentes (401, 400, JSON invalide) → pas de retry.

Nouveau source possible : "llm_retried" (succès après un retry).
Nouveau champ : "attempts" (int) dans le dict retourné.
"""

from __future__ import annotations

import asyncio
import logging
import re
from typing import Any

from services.correction_v2 import evaluate_answer_v2

logger = logging.getLogger("khawarizmi.correction_v2_retry")

# ── Patterns d'erreurs transitoires ─────────────────────────────────

_TRANSIENT_EXCEPTION_PATTERNS: list[re.Pattern] = [
    re.compile(r"5\d{2}", re.IGNORECASE),
    re.compile(r"timeout", re.IGNORECASE),
    re.compile(r"connection.*(reset|refused|closed|error)", re.IGNORECASE),
    re.compile(r"temporarily.unavailable", re.IGNORECASE),
    re.compile(r"overloaded", re.IGNORECASE),
    re.compile(r"high.demand", re.IGNORECASE),
    re.compile(r"try.again.later", re.IGNORECASE),
    re.compile(r"service.unavailable", re.IGNORECASE),
    re.compile(r"rate.limit", re.IGNORECASE),
    re.compile(r"quota", re.IGNORECASE),
    re.compile(r"429", re.IGNORECASE),
    re.compile(r"deadline.exceeded", re.IGNORECASE),
    re.compile(r"cancelled", re.IGNORECASE),
]

_PERMANENT_ERROR_MARKERS: list[str] = [
    "401", "403", "400", "404",
    "api.key", "api_key", "invalid key", "unauthorized",
    "impossible de parser", "json_parse_failed", "json parse",
    "jsom_parse", "ne correspond à aucun verbe",
]


def _is_transient_error(result: dict[str, Any]) -> bool:
    """Détermine si erreur est transitoire (retryable)."""
    source = result.get("source", "")
    if source != "llm_error":
        return False

    error_msg = result.get("error_message", "")
    if not error_msg:
        return False

    error_str = str(error_msg)

    for marker in _PERMANENT_ERROR_MARKERS:
        if marker in error_str.lower():
            return False

    return any(pattern.search(error_str) for pattern in _TRANSIENT_EXCEPTION_PATTERNS)


def _is_sanity_result(result: dict[str, Any]) -> bool:
    return result.get("source") == "sanity"


def _build_retry_result(
    result: dict[str, Any],
    attempts: int,
    was_retried: bool,
) -> dict[str, Any]:
    """Ajoute le champ attempts et ajuste source si retry réussi."""
    enriched = dict(result)
    enriched["attempts"] = attempts

    if was_retried and enriched.get("source") == "llm":
        enriched["source"] = "llm_retried"

    return enriched


async def evaluate_answer_v2_with_retry(
    *,
    max_attempts: int = 2,
    backoff_base_seconds: float = 1.5,
    backoff_mult: float = 2.0,
    **kwargs: Any,
) -> dict[str, Any]:
    """Wrapper de evaluate_answer_v2 avec retry sur erreurs transitoires.

    Mêmes paramètres que evaluate_answer_v2, plus :
        max_attempts: nombre max de tentatives (défaut: 2)
        backoff_base_seconds: délai initial entre tentatives (défaut: 1.5s)
        backoff_mult: multiplicateur du backoff (défaut: 2.0)

    Returns:
        dict identique à evaluate_answer_v2, avec en plus :
            "attempts": int — nombre de tentatives effectuées
        Et source="llm_retried" si succès après un retry.
    """
    request_id = kwargs.get("request_id")

    for attempt in range(1, max_attempts + 1):
        result = await evaluate_answer_v2(**kwargs)

        # Sanity check : jamais de retry pour du charabia
        if _is_sanity_result(result):
            return _build_retry_result(result, attempts=attempt, was_retried=False)

        # Erreur LLM : retry uniquement si transitoire
        if _is_transient_error(result):
            if attempt < max_attempts:
                backoff = backoff_base_seconds * (backoff_mult ** (attempt - 1))
                logger.warning(
                    f"[{request_id}] transient error on attempt {attempt}/{max_attempts} "
                    f"| error={result.get('error_message', '?')[:100]} "
                    f"| retrying in {backoff:.1f}s"
                )
                await asyncio.sleep(backoff)
                continue

            # Dernière tentative : on retourne l'erreur avec le compteur
            logger.error(
                f"[{request_id}] all {max_attempts} attempts failed "
                f"| last error={result.get('error_message', '?')[:100]}"
            )
            return _build_retry_result(result, attempts=max_attempts, was_retried=False)

        # Cas normal (succès LLM, recovered, etc.)
        was_retried = attempt > 1
        if was_retried:
            logger.info(
                f"[{request_id}] succeeded after {attempt} attempts "
                f"| source={result.get('source')} score={result.get('score')}/{result.get('score_max')}"
            )
        return _build_retry_result(result, attempts=attempt, was_retried=was_retried)

    # Ne devrait jamais arriver (l'erreur est retournée dans la boucle)
    return _build_retry_result(
        {"source": "llm_error", "score": 0, "score_max": kwargs.get("score_max", 0),
         "percentage": 0, "highlights": [], "matched_criteria": [],
         "unmatched_criteria": [], "feedback_ar": "", "advice_ar": "",
         "confidence": 0.0, "sanity_code": "ok",
         "error_message": "Max attempts reached without clear outcome"},
        attempts=max_attempts,
        was_retried=False,
    )
