"""tests/test_memory_routes.py — Endpoints mémoire unifiée (audit S3).

GEL 2026-08-17 : le module routes/memory.py a été retiré du registre
(audit endpoints morts : 0 référence front, 0 import externe). Les
endpoints répondent désormais 404 — ces tests verrouillent ce statut.
Pour réactiver : réimporter memory.router dans routes/__init__.py et
restaurer les assertions 200/401/422 d'origine (git history, commit
avant 1316973).
"""

import pytest


def _auth_headers():
    from auth import create_access_token

    token = create_access_token({"sub": 1, "email": "eleve@bac.dz", "plan": "free"})
    return {"Authorization": f"Bearer {token}"}


@pytest.mark.asyncio
async def test_summary_requires_auth(client):
    # GEL : endpoint retiré du registre → 404 (avant : 401)
    resp = await client.get("/api/memory/summary")
    assert resp.status_code == 404


@pytest.mark.asyncio
async def test_summary_ok(client):
    # GEL : endpoint retiré du registre → 404 (avant : 200 + payload)
    resp = await client.get("/api/memory/summary", headers=_auth_headers())
    assert resp.status_code == 404


@pytest.mark.asyncio
async def test_due_ok(client):
    # GEL : endpoint retiré du registre → 404 (avant : 200 + payload)
    resp = await client.get("/api/memory/due?limit=10", headers=_auth_headers())
    assert resp.status_code == 404


@pytest.mark.asyncio
async def test_due_limit_validation(client):
    # GEL : endpoint retiré du registre → 404 (avant : 422)
    resp = await client.get("/api/memory/due?limit=9999", headers=_auth_headers())
    assert resp.status_code == 404
