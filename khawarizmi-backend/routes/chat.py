import json
import logging

from fastapi import APIRouter, Depends, HTTPException, Request
from openai import AsyncOpenAI
from sqlalchemy.ext.asyncio import AsyncSession

from cache import get_cache, make_cache_key, set_cache
from config import get_settings
from deps import get_current_user, get_db, get_openai, get_tutor
from rate_limit import chat_limit, limiter
from schemas.session import ChatRequest
from services.khawarizmi_engine import KhawarizmiTutor
from services.metrics import MetricsCollector, record_request

logger = logging.getLogger("khawarizmi.api")
router = APIRouter()


@router.post("/api/chat", tags=["IA"])
@limiter.limit(chat_limit)
async def chat_socratique(
    request: Request,
    body: ChatRequest,
    current_user: dict = Depends(get_current_user),
    tutor: KhawarizmiTutor = Depends(get_tutor),
    openai_client: AsyncOpenAI = Depends(get_openai),
    db: AsyncSession = Depends(get_db),
):
    cfg = get_settings()
    mc = MetricsCollector(user_id=str(current_user["id"]), endpoint="/api/chat")

    mc.start("cache_lookup")
    cache_key = make_cache_key("chat", body.sujet_id, body.question_id, body.message, body.mode_force or "auto")
    cached = await get_cache(cache_key)
    mc.end("cache_lookup")
    mc.set("cache_hit", cached is not None)

    if cached:
        logger.debug(f"Cache HIT : {cache_key[:20]}...")
        result = json.loads(cached)
        result["from_cache"] = True
        record_request("/api/chat", cache_hit=True, fallback=False)
        mc.flush()
        return result

    mc.start("pre_analyse")
    pre_analyse = tutor.pre_analyser_sans_ia(
        body.sujet_id,
        body.question_id,
        body.message,
    )
    mc.end("pre_analyse")

    from services.calendar_context import get_calendar_context

    calendar_context = await get_calendar_context(db, current_user["id"])

    mc.start("llm")
    try:
        ia_result = await tutor.interroger_ia(
            sujet_id=body.sujet_id,
            question_id=body.question_id,
            student_input=body.message,
            openai_client=openai_client,
            cfg=cfg,
            pre_analyse=pre_analyse,
            niveau_sm2=body.niveau_sm2,
            score_actuel=body.score_actuel,
            mode_force=body.mode_force,
            calendar_context=calendar_context,
        )
    except ValueError as e:
        raise HTTPException(404, f"Contenu introuvable : {e}")
    except Exception as e:
        logger.error(f"Erreur IA : {e}")
        raise HTTPException(502, f"Service IA temporairement indisponible : {e}")
    mc.end("llm")

    result = {
        **ia_result,
        "pre_analyse": pre_analyse,
        "economie_tokens": pre_analyse.get("economie_tokens", 0) if pre_analyse else 0,
        "from_cache": False,
    }

    mc.start("cache_store")
    await set_cache(cache_key, json.dumps(result, ensure_ascii=False), cfg.cache_ttl)
    mc.end("cache_store")

    record_request("/api/chat", cache_hit=False, fallback=False)
    mc.flush()

    logger.info(f"Chat : user={current_user['id']} sujet={body.sujet_id} q={body.question_id} tokens={ia_result.get('tokens_utilises', 0)}")

    return result


@router.get("/api/chapitres/{matiere}", tags=["Contenu"])
async def get_chapitres(
    matiere: str,
    current_user: dict = Depends(get_current_user),
    tutor: KhawarizmiTutor = Depends(get_tutor),
):
    if hasattr(tutor, "programme_canonical") and tutor.programme_canonical:
        programme = tutor.programme_canonical
    else:
        programme = {
            "maths": tutor.programme_maths,
            "physique": tutor.programme_physique,
            "sciences": tutor.programme_sciences,
        }.get(matiere)

    if not programme:
        raise HTTPException(404, f"Matière '{matiere}' introuvable")

    chapitres = programme.get("chapitres", [])

    return {
        "matiere": matiere,
        "nb_chapitres": len(chapitres),
        "chapitres": [
            {
                "id": ch.get("id"),
                "nom": ch.get("nom"),
                "nb_micro_concepts": len(ch.get("micro_concepts", [])),
            }
            for ch in chapitres
        ],
    }
