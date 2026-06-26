# tests/test_chatbot.py
# Tests du chatbot v2 (RAG hybride + sources + engagement)

from unittest.mock import AsyncMock, MagicMock

from httpx import AsyncClient


class TestChatbotHealth:
    async def test_health_no_auth(self, client: AsyncClient):
        response = await client.get("/api/chatbot/health")
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "ok"
        assert data["service"] == "chatbot-v2"


class TestChatbotAsk:
    async def test_ask_requires_auth(self, client: AsyncClient):
        response = await client.post("/api/chatbot/ask", json={"message": "test"})
        assert response.status_code in [401, 503]

    async def test_ask_empty_message(self, client: AsyncClient, auth_headers: dict):
        response = await client.post(
            "/api/chatbot/ask", headers=auth_headers, json={"message": ""}
        )
        assert response.status_code == 400

    async def test_chatbot_fallback_when_no_ai(self, client: AsyncClient, auth_headers: dict):
        """Sans IA configurée, le chatbot doit répondre en fallback avec cartes."""
        response = await client.post(
            "/api/chatbot/ask",
            headers=auth_headers,
            json={"message": "اشرح لي تركيب البروتين", "mode": "tutor"},
        )
        assert response.status_code == 200
        data = response.json()
        assert "response" in data
        assert data.get("fallback_active") is True
        assert "cartes" in data
        assert isinstance(data["cartes"], list)
        assert data["lang"] == "ar"
        assert "sources" in data

    async def test_chatbot_returns_sources_in_fallback(self, client: AsyncClient, auth_headers: dict, monkeypatch):
        """Vérifie que /api/chatbot/ask retourne des sources RAG même en fallback."""
        from routes import chatbot

        async def fake_rag(db, message, chapter=None, limit=3):
            return [{
                "content": "La synthèse des protéines comprend transcription puis traduction.",
                "source": "manuel_svt",
                "chapter": "proteines",
                "retrieval": "hybrid",
                "score_rerank": 0.92,
            }]

        monkeypatch.setattr(chatbot, "_rag_search", fake_rag)

        response = await client.post(
            "/api/chatbot/ask",
            headers=auth_headers,
            json={"message": "اشرح تركيب البروتين", "chapitre": "proteines"},
        )
        assert response.status_code == 200
        data = response.json()
        assert data.get("fallback_active") is True
        assert "sources" in data
        assert isinstance(data["sources"], list)
        assert len(data["sources"]) > 0
        assert data["sources"][0]["source"] == "manuel_svt"

    async def test_chatbot_empty_rag_returns_empty_sources(self, client: AsyncClient, auth_headers: dict, monkeypatch):
        """Vérifie que sources est vide quand le RAG ne trouve rien."""
        from routes import chatbot

        async def fake_rag(db, message, chapter=None, limit=3):
            return []

        monkeypatch.setattr(chatbot, "_rag_search", fake_rag)

        response = await client.post(
            "/api/chatbot/ask",
            headers=auth_headers,
            json={"message": "question quelconque", "lang": "ar"},
        )
        assert response.status_code == 200
        data = response.json()
        assert data.get("fallback_active") is True
        assert "sources" in data
        assert data["sources"] == []

    async def test_chatbot_source_rag_field(self, client: AsyncClient, auth_headers: dict, monkeypatch):
        """Vérifie que source_rag est la source du premier chunk."""
        from routes import chatbot

        async def fake_rag(db, message, chapter=None, limit=3):
            return [{
                "content": "Contenu genetique",
                "source": "annales_bac_2024",
                "chapter": "genetique",
                "retrieval": "vector",
                "score_rerank": 0.85,
            }]

        monkeypatch.setattr(chatbot, "_rag_search", fake_rag)

        response = await client.post(
            "/api/chatbot/ask",
            headers=auth_headers,
            json={"message": "génétique", "lang": "ar", "chapitre": "genetique"},
        )
        assert response.status_code == 200
        data = response.json()
        assert "source_rag" in data
        assert data["source_rag"] == "annales_bac_2024"

    async def test_chatbot_response_contains_cartes(self, client: AsyncClient, auth_headers: dict):
        """Vérifie que la réponse contient des cartes d'orientation."""
        response = await client.post(
            "/api/chatbot/ask",
            headers=auth_headers,
            json={"message": "ما هي الخلايا", "lang": "ar"},
        )
        assert response.status_code == 200
        data = response.json()
        assert "response" in data
        assert "cartes" in data
        assert isinstance(data["cartes"], list)

    async def test_merge_chunks_deduplicates(self):
        """Vérifie que _merge_chunks déduplique et marque hybrid."""
        from routes.chatbot import _merge_chunks

        vector = [
            {"content": "Chunk A content here", "source": "manuel", "chapter": "ch1", "retrieval": "vector"},
            {"content": "Chunk B content here", "source": "manuel", "chapter": "ch2", "retrieval": "vector"},
        ]
        keyword = [
            {"content": "Chunk A content here", "source": "manuel", "chapter": "ch1", "retrieval": "keyword"},
            {"content": "Chunk C content here", "source": "annales", "chapter": "ch3", "retrieval": "keyword"},
        ]

        merged = _merge_chunks(vector, keyword)

        assert len(merged) == 3
        chunk_a = next(c for c in merged if "Chunk A" in c["content"])
        assert chunk_a["retrieval"] == "hybrid"
        chunk_b = next(c for c in merged if "Chunk B" in c["content"])
        assert chunk_b["retrieval"] == "vector"
        chunk_c = next(c for c in merged if "Chunk C" in c["content"])
        assert chunk_c["retrieval"] == "keyword"

    async def test_source_cards_deduplicates(self):
        """Vérifie que _source_cards déduplique par (source, chapter)."""
        from routes.chatbot import _source_cards

        chunks = [
            {"content": "Content 1", "source": "manuel", "chapter": "ch1"},
            {"content": "Content 2", "source": "manuel", "chapter": "ch1"},
            {"content": "Content 3", "source": "manuel", "chapter": "ch2"},
        ]
        cards = _source_cards(chunks)
        assert len(cards) == 2
        assert cards[0]["chapter"] == "ch1"
        assert cards[1]["chapter"] == "ch2"


