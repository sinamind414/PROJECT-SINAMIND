from httpx import AsyncClient


class TestPhase5:
    async def test_live_stats(self, client: AsyncClient, auth_headers: dict):
        response = await client.get("/api/phase5/live-stats/proteines", headers=auth_headers)
        assert response.status_code == 200
        data = response.json()
        assert "active_students" in data
        assert "top_3" in data

    async def test_friends_activity(self, client: AsyncClient, auth_headers: dict):
        response = await client.get("/api/phase5/friends-activity", headers=auth_headers)
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)

    async def test_create_challenge(self, client: AsyncClient, auth_headers: dict):
        response = await client.post("/api/phase5/challenge/friend_abc", headers=auth_headers)
        assert response.status_code == 200
        data = response.json()
        assert "challenge_id" in data
        assert data["status"] == "pending"
