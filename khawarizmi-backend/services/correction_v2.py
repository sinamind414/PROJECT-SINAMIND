"""services/correction_v2.py — Façade de compatibilité (S2.1f).

La logique vit dans grading/pipeline.py (sanity → savoir → prompt → LLM →
parser → mapping → post-validation, L2 en fallback). Ce fichier conserve la
signature publique historique, les alias des helpers et les constantes LLM —
ne PAS ajouter de logique ici. Le retry (correction_v2_retry.py) importe
evaluate_answer_v2 depuis ici : il enveloppe le pipeline (budget C3 conservé).
"""

from __future__ import annotations

import logging
from typing import Any, Protocol

from grading.pipeline import (
    LLM_MAX_TOKENS,
    LLM_TEMPERATURE,
    LLM_TIMEOUT_SECONDS,
    evaluate_answer_v2_pipeline,
)
from grading.post_validate import (
    build_error_result,
    build_sanity_result,
    clamp,
    compute_dominant_error_code,
    normalize_unmatched,
    validate_highlights,
)

# ── Alias de compatibilité (helpers → grading.post_validate) ────────
_clamp, _validate_highlights, _normalize_unmatched = clamp, validate_highlights, normalize_unmatched
_compute_dominant_error_code, _build_sanity_result = compute_dominant_error_code, build_sanity_result
_build_error_result = build_error_result

__all__ = ["evaluate_answer_v2", "LLM_TEMPERATURE", "LLM_MAX_TOKENS", "LLM_TIMEOUT_SECONDS",
           "_extract_json_from_response", "_validate_highlights", "_normalize_unmatched",
           "_clamp", "_build_sanity_result", "_build_error_result", "_compute_dominant_error_code"]

logger = logging.getLogger("khawarizmi.correction_v2")


# ── Type pour injection du client LLM ─────────────

class LLMCaller(Protocol):
    """Protocole d'appel LLM injectable (tests : mock ; prod : _call_with_fallback)."""

    async def __call__(self, **kwargs: Any) -> Any: ...


def _extract_json_from_response(raw: str) -> dict | None:
    """Compat : délègue à grading/parser.parse_correction_response."""
    from grading.parser import parse_correction_response

    parsed, _ = parse_correction_response(raw)
    return parsed


async def evaluate_answer_v2(
    *,
    scenario_context: str,
    documents: list[dict[str, Any]] | None,
    question_prompt: str,
    question_skill: str,
    verb_slug: str,
    model_answer: str,
    learning_focus: str | None,
    score_max: int,
    student_answer: str,
    llm_call: LLMCaller,
    primary_client: Any,
    primary_model: str,
    rag_context_provider: Any = None,
    request_id: str | None = None,
    use_v2_prompt: bool = False,
    local_fallback: bool = False,
    local_fallback_db: Any = None,
    llm_timeout: float | None = None,
    precomputed_sanity: tuple[bool, str, str] | None = None,
    **kwargs: Any,
) -> dict[str, Any]:
    """Façade — délègue au pipeline complet (signature historique conservée)."""
    return await evaluate_answer_v2_pipeline(
        scenario_context=scenario_context, documents=documents,
        question_prompt=question_prompt, question_skill=question_skill,
        verb_slug=verb_slug, model_answer=model_answer,
        learning_focus=learning_focus, score_max=score_max,
        student_answer=student_answer, llm_call=llm_call,
        primary_client=primary_client, primary_model=primary_model,
        rag_context_provider=rag_context_provider, request_id=request_id,
        use_v2_prompt=use_v2_prompt, local_fallback=local_fallback,
        local_fallback_db=local_fallback_db, llm_timeout=llm_timeout,
        precomputed_sanity=precomputed_sanity, **kwargs,
    )
