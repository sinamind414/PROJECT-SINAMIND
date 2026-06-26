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

    async def test_mystery_box_create_available_open_flow(self, client: AsyncClient, auth_headers: dict):
        create_response = await client.post("/api/mystery-box/create?rarity=rare", headers=auth_headers)
        assert create_response.status_code == 200
        created = create_response.json()
        assert created["id"]
        assert created["rarity"] == "rare"
        assert created["opened"] is False

        available_response = await client.get("/api/mystery-box/available", headers=auth_headers)
        assert available_response.status_code == 200
        boxes = available_response.json()["boxes"]
        assert any(box["id"] == created["id"] for box in boxes)

        open_response = await client.post(
            "/api/mystery-box/open",
            headers=auth_headers,
            json={"box_id": created["id"]},
        )
        assert open_response.status_code == 200
        reward = open_response.json()
        assert reward["box_id"] == created["id"]
        assert reward["rarity"] == "rare"
        assert "type" in reward
        assert "value" in reward

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
