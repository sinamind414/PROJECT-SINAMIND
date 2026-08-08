"""
services/correction_v2.py — Orchestrateur « correcteur comme un prof ».

Pipeline hybride :
  1. SANITY CHECK  → filtre charabia/vide sans LLM
  2. BUILD PROMPT  → contexte + docs + consigne + modèle + copie
  3. APPEL LLM     → _call_with_fallback (injectable pour tests)
  4. POST-VALIDATION → parse JSON tolérant, clamp score, validate highlights

Fonction exportée : evaluate_answer_v2(...)
Type exporté : LLMCaller (Protocol pour injection de dépendance)
"""

from __future__ import annotations

import logging
from typing import Any, Protocol, runtime_checkable

from config import get_settings
from cost_logger import get_logger
from grading.mapping import map_v2_to_v1
from grading.parser import parse_correction_response, record_parse_strategy
from grading.post_validate import (
    build_error_result,
    build_sanity_result,
    clamp,
    compute_dominant_error_code,
    finalize_result,
    normalize_unmatched,
    validate_highlights,
)
from grading.prompts import build_prompt
from grading.schemas.correction_output import (
    CORRECTION_V1_JSON_SCHEMA,
    CORRECTION_V2_JSON_SCHEMA,
)
from services.answer_sanity import check_answer_sanity

# ── Alias de compatibilité (S2.1e) ────────────────
# Les helpers vivent dans grading/post_validate.py ; les noms _* sont
# conservés pour les tests existants et le code interne du monolithe.
_clamp = clamp
_validate_highlights = validate_highlights
_normalize_unmatched = normalize_unmatched
_compute_dominant_error_code = compute_dominant_error_code
_build_sanity_result = build_sanity_result
_build_error_result = build_error_result

logger = logging.getLogger("khawarizmi.correction_v2")

# ── Paramètres LLM ────────────────────────────────
# NE PAS modifier sans accord utilisateur (cf. HANDOFF § 8)

LLM_TEMPERATURE = 0.0
LLM_MAX_TOKENS = 900  # audit C1.3 : un JSON v2 tient dans ~900 tokens ; 4096 = ~4× le besoin
LLM_TIMEOUT_SECONDS = 25.0

# ── Type pour injection du client LLM ─────────────


@runtime_checkable
class LLMCaller(Protocol):
    """Protocol pour l'appel LLM — permet le mock dans les tests."""

    async def __call__(
        self,
        messages: list,
        primary_client: Any,
        primary_model: str,
        temperature: float = 0,
        max_tokens: int = 400,
        timeout: float = 8.0,
        response_validator: Any = None,
    ) -> Any: ...


# ── Utilitaires de parsing JSON tolérant ──────────


def _extract_json_from_response(raw: str) -> dict | None:
    """Compat : délègue à grading/parser.parse_correction_response (O7).

    Le parsing tolérant (direct → fence → regex → partial) vit désormais dans
    grading/parser.py avec la stratégie native_json en tête quand le provider
    a répondu en mode JSON natif.
    """
    parsed, _ = parse_correction_response(raw)
    return parsed


async def _evaluate_local_fallback(
    *,
    student_answer: str,
    model_answer: str,
    question_skill: str,
    score_max: int,
    db: Any,
    log_prefix: str,
) -> dict[str, Any] | None:
    """Évaluation 100 % locale (0 token, 0 clé API) via fallback_v2 (L2).

    S2.1d : la logique vit dans grading/l2.py (run_l2) — cette fonction est
    une délégation conservée pour les 2 appels internes du monolithe.
    Retourne un résultat au format v2 (source="local"), ou None si l'échec.
    """
    from grading.l2 import run_l2

    return await run_l2(
        student_answer=student_answer,
        model_answer=model_answer,
        question_skill=question_skill,
        score_max=score_max,
        db=db,
        log_prefix=log_prefix,
    )


# ── Fonction principale ──────────────────────────


