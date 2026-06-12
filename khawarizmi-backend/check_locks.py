import os
import asyncio
from sqlalchemy import text
from sqlalchemy.ext.asyncio import create_async_engine

async def check_activity():
    db_url = os.getenv("DATABASE_URL")
    if not db_url:
        db_url = "postgresql+asyncpg://postgres:OxDIJWQlRMyyYdyKfElFdfJPXvsJNyRO@postgres.railway.internal:5432/railway"
    else:
        if db_url.startswith("postgres://"):
            db_url = db_url.replace("postgres://", "postgresql+asyncpg://", 1)
        elif db_url.startswith("postgresql://"):
            db_url = db_url.replace("postgresql://", "postgresql+asyncpg://", 1)
            
    print("Connecting to database to check activity...")
    engine = create_async_engine(db_url, echo=False)
    async with engine.connect() as conn:
        print("\n--- ACTIVE QUERIES ---")
        res = await conn.execute(text("""
            SELECT pid, query, state, wait_event_type, wait_event, query_start 
            FROM pg_stat_activity 
            WHERE state != 'idle' AND pid != pg_backend_pid();
        """))
        for r in res:
            print(dict(r._mapping))
            
        print("\n--- LOCKS WAITING ---")
        res_locks = await conn.execute(text("""
            SELECT 
                blocked_locks.pid     AS blocked_pid,
                blocked_activity.query    AS blocked_statement,
                blocking_locks.pid    AS blocking_pid,
                blocking_activity.query   AS blocking_statement
            FROM  pg_catalog.pg_locks         blocked_locks
            JOIN pg_catalog.pg_stat_activity blocked_activity ON blocked_activity.pid = blocked_locks.pid
            JOIN pg_catalog.pg_locks         blocking_locks 
                ON blocking_locks.locktype = blocked_locks.locktype
                AND blocking_locks.database IS NOT DISTINCT FROM blocked_locks.database
                AND blocking_locks.relation IS NOT DISTINCT FROM blocked_locks.relation
                AND blocking_locks.page IS NOT DISTINCT FROM blocked_locks.page
                AND blocking_locks.tuple IS NOT DISTINCT FROM blocked_locks.tuple
                AND blocking_locks.virtualxid IS NOT DISTINCT FROM blocked_locks.virtualxid
                AND blocking_locks.transactionid IS NOT DISTINCT FROM blocked_locks.transactionid
                AND blocking_locks.classid IS NOT DISTINCT FROM blocked_locks.classid
                AND blocking_locks.objid IS NOT DISTINCT FROM blocked_locks.objid
                AND blocking_locks.objsubid IS NOT DISTINCT FROM blocked_locks.objsubid
                AND blocking_locks.pid != blocked_locks.pid
            JOIN pg_catalog.pg_stat_activity blocking_activity ON blocking_activity.pid = blocking_locks.pid
            WHERE NOT blocked_locks.granted;
        """))
        for r in res_locks:
            print(dict(r._mapping))
            
    await engine.dispose()
    print("Done.")

if __name__ == "__main__":
    asyncio.run(check_activity())
