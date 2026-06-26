from httpx import AsyncClient


class TestGamification:
    async def test_update_streak_requires_auth(self, client: AsyncClient):
        response = await client.post("/api/gamification/streak/update")
        assert response.status_code in [401, 503]

    async def test_update_streak_authenticated(self, client: AsyncClient, auth_headers: dict):
        response = await client.post("/api/gamification/streak/update", headers=auth_headers)
        assert response.status_code == 200
        data = response.json()
        assert "current_streak" in data
        assert "updated" in data

    async def test_get_streak(self, client: AsyncClient, auth_headers: dict):
        response = await client.get("/api/gamification/streak", headers=auth_headers)
        assert response.status_code == 200
        data = response.json()
        assert "current_streak" in data
        assert "longest_streak" in data

    async def test_add_points(self, client: AsyncClient, auth_headers: dict):
        response = await client.post("/api/gamification/points/add?points=50", headers=auth_headers)
        assert response.status_code == 200
        data = response.json()
        assert "total_points" in data

    async def test_open_mystery_box_requires_auth(self, client: AsyncClient):
        response = await client.post("/api/mystery-box/open", json={"box_id": "test"})
        assert response.status_code in [401, 503]

    async def test_open_mystery_box(self, client: AsyncClient, auth_headers: dict):
        response = await client.post("/api/mystery-box/open", headers=auth_headers, json={"box_id": "test"})
        assert response.status_code in [200, 404]

    async def test_avatar_add_xp(self, client: AsyncClient, auth_headers: dict):
        response = await client.post("/api/avatar/add-xp?xp=100", headers=auth_headers)
        assert response.status_code == 200
        data = response.json()
        assert "level" in data
        assert "xp" in data
        assert "leveled_up" in data

    async def test_get_avatar(self, client: AsyncClient, auth_headers: dict):
        response = await client.get("/api/avatar/", headers=auth_headers)
        assert response.status_code == 200
        data = response.json()
        assert "level" in data
        assert "xp" in data
