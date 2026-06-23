# main.py — Khawarizmi Pro v2.0.0 (max 100 lignes)
import os, asyncio, logging, pathlib
from contextlib import asynccontextmanager
from dataclasses import dataclass
from fastapi import FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from slowapi import _rate_limit_exceeded_handler
from slowapi.middleware import SlowAPIMiddleware
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, async_sessionmaker
from sqlalchemy import text
from redis.asyncio import Redis as AsyncRedis
from config import get_settings, get_allowed_origins
from monitoring import setup_monitoring
from rate_limit import limiter

setup_monitoring()
logger = logging.getLogger("khawarizmi.api")


@dataclass
class AppState:
    tutor: object = None; scheduler: object = None; interleaving: object = None
    dual_coding: object = None; openai: object = None
    redis: AsyncRedis | None = None; db_engine: object = None
    db_session: object = None; reconciliation_task: asyncio.Task | None = None

state = AppState()


@asynccontextmanager
async def lifespan(app: FastAPI):
    cfg = get_settings()
    data_dir = cfg.data_dir or str(pathlib.Path(__file__).parent / "data")
    from services.khawarizmi_engine import KhawarizmiTutor
    state.tutor = KhawarizmiTutor(data_dir=data_dir)
    # === DEEP DATA FOUNDATION REPORT ===
    try:
        report = state.tutor.loader.get_data_foundation_report()
        logger.warning(f"DATA FOUNDATION | {report['programme']['source']} | {report['programme']['total_micro_concepts']} micro-concepts")
    except Exception as e:
        logger.error(f"Data foundation report: {e}")
    from services.scheduler import KhawarizmiScheduler
    state.scheduler = KhawarizmiScheduler()
    from services.interleaving import InterleavingSession
    state.interleaving = InterleavingSession()
    if cfg.OPENAI_API_KEY:
        from openai import AsyncOpenAI
        state.openai = AsyncOpenAI(api_key=cfg.OPENAI_API_KEY, base_url=cfg.openai_base_url)
    from services.dual_coding import DualCodingService
    state.dual_coding = DualCodingService(state.openai)
    if cfg.DATABASE_URL:
        try:
            db_url = cfg.DATABASE_URL.replace("postgresql://", "postgresql+asyncpg://", 1).replace("postgres://", "postgresql+asyncpg://", 1)
            state.db_engine = create_async_engine(db_url, pool_size=10, max_overflow=20, pool_pre_ping=True)
            state.db_session = async_sessionmaker(state.db_engine, class_=AsyncSession, expire_on_commit=False)
        except Exception as e:
            logger.error(f"PostgreSQL : {e}")
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
    state.redis and await state.redis.aclose()
    state.db_engine and await state.db_engine.dispose()


app = FastAPI(title="Khawarizmi API", version="2.0.0", lifespan=lifespan,
              docs_url="/docs" if get_settings().ENVIRONMENT != "production" else None)
app.add_middleware(CORSMiddleware, allow_origins=get_allowed_origins(),
                   allow_origin_regex=r"https://.*\.vercel\.app",
                   allow_credentials=True, allow_methods=["*"], allow_headers=["*"])
app.state.limiter = limiter
app.add_exception_handler(429, _rate_limit_exceeded_handler)
app.add_middleware(SlowAPIMiddleware)

from routes import health, auth, chat, cours, exercices, flashcards, sessions, mindmap, evaluate, session, payment, programme, lexique, videos, annales, action_verbs, document_analysis, orientation, tuteur, lessons, bac_blanc, dual_coding
for r in [health,auth,chat,cours,exercices,flashcards,sessions,mindmap,evaluate,session,payment,programme,lexique,videos,annales,action_verbs,document_analysis,orientation,tuteur,lessons,bac_blanc,dual_coding]:
    app.include_router(r.router)


@app.exception_handler(HTTPException)
async def http_exception_handler(request: Request, exc: HTTPException):
    return JSONResponse(status_code=exc.status_code, content={"erreur": exc.detail})
@app.exception_handler(Exception)
async def generic_exception_handler(request: Request, exc: Exception):
    logger.error(f"Erreur non gérée : {exc}", exc_info=True)
    return JSONResponse(status_code=500, content={"erreur": "Erreur serveur interne"})
if __name__ == "__main__":
    import uvicorn; uvicorn.run("main:app", host="0.0.0.0", port=int(os.environ.get("PORT", 8000)), log_level="info")
