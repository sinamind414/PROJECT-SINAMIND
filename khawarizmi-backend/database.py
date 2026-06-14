from fastapi import HTTPException
from sqlalchemy.orm import declarative_base
from sqlalchemy.ext.asyncio import AsyncSession

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
