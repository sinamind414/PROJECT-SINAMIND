from httpx import AsyncClient


class TestGamificationPhase0:
    async def test_streak_update(self, client: AsyncClient, auth_headers: dict):
        response = await client.post("/api/gamification/streak/update", headers=auth_headers)
        assert response.status_code == 200
        assert "current_streak" in response.json()

    async def test_add_points(self, client: AsyncClient, auth_headers: dict):
        response = await client.post("/api/gamification/points/add?points=100", headers=auth_headers)
        assert response.status_code == 200

    async def test_avatar_xp(self, client: AsyncClient, auth_headers: dict):
        response = await client.post("/api/avatar/add-xp?xp=150", headers=auth_headers)
        assert response.status_code == 200

    async def test_get_avatar(self, client: AsyncClient, auth_headers: dict):
        response = await client.get("/api/avatar/", headers=auth_headers)
        assert response.status_code == 200

    async def test_open_mystery_box(self, client: AsyncClient, auth_headers: dict):
        response = await client.post(
            "/api/mystery-box/open", headers=auth_headers, json={"box_id": "test"}
        )
        assert response.status_code in [200, 404]

    async def test_create_mystery_box(self, client: AsyncClient, auth_headers: dict):
        response = await client.post(
            "/api/mystery-box/create?rarity=common", headers=auth_headers
        )
        assert response.status_code == 200

    async def test_available_boxes(self, client: AsyncClient, auth_headers: dict):
        response = await client.get("/api/mystery-box/available", headers=auth_headers)
        assert response.status_code == 200

    async def test_get_streak(self, client: AsyncClient, auth_headers: dict):
        response = await client.get("/api/gamification/streak", headers=auth_headers)
        assert response.status_code == 200
