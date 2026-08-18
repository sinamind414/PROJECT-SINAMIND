"""tests/test_social_idor.py — Verrouille la correction IDOR (audit technique 2026-08-18).

Avant : GET /conversations/{cid}/messages lisait les messages sans vérifier
l'appartenance ; POST /messages écrivait dans n'importe quelle conversation.
Après : lecture filtrée par EXISTS conversation_members ; écriture refusée
(403) pour un non-membre.
"""

from unittest.mock import patch

import pytest

from tests.conftest import MockAsyncSession


class _FakeResult:
    def __init__(self, row=None, rows=None):
        self._row = row
        self._rows = rows if rows is not None else []

    def fetchone(self):
        return self._row

    def fetchall(self):
        return self._rows


@pytest.mark.asyncio
async def test_read_messages_sql_contient_le_filtre_d_appartenance(client, auth_headers):
    """La requête de lecture doit contenir la vérification conversation_members."""
    executed: list[str] = []
    original = MockAsyncSession.execute

    async def spy_execute(self, statement, *args, **kwargs):
        sql = str(statement)
        executed.append(sql)
        if "FROM users" in sql and "SELECT" in sql and "conversation_members" not in sql:
            return await original(self, statement, *args, **kwargs)  # auth
        if "FROM messages" in sql:
            return _FakeResult(rows=[])  # non-membre : aucune ligne
        return _FakeResult()

    with patch("tests.conftest.MockAsyncSession.execute", new=spy_execute):
        resp = await client.get("/api/social/conversations/999/messages", headers=auth_headers)
    assert resp.status_code == 200
    assert resp.json() == []
    read_sql = next((s for s in executed if "FROM messages" in s), "")
    assert "conversation_members" in read_sql, "le filtre d'appartenance a disparu du SQL de lecture"
    assert ":uid" in read_sql


@pytest.mark.asyncio
async def test_send_message_refuse_un_non_membre(client, auth_headers):
    """POST /messages : un non-membre reçoit 403."""
    original = MockAsyncSession.execute

    async def spy_execute(self, statement, *args, **kwargs):
        sql = str(statement)
        if "FROM users" in sql and "SELECT" in sql and "conversation_members" not in sql:
            return await original(self, statement, *args, **kwargs)  # auth
        if "SELECT 1 FROM conversation_members" in sql:
            return _FakeResult(row=None)  # non-membre
        return _FakeResult()

    with patch("tests.conftest.MockAsyncSession.execute", new=spy_execute):
        resp = await client.post(
            "/api/social/messages",
            json={"conversation_id": 999, "content": "intrusion"},
            headers=auth_headers,
        )
    assert resp.status_code == 403


@pytest.mark.asyncio
async def test_send_message_accepte_un_membre(client, auth_headers):
    """POST /messages : un membre passe (comportement d'origine préservé)."""
    original = MockAsyncSession.execute

    async def spy_execute(self, statement, *args, **kwargs):
        sql = str(statement)
        if "FROM users" in sql and "SELECT" in sql and "conversation_members" not in sql:
            return await original(self, statement, *args, **kwargs)  # auth
        if "SELECT 1 FROM conversation_members" in sql:
            return _FakeResult(row=(1,))  # membre
        return _FakeResult()

    with patch("tests.conftest.MockAsyncSession.execute", new=spy_execute):
        resp = await client.post(
            "/api/social/messages",
            json={"conversation_id": 1, "content": "bonjour"},
            headers=auth_headers,
        )
    assert resp.status_code == 200
    assert resp.json() == {"status": "sent"}
