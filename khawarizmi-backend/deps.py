from __future__ import annotations

from typing import Any

from fastapi import Depends, HTTPException, Request, status
from jose import JWTError, jwt
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession

from config import get_settings


def _get_state():
    from main import state

    return state


async def get_db() -> AsyncSession:
    from database import get_db as _get_db

    async for session in _get_db():
        yield session


def get_tutor():
    s = _get_state()
    if not s.tutor:
        raise HTTPException(503, "Moteur pédagogique non initialisé")
    return s.tutor


def get_scheduler():
    s = _get_state()
    if not s.scheduler:
        raise HTTPException(503, "Scheduler FSRS non initialisé")
    return s.scheduler


def get_openai():
    s = _get_state()
    if not s.openai:
        raise HTTPException(503, "Service IA non configuré - clé API manquante")
    return s.openai


def get_dual_coding():
    s = _get_state()
    if not s.dual_coding:
        raise HTTPException(503, "Dual Coding non configuré - clé Vision API manquante")
    return s.dual_coding


async def get_current_user(
    request: Request,
    db: AsyncSession = Depends(get_db),
) -> dict[str, Any]:
    cfg = get_settings()
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Token invalide ou expiré",
        headers={"WWW-Authenticate": "Bearer"},
    )

    token = request.cookies.get("khawarizmi_access_token")
    if not token:
        token = request.headers.get("Authorization", "").replace("Bearer ", "")
    if not token:
        raise credentials_exception

    try:
        payload = jwt.decode(token, cfg.SECRET_KEY, algorithms=[cfg.JWT_ALGORITHM], options={"verify_sub": False})
        user_id: int = int(payload.get("sub"))
        if not user_id:
            raise credentials_exception
    except JWTError:
        raise credentials_exception

    result = await db.execute(
        text("SELECT id, email, prenom, plan, filiere FROM users WHERE id = :id"),
        {"id": user_id},
    )
    user = result.fetchone()
    if not user:
        raise credentials_exception

    return {"id": user[0], "email": user[1], "prenom": user[2], "plan": user[3], "filiere": user[4]}
