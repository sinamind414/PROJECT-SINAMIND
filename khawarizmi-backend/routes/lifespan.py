# routes/lifespan.py — AppState, state, lifespan

import asyncio
import logging
import pathlib
from contextlib import asynccontextmanager
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


state = AppState()


@asynccontextmanager
async def lifespan(app: FastAPI):
    cfg = get_settings()
    data_dir = cfg.data_dir or str(pathlib.Path(__file__).parent.parent / "data")

    from services.khawarizmi_engine import KhawarizmiTutor
    state.tutor = KhawarizmiTutor(data_dir=data_dir)

    try:
        report = state.tutor.loader.get_data_foundation_report()
        logger.warning("═══════════════════════════════════════════════")
        logger.warning("DATA FOUNDATION STATUS (DEEP MIGRATION)")
        logger.warning(f"  Programme source : {report['programme']['source']}")
        logger.warning(f"  Micro-concepts   : {report['programme']['total_micro_concepts']}")
        logger.warning("═══════════════════════════════════════════════")
    except Exception as e:
        logger.error(f"Failed to report data foundation: {e}")

    from services.scheduler import KhawarizmiScheduler
    state.scheduler = KhawarizmiScheduler()

    from services.interleaving import InterleavingSession
    state.interleaving = InterleavingSession()

    if cfg.OPENAI_API_KEY:
        from openai import AsyncOpenAI
        from services.dual_coding import DualCodingService
        # Auto-détection provider depuis la clé (fabuleux V4)
        api_key = cfg.OPENAI_API_KEY
        base_url = cfg.openai_base_url
        model = cfg.openai_model
        # Groq : gsk_*
        if api_key.startswith("gsk_"):
            base_url = "https://api.groq.com/openai/v1"
            if model in ("gpt-4o-mini", "", None) or "gpt" in model:
                model = "llama-3.3-70b-versatile"
            logger.info(f"IA Provider auto-détecté: Groq ({model})")
        # Gemini via OpenAI-compat
        elif api_key.startswith("AIza"):
            base_url = "https://generativelanguage.googleapis.com/v1beta/openai/"
            if "gemini" not in model:
                model = "gemini-2.5-flash"
            logger.info(f"IA Provider auto-détecté: Gemini ({model})")
        # Z.AI
        elif len(api_key) > 20 and "z.ai" in base_url or "zai" in api_key.lower()[:10]:
            base_url = cfg.zai_base_url or "https://api.z.ai/api/paas/v4/"
            logger.info(f"IA Provider auto-détecté: Z.AI")
        state.openai = AsyncOpenAI(api_key=api_key, base_url=base_url)
        # patch config en mémoire pour que chat.py utilise le bon modèle
        try:
            cfg.openai_model = model
            cfg.openai_base_url = base_url
        except Exception:
            pass
        state.dual_coding = DualCodingService(state.openai)
        logger.info(f"IA initialisée: {base_url} | model={model}")

    if cfg.DATABASE_URL:
        try:
            db_url = cfg.DATABASE_URL.replace("postgresql://", "postgresql+asyncpg://", 1).replace("postgres://", "postgresql+asyncpg://", 1)
            state.db_engine = create_async_engine(db_url, pool_size=10, max_overflow=20, pool_pre_ping=True)
            state.db_session = async_sessionmaker(state.db_engine, class_=AsyncSession, expire_on_commit=False)
        except Exception as e:
            logger.error(f"PostgreSQL init error: {e}")

    if cfg.REDIS_URL:
        try:
            state.redis = await AsyncRedis.from_url(cfg.REDIS_URL, encoding="utf-8", decode_responses=True)
            await state.redis.ping()
        except Exception as e:
            logger.warning(f"Redis indisponible: {e}")

    from services.reconciliation_queue import process_review_queue
    state.reconciliation_task = asyncio.create_task(process_review_queue())

    logger.info(f"Khawarizmi API prete [{cfg.ENVIRONMENT}]")
    yield

    if state.reconciliation_task:
        state.reconciliation_task.cancel()
        try: await state.reconciliation_task
        except asyncio.CancelledError: pass
    if state.redis: await state.redis.aclose()
    if state.db_engine: await state.db_engine.dispose()
