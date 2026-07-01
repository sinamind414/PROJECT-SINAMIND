import pytest
from httpx import AsyncClient


@pytest.mark.xfail(reason="Routes phase4 retirées (doublons): non enregistrées dans ALL_ROUTERS")
class TestPhase4:
    async def test_award_points_excellent(self, client: AsyncClient, auth_headers: dict):
        response = await client.post(
            "/api/phase4/methodology-action",
            headers=auth_headers,
            json={"verb": "وضّح", "quality": "excellent"},
        )
        assert response.status_code == 200
        data = response.json()
        assert data["points"] == 30
        assert "excellent" in data["message"]

    async def test_award_points_poor(self, client: AsyncClient, auth_headers: dict):
        response = await client.post(
            "/api/phase4/methodology-action",
            headers=auth_headers,
            json={"verb": "وضّح", "quality": "poor"},
        )
        assert response.status_code == 200
        data = response.json()
        assert data["points"] == 3

    async def test_check_badges(self, client: AsyncClient, auth_headers: dict):
        response = await client.get("/api/phase4/check-badges", headers=auth_headers)
        assert response.status_code == 200
        data = response.json()
        assert "badges" in data