async def evaluate_answer_v2(
    *,
    # Le sujet (chargé depuis la DB par la route)
    scenario_context: str,
    documents: list[dict[str, Any]] | None,
    question_prompt: str,
    question_skill: str,
    verb_slug: str,
    model_answer: str,
    learning_focus: str | None,
    score_max: int,
    # La copie
    student_answer: str,
    # Injection LLM (prod : _call_with_fallback ; test : mock)
    llm_call: LLMCaller,
    primary_client: Any,
    primary_model: str,
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
    # S2.1b : sanity pré-calculée par le pipeline (grading/pipeline.py) —
    # évite de la refaire. Rétrocompatible : None = comportement historique.
    precomputed_sanity: tuple[bool, str, str] | None = None,
) -> dict[str, Any]:
    """Évalue une réponse d'élève avec le pipeline hybride sanity + LLM.

    Pipeline :
      1. Sanity check → rejet immédiat si charabia/vide
      2. Build prompt → contexte complet pour le LLM (v1 ou v2)
      3. Appel LLM → via llm_call injectable
      4. Post-validation → parse JSON, clamp score, validate highlights

    Args:
        use_v2_prompt: Si True, utilise le prompt v2 optimisé (~918 tokens vs ~3742).
                      Le format de sortie est mappé au format v1 pour compatibilité.

    Returns:
        dict conforme au format documenté dans le HANDOFF § 4
    """
    log_prefix = f"[{request_id}] " if request_id else ""

    # ── 1. SANITY CHECK ──────────────────────────

    # S2.1b : le pipeline (grading/pipeline.py) peut fournir un résultat
    # pré-calculé — le monolithe ne refait pas le calcul, mais reste la
    # SEULE source du format de résultat (parité garantie).
    if precomputed_sanity is not None:
        is_valid, sanity_code, sanity_message = precomputed_sanity
    else:
        is_valid, sanity_code, sanity_message = check_answer_sanity(student_answer)

    if not is_valid:
        logger.info(
            f"{log_prefix}sanity_reject | code={sanity_code} "
            f"verb={verb_slug} len={len(student_answer)}"
        )
        return _build_sanity_result(
            sanity_code=sanity_code,
            message_ar=sanity_message,
            score_max=score_max,
            student_answer=student_answer,
        )

    # ── 2. BUILD PROMPT ──────────────────────────
    # S2.1e : construction extraite dans grading/prompts.py (fonction pure) —
    # le plumbing async du RAG (v1) reste ici jusqu'à S2.1f.

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
        # Note: v2 inclut déjà le system prompt dans le user_prompt
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

        # Prompt v1 original (+ RAG)
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

    # ── 3. APPEL LLM ────────────────────────────

    llm_raw: str | None = None
    provider = "unknown"
    model = primary_model
    finish_reason = "unknown"
    json_mode_used = False

    # O7 : JSON natif provider. Le schéma doit correspondre au format demandé
    # par le prompt (v2 en prod : score 0-100 / errors / feedback / grade —
    # cf. grading/schemas/correction_output.py pour la divergence documentée).
    # Activation PROGRESSIVE : json_mode_providers (config) — défaut vide =
    # aucun response_format (comportement pré-O7). Le contrôle fin par
    # provider se fait dans apply_json_mode (services/llm_providers.py).
    cfg = get_settings()
    enabled_providers = getattr(cfg, "json_mode_providers", None) or []
    json_schema = (
        CORRECTION_V2_JSON_SCHEMA if use_v2_prompt else CORRECTION_V1_JSON_SCHEMA
    ) if enabled_providers else None

    def _llm_response_validator(content: str) -> bool:
        """Valide que la réponse LLM contient du JSON exploitable."""
        return parse_correction_response(content)[0] is not None

    try:
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
        # Correcteur local sans clé API : mieux qu'une erreur technique.
        if local_fallback:
            local_result = await _evaluate_local_fallback(
                student_answer=student_answer,
                model_answer=model_answer,
                question_skill=question_skill,
                score_max=score_max,
                db=local_fallback_db,
                log_prefix=log_prefix,
            )
            if local_result is not None:
                return local_result
        return _build_error_result(
            score_max=score_max,
            error_message=str(e),
            prompt_hash=prompt_hash,
            student_answer=student_answer,
            provider=provider,
            model=model,
        )

    # ── 4. POST-VALIDATION ───────────────────────

    # O7 : stratégie native_json en tête quand le provider a répondu en mode
    # JSON natif ; sinon fallback tolérant (direct → fence → regex → partial).
    parsed, parse_strategy = parse_correction_response(
        llm_raw, json_mode_used=json_mode_used
    )
    # Label provider (audit O7) : permet de savoir QUI produit des stratégies
    # de rattrapage (ex. 90 % des fence sur Groq → alerte d'intégration) et
    # de décider quels providers activer en JSON natif en priorité.
    record_parse_strategy(parse_strategy, provider)

    if parsed is None:
        logger.warning(
            f"{log_prefix}json_parse_failed | raw_len={len(llm_raw)} "
            f"raw_start={llm_raw[:100]!r}"
        )
        # Correcteur local sans clé API : mieux qu'une erreur technique.
        if local_fallback:
            local_result = await _evaluate_local_fallback(
                student_answer=student_answer,
                model_answer=model_answer,
                question_skill=question_skill,
                score_max=score_max,
                db=local_fallback_db,
                log_prefix=log_prefix,
            )
            if local_result is not None:
                return local_result
        return _build_error_result(
            score_max=score_max,
            error_message="Impossible de parser la réponse JSON du LLM.",
            llm_raw=llm_raw,
            prompt_hash=prompt_hash,
            student_answer=student_answer,
            provider=provider,
            model=model,
            finish_reason=finish_reason,
        )

    # ── Phase C — Mapping v2 → v1 si prompt v2 ──
    # Fonction pure extraite (audit O7, point 2) : grading/mapping.py —
    # testable unitairement avec du JSON natif parfait.
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

        score = _clamp(int(raw_score), 0, score_max)

        # Highlights
        raw_highlights = parsed.get("highlights", [])
        if not isinstance(raw_highlights, list):
            raw_highlights = []
            source = "llm_recovered"
        highlights = _validate_highlights(raw_highlights, student_answer)

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
        unmatched = _normalize_unmatched(raw_unmatched)

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

    # S2.1e : finalisation extraite dans grading/post_validate.py (finalize_result)
    return finalize_result(
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
