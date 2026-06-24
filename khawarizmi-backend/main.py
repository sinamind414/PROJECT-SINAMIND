# main.py — Khawarizmi Pro Entrypoint
import os

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from slowapi import _rate_limit_exceeded_handler
from slowapi.middleware import SlowAPIMiddleware

from config import get_allowed_origins, get_settings
from monitoring import setup_monitoring
from rate_limit import limiter
from routes.errors import generic_exception_handler, http_exception_handler, validation_exception_handler
from routes.lifespan import lifespan, state
from routes.openapi_config import openapi_metadata

setup_monitoring()

app = FastAPI(**openapi_metadata, lifespan=lifespan,
    docs_url="/docs" if os.getenv("ENVIRONMENT") != "production" else None, redoc_url="/redoc")

app.add_middleware(CORSMiddleware, allow_origins=get_allowed_origins(),
    allow_origin_regex=r"https://.*\.vercel\.app", allow_credentials=True,
    allow_methods=["*"], allow_headers=["*"])
app.state.limiter = limiter
app.add_exception_handler(429, _rate_limit_exceeded_handler)
app.add_exception_handler(422, validation_exception_handler)
app.add_middleware(SlowAPIMiddleware)

from routes import (
    annales, auth, chat, chatbot, cours, dual_coding, evaluate,
    exercices, flashcards, health, lexique, mindmap, payment,
    programme, progress, session, videos,
)

routers = [health.router, auth.router, chat.router, chatbot.router,
    cours.router, exercices.router, flashcards.router, mindmap.router,
    evaluate.router, session.router, payment.router, programme.router,
    progress.router, lexique.router, videos.router, annales.router,
    dual_coding.router]

for router in routers:
    app.include_router(router)

for code in (400, 401, 403, 404):
    app.add_exception_handler(code, http_exception_handler)
app.add_exception_handler(500, generic_exception_handler)

if __name__ == "__main__":
    import uvicorn
    cfg = get_settings()
    uvicorn.run("main:app", host="0.0.0.0", port=int(os.environ.get("PORT", 8000)), log_level="info")
