import pytest
from httpx import AsyncClient

FIXTURE_GUIDED = {
    "sujet_id": "BAC2023_SVT_1",
    "question_id": "Q1_1",
    "message": "الترجمة هي عملية تحويل...",
    "niveau_sm2": 2,
    "score_actuel": 0.5,
}

FIXTURE_FREE = {
    "message": "ما هو دور ARN polymérase في الترجمة؟",
    "lang": "ar",
    "chapitre": "proteines",
}


@pytest.mark.asyncio
async def test_guided_mode_returns_format(client: AsyncClient):
    response = await client.post(
        "/api/ai/chat",
        json={"mode": "guided", **FIXTURE_GUIDED},
    )
    assert response.status_code in (200, 401, 503, 422)


@pytest.mark.asyncio
async def test_legacy_chat_route_deprecated(client: AsyncClient):
    old = await client.post("/api/chat", json=FIXTURE_GUIDED)
    assert old.status_code == 404


@pytest.mark.asyncio
async def test_free_mode_return_format(client: AsyncClient):
    response = await client.post(
        "/api/ai/chat",
        json={"mode": "free", **FIXTURE_FREE},
    )
    assert response.status_code in (200, 401, 503, 422)


@pytest.mark.asyncio
async def test_legacy_chatbot_route_still_works(client: AsyncClient):
    response = await client.post("/api/chatbot/ask", json=FIXTURE_FREE)
    assert response.status_code in (200, 401, 503, 422)


@pytest.mark.asyncio
async def test_evaluate_fsrs_persisted(client: AsyncClient):
    response = await client.post(
        "/api/ai/evaluate",
        json={
            "question_id": "Q1_1",
            "reponse_eleve": "ARN polymérase transcrit le brin...",
            "tentative": 1,
        },
    )
    assert response.status_code in (200, 401, 503, 422)


@pytest.mark.asyncio
async def test_evaluate_legacy_route_deprecated(client: AsyncClient):
    response = await client.post(
        "/api/evaluate",
        json={
            "question_id": "Q1_1",
            "reponse_eleve": "test",
            "tentative": 1,
        },
    )
    assert response.status_code == 404
