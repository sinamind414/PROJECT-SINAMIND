# routes/errors.py — Gestionnaire d'erreurs uniforme

import logging
from fastapi import Request
from fastapi.responses import JSONResponse
from pydantic import BaseModel

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
