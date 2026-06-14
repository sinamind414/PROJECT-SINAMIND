# tests/conftest.py
# Khawarizmi Pro — Fixtures globales pytest

import pytest
import asyncio
import sys
import os
from pathlib import Path
from typing import AsyncGenerator
from httpx import AsyncClient, ASGITransport
from unittest.mock import AsyncMock, patch

sys.path.insert(0, str(Path(__file__).parent.parent))

os.environ.setdefault("SECRET_KEY", "test-secret-key-khawarizmi-2026")
os.environ.setdefault("DATABASE_URL",
    "postgresql+asyncpg://postgres:testpass@localhost/khawarizmi_test")
os.environ.setdefault("REDIS_URL", "redis://localhost:6379/1")
os.environ.setdefault("GEMINI_API_KEY", "test-gemini-key")
os.environ.setdefault("ENVIRONMENT", "test")

from main import app
from deps import get_db

TEST_PWD_HASH = "$2b$12$7.cA3KDwXgXygLhjVDrNl.fZPK3kqUcd5.LXeRZ2b0Yf7TkPwdjea"


class MockRow:
    def __init__(self, data):
        self._data = data
        self._items = list(data.values()) if data else []

    def __getitem__(self, key):
        if isinstance(key, int):
            return self._items[key] if key < len(self._items) else None
        return self._data.get(key)

    def __bool__(self):
        return bool(self._data)

    def _mapping(self):
        return self._data


class MockAsyncExecResult:
    def __init__(self, rows=None):
        self._rows = rows or []

    def fetchone(self):
        return MockRow(self._rows[0]) if self._rows else None

    def fetchall(self):
        return [MockRow(r) if isinstance(r, dict) else MockRow({}) for r in self._rows]

    def first(self):
        return MockRow(self._rows[0]) if self._rows else None

    def all(self):
        return [MockRow(r) if isinstance(r, dict) else MockRow({}) for r in self._rows]

    def scalars(self):
        return self

    def __iter__(self):
        return iter(self._rows)


_inserted_emails = set()


class MockAsyncSession:
    def __init__(self):
        self._user_data = {
            "id": 1,
            "email": "eleve@bac.dz",
            "password_hash": TEST_PWD_HASH,
            "prenom": "Test",
            "plan": "free",
            "created_at": "2026-01-01"
        }

    async def __aenter__(self):
        return self

    async def __aexit__(self, *args):
        pass

    async def execute(self, statement, *args, **kwargs):
        sql = str(statement) if hasattr(statement, '__str__') else str(statement)
        params = args[0] if args else kwargs

        if "INSERT INTO users" in sql:
            email = (params.get("email", "") if isinstance(params, dict)
                     else getattr(params, "get", lambda x: "")("email", ""))
            _inserted_emails.add(email)
            return MockAsyncExecResult([{"id": 1}])

        if "SELECT" in sql:
            if "users" in sql:
                if isinstance(params, dict):
                    query_email = params.get("email", "")
                else:
                    query_email = ""
                if not query_email:
                    return MockAsyncExecResult([self._user_data])
                if "email" in sql and query_email not in _inserted_emails:
                    return MockAsyncExecResult()
                return MockAsyncExecResult([self._user_data])
            return MockAsyncExecResult()

        if "UPDATE" in sql or "DELETE" in sql:
            return MockAsyncExecResult([{"id": 1}])

        return MockAsyncExecResult()

    async def commit(self):
        pass

    async def rollback(self):
        pass

    async def close(self):
        pass

    def __call__(self):
        return self


@pytest.fixture(scope="session")
def event_loop():
    policy = asyncio.get_event_loop_policy()
    loop = policy.new_event_loop()
    yield loop
    loop.close()


async def override_get_db():
    session = MockAsyncSession()
    try:
        yield session
    finally:
        await session.close()


@pytest.fixture(autouse=True)
def override_deps():
    _inserted_emails.clear()
    app.dependency_overrides[get_db] = override_get_db
    yield
    app.dependency_overrides.clear()


@pytest.fixture
async def client() -> AsyncGenerator:
    transport = ASGITransport(app=app)
    async with AsyncClient(
        transport=transport,
        base_url="http://test"
    ) as ac:
        yield ac


@pytest.fixture
async def auth_headers() -> dict:
    from auth import create_access_token
    token = create_access_token({"sub": 1, "email": "eleve@bac.dz", "plan": "free"})
    return {"Authorization": f"Bearer {token}"}


@pytest.fixture
def mock_gemini():
    with patch("services.llm.call_gpt4o_evaluator") as mock:
        mock.return_value = AsyncMock(return_value={
            "response": "Réponse simulée",
            "model_used": "gemini-2.5-flash",
            "fallback_active": False
        })
        yield mock
