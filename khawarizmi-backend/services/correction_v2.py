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

import hashlib
import json
import logging
import re
from typing import Any, Protocol, runtime_checkable

from prompts.correction_prompt import (
    SYSTEM_PROMPT_AR,
    build_correction_prompt,
)
from services.answer_sanity import check_answer_sanity
from services.remediation_service import get_generic_remediation, get_remediation

logger = logging.getLogger("khawarizmi.correction_v2")

# ── Paramètres LLM ────────────────────────────────
# NE PAS modifier sans accord utilisateur (cf. HANDOFF § 8)

LLM_TEMPERATURE = 0.0
LLM_MAX_TOKENS = 4096
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
    if not raw:
        return None

    # Essai 1: parsing direct
    for attempt in (raw.strip(),):
        try:
            return json.loads(attempt)
        except (json.JSONDecodeError, ValueError):
            pass

    # Essai 2: fences markdown
    fence = re.search(r"```(?:json)?\s*[\r\n]+(.+?)[\r\n]+\s*```", raw, re.DOTALL)
    if fence:
        try:
            return json.loads(fence.group(1).strip())
        except (json.JSONDecodeError, ValueError):
            pass

    # Essai 3: premier { au dernier } (tolérant JSON tronqué)
    start = raw.find("{")
    end = raw.rfind("}")
    if start != -1 and end != -1 and end > start:
        try:
            return json.loads(raw[start:end + 1])
        except (json.JSONDecodeError, ValueError):
            pass

    # Essai 4: { ... } englobant (depth)
    depth = 0
    start_idx = None
    for i, ch in enumerate(raw):
        if ch == "{":
            start_idx = i if start_idx is None else start_idx
            depth += 1
        elif ch == "}":
            depth -= 1
            if depth == 0 and start_idx is not None:
                try:
                    return json.loads(raw[start_idx:i + 1])
                except (json.JSONDecodeError, ValueError):
                    start_idx = None

    return None


def _clamp(value: int, min_val: int, max_val: int) -> int:
    """Clampe une valeur entre min et max."""
    return max(min_val, min(value, max_val))


def _validate_highlights(
    highlights: list[dict],
    student_answer: str,
) -> list[dict]:
    """Valide et corrige les highlights retournés par le LLM.

    - Filtre les highlights avec start/end invalides
    - Clampe start/end dans les bornes du texte
    - S'assure que type est un type valide
    """
    valid_types = {
        "gibberish",
        "off_topic",
        "missing_link",
        "wrong_formulation",
        "irrelevant",
        "good_element",
    }
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
        start = _clamp(start, 0, text_len)
        end = _clamp(end, 0, text_len)

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


def _normalize_unmatched(unmatched: list) -> list[dict]:
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


# ── Résultat sanity (score = 0, pas d'appel LLM) ─


