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
from services.llm import _call_with_fallback
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

    # ─── Calcul du Contexte Temporel & FSRS ──────────────
    from datetime import date

    from sqlalchemy import text as sa_text

    today = date.today()
    year = today.year
    if today.month > 6 or (today.month == 6 and today.day > 10):
        year += 1
    bac_date = date(year, 6, 5)
    days_to_bac = (bac_date - today).days

    if days_to_bac > 90:
        phase_label = "Phase 1 : Apprentissage progressif (Septembre - Mars)"
    elif days_to_bac > 15:
        phase_label = "Phase 2 : Révisions intensives (Avril - Mai)"
    else:
        phase_label = "Phase 3 : Sprint final (J-15 avant le BAC)"

    user_stats = {"mastered": 0, "total": 0, "avg_stability": 0.0}
    try:
        result_stats = await db.execute(
            sa_text("""
                SELECT
                    COUNT(*) as total,
                    COUNT(*) FILTER (WHERE stability > 10.0) as mastered,
                    COALESCE(AVG(stability), 0.0) as avg_stability
                FROM mastery_micro_concepts
                WHERE user_id = :uid
            """),
            {"uid": current_user["id"]},
        )
        row_stats = result_stats.fetchone()
        if row_stats:
            user_stats = {
                "total": row_stats[0],
                "mastered": row_stats[1],
                "avg_stability": round(row_stats[2] or 0.0, 1),
            }
    except Exception as e:
        logger.error(f"Erreur stats chat FSRS: {e}")

    calendar_context = {"days_to_bac": days_to_bac, "phase": phase_label, "user_stats": user_stats}

    try:
        system_prompt = tutor.build_system_prompt(
            sujet_id=body.sujet_id,
            question_id=body.question_id,
            student_input=body.message,
            pre_analyse=pre_analyse,
            niveau_sm2=body.niveau_sm2,
            score_actuel=body.score_actuel,
            mode_force=body.mode_force or "ANNALES_COMPLEXES",
            calendar_context=calendar_context,
        )
    except ValueError as e:
        raise HTTPException(404, f"Contenu introuvable : {e}")
    mc.start("llm")
    fallback_used = False
    try:
        # Fabuleux V4 + Groq : fallback automatique
        response = await _call_with_fallback(
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": body.message},
            ],
            primary_client=openai_client,
            primary_model=cfg.openai_model,
            temperature=cfg.ia_temperature,
            max_tokens=cfg.ia_max_tokens,
            timeout=30.0,
        )
        # _call_with_fallback peut logger un fallback → on le détecte
        # (simple heuristics: si on arrive ici sans exception, on considère primary OK)
        raw_content = response.choices[0].message.content or ""
        try:
            tokens_used = response.usage.total_tokens if response.usage else 0
        except Exception:
            tokens_used = 0

        raw_content = raw_content.strip()
        if raw_content.startswith("```"):
            lines = raw_content.splitlines()
            if len(lines) >= 2 and lines[0].startswith("```") and lines[-1].startswith("```"):
                raw_content = "\n".join(lines[1:-1]).strip()

        ia_result = json.loads(raw_content)

    except json.JSONDecodeError:
        logger.error(f"Réponse IA non-JSON : {raw_content[:200]}")
        raise HTTPException(500, "Réponse IA malformée")
    except Exception as e:
        logger.error(f"Erreur OpenAI : {e}")
        raise HTTPException(502, f"Service IA temporairement indisponible : {e}")
    mc.end("llm")

    mc.set("tokens_total", tokens_used)
    mc.set("tokens_input", response.usage.prompt_tokens if response.usage else 0)
    mc.set("tokens_output", response.usage.completion_tokens if response.usage else 0)

    result = {
        **ia_result,
        "pre_analyse": pre_analyse,
        "tokens_utilises": tokens_used,
        "economie_tokens": pre_analyse.get("economie_tokens", 0) if pre_analyse else 0,
        "from_cache": False,
    }

    mc.start("cache_store")
    await set_cache(cache_key, json.dumps(result, ensure_ascii=False), cfg.cache_ttl)
    mc.end("cache_store")

    record_request("/api/chat", cache_hit=False, fallback=fallback_used)
    mc.flush()

    logger.info(f"Chat : user={current_user['id']} sujet={body.sujet_id} q={body.question_id} tokens={tokens_used}")

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
