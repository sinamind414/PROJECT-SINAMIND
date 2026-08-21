"""Tests du sondage « verbe le plus difficile » (fix 2026-08-21).

Le frontend (HardestVerbPoll) postait /api/action-verbs/feedback/hardest
qui n'existait PAS au backend (404 avalé par catch silencieux — aucun vote
jamais collecté). L'endpoint public existe désormais : 200 avec compteur
Redis optionnel, 400 si verb_slug absent/vide/trop long.
"""
from __future__ import annotations

import pytest
from httpx import ASGITransport, AsyncClient

from main import app
from routes.lifespan import lifespan

pytestmark = pytest.mark.asyncio


@pytest.fixture(scope="module")
async def client():
    async with lifespan(app):
        transport = ASGITransport(app=app)
        async with AsyncClient(transport=transport, base_url="http://test") as c:
            yield c


async def test_vote_valide_sans_auth(client: AsyncClient) -> None:
    r = await client.post("/api/action-verbs/feedback/hardest", json={"verb_slug": "analyse"})
    assert r.status_code == 200
    data = r.json()
    assert data["status"] == "ok"
    assert data["verb_slug"] == "analyse"
    # count = None en preview (Redis absent) — jamais d'erreur
    assert "count" in data


async def test_vote_sans_slug_400(client: AsyncClient) -> None:
    r = await client.post("/api/action-verbs/feedback/hardest", json={"verb_slug": ""})
    assert r.status_code == 400


async def test_vote_corps_vide_400(client: AsyncClient) -> None:
    r = await client.post("/api/action-verbs/feedback/hardest", json={})
    assert r.status_code == 400


async def test_vote_slug_trop_long_400(client: AsyncClient) -> None:
    r = await client.post("/api/action-verbs/feedback/hardest", json={"verb_slug": "x" * 81})
    assert r.status_code == 400


async def test_vote_repetable(client: AsyncClient) -> None:
    """Deux votes consécutifs : les deux 200 (idempotent, pas d'unicité)."""
    r1 = await client.post("/api/action-verbs/feedback/hardest", json={"verb_slug": "deduce"})
    r2 = await client.post("/api/action-verbs/feedback/hardest", json={"verb_slug": "deduce"})
    assert r1.status_code == 200
    assert r2.status_code == 200
