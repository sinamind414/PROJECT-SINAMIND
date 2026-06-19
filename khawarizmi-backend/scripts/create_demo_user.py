"""Crée un compte démo pour tester l'application."""
import asyncio, os, sys
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy import text
from auth import hash_password, create_access_token


async def main():
    db_url = os.environ.get(
        "DATABASE_URL",
        "postgresql+asyncpg://khawarizmi_user:CHANGE_ME_STRONG_PASSWORD@localhost:5432/khawarizmi",
    )
    if db_url.startswith("postgresql://"):
        db_url = db_url.replace("postgresql://", "postgresql+asyncpg://", 1)
    elif db_url.startswith("postgres://"):
        db_url = db_url.replace("postgres://", "postgresql+asyncpg://", 1)

    engine = create_async_engine(db_url, pool_size=2)

    demo_email = "demo@khawarizmi.dz"
    demo_pwd = "demo1234"
    hashed = hash_password(demo_pwd)

    async with AsyncSession(engine) as session:
        r = await session.execute(
            text("SELECT id, email FROM users WHERE email = :e"), {"e": demo_email}
        )
        existing = r.fetchone()

        if existing:
            print(f"Demo user already exists: id={existing[0]} email={existing[1]}")
            user_id = existing[0]
        else:
            r = await session.execute(
                text("""
                    INSERT INTO users (email, password_hash, prenom, wilaya, filiere, plan)
                    VALUES (:email, :pwd, :prenom, :wilaya, :filiere, :plan)
                    RETURNING id, email, prenom, plan
                """),
                {
                    "email": demo_email,
                    "pwd": hashed,
                    "prenom": "Ahmed Demo",
                    "wilaya": "16",
                    "filiere": "Sciences Naturelles",
                    "plan": "premium",
                },
            )
            user = r.fetchone()
            await session.commit()
            user_id = user[0]
            print(f"Demo user created: id={user[0]} email={user[1]}")

        token = create_access_token({"sub": user_id, "plan": "premium"})

        print(f"\n{'='*45}")
        print(f"  DEMO ACCOUNT")
        print(f"{'='*45}")
        print(f"  Email:    {demo_email}")
        print(f"  Password: {demo_pwd}")
        print(f"  Plan:     Premium")
        print(f"{'='*45}")
        print(f"\nToken JWT (pour tests API):")
        print(f"{token}\n")

    await engine.dispose()


if __name__ == "__main__":
    asyncio.run(main())
