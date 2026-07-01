import pytest
from httpx import AsyncClient


class TestPhase2Social:
    @pytest.mark.xfail(reason="Routes phase2 retirées (doublons): non enregistrées dans ALL_ROUTERS")
    async def test_open_mystery_box_v2(self, client: AsyncClient, auth_headers: dict):
        response = await client.post(
            "/api/phase2/mystery-box/open",
            headers=auth_headers,
            json={"box_id": "test"},
        )
        assert response.status_code == 200
        data = response.json()
        assert "rarity" in data
        assert "reward" in data
        assert data["rarity"] in ("common", "rare", "epic", "legendary")

    @pytest.mark.xfail(reason="Routes phase2 retirées (doublons): non enregistrées dans ALL_ROUTERS")
    async def test_social_stats(self, client: AsyncClient, auth_headers: dict):
        response = await client.get(
            "/api/phase2/social-stats/proteines",
            headers=auth_headers,
        )
        assert response.status_code == 200
        data = response.json()
        assert "active_users_today" in data
        assert "completed_today" in data
        assert "top_player" in data


class TestBadges:
    async def test_badges_list(self, client: AsyncClient, auth_headers: dict):
        response = await client.get(
            "/api/badges",
            headers=auth_headers,
        )
        assert response.status_code in [200, 404]
