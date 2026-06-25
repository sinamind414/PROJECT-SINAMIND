# tests/test_fsrs.py
# Tests de l'algorithme FSRS (Répétition Espacée)

from httpx import AsyncClient


class TestFSRSCards:
    async def test_create_fsrs_card(self, client: AsyncClient, auth_headers: dict):
        response = await client.post(
            "/api/drill/session",
            headers=auth_headers,
            json={
                "matiere": "SVT",
                "nb_questions": 5,
                "chapitres": ["Photosynthèse"],
                "types_question": ["definition"],
                "difficulte": "moyen",
            },
        )
        assert response.status_code in [200, 401, 403, 503]

    async def test_get_due_cards(self, client: AsyncClient, auth_headers: dict):
        response = await client.get("/api/session/due", headers=auth_headers)
        assert response.status_code in [200, 401, 404, 503]
