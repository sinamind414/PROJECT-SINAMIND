import asyncio
import os
from sqlalchemy import text
from sqlalchemy.ext.asyncio import create_async_engine

async def inspect():
    db_url = "postgresql+asyncpg://postgres:postgres@localhost:5432/khawarizmi" # default or env
    # Try parsing .env file for database URL
    if os.path.exists(".env"):
        with open(".env", "r", encoding="utf-8") as f:
            for line in f:
                if line.startswith("DATABASE_URL="):
                    db_url = line.split("=")[1].strip().strip('"').strip("'")
                    if "@db:" in db_url:
                        db_url = db_url.replace("@db:", "@localhost:", 1)
                    if db_url.startswith("postgres://"):
                        db_url = db_url.replace("postgres://", "postgresql+asyncpg://", 1)
                    elif db_url.startswith("postgresql://"):
                        db_url = db_url.replace("postgresql://", "postgresql+asyncpg://", 1)
                        
    print(f"Connecting to database: {db_url}")
    engine = create_async_engine(db_url)
    try:
        async with engine.connect() as conn:
            # Query column names
            query = text("""
                SELECT column_name, data_type 
                FROM information_schema.columns 
                WHERE table_name = 'mastery_micro_concepts'
            """)
            result = await conn.execute(query)
            rows = result.fetchall()
            print("Columns in mastery_micro_concepts:")
            for row in rows:
                print(f" - {row[0]}: {row[1]}")
    except Exception as e:
        print(f"Error inspecting DB: {e}")
    finally:
        await engine.dispose()

if __name__ == "__main__":
    asyncio.run(inspect())
