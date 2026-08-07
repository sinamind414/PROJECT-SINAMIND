"""seed_preview.py — Peuple la base (preview SQLite ou locale) avec les seeds.

Wrapper : initialise state.db_session (normalement fait au boot du serveur),
puis exécute les seeds lessons / bac-blanc / document-analysis.

Usage:
    SECRET_KEY=... DATABASE_URL=sqlite+aiosqlite:///./preview.db \
    python scripts/seed_preview.py
"""
from __future__ import annotations

import asyncio
import importlib
import os

from sqlalchemy.ext.asyncio import async_sessionmaker, create_async_engine


async def main() -> None:
    db_url = os.environ.get("DATABASE_URL", "sqlite+aiosqlite:///./preview.db")
    if db_url.startswith("postgresql://") or db_url.startswith("postgres://"):
        db_url = db_url.replace("postgresql://", "postgresql+asyncpg://", 1).replace(
            "postgres://", "postgresql+asyncpg://", 1
        )
    engine = create_async_engine(db_url, pool_pre_ping=True)
    session_factory = async_sessionmaker(engine, expire_on_commit=False)

    # Initialiser l'état global (ce que fait le lifespan au boot)
    from app_state import state

    state.db_engine = engine
    state.db_session = session_factory

    for mod_name in ("scripts.seed_lessons", "scripts.seed_bac_blanc",
                     "scripts.seed_document_analysis"):
        try:
            mod = importlib.import_module(mod_name)
            await mod.seed()
            print(f"✅ {mod_name}")
        except Exception as exc:
            print(f"⚠️ {mod_name} échoué: {type(exc).__name__}: {exc}")

    await engine.dispose()


if __name__ == "__main__":
    asyncio.run(main())
