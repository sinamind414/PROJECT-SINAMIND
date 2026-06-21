import json
import logging
from typing import Dict
from fastapi import APIRouter, HTTPException, Depends, Request
from fastapi.responses import JSONResponse
from sqlalchemy.ext.asyncio import AsyncSession
from openai import AsyncOpenAI
from config import get_settings
from cache import get_cache, set_cache, make_cache_key
from deps import get_current_user, get_tutor, get_openai
from rate_limit import limiter, chat_limit
from schemas.session import ChatRequest
from services.khawarizmi_engine import KhawarizmiTutor

logger = logging.getLogger("khawarizmi.api")
router = APIRouter()


@router.post("/api/chat", tags=["IA"])
@limiter.limit(chat_limit)
async def chat_socratique(
    request:      Request,
    body:         ChatRequest,
    current_user: Dict        = Depends(get_current_user),
    tutor:        KhawarizmiTutor = Depends(get_tutor),
    openai_client:AsyncOpenAI = Depends(get_openai),
):
    cfg = get_settings()

    cache_key = make_cache_key(
        "chat", body.sujet_id, body.question_id,
        body.message[:100], body.mode_force or "auto"
    )
    cached = await get_cache(cache_key)
    if cached:
        logger.debug(f"Cache HIT : {cache_key[:20]}...")
        result = json.loads(cached)
        result["from_cache"] = True
        return result

    pre_analyse = tutor.pre_analyser_sans_ia(
        body.sujet_id,
        body.question_id,
        body.message,
    )

    try:
        system_prompt = tutor.build_system_prompt(
            sujet_id      = body.sujet_id,
            question_id   = body.question_id,
            student_input = body.message,
            pre_analyse   = pre_analyse,
            niveau_sm2    = body.niveau_sm2,
            score_actuel  = body.score_actuel,
            mode_force    = body.mode_force,
        )
    except ValueError as e:
        raise HTTPException(404, f"Contenu introuvable : {e}")

    try:
        response = await openai_client.chat.completions.create(
            model           = cfg.openai_model,
            messages        = [
                {"role": "system", "content": system_prompt},
                {"role": "user",   "content": body.message},
            ],
            temperature     = cfg.ia_temperature,
            max_tokens      = cfg.ia_max_tokens,
            timeout         = 30.0,
        )

        raw_content  = response.choices[0].message.content or ""
        tokens_used  = response.usage.total_tokens

        raw_content = raw_content.strip()
        if raw_content.startswith("```"):
            lines = raw_content.splitlines()
            if len(lines) >= 2 and lines[0].startswith("```") and lines[-1].startswith("```"):
                raw_content = "\n".join(lines[1:-1]).strip()

        ia_result    = json.loads(raw_content)

    except json.JSONDecodeError:
        logger.error(f"Réponse IA non-JSON : {raw_content[:200]}")
        raise HTTPException(500, "Réponse IA malformée")
    except Exception as e:
        logger.error(f"Erreur OpenAI : {e}")
        raise HTTPException(502, f"Service IA temporairement indisponible : {e}")

    result = {
        **ia_result,
        "pre_analyse":     pre_analyse,
        "tokens_utilises": tokens_used,
        "economie_tokens": pre_analyse.get("economie_tokens", 0) if pre_analyse else 0,
        "from_cache":      False,
    }

    await set_cache(cache_key, json.dumps(result, ensure_ascii=False), cfg.cache_ttl)

    logger.info(
        f"Chat : user={current_user['id']} "
        f"sujet={body.sujet_id} q={body.question_id} "
        f"tokens={tokens_used}"
    )

    return result


@router.get("/api/chapitres/{matiere}", tags=["Contenu"])
async def get_chapitres(
    matiere:      str,
    current_user: Dict = Depends(get_current_user),
    tutor:        KhawarizmiTutor = Depends(get_tutor),
):
    if hasattr(tutor, 'programme_canonical') and tutor.programme_canonical:
        programme = tutor.programme_canonical
    else:
        programme = {
            "maths":    tutor.programme_maths,
            "physique": tutor.programme_physique,
            "sciences": tutor.programme_sciences,
        }.get(matiere)

    if not programme:
        raise HTTPException(404, f"Matière '{matiere}' introuvable")

    chapitres = programme.get("chapitres", [])

    return {
        "matiere":    matiere,
        "nb_chapitres": len(chapitres),
        "chapitres":  [
            {
                "id":   ch.get("id"),
                "nom":  ch.get("nom"),
                "nb_micro_concepts": len(ch.get("micro_concepts", [])),
            }
            for ch in chapitres
        ],
    }
