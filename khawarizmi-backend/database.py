from contextlib import asynccontextmanager

from fastapi import HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import declarative_base

Base = declarative_base()


def _get_state():
    from main import state

    return state


async def get_db() -> AsyncSession:
    s = _get_state()
    if not s.db_session:
        raise HTTPException(503, "Base de données indisponible")
    async with s.db_session() as session:
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise


@asynccontextmanager
async def get_db_context():
    s = _get_state()
    if not s.db_session:
        raise RuntimeError("Base de données indisponible")
    async with s.db_session() as session:
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise
