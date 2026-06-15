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
        # On simule une base de données RAG vide
        class MockSessionRAGEmpty:
            async def __aenter__(self): return self
            async def __aexit__(self, *args): pass
            async def execute(self, statement, *args, **kwargs):
                sql = str(statement)
                if "users" in sql:
                    # Pour get_current_user
                    mock_res = MagicMock()
                    mock_res.fetchone.return_value = (1, "eleve@bac.dz", "Test", "free", "Sciences")
                    return mock_res
                # Pas de chunks
                return MockAsyncExecResult([])
            async def commit(self): pass
            async def rollback(self): pass
            async def close(self): pass

        async def override_get_db_empty():
            yield MockSessionRAGEmpty()

        app.dependency_overrides[get_db] = override_get_db_empty
        
        # Mock OpenAI to prevent 503
        mock_openai = MagicMock()
        async def override_get_openai():
            return mock_openai
        app.dependency_overrides[get_openai] = override_get_openai
        
        with patch("services.embedder.embedder.encode") as mock_encode:
            import numpy as np
            mock_encode.return_value = np.zeros((1, 384))
            
            response = await client.post(
                "/api/mindmap/generate",
                headers=auth_headers,
                json=VALID_REQUEST
            )
            
            assert response.status_code == 200
            data = response.json()
            assert data["status"] == "no_context"
            assert "Je n'ai pas trouve cette information" in data["message"]

    async def test_generate_success(self, client: AsyncClient, auth_headers: dict):
        # Simuler un chunk RAG trouvé dans la base de données
        class MockSessionRAGSuccess:
            def __init__(self):
                self.committed = False
                self.saved_mindmap = False
                
            async def __aenter__(self): return self
            async def __aexit__(self, *args): pass
            async def execute(self, statement, *args, **kwargs):
                sql = str(statement)
                params = args[0] if args else kwargs
                if "users" in sql:
                    mock_res = MagicMock()
                    mock_res.fetchone.return_value = (1, "eleve@bac.dz", "Test", "free", "Sciences")
                    return mock_res
                if "rag_chunks" in sql:
                    # Retourne un chunk valide utilisant MockRAGRow
                    mock_res = MagicMock()
                    mock_res.fetchall.return_value = [
                        MockRAGRow(
                            content="La transcription de l'ADN en ARN messager se déroule dans le noyau chez les eucaryotes.",
                            source="transcription_adn.txt"
                        )
                    ]
                    return mock_res
                if "SELECT data FROM mindmaps" in sql:
                    mock_res = MagicMock()
                    mock_res.fetchone.return_value = None
                    return mock_res
                if "INSERT INTO mindmaps" in sql:
                    self.saved_mindmap = True
                    mock_res = MagicMock()
                    mock_res.fetchone.return_value = ("test-id",)
                    return mock_res
                if "INSERT INTO mindmap_nodes" in sql:
                    mock_res = MagicMock()
                    mock_res.fetchone.return_value = ("node-id",)
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

        # Mock OpenAI / Gemini client
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

        with patch("services.embedder.embedder.encode") as mock_encode:
            import numpy as np
            mock_encode.return_value = np.zeros((1, 384))
            
            response = await client.post(
                "/api/mindmap/generate",
                headers=auth_headers,
                json=VALID_REQUEST
            )
            
            assert response.status_code == 200
            data = response.json()
            assert data["status"] == "success"
            
            # Vérifications structurelles
            mindmap = data["mindmap"]
            assert mindmap["titre"] == "TRANSCRIPTION ADN"
            assert mindmap["matiere"] == "SVT"
            assert mindmap["filiere"] == "Sciences Naturelles"
            assert mindmap["racine"]["label"] == "Transcription de l'ADN"
            assert len(mindmap["racine"]["enfants"]) == 1
            assert mindmap["racine"]["enfants"][0]["label"] == "ARN Polymérase"
            
            # Flashcards auto-générées
            assert len(data["flashcards_generees"]) >= 2
            assert data["flashcards_generees"][0]["recto"] == "Transcription de l'ADN"
            
            # Persistance DB validée
            assert db_session.saved_mindmap is True
            assert db_session.committed is True
