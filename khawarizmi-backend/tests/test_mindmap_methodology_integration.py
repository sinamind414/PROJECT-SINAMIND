from unittest.mock import AsyncMock, patch

from httpx import AsyncClient


class TestMindMapMethodologyIntegration:
    async def test_generate_methodological_requires_auth(self, client: AsyncClient):
        response = await client.post(
            "/api/mindmap/generate-methodological",
            json={"matiere": "SVT", "chapitre": "Protéines", "filiere": "Sciences"},
        )
        assert response.status_code in [401, 503]

    @patch("services.mindmap_service.generate_mindmap")
    async def test_enrich_mindmap_with_methodology(
        self, mock_generate: AsyncMock, client: AsyncClient, auth_headers: dict
    ):
        mock_generate.return_value = {
            "status": "success",
            "mindmap": {
                "titre": "Protéines",
                "racine": {
                    "id": "root",
                    "label": "Protéines",
                    "enfants": [
                        {"id": "n1", "label": "وضّح في نص علمي", "enfants": []},
                    ],
                },
            },
        }
        response = await client.post(
            "/api/mindmap/generate-methodological",
            headers=auth_headers,
            json={"matiere": "SVT", "chapitre": "Protéines", "filiere": "Sciences"},
        )
        assert response.status_code == 200
        data = response.json()
        assert "methodology" in data.get("mindmap", {})
        assert "verbes_detectes" in data["mindmap"]["methodology"]

    async def test_award_points_structure(self):
        from services.mindmap_methodology_service import award_mindmap_methodology_points

        mindmap_data = {
            "methodology": {
                "verbes_detectes": ["وضّح في نص علمي", "أثبت"],
            },
        }
        result = await award_mindmap_methodology_points(1, mindmap_data, None)
        assert result["points"] > 0
        assert "verbes méthodologiques" in result["message"]
