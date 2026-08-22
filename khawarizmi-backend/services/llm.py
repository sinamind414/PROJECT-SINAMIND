"""
services/llm.py — Moteur d'évaluation IA avec fallback multi-provider.

CHAÎNE DE FALLBACK (dans l'ordre) :
1. Provider principal (OPENAI_API_KEY + openai_base_url)
   → Auto-détecté : gsk_* → Groq, AIza* → Gemini, sinon OpenAI
2. Gemini 2.5 Flash (GEMINI_API_KEY) — 15 req/min gratuites
3. Cloudflare GLM-5.2 (CLOUDFLARE_API_TOKEN) — 10K neurons/jour
4. Z.AI GLM-4.7 (ZAI_API_KEY)
5. ZenMux GLM-5.2 (ZENMUX_API_KEY)
6. NaraRouter (NARA_API_KEY) — proxy OpenAI-compatible, 5M tokens/jour gratuit
7. OpenAI gpt-4o-mini (OPENAI_FALLBACK_API_KEY ou REAL_OPENAI_API_KEY)

Fallback sur rate limit (429/quota) et, si un validateur est fourni,
sur réponse HTTP 200 inexploitable (ex. JSON invalide).
"""

import logging
import time
from collections.abc import Callable

from openai import AsyncOpenAI
from tenacity import retry, stop_after_attempt, wait_exponential

from config import get_settings
from prompts.evaluation_prompt import EVALUATION_SYSTEM_PROMPT, build_evaluation_prompt
from services.llm_budget import LLMExternalDisabled, get_budget
from services.llm_parser import parse_llm_json
from services.llm_providers import apply_json_mode

logger = logging.getLogger("khawarizmi.llm")

# ── Budget global + circuit breaker (audit C3) ─────────────────────────
# Pire cas historique : 7 providers × timeout individuel → 175 s de blocage.
# Désormais : un DEADLINE global partagé + un breaker par provider.
GLOBAL_LLM_DEADLINE_SECONDS = 20.0
_BREAKER_COOLDOWN_SECONDS = 60.0
_BREAKER_FAIL_THRESHOLD = 3

_breaker_state: dict[str, tuple[int, float]] = {}  # name -> (failures, opened_at)


def _breaker_allow(name: str) -> bool:
    failures, opened_at = _breaker_state.get(name, (0, 0.0))
    if failures >= _BREAKER_FAIL_THRESHOLD:
        if time.monotonic() - opened_at > _BREAKER_COOLDOWN_SECONDS:
            _breaker_state[name] = (0, 0.0)  # half-open : on réessaie
            return True
        return False
    return True


def _breaker_record_failure(name: str) -> None:
    failures, _ = _breaker_state.get(name, (0, 0.0))
    _breaker_state[name] = (failures + 1, time.monotonic())


def _breaker_record_success(name: str) -> None:
    _breaker_state[name] = (0, 0.0)


def _tag_response_provider(
    response: object,
    provider: str,
    model: str,
    json_mode_used: bool = False,
) -> object:
    """Ajoute des métadonnées non bloquantes pour l'audit."""
    try:
        response._khawarizmi_provider = provider
        response._khawarizmi_model = model
        response._khawarizmi_json_mode = json_mode_used
    except Exception:
        pass
    return response


def _get_glm47_client():
    cfg = get_settings()
    if cfg.ZAI_API_KEY:
        return AsyncOpenAI(
            api_key=cfg.ZAI_API_KEY,
            base_url=cfg.zai_base_url,
        )
    return None


def _record_llm_usage(response: object, model: str, feature: str) -> None:
    """Enregistre le coût RÉEL d'un appel LLM externe réussi (G0-3) :
    cost_log.jsonl (cost_logger) + compteur budgétaire journalier
    (services/llm_budget). Défensif : un échec de traçage ne doit jamais
    casser l'appel lui-même."""
    try:
        usage = getattr(response, "usage", None)
        tin = int(getattr(usage, "prompt_tokens", 0) or 0)
        tout = int(getattr(usage, "completion_tokens", 0) or 0)
        if tin <= 0 and tout <= 0:
            return
        from cost_logger import get_logger

        entry = get_logger().record(model, tin, tout, "", feature=feature)
        get_budget().record_cost(entry["cost_usd"], model=model)
    except Exception as e:  # traçage = best-effort
        logger.debug(f"usage_record_skip | {e!s}")


