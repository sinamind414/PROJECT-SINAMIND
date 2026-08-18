"""tests/test_actions_immediates.py — Verrouille les 4 fixes backend
des actions « immédiates » de l'audit technique 2026-08-18 :

1. hashing.py : plus de fallback pepper dev-only-key (ValueError si SECRET_KEY vide).
2. social.py upload : whitelist d'extensions + limite de taille (10 Mo).
3. social.py users/search : email absent de la réponse.
4. admin_ingest : hmac.compare_digest (le module contient l'import hmac).
"""

import pytest
from unittest.mock import patch

from tests.conftest import MockAsyncSession


class _FakeResult:
    def __init__(self, rows=None):
        self._rows = rows if rows is not None else []

    def fetchall(self):
        return self._rows


class _FakeRow:
    """Émule un Row SQLAlchemy : dict(r._mapping) doit fonctionner."""

    def __init__(self, mapping: dict):
        self._mapping = mapping


# ── 1. Pepper ─────────────────────────────────────────────────────
def test_pepper_sans_secret_key_leve_une_erreur(monkeypatch):
    from services import hashing

    class _NoKey:
        SECRET_KEY = ""

    monkeypatch.setattr(hashing, "get_settings", lambda: _NoKey())
    with pytest.raises(ValueError):
        hashing.hash_answer("réponse élève")


def test_pepper_avec_secret_key_hache_normalement():
    from services.hashing import hash_answer

    assert len(hash_answer("réponse élève")) == 64  # HMAC-SHA256 hex


# ── 2. Upload ─────────────────────────────────────────────────────
def _auth_headers():
    from auth import create_access_token

    token = create_access_token({"sub": 1, "email": "eleve@bac.dz", "plan": "free"})
    return {"Authorization": f"Bearer {token}"}


@pytest.mark.asyncio
async def test_upload_refuse_extension_non_autorisee(client):
    resp = await client.post(
        "/api/social/upload",
        headers=_auth_headers(),
        files={"file": ("exploit.sh", b"#!/bin/sh", "text/x-shellscript")},
    )
    assert resp.status_code == 400


@pytest.mark.asyncio
async def test_upload_refuse_fichier_trop_gros(client):
    from routes.social import MAX_UPLOAD_BYTES

    gros = b"0" * (MAX_UPLOAD_BYTES + 100)
    resp = await client.post(
        "/api/social/upload",
        headers=_auth_headers(),
        files={"file": ("gros.pdf", gros, "application/pdf")},
    )
    assert resp.status_code == 400


# ── 3. Email masqué dans la recherche ─────────────────────────────
@pytest.mark.asyncio
async def test_users_search_ne_retourne_pas_le_mail(client):
    original = MockAsyncSession.execute

    async def spy_execute(self, statement, *args, **kwargs):
        sql = str(statement)
        if "FROM users" in sql and "LIKE" in sql:
            return _FakeResult(rows=[_FakeRow({"id": 2, "nom": "Aya"})])
        if "FROM users" in sql and "SELECT" in sql and "conversation_members" not in sql:
            return await original(self, statement, *args, **kwargs)  # auth
        return _FakeResult()

    with patch("tests.conftest.MockAsyncSession.execute", new=spy_execute):
        resp = await client.get("/api/social/users/search?q=Aya", headers=_auth_headers())
    assert resp.status_code == 200
    data = resp.json()
    assert data[0]["nom"] == "Aya"
    assert "email" not in data[0]


# ── 4. compare_digest présent ─────────────────────────────────────
def test_admin_ingest_utilise_compare_digest():
    import ast
    from pathlib import Path

    src = Path("routes/admin_ingest.py").read_text(encoding="utf-8")
    assert "hmac.compare_digest" in src
    tree = ast.parse(src)
    imports = [
        n
        for n in ast.walk(tree)
        if isinstance(n, ast.Import) and any(a.name == "hmac" for a in n.names)
    ]
    assert imports, "import hmac manquant dans admin_ingest.py"
