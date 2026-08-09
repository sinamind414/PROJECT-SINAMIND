"""grading/pipeline.py — Orchestrateur complet du pipeline de correction (S2.1f).

Le pipeline appelle TOUTES les étapes directement :
    sanity → savoir (0 token) → prompt → LLM → parser → mapping v2→v1 →
    post-validation (finalize) ; L2 en fallback si LLM indisponible/JSON
    irrécupérable ; build_error_result sinon.

Contraintes architecturales (critère S2.1) :
- AUCUN import FastAPI / SQLAlchemy / Redis ici.
- AUCUN import de services/correction_v2 (la façade importe le pipeline,
  pas l'inverse — pas de cycle). L'étage savoir vient de grading/savoir,
  l'évaluation locale de grading/l2.
- Le cache C2 reste un décorateur extérieur (grading/cache.py).
- Le contexte est request-scoped (grading/context.py).

Fidélité stricte au comportement historique (les 43 tests de
test_correction_v2.py + test_correction_v2_retry.py, qui passent par la
façade, le garantissent) : même format de résultat, même mapping, même
cost logging, même gestion des erreurs.
"""

from __future__ import annotations

import logging
import time
from collections.abc import Awaitable, Callable
from typing import Any

from config import get_settings
from cost_logger import get_logger
from grading.context import PipelineContext
from grading.l2 import run_l2
from grading.mapping import map_v2_to_v1
from grading.metrics import record_grading_source
from grading.parser import parse_correction_response, record_parse_strategy
from grading.post_validate import (
    build_error_result,
    build_sanity_result,
    clamp,
    finalize_result,
    normalize_unmatched,
    validate_highlights,
)
from grading.prompts import build_prompt
from grading.sanity import run_sanity
from grading.savoir import run_savoir
from grading.schemas.correction_output import (
    CORRECTION_V1_JSON_SCHEMA,
    CORRECTION_V2_JSON_SCHEMA,
)
from grading.tracing import record_exception, set_span_attribute, trace_step

logger = logging.getLogger("khawarizmi.grading_pipeline")

# ── Paramètres LLM (S2.1f : vivent ici ; correction_v2 les ré-exporte) ──
# NE PAS modifier sans accord utilisateur (cf. HANDOFF § 8)
LLM_TEMPERATURE = 0.0
LLM_MAX_TOKENS = 900  # audit C1.3 : un JSON v2 tient dans ~900 tokens ; 4096 = ~4× le besoin
LLM_TIMEOUT_SECONDS = 25.0

# Champs variables exclus de la comparaison de parité (tests) : ils dépendent
# du run (hashes, horodatage).
VOLATILE_FIELDS = {
    "attempts",
    "prompt_hash",
    "student_answer_hash",
    "llm_raw_hash",
    "latency_ms",
}