async def _call_with_fallback(
    messages: list,
    primary_client: AsyncOpenAI,
    primary_model: str,
    temperature: float = 0,
    max_tokens: int = 400,
    timeout: float = 8.0,
    response_validator: Callable[[str], bool] | None = None,
    json_schema: dict | None = None,
    feature: str = "general",
) -> object:
    # ── Budget LLM + kill-switch (G0-3) : porte d'entrée unique du LLM externe ──
    budget = get_budget()
    if not budget.is_allowed(feature):
        st = budget.status()
        logger.warning(
            f"🛑 LLM_EXTERNAL_DISABLED | feature={feature} | "
            f"day_cost={st['day_cost_usd']} USD / budget={st['budget_usd']} USD | "
            f"auto_killed={st['auto_killed']} manual_kill={st['manual_kill']} "
            f"killed_features={st['killed_features']} → bascule étages locaux."
        )
        raise LLMExternalDisabled(
            f"LLM externe désactivé (feature={feature}) : budget journalier "
            f"dépassé ou kill-switch actif (LLM_KILL / LLM_KILL_FEATURES)."
        )
    cfg = get_settings()
    providers = []

    if cfg.GEMINI_API_KEY and cfg.GEMINI_API_KEY != "test-gemini-key":
        providers.append((
            "Gemini 2.5 Flash",
            AsyncOpenAI(
                api_key=cfg.GEMINI_API_KEY,
                base_url="https://generativelanguage.googleapis.com/v1beta/openai/",
            ),
            "gemini-2.5-flash",
        ))

    if cfg.CLOUDFLARE_API_TOKEN:
        providers.append((
            "Cloudflare GLM-5.2",
            AsyncOpenAI(
                api_key=cfg.CLOUDFLARE_API_TOKEN,
                base_url=f"https://api.cloudflare.com/client/v4/accounts/{cfg.CLOUDFLARE_ACCOUNT_ID}/ai/v1",
            ),
            "@cf/zai-org/glm-5.2",
        ))

    glm_client = _get_glm47_client()
    if glm_client:
        providers.append(("GLM-4.7", glm_client, cfg.zai_model))

    if cfg.ZENMUX_API_KEY:
        providers.append((
            "ZenMux GLM-5.2",
            AsyncOpenAI(api_key=cfg.ZENMUX_API_KEY, base_url=cfg.zenmux_base_url),
            cfg.zenmux_model,
        ))

    if cfg.NARA_API_KEY:
        providers.append((
            "NaraRouter",
            AsyncOpenAI(api_key=cfg.NARA_API_KEY, base_url=cfg.nara_base_url),
            cfg.nara_model,
        ))

    fallback_key = cfg.OPENAI_FALLBACK_API_KEY or cfg.REAL_OPENAI_API_KEY
    if fallback_key:
        providers.append((
            "OpenAI gpt-4o-mini",
            AsyncOpenAI(api_key=fallback_key, base_url="https://api.openai.com/v1"),
            "gpt-4o-mini",
        ))

    deadline = time.monotonic() + GLOBAL_LLM_DEADLINE_SECONDS

    try:
        primary_kwargs: dict = {
            "model": primary_model,
            "temperature": temperature,
            "max_tokens": max_tokens,
            "timeout": min(timeout, max(1.0, deadline - time.monotonic())),
            "messages": messages,
        }
        # JSON natif (O7) : dispatch par capacité déclarée du provider
        primary_json = apply_json_mode(primary_kwargs, "primary", json_schema, cfg)
        primary_response = await primary_client.chat.completions.create(**primary_kwargs)
        # Si un validateur est fourni et que le contenu du provider primaire
        # est invalide, on bascule vers les fallbacks au lieu de rendre
        # l'erreur silencieusement.
        if response_validator is not None:
            try:
                content = primary_response.choices[0].message.content or ""
                if not response_validator(content):
                    logger.warning(
                        "⚠️ Contenu primaire invalide (validateur) — "
                        "tentative fallback..."
                    )
                    raise ValueError("response_validator: contenu invalide")
            except (IndexError, AttributeError) as ve:
                logger.warning(
                    f"⚠️ Impossible d'extraire le contenu primaire pour "
                    f"validation — fallback. Erreur: {ve}"
                )
                raise ValueError(f"extract_failed: {ve}")
        _breaker_record_success("primary")
        _record_llm_usage(primary_response, primary_model, feature)
        return _tag_response_provider(
            primary_response, "primary", primary_model, primary_json
        )
    except Exception as e:
        is_rate_limit = "429" in str(e) or "quota" in str(e).lower() or "quota" in str(e)
        is_validator_reject = "response_validator" in str(e) or "extract_failed" in str(e)
        _breaker_record_failure("primary")
        if not is_rate_limit and not is_validator_reject:
            raise

    for name, client, model in providers:
        remaining = deadline - time.monotonic()
        if remaining < 2.0:
            logger.warning("⚠️ Deadline global LLM atteint — abandon des fallbacks.")
            break
        if not _breaker_allow(name):
            logger.warning(f"⛔ Circuit breaker OPEN pour {name} — provider sauté.")
            continue
        try:
            logger.warning(f"⚠️ Fallback vers {name}...")
            fallback_kwargs: dict = {
                "model": model,
                "temperature": temperature,
                "max_tokens": max_tokens,
                "timeout": min(timeout, remaining),
                "messages": messages,
            }
            # JSON natif (O7) : capacité déclarée du provider fallback
            fallback_json = apply_json_mode(fallback_kwargs, name, json_schema, cfg)
            resp = await client.chat.completions.create(**fallback_kwargs)
            if response_validator is not None:
                try:
                    content = resp.choices[0].message.content or ""
                    if not response_validator(content):
                        logger.warning(f"⚠️ Réponse fallback {name} invalide — provider suivant...")
                        _breaker_record_failure(name)
                        continue
                except (IndexError, AttributeError) as ve:
                    logger.warning(f"⚠️ Extraction réponse fallback {name} impossible — provider suivant. Erreur: {ve}")
                    _breaker_record_failure(name)
                    continue
            _breaker_record_success(name)
            logger.info(f"✅ Fallback {name} réussi.")
            _record_llm_usage(resp, model, feature)
            return _tag_response_provider(resp, name, model, fallback_json)
        except Exception as fallback_err:
            _breaker_record_failure(name)
            logger.error(f"❌ Échec {name} : {fallback_err}")

    raise RuntimeError("Tous les providers IA ont échoué ou retourné une réponse invalide. Réessaie plus tard.")


