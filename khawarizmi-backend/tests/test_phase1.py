from httpx import AsyncClient


class TestPhase1:
    async def test_next_actions_requires_auth(self, client: AsyncClient):
        response = await client.post("/api/phase1/next-actions", json={"last_action": "quiz"})
        assert response.status_code in [401, 503]

    async def test_next_actions(self, client: AsyncClient, auth_headers: dict):
        response = await client.post(
            "/api/phase1/next-actions",
            headers=auth_headers,
            json={"last_action": "quiz"},
        )
        assert response.status_code == 200
        data = response.json()
        assert "actions" in data
        assert len(data["actions"]) == 3

    async def test_combo_success(self, client: AsyncClient, auth_headers: dict):
        response = await client.post(
            "/api/phase1/combo",
            headers=auth_headers,
            json={"success": True},
        )
        assert response.status_code == 200
        data = response.json()
        assert "multiplier" in data
        assert "points_earned" in data
        assert "combo_count" in data

    async def test_combo_failure(self, client: AsyncClient, auth_headers: dict):
        response = await client.post(
            "/api/phase1/combo",
            headers=auth_headers,
            json={"success": False},
        )
        assert response.status_code == 200
        data = response.json()
        assert data["combo_count"] == 0

    async def test_combo_escalates_multiplier(self, client: AsyncClient, auth_headers: dict):
        for _ in range(3):
            await client.post("/api/phase1/combo", headers=auth_headers, json={"success": True})
        response = await client.post(
            "/api/phase1/combo", headers=auth_headers, json={"success": True}
        )
        data = response.json()
        assert data["multiplier"] >= 2
