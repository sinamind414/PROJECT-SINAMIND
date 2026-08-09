"""tests/test_memory_routes.py — Endpoints mémoire unifiée (audit S3).

- /api/memory/summary : 401 sans auth, 200 avec auth (DB mockée → tolérant).
- /api/memory/due : items dus formatés.
"""

from unittest.mock import patch

import pytest


def _auth_headers():
    from auth import create_access_token

    token = create_access_token({"sub": 1, "email": "eleve@bac.dz", "plan": "free"})
    return {"Authorization": f"Bearer {token}"}


@pytest.mark.asyncio
async def test_summary_requires_auth(client):
    resp = await client.get("/api/memory/summary")
    assert resp.status_code == 401


@pytest.mark.asyncio
async def test_summary_ok(client):
    from tests.conftest import MockAsyncSession

    original_execute = MockAsyncSession.execute

    async def mock_execute(self, statement, *args, **kwargs):
        sql = str(statement)
        if "FROM users" in sql and "SELECT" in sql:
            return await original_execute(self, statement, *args, **kwargs)
        # tables mémoire absentes du preview → le service retourne des sources
        # vides (tolérance) ; on simule la table indisponible
        raise Exception("table indisponible")

    with patch("tests.conftest.MockAsyncSession.execute", new=mock_execute):
        resp = await client.get("/api/memory/summary", headers=_auth_headers())
    assert resp.status_code == 200
    data = resp.json()
    assert data["total_items"] == 0
    assert data["by_kind"] == {}
    assert data["due_count"] == 0


@pytest.mark.asyncio
async def test_due_ok(client):
    from tests.conftest import MockAsyncSession

    original_execute = MockAsyncSession.execute

    async def mock_execute(self, statement, *args, **kwargs):
        sql = str(statement)
        if "FROM users" in sql and "SELECT" in sql:
            return await original_execute(self, statement, *args, **kwargs)
        raise Exception("table indisponible")

    with patch("tests.conftest.MockAsyncSession.execute", new=mock_execute):
        resp = await client.get("/api/memory/due?limit=10", headers=_auth_headers())
    assert resp.status_code == 200
    data = resp.json()
    assert data["count"] == 0
    assert data["items"] == []


@pytest.mark.asyncio
async def test_due_limit_validation(client):
    resp = await client.get("/api/memory/due?limit=9999", headers=_auth_headers())
    assert resp.status_code == 422
