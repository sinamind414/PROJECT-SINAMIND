from httpx import AsyncClient


class TestPhase6:
    async def test_global_metrics(self, client: AsyncClient):
        response = await client.get("/api/phase6/metrics")
        assert response.status_code == 200
        data = response.json()
        assert "daily_active_users" in data
        assert "streak_retention_j7" in data

    async def test_user_engagement(self, client: AsyncClient, auth_headers: dict):
        response = await client.get("/api/phase6/user-engagement", headers=auth_headers)
        assert response.status_code == 200
        data = response.json()
        assert "current_streak" in data

    async def test_top_performers(self, client: AsyncClient):
        response = await client.get("/api/phase6/top-performers")
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
