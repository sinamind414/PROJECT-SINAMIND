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

Un fallback ne se déclenche QUE sur rate limit (429/quota).
Les erreurs réseau/non-429 remontent directement.
"""

import json
import logging
import re

from openai import AsyncOpenAI
from tenacity import retry, stop_after_attempt, wait_exponential

from config import get_settings
from services.llm_parser import parse_llm_json
from prompts.evaluation_prompt import EVALUATION_SYSTEM_PROMPT, build_evaluation_prompt

logger = logging.getLogger("khawarizmi.llm")


def _get_glm47_client():
    cfg = get_settings()
    if cfg.ZAI_API_KEY:
        return AsyncOpenAI(
            api_key=cfg.ZAI_API_KEY,
            base_url=cfg.zai_base_url,
        )
    return None


async def _call_with_fallback(
    messages: list,
    primary_client: AsyncOpenAI,
    primary_model: str,
    temperature: float = 0,
    max_tokens: int = 400,
    timeout: float = 8.0,
) -> object:
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

    try:
        return await primary_client.chat.completions.create(
            model=primary_model,
            temperature=temperature,
            max_tokens=max_tokens,
            timeout=timeout,
            messages=messages,
        )
    except Exception as e:
        is_rate_limit = "429" in str(e) or "quota" in str(e).lower()
        if not is_rate_limit:
            raise

    for name, client, model in providers:
        try:
            logger.warning(f"⚠️ Fallback vers {name}...")
            resp = await client.chat.completions.create(
                model=model,
                temperature=temperature,
                max_tokens=max_tokens,
                timeout=timeout,
                messages=messages,
            )
            logger.info(f"✅ Fallback {name} réussi.")
            return resp
        except Exception as fallback_err:
            logger.error(f"❌ Échec {name} : {fallback_err}")

    raise RuntimeError("Tous les providers IA ont échoué (rate limit). Réessaie plus tard.")


@retry(stop=stop_after_attempt(3), wait=wait_exponential(multiplier=1, min=1, max=4))
async def call_gpt4o_evaluator(client: AsyncOpenAI, question: dict, reponse: str, tentative: int) -> dict:
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
    )

    content = response.choices[0].message.content or ""
    result = parse_llm_json(content)

    if not result:
        raise ValueError(f"Échec de l'extraction JSON de la réponse : {content!r}")

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
