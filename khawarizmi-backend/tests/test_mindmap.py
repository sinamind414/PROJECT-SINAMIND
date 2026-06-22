# tests/test_mindmap.py
# Tests du Mind Map JSON Dynamique (Pilier 4)

import pytest
import json
from unittest.mock import AsyncMock, patch, MagicMock
from httpx import AsyncClient

from main import app
from deps import get_db, get_openai
from tests.conftest import MockAsyncExecResult

VALID_REQUEST = {
    "matiere": "SVT",
    "chapitre": "Transcription ADN",
    "filiere": "Sciences Naturelles",
    "niveau_detail": "standard"
}


class MockRAGRow:
    def __init__(self, content, source):
        self.content = content
        self.source = source
        self._data = {"content": content, "source": source}

    def __getitem__(self, key):
        return self._data[key]

    def _mapping(self):
        return self._data


class TestMindMapAuth:
    async def test_generate_requires_auth(self, client: AsyncClient):
        response = await client.post(
            "/api/mindmap/generate",
            json=VALID_REQUEST
        )
        assert response.status_code in [401, 503]


class TestMindMapMaitrise:
    async def test_update_maitrise_invalid_value(
        self,
        client: AsyncClient,
        auth_headers: dict
    ):
        response = await client.patch(
            "/api/mindmap/fake-node/maitrise",
            headers=auth_headers,
            json={"maitrise": 5}
        )
        assert response.status_code in [400, 401, 422, 503]


class TestMindMapDynamicGeneration:
    async def test_generate_no_context(self, client: AsyncClient, auth_headers: dict):
        # Test async : la génération retourne pending (non-bloquant)
        class MockSessionRAGEmpty:
            async def __aenter__(self): return self
            async def __aexit__(self, *args): pass
            async def execute(self, statement, *args, **kwargs):
                sql = str(statement)
                if "users" in sql:
                    mock_res = MagicMock()
                    mock_res.fetchone.return_value = (1, "eleve@bac.dz", "Test", "free", "Sciences")
                    return mock_res
                if "mindmap_tasks" in sql:
                    mock_res = MagicMock()
                    mock_res.fetchone.return_value = None
                    return mock_res
                if "SELECT data FROM mindmaps" in sql:
                    mock_res = MagicMock()
                    mock_res.fetchone.return_value = None
                    return mock_res
                return MockAsyncExecResult([])
            async def commit(self): pass
            async def rollback(self): pass
            async def close(self): pass

        async def override_get_db_empty():
            yield MockSessionRAGEmpty()

        app.dependency_overrides[get_db] = override_get_db_empty

        mock_openai = MagicMock()
        async def override_get_openai():
            return mock_openai
        app.dependency_overrides[get_openai] = override_get_openai

        # Empêcher la tâche d'arrière-plan de se connecter à PostgreSQL
        with patch("services.embedder.embedder.encode") as mock_encode, \
             patch("routes.mindmap.run_generation_background", new_callable=AsyncMock):
            import numpy as np
            mock_encode.return_value = np.zeros((1, 384))

            response = await client.post(
                "/api/mindmap/generate",
                headers=auth_headers,
                json=VALID_REQUEST
            )

            # Le nouveau flux async retourne pending avec un task_id
            assert response.status_code == 200
            data = response.json()
            assert data["status"] == "pending"
            assert "task_id" in data

    async def test_generate_success(self, client: AsyncClient, auth_headers: dict):
        # Test async : la génération retourne pending (non-bloquant)
        class MockSessionRAGSuccess:
            def __init__(self):
                self.committed = False

            async def __aenter__(self): return self
            async def __aexit__(self, *args): pass
            async def execute(self, statement, *args, **kwargs):
                sql = str(statement)
                if "users" in sql:
                    mock_res = MagicMock()
                    mock_res.fetchone.return_value = (1, "eleve@bac.dz", "Test", "free", "Sciences")
                    return mock_res
                if "mindmap_tasks" in sql:
                    mock_res = MagicMock()
                    mock_res.fetchone.return_value = None
                    return mock_res
                if "SELECT data FROM mindmaps" in sql:
                    mock_res = MagicMock()
                    mock_res.fetchone.return_value = None
                    return mock_res
                return MockAsyncExecResult([])

            async def commit(self):
                self.committed = True
            async def rollback(self): pass
            async def close(self): pass

        db_session = MockSessionRAGSuccess()
        async def override_get_db_success():
            yield db_session

        app.dependency_overrides[get_db] = override_get_db_success

        mock_openai = MagicMock()
        mock_choice = MagicMock()
        mock_choice.message.content = json.dumps({
            "racine": {
                "id": "root-node-uuid",
                "label": "Transcription de l'ADN",
                "type": "processus",
                "importance": "critique",
                "bac_frequent": True,
                "flashcard_auto": True,
                "enfants": [
                    {
                        "id": "child-node-uuid",
                        "label": "ARN Polymérase",
                        "type": "concept",
                        "importance": "haute",
                        "bac_frequent": True,
                        "flashcard_auto": True,
                        "enfants": []
                    }
                ]
            },
            "liens_transversaux": []
        })
        mock_openai.chat.completions.create = AsyncMock(
            return_value=MagicMock(choices=[mock_choice])
        )

        async def override_get_openai():
            return mock_openai

        app.dependency_overrides[get_openai] = override_get_openai

        # Empêcher la tâche d'arrière-plan de se connecter à PostgreSQL
        with patch("services.embedder.embedder.encode") as mock_encode, \
             patch("routes.mindmap.run_generation_background", new_callable=AsyncMock):
            import numpy as np
            mock_encode.return_value = np.zeros((1, 384))

            response = await client.post(
                "/api/mindmap/generate",
                headers=auth_headers,
                json=VALID_REQUEST
            )

            # Le nouveau flux async retourne pending immédiatement
            assert response.status_code == 200
            data = response.json()
            assert data["status"] == "pending"
            assert "task_id" in data
            assert db_session.committed is True  # La tâche a été créée en DB
