import asyncio
import asyncpg
import redis.asyncio as redis

async def test_conn():
    print("Testing Redis...")
    try:
        r = await redis.from_url("redis://localhost:6379/0")
        await r.ping()
        print("Redis OK")
    except Exception as e:
        print(f"Redis FAIL: {e}")

    print("Testing PostgreSQL...")
    try:
        conn = await asyncpg.connect("postgresql://khawarizmi_user:MOT_DE_PASSE_FORT_ICI@localhost:5432/khawarizmi")
        await conn.close()
        print("PostgreSQL OK")
    except Exception as e:
        print(f"PostgreSQL FAIL: {e}")

if __name__ == "__main__":
    asyncio.run(test_conn())
