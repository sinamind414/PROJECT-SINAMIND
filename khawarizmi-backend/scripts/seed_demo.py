"""Seed un compte démo pour le développement local.

Usage :
    cd khawarizmi-backend
    python scripts/seed_demo.py

Crée ou met à jour l'utilisateur de démo :
    email   : eleve@bac.dz
    mdp     : Demo1234!
    prenom  : Ahmed
    filiere : Sciences Naturelles
    plan    : free
"""

import asyncio
import os
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))
os.environ.setdefault("ENVIRONMENT", "development")

from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine

from auth import hash_password

DATABASE_URL = os.getenv(
    "DATABASE_URL",
    "postgresql+asyncpg://postgres:test@localhost/khawarizmi_test"
)

DEMO_EMAIL = "eleve@bac.dz"
DEMO_PASSWORD = "Demo1234!"
DEMO_PRENOM = "Ahmed"
DEMO_FILIERE = "Sciences Naturelles"


async def seed():
    engine = create_async_engine(DATABASE_URL, echo=False)

    async with AsyncSession(engine) as session:
        result = await session.execute(
            text("SELECT id FROM users WHERE email = :email"),
            {"email": DEMO_EMAIL},
        )
        existing = result.fetchone()

        if existing:
            await session.execute(
                text("""
                    UPDATE users
                    SET password_hash = :pwd, prenom = :prenom, filiere = :filiere, plan = 'free'
                    WHERE email = :email
                """),
                {
                    "pwd": hash_password(DEMO_PASSWORD),
                    "prenom": DEMO_PRENOM,
                    "filiere": DEMO_FILIERE,
                    "email": DEMO_EMAIL,
                },
            )
            print(f"✅ Utilisateur mis à jour : {DEMO_EMAIL}")
        else:
            await session.execute(
                text("""
                    INSERT INTO users (email, password_hash, prenom, filiere, plan)
                    VALUES (:email, :pwd, :prenom, :filiere, 'free')
                """),
                {
                    "email": DEMO_EMAIL,
                    "pwd": hash_password(DEMO_PASSWORD),
                    "prenom": DEMO_PRENOM,
                    "filiere": DEMO_FILIERE,
                },
            )
            print(f"✅ Utilisateur créé : {DEMO_EMAIL}")

        await session.commit()

        # Afficher l'ID
        result = await session.execute(
            text("SELECT id, email, prenom, filiere, plan FROM users WHERE email = :email"),
            {"email": DEMO_EMAIL},
        )
        user = result.fetchone()
        if user:
            print(f"   ID     : {user[0]}")
            print(f"   Email  : {user[1]}")
            print(f"   Prénom : {user[2]}")
            print(f"   Filière: {user[3]}")
            print(f"   Plan   : {user[4]}")

    await engine.dispose()
    print("\n🔑 Identifiants de démo :")
    print(f"   Email    : {DEMO_EMAIL}")
    print(f"   Mot de passe : {DEMO_PASSWORD}")
    print(f"   URL      : http://localhost:3000/auth/login")


if __name__ == "__main__":
    asyncio.run(seed())
