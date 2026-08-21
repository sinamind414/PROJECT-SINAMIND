"""Tests du seed vidéos — fix drift d'auto-DDL (2026-08-21).

La table SQLite auto-créée avait `url TEXT NOT NULL` alors que la migration
006 (production PostgreSQL) n'a PAS cette colonne → POST /api/videos/seed
échouait en preview (NOT NULL constraint failed) bien que la production
l'acceptât. Aligné : l'auto-DDL suit la migration, le seed fonctionne partout.

Deux angles :
1. Garde sur l'auto-DDL (database.py ne doit plus exiger url pour videos).
2. End-to-end en sous-processus (le lifespan ne peut pas être re-entré sous
   pytest-asyncio : la queue du worker de réconciliation est liée au premier
   event loop — artefact de test, pas un bug prod).
"""
from __future__ import annotations

import os
import pathlib
import subprocess
import sys
import tempfile

BACKEND = pathlib.Path(__file__).resolve().parent.parent

_SEED_E2E = """
import asyncio
from httpx import ASGITransport, AsyncClient
from main import app
from routes.lifespan import lifespan

async def main():
    async with lifespan(app):
        t = ASGITransport(app=app)
        async with AsyncClient(transport=t, base_url="http://seed") as c:
            r1 = await c.post("/api/videos/seed")
            print("SEED1", r1.status_code, r1.json())
            r2 = await c.post("/api/videos/seed")
            print("SEED2", r2.status_code, r2.json())
            assert r1.status_code == 200, r1.text
            assert r2.status_code == 200, r2.text

asyncio.run(main())
"""


def test_auto_ddl_videos_sans_colonne_url() -> None:
    """L'auto-DDL SQLite est alignée sur la migration 006 (pas de url NOT NULL)."""
    source = (BACKEND / "database.py").read_text(encoding="utf-8")
    marker = "CREATE TABLE IF NOT EXISTS videos ("
    assert marker in source
    block = source.split(marker, 1)[1].split(")", 1)[0]
    assert "url" not in block, (
        f"database.py : la table videos auto-créée ne doit PAS avoir de colonne url "
        f"(absente de la migration 006 → seed planté en preview). DDL: {block[:200]}"
    )


def test_seed_end_to_end_sqlite() -> None:
    """Processus frais : lifespan + POST /api/videos/seed ×2 → 200 (pas de 500)."""
    with tempfile.TemporaryDirectory() as tmp:
        env = {
            **{k: v for k, v in os.environ.items() if k not in ("DATABASE_URL",)},
            "DATABASE_URL": f"sqlite+aiosqlite:///{tmp}/videos.db",
            "SECRET_KEY": "videos-seed-secret-key-16ch",
            "ENVIRONMENT": "ci",
            "REDIS_URL": "",
            "PYTHONPATH": str(BACKEND),
        }
        result = subprocess.run(
            [sys.executable, "-c", _SEED_E2E],
            capture_output=True, text=True, env=env, cwd=str(BACKEND), timeout=120,
        )
    assert result.returncode == 0, f"stdout={result.stdout}\nstderr={result.stderr[-1000:]}"
    assert "SEED1 200" in result.stdout
    assert "SEED2 200" in result.stdout
