"""G9 / hotfix T2 — IDOR Bac blanc : session d'un autre élève → 403."""

from __future__ import annotations

import asyncio
import re
from pathlib import Path

import pytest

BACKEND = Path(__file__).resolve().parent.parent
SRC = (BACKEND / "routes" / "bac_blanc.py").read_text(encoding="utf-8")


def test_helper_exists():
    assert "async def _require_own_session" in SRC
    assert "AND user_id = :uid" in SRC
    assert "Session d'un autre élève" in SRC


def test_choose_save_submit_correction_call_helper():
    for name in ("choose_subject", "save_answer", "submit_bac", "get_correction"):
        assert f"async def {name}" in SRC, name
    assert SRC.count("_require_own_session(") >= 5  # def + 4 routes


def test_updates_on_sessions_include_user_id():
    """Défense en profondeur : UPDATE bac_sessions … AND user_id."""
    updates = re.findall(
        r"UPDATE bac_sessions[\s\S]{0,400}WHERE[^\n]+",
        SRC,
    )
    assert updates, "aucun UPDATE bac_sessions"
    for stmt in updates:
        assert "user_id" in stmt, stmt


def test_no_bare_session_select_in_routes():
    """Hors probe 403, pas de WHERE id = :sid sans user_id sur bac_sessions."""
    cleaned = SRC.replace("SELECT 1 FROM bac_sessions WHERE id = :sid", "")
    bare = re.findall(
        r"FROM bac_sessions\s+WHERE id = :sid(?!\s+AND user_id)",
        cleaned,
    )
    assert bare == [], bare


class _FakeResult:
    def __init__(self, row=None):
        self._row = row

    def fetchone(self):
        return self._row


class _MapRow:
    def __init__(self, data: dict):
        self._mapping = data


class _FakeDB:
    def __init__(self, *, owned=None, exists=False):
        self.owned = owned
        self.exists = exists
        self.sqls: list[str] = []

    async def execute(self, statement, params=None):
        sql = str(statement)
        self.sqls.append(sql)
        if "AND user_id = :uid" in sql.replace("\n", " "):
            return _FakeResult(_MapRow(self.owned) if self.owned else None)
        if "SELECT 1 FROM bac_sessions" in sql.replace("\n", " "):
            return _FakeResult((1,) if self.exists else None)
        return _FakeResult()


def test_require_own_returns_row():
    pytest.importorskip("fastapi")
    from routes.bac_blanc import _require_own_session

    async def _run():
        db = _FakeDB(owned={"id": "s1", "user_id": 1, "status": "in_progress"})
        row = await _require_own_session(db, "s1", 1)
        assert row["id"] == "s1"
        assert any("user_id = :uid" in s.replace("\n", " ") for s in db.sqls)

    asyncio.run(_run())


def test_require_own_other_user_is_403():
    pytest.importorskip("fastapi")
    from fastapi import HTTPException

    from routes.bac_blanc import _require_own_session

    async def _run():
        db = _FakeDB(owned=None, exists=True)
        with pytest.raises(HTTPException) as ei:
            await _require_own_session(db, "s-other", 1)
        assert ei.value.status_code == 403

    asyncio.run(_run())


def test_require_own_missing_is_404():
    pytest.importorskip("fastapi")
    from fastapi import HTTPException

    from routes.bac_blanc import _require_own_session

    async def _run():
        db = _FakeDB(owned=None, exists=False)
        with pytest.raises(HTTPException) as ei:
            await _require_own_session(db, "missing", 1)
        assert ei.value.status_code == 404

    asyncio.run(_run())
