# routes/lifespan.py — AppState, state, lifespan

import asyncio
import logging
import pathlib
from contextlib import asynccontextmanager, suppress
from dataclasses import dataclass
from typing import Any

from fastapi import FastAPI
from redis.asyncio import Redis as AsyncRedis
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

from config import get_settings

logger = logging.getLogger("khawarizmi.api")


@dataclass
class AppState:
    tutor: Any | None = None
    scheduler: Any | None = None
    interleaving: Any | None = None
    dual_coding: Any | None = None
    openai: Any | None = None
    redis: AsyncRedis | None = None
    db_engine: Any | None = None
    db_session: async_sessionmaker[AsyncSession] | None = None
    reconciliation_task: asyncio.Task | None = None
    # Modèle IA réellement résolu (Groq llama / Gemini / gpt-4o-mini) ou None.
    # Health le lit au lieu du défaut statique cfg.AI_MODEL_PRIMARY (souvent faux).
    ai_model: str | None = None


state = AppState()


@asynccontextmanager
async def lifespan(app: FastAPI):
    cfg = get_settings()
    data_dir = cfg.data_dir or str(pathlib.Path(__file__).parent.parent / "data")

    from services.khawarizmi_engine import KhawarizmiTutor

    try:
        state.tutor = KhawarizmiTutor(data_dir=data_dir)
    except Exception as e:
        logger.error(f"❌ KhawarizmiTutor init failed: {e} — tutor disabled")
        state.tutor = None

    try:
        report = state.tutor.loader.get_data_foundation_report()
        logger.warning("═══════════════════════════════════════════════")
        logger.warning("DATA FOUNDATION STATUS (DEEP MIGRATION)")
        logger.warning(f"  Programme source : {report['programme']['source']}")
        logger.warning(f"  Micro-concepts   : {report['programme']['total_micro_concepts']}")
        logger.warning("═══════════════════════════════════════════════")
    except Exception as e:
        logger.error(f"Failed to report data foundation: {e}")

    try:
        from services.scheduler import KhawarizmiScheduler

        state.scheduler = KhawarizmiScheduler()
    except Exception as e:
        logger.error(f"❌ Scheduler init failed: {e} — scheduler disabled")
        state.scheduler = None

    try:
        from services.interleaving import InterleavingSession

        state.interleaving = InterleavingSession()
    except Exception as e:
        logger.error(f"❌ Interleaving init failed: {e} — interleaving disabled")
        state.interleaving = None

    if cfg.OPENAI_API_KEY:
        try:
            from openai import AsyncOpenAI

            from services.dual_coding import DualCodingService

            api_key = cfg.OPENAI_API_KEY
            base_url = cfg.openai_base_url
            model = cfg.openai_model

            # Auto-détection Groq : gsk_* prefix
            if api_key.startswith("gsk_"):
                base_url = "https://api.groq.com/openai/v1"
                if not model or model in ("gpt-4o-mini",) or "gpt" in model:
                    model = "llama-3.3-70b-versatile"
                logger.info(f"IA Provider auto-détecté: Groq ({model})")

            # Auto-détection Gemini : AIza* prefix
            elif api_key.startswith("AIza"):
                base_url = "https://generativelanguage.googleapis.com/v1beta/openai/"
                if not model or "gpt" in model:
                    model = "gemini-2.5-flash"
                logger.info(f"IA Provider auto-détecté: Gemini ({model})")

            state.openai = AsyncOpenAI(api_key=api_key, base_url=base_url)
            state.dual_coding = DualCodingService(state.openai)
            state.ai_model = model  # modèle réellement résolu — health lira ceci
            logger.info(f"IA initialisée: {base_url} | model={model}")
        except Exception as e:
            logger.error(f"❌ IA init failed: {e} — IA désactivée")
    else:
        # Pas de clé IA configurée — on le dit au boot plutôt que d'afficher
        # le défaut statique "gemini-2.5-flash" qui n'est même pas installé.
        state.ai_model = None
        logger.warning("IA désactivée — OPENAI_API_KEY non configuré")

    if cfg.DATABASE_URL:
        try:
            db_url = cfg.DATABASE_URL.replace("postgresql://", "postgresql+asyncpg://", 1).replace(
                "postgres://", "postgresql+asyncpg://", 1
            )
            state.db_engine = create_async_engine(db_url, pool_size=10, max_overflow=20, pool_pre_ping=True)
            state.db_session = async_sessionmaker(state.db_engine, class_=AsyncSession, expire_on_commit=False)

            # Auto-migration : supprimer la FK qui bloque les inserts drill
            async with state.db_engine.begin() as conn:
                from sqlalchemy import text
                await conn.execute(text(
                    "ALTER TABLE mastery_micro_concepts "
                    "DROP CONSTRAINT IF EXISTS mastery_micro_concepts_micro_concept_id_fkey"
                ))
                # Normaliser concept_id : fallback sur micro_concept_id si vide
                await conn.execute(text(
                    "UPDATE mastery_micro_concepts "
                    "SET concept_id = micro_concept_id "
                    "WHERE concept_id IS NULL OR concept_id = ''"
                ))
            logger.info("Migration 013+014: FK dropped + concept_id normalized")
        except Exception as e:
            logger.error(f"PostgreSQL init error: {e}")

    if cfg.REDIS_URL:
        try:
            state.redis = await AsyncRedis.from_url(cfg.REDIS_URL, encoding="utf-8", decode_responses=True)
            await state.redis.ping()
        except Exception as e:
            logger.warning(f"Redis indisponible: {e}")

    try:
        from services.reconciliation_queue import process_review_queue

        state.reconciliation_task = asyncio.create_task(process_review_queue())
        logger.info("✅ Reconciliation task started")
    except Exception as e:
        logger.error(f"❌ Reconciliation task init failed: {e}")

    try:
        from services.eval_calibration import get_calibration_stats
        cal_stats = get_calibration_stats()
        if cal_stats["total_questions"] == 0:
            logger.error(
                "GOLDEN_SET_ABSENT | "
                "Évaluations sans calibration ONEC. "
                "Vérifier data/golden_set_onec.json"
            )
        else:
            logger.info(
                f"GOLDEN_SET_OK | "
                f"{cal_stats['total_questions']} exemples chargés | "
                f"chapitres={list(cal_stats['by_chapter'].keys())}"
            )
    except Exception as e:
        logger.warning(f"GOLDEN_SET_CHECK_FAILED | {e}")

    logger.info(f"Khawarizmi API prete [{cfg.ENVIRONMENT}]")
    yield

    if state.reconciliation_task:
        state.reconciliation_task.cancel()
        try:
            await state.reconciliation_task
        except asyncio.CancelledError:
            pass
    if state.redis:
        await state.redis.aclose()
    if state.db_engine:
        await state.db_engine.dispose()
