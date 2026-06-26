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
from routes.lifespan import lifespan, state  # noqa: F401 — re-exported for deps.py
from routes.openapi_config import openapi_metadata

setup_monitoring()

app = FastAPI(
    **openapi_metadata,
    lifespan=lifespan,
    docs_url="/docs" if os.getenv("ENVIRONMENT") != "production" else None,
    redoc_url="/redoc",
)

app.state.limiter = limiter
app.add_exception_handler(429, _rate_limit_exceeded_handler)
app.add_exception_handler(422, validation_exception_handler)
app.add_middleware(SlowAPIMiddleware)
app.add_middleware(
    CORSMiddleware,
    allow_origins=get_allowed_origins(),
    allow_origin_regex=r"https://.*\.(vercel|netlify)\.app",
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS", "PATCH"],
    allow_headers=["*"],
)

from routes import (
    annales,
    auth,
    avatar,
    # === Methodology Intelligence (Semaines 1-8) ===
    bac_blanc_intelligent,
    badges,
    chat,
    chatbot,
    cours,
    diagnostic,
    dual_coding,
    evaluate,
    exercices,
    flashcards,
    gamification,
    health,
    lexique,
    methodology,
    methodology_flashcards,
    mindmap,
    mindmap_methodology,
    mystery_box,
    payment,
    phase1,
    phase2,
    phase3,
    phase4,
    phase5,
    phase6,
    programme,
    progress,
    session,
    tuteur,
    tutor,
    videos,
)

routers = [
    health.router,
    auth.router,
    chat.router,
    chatbot.router,
    cours.router,
    exercices.router,
    flashcards.router,
    mindmap.router,
    evaluate.router,
    session.router,
    payment.router,
    programme.router,
    progress.router,
    lexique.router,
    tuteur.router,
    videos.router,
    annales.router,
    dual_coding.router,
    # === Gamification (Phase 0) ===
    gamification.router,
    mystery_box.router,
    avatar.router,
    # === Phase 1 — One More Click Loop ===
    phase1.router,
    # === Phase 2 — Mystery Box + Social + Badges ===
    phase2.router,
    badges.router,
    # === Phase 3 — Avatar Avancé + Live Stats ===
    phase3.router,
    # === Phase 4 — Méthodologie + Gamification ===
    phase4.router,
    # === Phase 5 — Social + Live Classroom ===
    phase5.router,
    # === Phase 6 — Analytics & Optimisation ===
    phase6.router,
    # === Methodology Intelligence Routers (Semaines 1-8) ===
    bac_blanc_intelligent.router,
    diagnostic.router,
    methodology.router,
    methodology_flashcards.router,
    mindmap_methodology.router,
    tutor.router,
]

for router in routers:
    app.include_router(router)

for code in (400, 401, 403, 404):
    app.add_exception_handler(code, http_exception_handler)
app.add_exception_handler(500, generic_exception_handler)

if __name__ == "__main__":
    import uvicorn

    cfg = get_settings()
    uvicorn.run("main:app", host="0.0.0.0", port=int(os.environ.get("PORT", 8000)), log_level="info")
