# main.py — Khawarizmi Pro Entrypoint
import asyncio
import logging
import os
import pathlib
from contextlib import asynccontextmanager
from dataclasses import dataclass
from typing import Any

from fastapi import FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from redis.asyncio import Redis as AsyncRedis
from slowapi import _rate_limit_exceeded_handler
from slowapi.middleware import SlowAPIMiddleware
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

from config import get_allowed_origins, get_settings
from monitoring import setup_monitoring
from rate_limit import limiter

setup_monitoring()
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
    data_dir = cfg.data_dir or str(pathlib.Path(__file__).parent / "data")
    
    from services.khawarizmi_engine import KhawarizmiTutor
    state.tutor = KhawarizmiTutor(data_dir=data_dir)
    
    try:
        loader = state.tutor.loader
        report = loader.get_data_foundation_report()
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
            db_url = cfg.DATABASE_URL.replace("postgresql://", "postgresql+asyncpg://", 1).replace("postgres://", "postgresql+asyncpg://", 1)
            state.db_engine = create_async_engine(db_url, pool_size=10, max_overflow=20, pool_pre_ping=True)
            state.db_session = async_sessionmaker(state.db_engine, class_=AsyncSession, expire_on_commit=False)
        except Exception as e:
            logger.error(f"PostgreSQL init error : {e}")

    if cfg.REDIS_URL:
        try:
            state.redis = await AsyncRedis.from_url(cfg.REDIS_URL, encoding="utf-8", decode_responses=True)
            await state.redis.ping()
        except Exception as e:
            logger.warning(f"Redis indisponible : {e}")

    from services.reconciliation_queue import process_review_queue
    state.reconciliation_task = asyncio.create_task(process_review_queue())
    
    logger.info(f"Khawarizmi API prête [{cfg.ENVIRONMENT}]")
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


app = FastAPI(
    title="Khawarizmi API",
    version="2.0.0",
    lifespan=lifespan,
    docs_url="/docs" if os.getenv("ENVIRONMENT") != "production" else None
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=get_allowed_origins(),
    allow_origin_regex=r"https://.*\.vercel\.app",
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"]
)
app.state.limiter = limiter
app.add_exception_handler(429, _rate_limit_exceeded_handler)
app.add_middleware(SlowAPIMiddleware)

from routes import (
    annales,
    auth,
    chat,
    cours,
    dual_coding,
    evaluate,
    exercices,
    flashcards,
    health,
    lexique,
    mindmap,
    payment,
    programme,
    session,
    videos,
)

routers = [
    health.router,
    auth.router,
    chat.router,
    cours.router,
    exercices.router,
    flashcards.router,
    mindmap.router,
    evaluate.router,
    session.router,
    payment.router,
    programme.router,
    lexique.router,
    videos.router,
    annales.router,
    dual_coding.router,
]

for router in routers:
    app.include_router(router)


@app.exception_handler(HTTPException)
async def http_exception_handler(request: Request, exc: HTTPException):
    return JSONResponse(status_code=exc.status_code, content={"erreur": exc.detail})


@app.exception_handler(Exception)
async def generic_exception_handler(request: Request, exc: Exception):
    logger.error(f"Erreur non gérée : {exc}", exc_info=True)
    return JSONResponse(status_code=500, content={"erreur": "Erreur serveur interne"})


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=int(os.environ.get("PORT", 8000)), log_level="info")
