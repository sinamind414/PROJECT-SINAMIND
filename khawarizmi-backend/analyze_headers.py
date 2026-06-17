import asyncio
from pathlib import Path
from config import get_settings
from sqlalchemy.ext.asyncio import create_async_engine
from sqlalchemy import text

async def run():
    cfg = get_settings()
    url = cfg.DATABASE_URL
    if url.startswith("postgres://"):
        url = url.replace("postgres://", "postgresql+asyncpg://", 1)
    elif url.startswith("postgresql://"):
        url = url.replace("postgresql://", "postgresql+asyncpg://", 1)
    engine = create_async_engine(url)

    async with engine.begin() as conn:
        # Get content from programme_national_svt_claude_opus.md for one broad unit
        r = await conn.execute(
            text("""
                SELECT content, chunk_index
                FROM rag_chunks
                WHERE source = 'programme_national_svt_claude_opus.md'
                AND chapitre ILIKE '%Synthèse des Protéines%'
                ORDER BY chunk_index
                LIMIT 20
            """)
        )
        chunks = r.fetchall()
        print("=== Content from programme_national_svt_claude_opus.md ===\n")
        for i, chunk in enumerate(chunks, 1):
            safe = chunk.content.encode("ascii", "xmlcharrefreplace").decode()
            print(f"--- Chunk {i} (idx={chunk.chunk_index}, len={len(chunk.content)}) ---")
            print(safe[:1500])
            print()

    await engine.dispose()

asyncio.run(run())
