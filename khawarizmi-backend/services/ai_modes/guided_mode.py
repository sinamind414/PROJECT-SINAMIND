import json
import logging

from openai import AsyncOpenAI
from sqlalchemy.ext.asyncio import AsyncSession

from cache import get_cache, set_cache, make_cache_key
from config import get_settings
from services.calendar_context import get_calendar_context, get_user_stats
from services.khawarizmi_engine import KhawarizmiTutor
from services.metrics import MetricsCollector, record_request

logger = logging.getLogger("khawarizmi.guided_mode")


async def handle_guided_chat(
    body,
    user: dict,
    db: AsyncSession,
    openai_client: AsyncOpenAI,
    cfg,
    tutor: KhawarizmiTutor,
) -> dict:
    mc = MetricsCollector(user_id=str(user["id"]), endpoint="/api/ai/chat[guided]")

    mc.start("cache_lookup")
    cache_key = make_cache_key("guided", body.sujet_id, body.question_id, body.message, body.mode_force or "auto")
    cached = await get_cache(cache_key)
    mc.end("cache_lookup")

    if cached:
        result = json.loads(cached)
        result["from_cache"] = True
        record_request("/api/ai/chat", cache_hit=True, fallback=False)
        mc.flush()
        return result

    mc.start("pre_analyse")
    pre_analyse = tutor.pre_analyser_sans_ia(body.sujet_id, body.question_id, body.message)
    mc.end("pre_analyse")

    calendar_context = await get_calendar_context(db, user["id"])

    mc.start("llm")
    try:
        ia_result = await tutor.interroger_ia(
            sujet_id=body.sujet_id,
            question_id=body.question_id,
            student_input=body.message,
            openai_client=openai_client,
            cfg=cfg,
            pre_analyse=pre_analyse,
            niveau_sm2=body.niveau_sm2 or 0,
            score_actuel=body.score_actuel or 0.0,
            mode_force=body.mode_force,
            calendar_context=calendar_context,
        )
    except ValueError as e:
        from fastapi import HTTPException
        raise HTTPException(404, f"Contenu introuvable : {e}")
    except Exception as e:
        from fastapi import HTTPException
        logger.error(f"Erreur guided_mode : {e}")
        raise HTTPException(502, f"Service IA indisponible : {e}")
    mc.end("llm")

    result = {
        **ia_result,
        "mode": "guided",
        "pre_analyse": pre_analyse,
        "from_cache": False,
        "fallback_active": False,
    }

    await set_cache(cache_key, json.dumps(result, ensure_ascii=False), cfg.cache_ttl)

    record_request("/api/ai/chat", cache_hit=False, fallback=False)
    mc.flush()

    logger.info(f"guided | user={user['id']} sujet={body.sujet_id} q={body.question_id} tokens={ia_result.get('tokens_utilises', 0)}")

    return result
