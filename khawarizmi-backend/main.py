# main.py — Khawarizmi Pro Entrypoint
import os

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from slowapi.errors import RateLimitExceeded
from slowapi.middleware import SlowAPIMiddleware

from config import get_allowed_origins, get_settings
from monitoring import setup_monitoring
from rate_limit import limiter
from routes import ALL_ROUTERS
from routes.admin_ingest import router as admin_router
from routes.errors import (
    generic_exception_handler,
    http_exception_handler,
    rate_limit_exceeded_handler,
    validation_exception_handler,
)
from routes.lifespan import lifespan, state  # ruff: ignore[unused-import] — re-exported for deps.py
from routes.openapi_config import openapi_metadata

setup_monitoring()

_is_prod = os.getenv("ENVIRONMENT") == "production"
app = FastAPI(
    **openapi_metadata,
    lifespan=lifespan,
    docs_url=None if _is_prod else "/docs",
    redoc_url=None if _is_prod else "/redoc",
    openapi_url=None if _is_prod else "/openapi.json",
)

app.state.limiter = limiter
# S38 — le handler est branché sur la CLASSE RateLimitExceeded (les routes décorées),
# plus sur le statut 429. Enregistré sur 429, il interceptait aussi tout
# HTTPException(429) manuel — or il lit request.state.view_rate_limit, que seul le
# décorateur/middleware de limitation pose → AttributeError → 500 pour l'élève.
app.add_exception_handler(RateLimitExceeded, rate_limit_exceeded_handler)
app.add_exception_handler(422, validation_exception_handler)
app.add_middleware(SlowAPIMiddleware)
app.add_middleware(
    CORSMiddleware,
    allow_origins=get_allowed_origins(),
    # NOTE: allow_origin_regex removed — all allowed origins are in get_allowed_origins()
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS", "PATCH"],
    allow_headers=[
        "Accept",
        "Accept-Language",
        "Authorization",
        "Content-Type",
        "X-Requested-With",
    ],
)

app.include_router(admin_router)
for router in ALL_ROUTERS:
    app.include_router(router)

for code in (400, 401, 403, 404):
    app.add_exception_handler(code, http_exception_handler)
app.add_exception_handler(500, generic_exception_handler)

if __name__ == "__main__":
    import uvicorn

    cfg = get_settings()
    uvicorn.run("main:app", host="0.0.0.0", port=int(os.environ.get("PORT", 8000)), log_level="info")
