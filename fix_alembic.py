"""Fix alembic_version: replace 017_fix_user_id_types with 017."""
import asyncio
import os
from sqlalchemy import text
from sqlalchemy.ext.asyncio import create_async_engine

DB_URL = os.environ.get("DATABASE_URL", "")
if not DB_URL:
    print("NO DATABASE_URL")
    exit(1)
DB_URL = DB_URL.replace("postgresql://", "postgresql+asyncpg://", 1)


async def fix():
    engine = create_async_engine(DB_URL)
    async with engine.connect() as conn:
        r = await conn.execute(text("SELECT version_num FROM alembic_version"))
        row = r.fetchone()
        print(f"Current alembic version: {row[0] if row else 'NONE'}")
        if row and row[0] == "017_fix_user_id_types":
            await conn.execute(text("UPDATE alembic_version SET version_num = '017'"))
            await conn.commit()
            print("Fixed: 017_fix_user_id_types -> 017")
        else:
            print("No fix needed")
    await engine.dispose()


asyncio.run(fix())
