# routes/errors.py — Gestionnaire d'erreurs uniforme

import logging
import time

from fastapi import Request
from fastapi.responses import JSONResponse
from pydantic import BaseModel

from rate_limit import QUOTA_MESSAGE_AR

logger = logging.getLogger("khawarizmi.api")


class ErrorResponse(BaseModel):
    erreur: str
    status: int
    path: str
    method: str
    details: dict | None = None


async def http_exception_handler(request: Request, exc) -> JSONResponse:
    return JSONResponse(
        status_code=exc.status_code,
        content=ErrorResponse(
            erreur=exc.detail,
            status=exc.status_code,
            path=request.url.path,
            method=request.method,
        ).model_dump(),
    )


async def generic_exception_handler(request: Request, exc: Exception) -> JSONResponse:
    logger.error(f"Erreur non gérée : {exc}", exc_info=True)
    return JSONResponse(
        status_code=500,
        content=ErrorResponse(
            erreur="Erreur serveur interne",
            status=500,
            path=request.url.path,
            method=request.method,
        ).model_dump(),
    )


async def rate_limit_exceeded_handler(request: Request, exc) -> JSONResponse:
    """S38 (audit surfaces 2026-08-30) — 429 uniforme pour l'élève.

    Remplace le handler slowapi `_rate_limit_exceeded_handler`, qui lit
    `request.state.view_rate_limit` SANS garde : levé pour le statut 429 (et donc
    pour tout HTTPException(429) manuel), il plantait en
    `AttributeError: 'State' object has no attribute 'view_rate_limit'` → 500
    dès que l'auto-check du middleware ne passait pas par là (limiter désactivé,
    middleware court-circuité). Ici : état optionnel, corps conforme au contrat
    `erreur`/`status`, message arabe élève, `Retry-After` quand il est calculable.
    """
    retry_after: int | None = None
    state_limit = getattr(request.state, "view_rate_limit", None)
    if state_limit:
        try:
            limiter_obj = request.app.state.limiter.limiter
            reset_in, _remaining = limiter_obj.get_window_stats(state_limit[0], *state_limit[1])
            retry_after = max(1, int(reset_in - time.time()))
        except Exception:
            retry_after = None
    content = {
        "erreur": QUOTA_MESSAGE_AR,
        "code": "quota_exceeded",
        "status": 429,
        "path": request.url.path,
        "method": request.method,
        "banner_ar": QUOTA_MESSAGE_AR,
    }
    if retry_after is not None:
        content["retry_after_s"] = retry_after
    headers = {"Retry-After": str(retry_after)} if retry_after is not None else {}
    return JSONResponse(status_code=429, content=content, headers=headers)


async def validation_exception_handler(request: Request, exc) -> JSONResponse:
    return JSONResponse(
        status_code=422,
        content=ErrorResponse(
            erreur="Erreur de validation",
            status=422,
            path=request.url.path,
            method=request.method,
            details=exc.errors() if hasattr(exc, "errors") else None,
        ).model_dump(),
    )
