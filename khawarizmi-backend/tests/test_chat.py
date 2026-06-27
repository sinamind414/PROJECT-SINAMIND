# tests/test_chat.py
# Tests du tuteur IA (RAG + Piliers pédagogiques)

from httpx import AsyncClient


class TestChatRAG:
    async def test_chat_requires_auth(self, client: AsyncClient):
        response = await client.post(
            "/api/ai/chat",
            json={"mode": "free", "message": "test"},
        )
        assert response.status_code in [401, 503]

    async def test_chat_rate_limit(self, client: AsyncClient, auth_headers: dict):
        responses = []
        for _ in range(5):
            r = await client.post(
                "/api/ai/chat",
                headers=auth_headers,
                json={"mode": "free", "message": "test rate limit"},
            )
            responses.append(r.status_code)

        rate_limited = [s for s in responses if s == 429]
        assert len(rate_limited) < 2
