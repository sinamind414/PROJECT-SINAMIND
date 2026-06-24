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

        state.openai = AsyncOpenAI(api_key=cfg.OPENAI_API_KEY, base_url=cfg.openai_base_url)
        state.dual_coding = DualCodingService(state.openai)

    if cfg.DATABASE_URL:
        try:
            db_url = cfg.DATABASE_URL.replace("postgresql://", "postgresql+asyncpg://", 1).replace(
                "postgres://", "postgresql+asyncpg://", 1
            )
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
        with suppress(asyncio.CancelledError):
            await state.reconciliation_task
    if state.redis:
        await state.redis.aclose()
    if state.db_engine:
        await state.db_engine.dispose()
