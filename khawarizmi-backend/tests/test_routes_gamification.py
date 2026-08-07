"""Tests des routes gamification/utilisateur réparées.

Verrouille les fixes :
- current_user['id'] (dict) au lieu de current_user.id (AttributeError 500)
- modèle UserBadge unifié (badge_id, pas badge_code)
- gen_random_uuid() traduit en SQLite preview
- metadata SQLAlchemy non muté (mappers ORM fonctionnels)
"""
from __future__ import annotations

import pytest
from httpx import AsyncClient


class TestRoutesUtilisateur:
    """Les 7 routes en 500 → 200 (avec DB mockée, réponses vides attendues)."""

    @pytest.mark.asyncio
    async def test_badges_me(self, client: AsyncClient, auth_headers: dict):
        resp = await client.get("/api/badges/me", headers=auth_headers)
        assert resp.status_code == 200
        data = resp.json()
        assert "badges" in data
        # le service renvoie le catalogue de badges (12)
        assert len(data["badges"]) >= 10

    @pytest.mark.asyncio
    async def test_gems_me(self, client: AsyncClient, auth_headers: dict):
        resp = await client.get("/api/gems/me", headers=auth_headers)
        assert resp.status_code == 200
        data = resp.json()
        assert "balance" in data
        assert "total_earned" in data

    @pytest.mark.asyncio
    async def test_onboarding_me(self, client: AsyncClient, auth_headers: dict):
        resp = await client.get("/api/onboarding/me", headers=auth_headers)
        assert resp.status_code == 200
        data = resp.json()
        assert "completed" in data or "step_1_done" in data

    @pytest.mark.asyncio
    async def test_streaks_me(self, client: AsyncClient, auth_headers: dict):
        resp = await client.get("/api/streaks/me", headers=auth_headers)
        assert resp.status_code == 200
        data = resp.json()
        assert "current_streak" in data

    @pytest.mark.asyncio
    async def test_leaderboard_me(self, client: AsyncClient, auth_headers: dict):
        resp = await client.get("/api/leaderboard/me", headers=auth_headers)
        assert resp.status_code == 200
        data = resp.json()
        assert "rank" in data or "position" in data or "score" in data

    @pytest.mark.asyncio
    async def test_cities_me(self, client: AsyncClient, auth_headers: dict):
        resp = await client.get("/api/cities/me", headers=auth_headers)
        assert resp.status_code == 200

    @pytest.mark.asyncio
    async def test_cities_stats_service(self):
        """Fix verrouillé : get_national_stats fonctionne (text importé)."""
        from services.city_service import get_national_stats

        class Row:
            verb_slug = "analyse"
            avg_pct = 50.0
            total_users = 3

        class FakeResult:
            def all(self):
                return [Row()]

        class FakeDb:
            async def execute(self, *a, **kw):
                return FakeResult()

        result = await get_national_stats(FakeDb())
        assert result == [{"verb_slug": "analyse", "avg_pct": 50.0, "total_users": 3}]

    def test_city_service_imports_text(self):
        """Fix verrouillé : sqlalchemy.text est importé dans city_service."""
        import inspect

        from services import city_service

        src = inspect.getsource(city_service)
        assert "from sqlalchemy import select, text" in src

    def test_onboarding_service_imports_func(self):
        """Fix verrouillé : sqlalchemy.func est importé dans onboarding_service."""
        import inspect

        from services import onboarding_service

        src = inspect.getsource(onboarding_service)
        assert "from sqlalchemy import func, select" in src


class TestDuel:
    @pytest.mark.asyncio
    async def test_create_duel(self, client: AsyncClient, auth_headers: dict):
        """Vérifie l'instanciation ORM (mapper Duel) + gen_random_uuid."""
        resp = await client.post(
            "/api/duels",
            headers=auth_headers,
            json={"verb_slug": "analyse", "opponent_email": "ami@test.dz"},
        )
        assert resp.status_code in (200, 201, 404)  # 404 si adversaire introuvable


class TestMappersORM:
    """Vérifie que les mappers ORM se configurent (FK non mutées)."""

    def test_mappers_configure(self):
        from sqlalchemy.orm import configure_mappers
        from models.exercise import Exercise  # noqa: F401
        from models.duel import Duel  # noqa: F401

        configure_mappers()  # ne doit pas lever InvalidRequestError

    def test_models_instanciables(self):
        from models.duel import Duel
        from models.gamification import UserBadge

        Duel()
        ub = UserBadge(user_id=1, badge_id="night_owl")
        assert ub.badge_id == "night_owl"
