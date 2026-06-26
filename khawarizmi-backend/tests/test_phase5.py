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

    async def test_user_search_contract(self, client: AsyncClient, auth_headers: dict):
        response = await client.get("/api/phase5/users/search?q=eleve", headers=auth_headers)
        assert response.status_code == 200
        data = response.json()
        assert "users" in data
        assert isinstance(data["users"], list)

    async def test_friends_list(self, client: AsyncClient, auth_headers: dict):
        response = await client.get("/api/phase5/friends", headers=auth_headers)
        assert response.status_code == 200
        data = response.json()
        assert "friends" in data
        assert isinstance(data["friends"], list)

    async def test_strict_friend_request_to_user_contract(self, client: AsyncClient, auth_headers: dict):
        response = await client.post("/api/phase5/friend-requests/user/2", headers=auth_headers)
        assert response.status_code == 200
        data = response.json()
        assert "request_id" in data
        assert data["friend_user_id"] == 2
        assert data["status"] == "pending"

    async def test_friend_request_flow_contract(self, client: AsyncClient, auth_headers: dict):
        create_response = await client.post("/api/phase5/friend-requests/friend_abc", headers=auth_headers)
        assert create_response.status_code == 200
        created = create_response.json()
        assert "request_id" in created
        assert created["status"] == "pending"

        list_response = await client.get("/api/phase5/friend-requests", headers=auth_headers)
        assert list_response.status_code == 200
        assert "requests" in list_response.json()

        respond_response = await client.post(
            f"/api/phase5/friend-requests/{created['request_id']}/respond",
            headers=auth_headers,
            json={"accept": True},
        )
        assert respond_response.status_code == 200
        assert respond_response.json()["status"] == "accepted"

    async def test_strict_challenge_to_user_contract(self, client: AsyncClient, auth_headers: dict):
        response = await client.post("/api/phase5/challenge/user/2", headers=auth_headers)
        assert response.status_code == 200
        data = response.json()
        assert "challenge_id" in data
        assert data["friend_user_id"] == 2
        assert data["status"] == "pending"

    async def test_challenge_result_scoring_contract(self, client: AsyncClient, auth_headers: dict):
        challenge_response = await client.post("/api/phase5/challenge/friend_abc", headers=auth_headers)
        challenge_id = challenge_response.json()["challenge_id"]

        result_response = await client.post(
            f"/api/phase5/challenge/{challenge_id}/result",
            headers=auth_headers,
            json={"score": 120, "correct_answers": 8, "total_questions": 10, "duration_seconds": 240},
        )
        assert result_response.status_code == 200
        result = result_response.json()
        assert result["challenge_id"] == challenge_id
        assert result["points_awarded"] >= 120
        assert result["status"] == "completed"

        results_response = await client.get(f"/api/phase5/challenge/{challenge_id}/results", headers=auth_headers)
        assert results_response.status_code == 200
        assert "results" in results_response.json()
