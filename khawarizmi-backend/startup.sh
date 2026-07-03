#!/bin/sh
# Fix: old database has 017_fix_user_id_types but our migration is 017
python3 -c "
import sys, os, asyncio
sys.path.insert(0, '/app')
os.environ['DATABASE_URL'] = os.environ.get('DATABASE_URL', '')
from sqlalchemy import text
from sqlalchemy.ext.asyncio import create_async_engine
async def fix():
    db = os.environ['DATABASE_URL'].replace('postgresql://', 'postgresql+asyncpg://', 1)
    eng = create_async_engine(db)
    async with eng.connect() as c:
        r = await c.execute(text(\"SELECT version_num FROM alembic_version\"))
        row = r.fetchone()
        if row and row[0] == '017_fix_user_id_types':
            await c.execute(text(\"UPDATE alembic_version SET version_num = '017'\"))
            await c.commit()
    await eng.dispose()
asyncio.run(fix())
"
alembic upgrade head
uvicorn main:app --host 0.0.0.0 --port "${PORT:-8000}"
