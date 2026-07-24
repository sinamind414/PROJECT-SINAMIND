from __future__ import annotations

from datetime import datetime, timezone, timedelta

import pytest
from httpx import AsyncClient

from tests.mock_store import mock_store as _mock_orm_store


class TestAppendEvent:
    """B-T1 / B-T2 / B-T3 — tunnel event persistence."""

    async def test_bt1_append_event_nominal(
        self, client: AsyncClient, auth_headers: dict
    ):
        resp = await client.post(
            "/api/lesson/verb:analyse/event",
            headers=auth_headers,
            json={
                "session_id": "sess-1",
                "type": "DOCUMENT_SUBMIT",
                "payload": {"outcome": "passed"},
                "client_event_id": None,
            },
        )
        assert resp.status_code == 200
        data = resp.json()
        assert "event_id" in data
        assert len(data["event_id"]) > 10

    async def test_bt2_idempotent_client_event_id(
        self, client: AsyncClient, auth_headers: dict
    ):
        payload = {
            "session_id": "sess-2",
            "type": "FEEDBACK_SEEN",
            "payload": {},
            "client_event_id": "ceid-001",
        }
        resp1 = await client.post(
            "/api/lesson/da:co2/event",
            headers=auth_headers,
            json=payload,
        )
        assert resp1.status_code == 200
        eid1 = resp1.json()["event_id"]

        resp2 = await client.post(
            "/api/lesson/da:co2/event",
            headers=auth_headers,
            json=payload,
        )
        assert resp2.status_code == 200
        eid2 = resp2.json()["event_id"]

        assert eid1 == eid2

    async def test_bt3_abort_does_not_create_recall(
        self, client: AsyncClient, auth_headers: dict
    ):
        resp = await client.post(
            "/api/lesson/bac:svt2024/event",
            headers=auth_headers,
            json={
                "session_id": "sess-3",
                "type": "SESSION_EXIT",
                "payload": {},
                "client_event_id": "ceid-abort",
            },
        )
        assert resp.status_code == 200
        assert "event_id" in resp.json()

        recall_resp = await client.get(
            "/api/recall/due",
            headers=auth_headers,
        )
        assert recall_resp.status_code == 200
        assert recall_resp.json() == []


class TestListDueRecall:
    """B-T4 — recall due query."""

    async def test_bt4_list_due_recall(
        self, client: AsyncClient, auth_headers: dict
    ):
        now = datetime.now(timezone.utc)
        _mock_orm_store[("recall_items", 1)] = {
            "r1": {
                "id": "r1",
                "lesson_id": "verb:analyse",
                "concept_id": None,
                "stage": 1,
                "next_review_at": now - timedelta(hours=1),
                "last_result": None,
            },
            "r2": {
                "id": "r2",
                "lesson_id": "da:co2",
                "concept_id": None,
                "stage": 0,
                "next_review_at": now + timedelta(days=7),
                "last_result": None,
            },
        }

        resp = await client.get(
            "/api/recall/due?limit=50",
            headers=auth_headers,
        )
        assert resp.status_code == 200
        items = resp.json()
        assert len(items) == 1
        assert items[0]["recall_item_id"] == "r1"
        assert items[0]["lesson_id"] == "verb:analyse"


class TestApplyRecallResult:
    """B-T5 / B-T6 / B-T7 — recall result application."""

    @pytest.fixture(autouse=True)
    def seed_recall(self):
        now = datetime.now(timezone.utc)
        _mock_orm_store[("recall_items", 1)] = {
            "rec-fail": {
                "id": "rec-fail",
                "lesson_id": "verb:synthetiser",
                "concept_id": None,
                "stage": 2,
                "next_review_at": now - timedelta(hours=1),
                "last_result": None,
            },
            "rec-ok": {
                "id": "rec-ok",
                "lesson_id": "verb:analyser",
                "concept_id": None,
                "stage": 0,
                "next_review_at": now - timedelta(hours=1),
                "last_result": None,
            },
        }
        yield
        _mock_orm_store.pop(("recall_items", 1), None)

    async def test_bt5_recall_result_fail_resets_stage(
        self, client: AsyncClient, auth_headers: dict
    ):
        resp = await client.post(
            "/api/recall/rec-fail/result",
            headers=auth_headers,
            json={"success": False},
        )
        assert resp.status_code == 200
        data = resp.json()
        assert data["recall_item_id"] == "rec-fail"
        assert data["stage"] == 0
        assert data["last_result"] == "fail"

    async def test_bt6_recall_result_success_advances_stage(
        self, client: AsyncClient, auth_headers: dict
    ):
        resp = await client.post(
            "/api/recall/rec-ok/result",
            headers=auth_headers,
            json={"success": True},
        )
        assert resp.status_code == 200
        data = resp.json()
        assert data["recall_item_id"] == "rec-ok"
        assert data["stage"] == 1
        assert data["last_result"] == "success"

    async def test_bt7_recall_ownership_404(
        self, client: AsyncClient, auth_headers: dict
    ):
        resp = await client.post(
            "/api/recall/nonexistent-recall/result",
            headers=auth_headers,
            json={"success": True},
        )
        assert resp.status_code == 404


class TestRoutes:
    """B-T8 — route smoke tests (auth, no SM logic)."""

    async def test_bt8a_post_event_requires_auth(self, client: AsyncClient):
        resp = await client.post(
            "/api/lesson/verb:analyse/event",
            json={"session_id": "x", "type": "x", "payload": {}},
        )
        assert resp.status_code in (401, 403)

    async def test_bt8b_get_recall_due_requires_auth(self, client: AsyncClient):
        resp = await client.get("/api/recall/due")
        assert resp.status_code in (401, 403)

    async def test_bt8c_post_recall_result_requires_auth(self, client: AsyncClient):
        resp = await client.post(
            "/api/recall/x/result",
            json={"success": True},
        )
        assert resp.status_code in (401, 403)

    async def test_bt8d_get_recall_due_returns_json(
        self, client: AsyncClient, auth_headers: dict
    ):
        resp = await client.get(
            "/api/recall/due",
            headers=auth_headers,
        )
        assert resp.status_code == 200
        assert isinstance(resp.json(), list)