async def evaluate_answer_v2_pipeline(
    *,
    question_id: int | str | None = None,
    # Le sujet (chargé depuis la DB par la route)
    scenario_context: str = "",
    documents: list[dict[str, Any]] | None = None,
    question_prompt: str = "",
    question_skill: str = "",
    verb_slug: str,
    model_answer: str,
    learning_focus: str | None = None,
    score_max: int,
    # La copie
    student_answer: str,
    # Injection LLM (prod : _call_with_fallback ; test : mock)
    llm_call: Callable[..., Awaitable[Any]] | None = None,
    primary_client: Any = None,
    primary_model: str = "",
    # RAG context provider (optionnel — dégradation silencieuse si absent)
    rag_context_provider: Any = None,
    request_id: str | None = None,
    # Phase C — prompt v2 optimisé (réduction ~68% tokens)
    use_v2_prompt: bool = False,
    # Correcteur local sans clé API : si True et que le LLM est indisponible,
    # on évalue par pattern-matching local (fallback_v2 L2) au lieu de llm_error.
    local_fallback: bool = False,
    local_fallback_db: Any = None,
    # Budget LLM restant (audit C3) : partagé entre les retries — la cascade
    # interne (_call_with_fallback) a déjà son propre deadline de 20 s.
    llm_timeout: float | None = None,
    # Rétrocompat : sanity pré-calculée (S2.1b) — None = calcul ici.
    precomputed_sanity: tuple[bool, str, str] | None = None,
    **kwargs: Any,
) -> dict[str, Any]:
    """Évalue une réponse d'élève : sanity → savoir → prompt → LLM →
    parser → mapping → post-validation (L2 en fallback).

    Mêmes paramètres que l'historique evaluate_answer_v2, plus
    question_id (contexte). Retourne le dict au contrat v2.
    """
    log_prefix = f"[{request_id}] " if request_id else ""

    ctx = PipelineContext(
        question_id=question_id or 0,
        verb_slug=verb_slug,
        score_max=score_max,
        student_answer=student_answer,
        model_answer=model_answer,
        scenario_context=scenario_context,
        documents=documents or [],
        learning_focus=learning_focus or "",
        question_text=question_prompt,
        llm_timeout=llm_timeout,
        request_id=request_id,
        use_v2_prompt=use_v2_prompt,
        local_fallback=local_fallback,
        local_fallback_db=local_fallback_db,
    )

    # ── 1. SANITY CHECK (toujours première) ──────
    # S2.4 : span OTel (no-op si dépendance absente) — durée via sanity_ms
    with trace_step("grading.sanity", {"verb": verb_slug}):
        pass
    t_sanity = time.perf_counter()
    if precomputed_sanity is not None:
        is_valid, sanity_code, sanity_message = precomputed_sanity
        sanity = {"is_valid": is_valid, "sanity_code": sanity_code,
                  "message_ar": sanity_message}
    else:
        sanity = run_sanity(student_answer)
        is_valid = sanity["is_valid"]
        sanity_code = sanity["sanity_code"]
        sanity_message = sanity["message_ar"]
    ctx.sanity_result = sanity
    ctx.steps["sanity_ms"] = (time.perf_counter() - t_sanity) * 1000.0

    if not is_valid:
        logger.info(
            f"{log_prefix}sanity_reject | code={sanity_code} "
            f"verb={verb_slug} len={len(student_answer)}"
        )
        # S2.3 : événement Prometheus (no-op si dépendance absente)
        from grading.observability import record_pipeline_event as _prom_event

        _prom_event("sanity_reject")
        result = build_sanity_result(
            sanity_code=sanity_code,
            message_ar=sanity_message,
            score_max=score_max,
            student_answer=student_answer,
        )
        ctx.final_result = result
        ctx.source = "sanity"
        ctx.llm_called = False
        return result

    # ── 2. Étage SAVOIR (0 token, 0 clé — feature flag par verbe) ──
    # S2.4 : span OTel (no-op si dépendance absente)
    with trace_step("grading.savoir", {"verb": verb_slug}):
        pass
    ctx.savoir_result = run_savoir(
        question=question_prompt,
        student_answer=student_answer,
        verb_slug=verb_slug,
        score_max=score_max,
        model_answer=model_answer,
    )
    if ctx.savoir_result is not None:
        record_grading_source("local_savoir", verb_slug)
        from grading.observability import record_pipeline_event as _prom_event

        _prom_event("savoir_promoted")
        ctx.final_result = ctx.savoir_result
        ctx.source = "local_savoir"
        ctx.llm_called = False
        return ctx.savoir_result

    # ── 3. BUILD PROMPT ──────────────────────────
    if use_v2_prompt:
        messages, prompt_hash = build_prompt(
            use_v2_prompt=True,
            scenario_context=scenario_context,
            documents=documents,
            question_prompt=question_prompt,
            question_skill=question_skill,
            verb_slug=verb_slug,
            model_answer=model_answer,
            student_answer=student_answer,
            learning_focus=learning_focus,
            score_max=score_max,
        )
        logger.info(f"{log_prefix}using_v2_prompt | hash={prompt_hash}")
    else:
        # RAG enrichment : injecter les extraits du LIVRE MANHADJIYA si
        # disponible (v1 uniquement)
        rag_context = None
        if rag_context_provider is not None:
            try:
                rag_context = await rag_context_provider(
                    verb_slug=verb_slug,
                    question_prompt=question_prompt,
                    student_answer=student_answer,
                )
            except Exception:
                logger.warning(f"{log_prefix}rag_provider_failed — poursuite sans RAG")

        messages, prompt_hash = build_prompt(
            use_v2_prompt=False,
            scenario_context=scenario_context,
            documents=documents,
            question_prompt=question_prompt,
            question_skill=question_skill,
            verb_slug=verb_slug,
            model_answer=model_answer,
            student_answer=student_answer,
            learning_focus=learning_focus,
            score_max=score_max,
            rag_context=rag_context,
        )

    # ── 4. APPEL LLM ─────────────────────────────
    llm_raw: str | None = None
    provider = "unknown"
    model = primary_model
    finish_reason = "unknown"
    json_mode_used = False

    # O7 : JSON natif provider — activation progressive (json_mode_providers)
    cfg = get_settings()
    enabled_providers = getattr(cfg, "json_mode_providers", None) or []
    json_schema = (
        CORRECTION_V2_JSON_SCHEMA if use_v2_prompt else CORRECTION_V1_JSON_SCHEMA
    ) if enabled_providers else None

    def _llm_response_validator(content: str) -> bool:
        """Valide que la réponse LLM contient du JSON exploitable."""
        return parse_correction_response(content)[0] is not None

    if llm_call is None:
        logger.error(f"{log_prefix}llm_call_non_fourni")
        if local_fallback:
            local_result = await run_l2(
                student_answer=student_answer,
                model_answer=model_answer,
                question_skill=question_skill,
                score_max=score_max,
                db=local_fallback_db,
                log_prefix=log_prefix,
            )
            if local_result is not None:
                from grading.observability import record_pipeline_event as _prom_event
                _prom_event("l2_fallback")
                return local_result
        from grading.observability import record_pipeline_event as _prom_event
        _prom_event("llm_error")
        return build_error_result(
            score_max=score_max,
            error_message="llm_call non fourni (pipeline)",
            prompt_hash=prompt_hash,
            student_answer=student_answer,
            provider=provider,
            model=model,
        )

    t_llm = time.perf_counter()
    try:
        set_span_attribute("grading.verb", verb_slug)
        set_span_attribute("grading.provider", provider)
        response = await llm_call(
            messages=messages,
            primary_client=primary_client,
            primary_model=primary_model,
            temperature=LLM_TEMPERATURE,
            max_tokens=LLM_MAX_TOKENS,
            timeout=llm_timeout if llm_timeout is not None else LLM_TIMEOUT_SECONDS,
            response_validator=_llm_response_validator,
            json_schema=json_schema,
        )

        # Extraire le contenu textuel
        try:
            choice = response.choices[0]
            llm_raw = choice.message.content or ""
            provider = getattr(response, "_khawarizmi_provider", provider)
            model = getattr(response, "_khawarizmi_model", model)
            finish_reason = getattr(choice, "finish_reason", None) or "unknown"
            json_mode_used = bool(getattr(response, "_khawarizmi_json_mode", False))
            logger.warning(
                f"{log_prefix}llm_response_fr | "
                f"fr={choice.finish_reason} rl={len(llm_raw)}"
            )

            # ── Cost logging ─────────────────────────
            usage = getattr(response, "usage", None)
            if usage:
                try:
                    cost_log = get_logger()
                    cost_log.record(
                        model=model,
                        input_tokens=getattr(usage, "prompt_tokens", 0) or 0,
                        output_tokens=getattr(usage, "completion_tokens", 0) or 0,
                        prompt_hash=prompt_hash,
                        verb_slug=verb_slug,
                        scenario_id=request_id or "",
                        latency_ms=0,
                    )
                except Exception as log_err:
                    logger.warning(f"{log_prefix}cost_log_failed | {log_err}")

        except Exception as extract_err:
            logger.error(f"{log_prefix}llm_extract_failed | {extract_err}")
            llm_raw = str(response)[:500]

    except Exception as e:
        logger.error(f"{log_prefix}llm_call_failed | error={e}")
        record_exception(e)  # S2.4 : exception sur le span courant
        # Correcteur local sans clé API : mieux qu'une erreur technique.
        if local_fallback:
            local_result = await run_l2(
                student_answer=student_answer,
                model_answer=model_answer,
                question_skill=question_skill,
                score_max=score_max,
                db=local_fallback_db,
                log_prefix=log_prefix,
            )
            if local_result is not None:
                from grading.observability import record_pipeline_event as _prom_event
                _prom_event("l2_fallback")
                return local_result
        from grading.observability import record_pipeline_event as _prom_event
        _prom_event("llm_error")
        return build_error_result(
            score_max=score_max,
            error_message=str(e),
            prompt_hash=prompt_hash,
            student_answer=student_answer,
            provider=provider,
            model=model,
        )
    finally:
        ctx.steps["llm_ms"] = (time.perf_counter() - t_llm) * 1000.0
        # S2.3 : histogramme latence LLM (no-op si dépendance absente)
        from grading.observability import observe_llm_latency as _prom_latency

        _prom_latency(ctx.steps["llm_ms"] / 1000.0)

    # ── 5. POST-VALIDATION — parsing ─────────────
    # O7 : stratégie native_json en tête quand le provider a répondu en mode
    # JSON natif ; sinon fallback tolérant (direct → fence → regex → partial).
    parsed, parse_strategy = parse_correction_response(
        llm_raw, json_mode_used=json_mode_used
    )
    # Label provider (audit O7) : qui produit les stratégies de rattrapage.
    record_parse_strategy(parse_strategy, provider)
    ctx.parse_strategy = parse_strategy

    if parsed is None:
        logger.warning(
            f"{log_prefix}json_parse_failed | raw_len={len(llm_raw)} "
            f"raw_start={llm_raw[:100]!r}"
        )
        if local_fallback:
            local_result = await run_l2(
                student_answer=student_answer,
                model_answer=model_answer,
                question_skill=question_skill,
                score_max=score_max,
                db=local_fallback_db,
                log_prefix=log_prefix,
            )
            if local_result is not None:
                from grading.observability import record_pipeline_event as _prom_event
                _prom_event("l2_fallback")
                return local_result
        from grading.observability import record_pipeline_event as _prom_event
        _prom_event("llm_error")
        return build_error_result(
            score_max=score_max,
            error_message="Impossible de parser la réponse JSON du LLM.",
            llm_raw=llm_raw,
            prompt_hash=prompt_hash,
            student_answer=student_answer,
            provider=provider,
            model=model,
            finish_reason=finish_reason,
        )

    # ── 6. Mapping v2 → v1 si prompt v2 ──────────
    v2_mapped: dict | None = None
    if use_v2_prompt and "errors" in parsed:
        logger.info(f"{log_prefix}mapping_v2_to_v1 | score_raw={parsed.get('score')}")
        v2_mapped = map_v2_to_v1(
            parsed, score_max=score_max, student_answer=student_answer
        )
        score = v2_mapped["score"]
        highlights = v2_mapped["highlights"]
        matched = v2_mapped["matched"]
        unmatched = v2_mapped["unmatched"]
        feedback_ar = v2_mapped["feedback_ar"]
        advice_ar = v2_mapped["advice_ar"]
        confidence = v2_mapped["confidence"]
        source = v2_mapped["source"]

    else:
        # ── Format v1 standard ──────────────────────
        source = "llm"  # valeur par défaut ; les branches de récupération ci-dessous la remplacent
        raw_score = parsed.get("score", 0)
        if not isinstance(raw_score, (int, float)):
            try:
                raw_score = int(raw_score)
            except (ValueError, TypeError):
                raw_score = 0
                source = "llm_recovered"

        score = clamp(int(raw_score), 0, score_max)

        # Highlights
        raw_highlights = parsed.get("highlights", [])
        if not isinstance(raw_highlights, list):
            raw_highlights = []
            source = "llm_recovered"
        highlights = validate_highlights(raw_highlights, student_answer)

        # Critères matchés
        matched = parsed.get("matched_criteria", [])
        if not isinstance(matched, list):
            matched = []
            source = "llm_recovered"

        # Critères non matchés
        raw_unmatched = parsed.get("unmatched_criteria", [])
        if not isinstance(raw_unmatched, list):
            raw_unmatched = []
            source = "llm_recovered"
        unmatched = normalize_unmatched(raw_unmatched)

        # Feedback
        feedback_ar = parsed.get("feedback_ar", "")
        if not isinstance(feedback_ar, str):
            feedback_ar = str(feedback_ar)

        advice_ar = parsed.get("advice_ar", "")
        if advice_ar is None:  # champ optionnel nullable (O7) — pas de "None"
            advice_ar = ""
        elif not isinstance(advice_ar, str):
            advice_ar = str(advice_ar)

        # Confiance
        raw_confidence = parsed.get("confidence", 0.5)
        try:
            confidence = float(raw_confidence)
            confidence = max(0.0, min(1.0, confidence))
        except (ValueError, TypeError):
            confidence = 0.5
            source = "llm_recovered"

    from grading.observability import record_pipeline_event as _prom_event

    _prom_event("llm_ok")

    # ── 7. Finalisation (post_validate.finalize_result) ──
    result = finalize_result(
        source=source,
        score=score,
        score_max=score_max,
        highlights=highlights,
        matched=matched,
        unmatched=unmatched,
        feedback_ar=feedback_ar,
        advice_ar=advice_ar,
        confidence=confidence,
        provider=provider,
        model=model,
        finish_reason=finish_reason,
        prompt_hash=prompt_hash,
        student_answer=student_answer,
        llm_raw=llm_raw,
        verb_slug=verb_slug,
        dominant_error_code=(
            v2_mapped["dominant_error_code"] if v2_mapped is not None else None
        ),
        log_prefix=log_prefix,
    )

    ctx.final_result = result
    ctx.source = result.get("source", "unknown")
    ctx.llm_called = True
    return result


def assert_parity(
    pipeline_result: dict[str, Any],
    legacy_result: dict[str, Any],
    *,
    extra_volatile: set[str] | None = None,
) -> None:
    """Compare deux résultats (champs fonctionnels) — ignore les champs
    VOLATILE_FIELDS (variables par run) + extra_volatile."""
    ignored = VOLATILE_FIELDS | (extra_volatile or set())
    p = {k: v for k, v in pipeline_result.items() if k not in ignored}
    l = {k: v for k, v in legacy_result.items() if k not in ignored}
    assert p == l, (
        f"PARITÉ CASSÉE — pipeline ≠ legacy\n"
        f"  champs pipeline seuls : {set(p) - set(l)}\n"
        f"  champs legacy seuls : {set(l) - set(p)}\n"
        f"  différences : {[(k, p.get(k), l.get(k)) for k in set(p) & set(l) if p[k] != l[k]][:5]}"
    )