def _build_sanity_result(
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
        "llm_raw": None,
        "provider": "none",
        "model": "none",
        "finish_reason": "sanity",
        "prompt_hash": None,
        "student_answer_hash": _sha256_text(student_answer),
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


# ── Résultat erreur LLM ──────────────────────────


def _build_error_result(
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
        "llm_raw": llm_raw,
        "error_message": error_message,
        "provider": provider,
        "model": model,
        "finish_reason": finish_reason,
        "prompt_hash": prompt_hash,
        "student_answer_hash": _sha256_text(student_answer),
        "llm_raw_hash": _sha256_text(llm_raw) if llm_raw is not None else None,
        "parse_status": "failed",
        # Spec §3.1 — champs additionnels
        "missing": [],
        "dominant_error_code": "server_error",
        "success": [],
        "errors": [],
        "remediation": None,
    }


def _sha256_text(value: str) -> str:
    return hashlib.sha256(value.encode("utf-8")).hexdigest()


# ── dominant_error_code — Spec §3.1 ──────────────


def _compute_dominant_error_code(
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
) -> dict[str, Any]:
    """Évalue une réponse d'élève avec le pipeline hybride sanity + LLM.

    Pipeline :
      1. Sanity check → rejet immédiat si charabia/vide
      2. Build prompt → contexte complet pour le LLM
      3. Appel LLM → via llm_call injectable
      4. Post-validation → parse JSON, clamp score, validate highlights

    Returns:
        dict conforme au format documenté dans le HANDOFF § 4
    """
    log_prefix = f"[{request_id}] " if request_id else ""

    # ── 1. SANITY CHECK ──────────────────────────

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

    user_prompt = build_correction_prompt(
        scenario_context=scenario_context,
        documents=documents,
        question_prompt=question_prompt,
        question_skill=question_skill,
        verb_slug=verb_slug,
        model_answer=model_answer,
        learning_focus=learning_focus,
        score_max=score_max,
        student_answer=student_answer,
    )

    # RAG enrichment : injecter les extraits du LIVRE MANHADJIYA si disponible
    if rag_context_provider is not None:
        try:
            rag_context = await rag_context_provider(
                verb_slug=verb_slug,
                question_prompt=question_prompt,
                student_answer=student_answer,
            )
            if rag_context:
                user_prompt = (
                    f"{user_prompt}\n\n"
                    "═══ مقتطفات من الكتاب المنهجي (RAG) ═══\n"
                    f"{rag_context}"
                )
        except Exception:
            logger.warning(f"{log_prefix}rag_provider_failed — poursuite sans RAG")

    prompt_hash = _sha256_text(user_prompt)

    messages = [
        {"role": "system", "content": SYSTEM_PROMPT_AR},
        {"role": "user", "content": user_prompt},
    ]

    # ── 3. APPEL LLM ────────────────────────────

    llm_raw: str | None = None
    provider = "unknown"
    model = primary_model
    finish_reason = "unknown"

    def _llm_response_validator(content: str) -> bool:
        """Valide que la réponse LLM contient du JSON exploitable."""
        return _extract_json_from_response(content) is not None

    try:
        response = await llm_call(
            messages=messages,
            primary_client=primary_client,
            primary_model=primary_model,
            temperature=LLM_TEMPERATURE,
            max_tokens=LLM_MAX_TOKENS,
            timeout=LLM_TIMEOUT_SECONDS,
            response_validator=_llm_response_validator,
        )

        # Extraire le contenu textuel
        try:
            choice = response.choices[0]
            llm_raw = choice.message.content or ""
            provider = getattr(response, "_khawarizmi_provider", provider)
            model = getattr(response, "_khawarizmi_model", model)
            finish_reason = getattr(choice, "finish_reason", None) or "unknown"
            logger.warning(
                f"{log_prefix}llm_response_fr | "
                f"fr={choice.finish_reason} rl={len(llm_raw)}"
            )
        except Exception as extract_err:
            logger.error(f"{log_prefix}llm_extract_failed | {extract_err}")
            llm_raw = str(response)[:500]

    except Exception as e:
        logger.error(f"{log_prefix}llm_call_failed | error={e}")
        return _build_error_result(
            score_max=score_max,
            error_message=str(e),
            prompt_hash=prompt_hash,
            student_answer=student_answer,
            provider=provider,
            model=model,
        )

    # ── 4. POST-VALIDATION ───────────────────────

    parsed = _extract_json_from_response(llm_raw)

    if parsed is None:
        logger.warning(
            f"{log_prefix}json_parse_failed | raw_len={len(llm_raw)} "
            f"raw_start={llm_raw[:100]!r}"
        )
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

    # Extraire les champs avec valeurs par défaut
    source = "llm"

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
    if not isinstance(advice_ar, str):
        advice_ar = str(advice_ar)

    # Confiance
    raw_confidence = parsed.get("confidence", 0.5)
    try:
        confidence = float(raw_confidence)
        confidence = max(0.0, min(1.0, confidence))
    except (ValueError, TypeError):
        confidence = 0.5
        source = "llm_recovered"

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
    dominant_error_code = _compute_dominant_error_code(
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
        "llm_raw": llm_raw,
        "provider": provider,
        "model": model,
        "finish_reason": finish_reason,
        "prompt_hash": prompt_hash,
        "student_answer_hash": _sha256_text(student_answer),
        "llm_raw_hash": _sha256_text(llm_raw) if llm_raw is not None else None,
        "parse_status": "ok" if source == "llm" else "recovered",
        # Spec §3.1 — champs additionnels
        "missing": missing,
        "dominant_error_code": dominant_error_code,
        "success": success,
        "errors": errors,
        "remediation": remediation,
    }
