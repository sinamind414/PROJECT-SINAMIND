import asyncio
from sqlalchemy.ext.asyncio import create_async_engine
from sqlalchemy import text

DATABASE_URL = "postgresql+asyncpg://khawarizmi_user:khawarizmi_dev_pass_2024@localhost:5432/khawarizmi"

async def main():
    engine = create_async_engine(DATABASE_URL)
    async with engine.begin() as conn:
        # 1. Drop FK
        await conn.execute(text(
            "ALTER TABLE mastery_micro_concepts DROP CONSTRAINT IF EXISTS mastery_micro_concepts_micro_concept_id_fkey"
        ))
        print("FK constraint dropped.")

        # 2. Verify
        result = await conn.execute(text(
            "SELECT conname FROM pg_constraint WHERE conrelid = 'mastery_micro_concepts'::regclass AND contype = 'f'"
        ))
        remaining = result.fetchall()
        if remaining:
            print(f"WARNING: FK still exists: {[r[0] for r in remaining]}")
        else:
            print("Verified: no FK constraints on mastery_micro_concepts.")

        # 3. Check tables
        for table in ["rag_chunks", "mastery_micro_concepts", "mindmaps"]:
            result = await conn.execute(text(f"SELECT COUNT(*) FROM {table}"))
            print(f"{table} count: {result.scalar()}")

    await engine.dispose()
    print("Done.")

asyncio.run(main())
