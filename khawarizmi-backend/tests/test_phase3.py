from httpx import AsyncClient


class TestPhase3:
    async def test_avatar_details(self, client: AsyncClient, auth_headers: dict):
        response = await client.get("/api/phase3/avatar", headers=auth_headers)
        assert response.status_code == 200
        data = response.json()
        assert "level" in data
        assert "xp" in data
        assert "icon" in data

    async def test_live_stats(self, client: AsyncClient, auth_headers: dict):
        response = await client.get("/api/phase3/live-stats/proteines", headers=auth_headers)
        assert response.status_code == 200
        data = response.json()
        assert "active_users" in data
        assert "top_3" in data

    async def test_friends_activity(self, client: AsyncClient, auth_headers: dict):
        response = await client.get("/api/phase3/friends-activity", headers=auth_headers)
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