@retry(stop=stop_after_attempt(3), wait=wait_exponential(multiplier=1, min=1, max=4))
async def call_gpt4o_evaluator(client: AsyncOpenAI, question: dict, reponse: str, tentative: int) -> dict:
    """MOTEUR LEGACY — maintenu uniquement pour la réconciliation L1/L2
    (services/reconciliation_queue.py) et la route legacy /api/evaluate (non exposée).

    Le correcteur actif est evaluate_answer_v2 (services/correction_v2.py), utilisé
    par /api/document-analysis/evaluate-v2. Ne PAS brancher de nouvelle route sur
    ce moteur : deux notations cohabitent (score/10 ici vs score/score_max en v2).
    """
    concepts = question.get("concepts_requis", [])
    if not concepts and question.get("concept_cle"):
        concepts = [question["concept_cle"]]
    concepts_str = ", ".join(concepts)

    from services.eval_calibration import build_calibrated_prompt

    chapitre = question.get("chapitre_id", question.get("chapitre", ""))
    few_shot_block = build_calibrated_prompt(
        chapitre=chapitre,
        question_text=question.get("texte", ""),
        max_examples=3,
    )
    final_system_prompt = build_evaluation_prompt(EVALUATION_SYSTEM_PROMPT, few_shot_block)

    user_message = f"""QUESTION: {question.get("texte", "")}
REPONSE_ATTENDUE: {question.get("reponse_attendue", "")}
CONCEPT_CLE: {question.get("concept_cle", "")}
CONCEPTS_ATTENDUS: {concepts_str}
PATTERN_RECHERCHE: {question.get("pattern_recherche", "")}
TENTATIVE: {tentative}
REPONSE_ELEVE: {reponse}"""

    _model = get_settings().openai_model

    messages = [{"role": "system", "content": final_system_prompt}, {"role": "user", "content": user_message}]

    response = await _call_with_fallback(
        messages=messages,
        primary_client=client,
        primary_model=_model,
        feature="evaluate",
    )

    content = response.choices[0].message.content or ""
    result = parse_llm_json(content)

    if not result:
        # Tronqué : la sortie LLM peut citer la réponse de l'élève — on ne
        # veut pas qu'elle transite entière via le message d'exception
        # (logs / Sentry). Revue des logs 2026-08-21 (R19).
        raise ValueError(
            f"Échec de l'extraction JSON de la réponse : {content[:200]!r}"
        )

    global_score = float(result.get("global_score", 0.0))
    score_10 = int(round(global_score * 10))

    if global_score >= 0.85:
        statut = "CORRECT"
    elif global_score >= 0.35:
        statut = "PARTIEL"
    else:
        statut = "FAUX"

    has_arabic = any("\u0600" <= c <= "\u06ff" for c in reponse)
    feedback = result.get("feedback_ar") if has_arabic and result.get("feedback_ar") else result.get("feedback_fr")
    if not feedback:
        feedback = result.get("feedback_fr") or result.get("feedback_ar") or "Pas de feedback disponible."

    mapped_result = {
        "score": score_10,
        "statut": statut,
        "feedback": feedback,
        "manquant": result.get("missing_concepts", []),
        "scores_concepts": result.get("concept_scores", {}),
        "feedback_fr": result.get("feedback_fr", ""),
        "feedback_ar": result.get("feedback_ar", ""),
        "needs_l1_review": 0.35 <= global_score <= 0.70,
    }

    for concept in concepts:
        if concept not in mapped_result["scores_concepts"]:
            mapped_result["scores_concepts"][concept] = 0.5
            if not mapped_result["needs_l1_review"]:
                mapped_result["needs_l1_review"] = True

    return mapped_result