class TestChatbotEngagement:
    async def test_state_requires_auth(self, client: AsyncClient):
        response = await client.get("/api/chatbot/state")
        assert response.status_code in [401, 503]

    async def test_chatbot_state_feedback_and_daily_mission_contract(
        self, client: AsyncClient, auth_headers: dict, monkeypatch
    ):
        """Vérifie que les 3 endpoints engagement fonctionnent ensemble (mock RAG + get_openai)."""
        from routes import chatbot

        async def fake_rag(db, message, chapter=None, limit=3):
            return []

        monkeypatch.setattr(chatbot, "_rag_search", fake_rag)

        # 1. GET /state
        resp = await client.get("/api/chatbot/state", headers=auth_headers)
        assert resp.status_code == 200
        data = resp.json()
        assert "status" in data or "memory" in data

        # 2. POST /feedback
        resp2 = await client.post(
            "/api/chatbot/feedback",
            headers=auth_headers,
            json={"feedback": "confused"},
        )
        assert resp2.status_code == 200
        data2 = resp2.json()
        assert data2["status"] == "ok"

        # 3. POST /daily-mission/complete
        resp3 = await client.post(
            "/api/chatbot/daily-mission/complete",
            headers=auth_headers,
            json={"mission_id": 1},
        )
        assert resp3.status_code == 200


class TestChatbotAdvanced:
    async def test_confusion_detector_contract(self, client: AsyncClient, auth_headers: dict):
        """Vérifie que /api/chatbot/confusion/detect retourne une structure valide."""
        resp = await client.post(
            "/api/chatbot/confusion/detect",
            headers=auth_headers,
            json={"text": "لم أفهم لماذا تحدث الترجمة في الريبوزوم", "feedback_type": "confused"},
        )
        assert resp.status_code == 200
        data = resp.json()
        assert "concept" in data
        assert "confusion_type" in data
        assert "strategy" in data
        assert data["confusion_type"] in ("vocabulary", "mechanism", "cause_effect", "methodology", "prerequisite", "general")
        assert isinstance(data.get("scores", {}), dict)

    async def test_confusion_detector_empty_text(self, client: AsyncClient, auth_headers: dict):
        """Vérifie que confusion/detect valide le champ text."""
        resp = await client.post(
            "/api/chatbot/confusion/detect",
            headers=auth_headers,
            json={"text": ""},
        )
        assert resp.status_code == 400

    async def test_explain_back_contract(self, client: AsyncClient, auth_headers: dict, monkeypatch):
        """Vérifie que /api/chatbot/explain-back retourne un score."""
        resp = await client.post(
            "/api/chatbot/explain-back",
            headers=auth_headers,
            json={
                "concept": "traduction",
                "answer": "الترجمة تتم في الريبوزوم حيث يتم تركيب البروتين باستعمال الرامزات.",
            },
        )
        assert resp.status_code == 200
        data = resp.json()
        assert "clarity_score" in data
        assert "scientific_terms_score" in data
        assert "structure_score" in data
        assert "total_score" in data
        assert "feedback" in data
        assert isinstance(data["total_score"], (int, float))

    async def test_boss_fight_contract(self, client: AsyncClient, auth_headers: dict):
        """Vérifie le cycle complet start → submit d'un boss fight."""
        start = await client.post(
            "/api/chatbot/boss-fight/start",
            headers=auth_headers,
            json={"chapter": "synthese_proteines"},
        )
        assert start.status_code == 200
        start_data = start.json()
        assert "boss_fight_id" in start_data
        assert start_data["status"] == "started"

        bf_id = start_data["boss_fight_id"]
        submit = await client.post(
            f"/api/chatbot/boss-fight/{bf_id}/submit",
            headers=auth_headers,
            json={"answers": {"q1": "réponse 1", "q2": "réponse 2", "q3": "réponse 3"}},
        )
        assert submit.status_code == 200
        submit_data = submit.json()
        assert submit_data["status"] == "completed"
        assert isinstance(submit_data["score"], (int, float))
        assert isinstance(submit_data["passed"], bool)

    async def test_chatbot_mystery_box_contract(self, client: AsyncClient, auth_headers: dict):
        """Vérifie que /api/chatbot/mystery-box/open retourne une récompense."""
        resp = await client.post(
            "/api/chatbot/mystery-box/open",
            headers=auth_headers,
        )
        assert resp.status_code == 200
        data = resp.json()
        assert "rarity" in data
        assert "reward_type" in data
        assert data["rarity"] in ("common", "rare", "epic", "legendary")
        assert data["reward_type"] in ("points", "mission_boost", "boss_hint", "badge")
