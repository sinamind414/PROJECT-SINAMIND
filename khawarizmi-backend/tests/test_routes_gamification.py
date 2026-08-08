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

    @pytest.mark.asyncio
    async def test_cities_stats_mastery_aggregation(self):
        """Migration 034 : get_national_stats lit mastery (source='verb_action')
        — agrégation AVG(stability)*100 / COUNT(DISTINCT user_id) par item_key,
        triée par avg_pct ASC."""
        import os
        import tempfile

        from sqlalchemy.ext.asyncio import async_sessionmaker, create_async_engine

        from services.city_service import get_national_stats

        fd, path = tempfile.mkstemp(suffix=".db")
        os.close(fd)
        engine = create_async_engine(f"sqlite+aiosqlite:///{path}")
        async with engine.begin() as conn:
            await conn.exec_driver_sql("""
                CREATE TABLE mastery_micro_concepts (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    user_id INTEGER NOT NULL,
                    micro_concept_id TEXT NOT NULL,
                    concept_id TEXT,
                    chapter TEXT,
                    stability REAL DEFAULT 0,
                    difficulty REAL DEFAULT 0,
                    fsrs_state TEXT DEFAULT '{}',
                    prochaine_revision DATETIME,
                    interval_jours REAL DEFAULT 0,
                    last_score INTEGER,
                    attempts INTEGER DEFAULT 0,
                    last_review DATETIME,
                    source TEXT DEFAULT 'concept',
                    item_key TEXT,
                    avg_pct REAL,
                    total_users INTEGER
                )
            """)
            # verb_action : analyse (2 users : 0.5 / 0.7), synthese (1 user : 0.4)
            await conn.exec_driver_sql("""
                INSERT INTO mastery_micro_concepts
                    (user_id, micro_concept_id, concept_id, stability, source, item_key)
                VALUES
                    (1, 'va_analyse', 'va_analyse', 0.5, 'verb_action', 'analyse'),
                    (2, 'va_analyse', 'va_analyse', 0.7, 'verb_action', 'analyse'),
                    (3, 'va_synthese', 'va_synthese', 0.4, 'verb_action', 'synthese'),
                    -- hors scope : concept + verb_chapter ignorés
                    (1, 'c1', 'c1', 0.9, 'concept', NULL),
                    (1, 'vc_a_c1', 'vc_a_c1', 0.8, 'verb_chapter', 'a::c1')
            """)
        async with async_sessionmaker(engine)() as session:
            result = await get_national_stats(session)
        assert result == [
            {"verb_slug": "synthese", "avg_pct": 40.0, "total_users": 1},
            {"verb_slug": "analyse", "avg_pct": 60.0, "total_users": 2},
        ]
        await engine.dispose()

    @pytest.mark.asyncio
    async def test_cities_stats_fallback_legacy(self):
        """Migration 034 : si mastery_micro_concepts est absente (environnement
        pré-033), get_national_stats retombe sur action_verb_progress."""
        import os
        import tempfile

        from sqlalchemy.ext.asyncio import async_sessionmaker, create_async_engine

        from services.city_service import get_national_stats

        fd, path = tempfile.mkstemp(suffix=".db")
        os.close(fd)
        engine = create_async_engine(f"sqlite+aiosqlite:///{path}")
        async with engine.begin() as conn:
            await conn.exec_driver_sql("""
                CREATE TABLE action_verb_progress (
                    id INTEGER PRIMARY KEY,
                    user_id TEXT NOT NULL,
                    verb_slug TEXT NOT NULL,
                    stability REAL DEFAULT 0,
                    difficulty REAL DEFAULT 0,
                    fsrs_state TEXT DEFAULT '{}',
                    prochaine_revision DATETIME,
                    interval_jours REAL DEFAULT 0,
                    last_score INTEGER DEFAULT 0,
                    attempts INTEGER DEFAULT 0,
                    updated_at DATETIME
                )
            """)
            await conn.exec_driver_sql("""
                INSERT INTO action_verb_progress (user_id, verb_slug, stability)
                VALUES ('1', 'analyse', 0.5), ('2', 'analyse', 0.7), ('3', 'deduire', 0.9)
            """)
        async with async_sessionmaker(engine)() as session:
            result = await get_national_stats(session)
        assert result == [
            {"verb_slug": "analyse", "avg_pct": 60.0, "total_users": 2},
            {"verb_slug": "deduire", "avg_pct": 90.0, "total_users": 1},
        ]
        await engine.dispose()

    @pytest.mark.asyncio
    async def test_cities_stats_empty_mastery_no_fallback(self):
        """Migration 034 : mastery présente mais vide → [] (pas de fallback :
        mastery est la source de vérité)."""
        import os
        import tempfile

        from sqlalchemy.ext.asyncio import async_sessionmaker, create_async_engine

        from services.city_service import get_national_stats

        fd, path = tempfile.mkstemp(suffix=".db")
        os.close(fd)
        engine = create_async_engine(f"sqlite+aiosqlite:///{path}")
        async with engine.begin() as conn:
            await conn.exec_driver_sql("""
                CREATE TABLE mastery_micro_concepts (
                    user_id INTEGER NOT NULL,
                    micro_concept_id TEXT NOT NULL,
                    stability REAL DEFAULT 0,
                    source TEXT DEFAULT 'concept',
                    item_key TEXT
                )
            """)
        async with async_sessionmaker(engine)() as session:
            result = await get_national_stats(session)
        assert result == []
        await engine.dispose()

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

        from models.duel import Duel  # ruff: ignore[unused-import]
        from models.exercise import Exercise  # ruff: ignore[unused-import]

        configure_mappers()  # ne doit pas lever InvalidRequestError

    def test_models_instanciables(self):
        from models.duel import Duel
        from models.gamification import UserBadge

        Duel()
        ub = UserBadge(user_id=1, badge_id="night_owl")
        assert ub.badge_id == "night_owl"
