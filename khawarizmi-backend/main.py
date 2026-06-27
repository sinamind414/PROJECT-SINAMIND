# main.py — Khawarizmi Pro Entrypoint
import os

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from slowapi import _rate_limit_exceeded_handler
from slowapi.middleware import SlowAPIMiddleware

from config import get_allowed_origins, get_settings
from monitoring import setup_monitoring
from rate_limit import limiter
from routes import ALL_ROUTERS
from routes.errors import generic_exception_handler, http_exception_handler, validation_exception_handler
from routes.lifespan import lifespan, state  # noqa: F401 — re-exported for deps.py
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

for router in ALL_ROUTERS:
    app.include_router(router)

for code in (400, 401, 403, 404):
    app.add_exception_handler(code, http_exception_handler)
app.add_exception_handler(500, generic_exception_handler)

if __name__ == "__main__":
    import uvicorn

    cfg = get_settings()
    uvicorn.run("main:app", host="0.0.0.0", port=int(os.environ.get("PORT", 8000)), log_level="info")
