import os, asyncio, asyncpg

async def main():
    db_url = os.getenv("DATABASE_URL")
    if not db_url:
        print("No DATABASE_URL")
        return
    conn = await asyncpg.connect(dsn=db_url)
    await conn.execute("CREATE EXTENSION IF NOT EXISTS vector;")
    await conn.close()
    print("Extension created")

if __name__ == "__main__":
    asyncio.run(main())
