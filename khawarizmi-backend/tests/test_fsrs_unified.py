"""tests/test_fsrs_unified.py — Accès unifié mémoire FSRS (audit S3).

- get_user_memory consolide les 3 sources (concept, verb_chapter, verb_action)
- get_due_items filtre les items dus
- update_memory fait l'upsert dans la bonne table (lecture-écriture round-trip)
- Table absente (preview SQLite) → source vide, jamais d'erreur
- memory_summary consolide les stats
"""

from datetime import UTC, datetime, timedelta

import pytest
from sqlalchemy.ext.asyncio import async_sessionmaker, create_async_engine

from services.fsrs_unified import (
    get_concept_state,
    get_due_items,
    get_user_memory,
    memory_summary,
    save_concept_card,
    save_concept_review,
    update_memory,
)

DDL = """
CREATE TABLE mastery_micro_concepts (
    id INTEGER PRIMARY KEY,
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
    total_reviews INTEGER DEFAULT 0,
    avg_score REAL DEFAULT 0,
    streak INTEGER DEFAULT 0,
    reps INTEGER DEFAULT 0,
    lapses INTEGER DEFAULT 0,
    state INTEGER DEFAULT 0,
    due_date DATETIME,
    pending_real_evaluation BOOLEAN DEFAULT 0,
    updated_at DATETIME,
    UNIQUE(user_id, micro_concept_id)
);
CREATE TABLE da_fsrs (
    id INTEGER PRIMARY KEY,
    user_id TEXT,
    verb_slug TEXT,
    chapter_slug TEXT,
    stability REAL DEFAULT 0,
    difficulty REAL DEFAULT 0,
    fsrs_state TEXT DEFAULT '{}',
    prochaine_revision DATETIME,
    interval_jours REAL DEFAULT 0,
    last_score INTEGER DEFAULT 0,
    attempts INTEGER DEFAULT 0,
    last_review DATETIME,
    updated_at DATETIME,
    UNIQUE(user_id, verb_slug, chapter_slug)
);
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
    avg_pct REAL DEFAULT 0,
    total_users INTEGER DEFAULT 0,
    updated_at DATETIME,
    UNIQUE(user_id, verb_slug)
);
"""


@pytest.fixture
async def db():
    import os
    import tempfile

    fd, path = tempfile.mkstemp(suffix=".db")
    os.close(fd)
    engine = create_async_engine(f"sqlite+aiosqlite:///{path}")
    async with engine.begin() as conn:
        # SQLite n'accepte qu'une requête à la fois → split par CREATE
        for statement in DDL.strip().split(";"):
            if statement.strip():
                await conn.exec_driver_sql(statement.strip() + ";")
    factory = async_sessionmaker(engine, expire_on_commit=False)
    async with factory() as session:
        yield session
    await engine.dispose()
    os.unlink(path)


class TestGetUserMemory:
    @pytest.mark.asyncio
    async def test_consolidates_three_sources(self, db):
        # Écrire un item dans chaque source
        assert await update_memory(
            db, 1, "concept", item_id="transcription", chapter="ch1",
            stability=2.5, difficulty=5.0,
            fsrs_state={"stability": 2.5, "reps": 3},
        )
        assert await update_memory(
            db, 1, "verb_chapter", item_id="analyse::ch1",
            stability=1.2, last_score=75,
        )
        assert await update_memory(
            db, 1, "verb_action", item_id="interpret",
            stability=3.0, last_score=60,
        )

        items = await get_user_memory(db, 1)
        assert len(items) == 3
        kinds = {i.kind for i in items}
        assert kinds == {"concept", "verb_chapter", "verb_action"}

        by_kind = {i.kind: i for i in items}
        assert by_kind["concept"].item_id == "transcription"
        assert by_kind["concept"].stability == 2.5
        assert by_kind["concept"].fsrs_state["reps"] == 3
        assert by_kind["verb_chapter"].item_id == "analyse::ch1"
        assert by_kind["verb_chapter"].last_score == 75
        assert by_kind["verb_action"].item_id == "interpret"

    @pytest.mark.asyncio
    async def test_update_increments_attempts(self, db):
        await update_memory(db, 1, "verb_action", item_id="analyse", last_score=50)
        await update_memory(db, 1, "verb_action", item_id="analyse", last_score=80)
        items = await get_user_memory(db, 1)
        assert len(items) == 1
        assert items[0].attempts == 2
        assert items[0].last_score == 80  # upsert écrase

    @pytest.mark.asyncio
    async def test_isolated_per_user(self, db):
        await update_memory(db, 1, "concept", item_id="transcription")
        await update_memory(db, 2, "concept", item_id="traduction")
        items_user1 = await get_user_memory(db, 1)
        items_user2 = await get_user_memory(db, 2)
        assert [i.item_id for i in items_user1] == ["transcription"]
        assert [i.item_id for i in items_user2] == ["traduction"]

    @pytest.mark.asyncio
    async def test_kinds_filter(self, db):
        await update_memory(db, 1, "concept", item_id="a")
        await update_memory(db, 1, "verb_action", item_id="b")
        items = await get_user_memory(db, 1, kinds=("concept",))
        assert len(items) == 1
        assert items[0].kind == "concept"


class TestGetDueItems:
    @pytest.mark.asyncio
    async def test_due_filter_and_sort(self, db):
        past = datetime.now(UTC) - timedelta(days=2)
        future = datetime.now(UTC) + timedelta(days=2)
        await update_memory(db, 1, "concept", item_id="old", due=past)
        await update_memory(db, 1, "concept", item_id="new", due=future)
        await update_memory(db, 1, "concept", item_id="older", due=past - timedelta(days=5))

        due = await get_due_items(db, 1)
        assert [i.item_id for i in due] == ["older", "old"]  # tri par due

    @pytest.mark.asyncio
    async def test_limit(self, db):
        past = datetime.now(UTC) - timedelta(days=1)
        for i in range(5):
            await update_memory(db, 1, "concept", item_id=f"c{i}", due=past)
        due = await get_due_items(db, 1, limit=2)
        assert len(due) == 2


class TestUpdateMemory:
    @pytest.mark.asyncio
    async def test_unknown_kind_returns_false(self, db):
        assert await update_memory(db, 1, "inconnu", item_id="x") is False  # type: ignore[arg-type]


class TestMemorySummary:
    @pytest.mark.asyncio
    async def test_summary(self, db):
        await update_memory(db, 1, "concept", item_id="a", stability=2.0)
        await update_memory(db, 1, "concept", item_id="b", stability=4.0)
        await update_memory(db, 1, "verb_action", item_id="c", stability=3.0)
        summary = await memory_summary(db, 1)
        assert summary["total_items"] == 3
        assert summary["by_kind"] == {"concept": 2, "verb_action": 1}
        assert summary["avg_stability"] == 3.0
        assert summary["due_count"] == 0


class TestMissingTableTolerance:
    @pytest.mark.asyncio
    async def test_missing_mastery_table_returns_empty(self, db):
        """Preview SQLite : mastery_micro_concepts absente → source vide."""
        import os
        import tempfile

        fd, path = tempfile.mkstemp(suffix=".db")
        os.close(fd)
        engine = create_async_engine(f"sqlite+aiosqlite:///{path}")
        async with engine.begin() as conn:
            # Seulement da_fsrs et action_verb_progress (pas mastery)
            await conn.exec_driver_sql("""
                CREATE TABLE da_fsrs (
                    id INTEGER PRIMARY KEY, user_id TEXT, verb_slug TEXT,
                    chapter_slug TEXT, stability REAL DEFAULT 0,
                    difficulty REAL DEFAULT 0, fsrs_state TEXT DEFAULT '{}',
                    prochaine_revision DATETIME, interval_jours REAL DEFAULT 0,
                    last_score INTEGER DEFAULT 0, attempts INTEGER DEFAULT 0,
                    last_review DATETIME, updated_at DATETIME,
                    UNIQUE(user_id, verb_slug, chapter_slug)
                );
            """)
        factory = async_sessionmaker(engine, expire_on_commit=False)
        try:
            async with factory() as session:
                items = await get_user_memory(session, 1)
                assert all(i.kind != "concept" for i in items)  # concept absent
                # Écriture concept → False (pas d'erreur)
                assert await update_memory(session, 1, "concept", item_id="x") is False
                # Les autres sources fonctionnent
                assert await update_memory(
                    session, 1, "verb_chapter", item_id="analyse::ch1",
                ) is True
        finally:
            await engine.dispose()
            os.unlink(path)


class TestConceptHelpers:
    @pytest.mark.asyncio
    async def test_get_concept_state_none_when_absent(self, db):
        state = await get_concept_state(db, 1, "absent")
        assert state is None

    @pytest.mark.asyncio
    async def test_save_and_get_concept_state_roundtrip(self, db):
        from datetime import UTC, datetime, timedelta

        due = datetime.now(UTC) + timedelta(days=3)
        assert await save_concept_card(
            db, 1, "fc_1", concept_id_alias="fc_1", chapter="ch1",
            difficulty=5.0, state=0, due_date=due,
            prochaine_revision=due, interval_jours=1,
        )
        state = await get_concept_state(db, 1, "fc_1")
        assert state == {}  # pas de fsrs_state encore (création simple)

    @pytest.mark.asyncio
    async def test_save_concept_review_simple(self, db):
        from datetime import UTC, datetime, timedelta

        due = datetime.now(UTC) + timedelta(days=2)
        ok = await save_concept_review(
            db, 1, "fc_x", concept_id_alias="fc_x", chapter="ch1",
            prochaine_revision=due, interval_jours=2.0,
            difficulty=6.0, stability=3.5,
            fsrs_state={"stability": 3.5, "reps": 1},
            due_date=due, last_review=datetime.now(UTC),
            reps=1, lapses=0, state=1,
        )
        assert ok is True
        items = await get_user_memory(db, 1, kinds=("concept",))
        assert len(items) == 1
        assert items[0].stability == 3.5
        assert items[0].fsrs_state["reps"] == 1
        assert items[0].attempts == 0  # review simple : pas d'incrément attempts

    @pytest.mark.asyncio
    async def test_save_concept_review_with_avg_score(self, db):
        """Cas drill/result : total_reviews +1 et avg_score pondéré."""
        from datetime import UTC, datetime, timedelta

        due = datetime.now(UTC) + timedelta(days=2)
        # 1re révision à 60
        await save_concept_review(
            db, 1, "fc_y", concept_id_alias="fc_y",
            prochaine_revision=due, interval_jours=2.0,
            difficulty=5.0, stability=2.0,
            fsrs_state={"stability": 2.0},
            due_date=due, last_review=datetime.now(UTC),
            reps=1, lapses=0, state=1, avg_score=60.0,
        )
        # 2e révision à 80 → avg = (60*1 + 80)/2 = 70, total_reviews = 2
        await save_concept_review(
            db, 1, "fc_y", concept_id_alias="fc_y",
            prochaine_revision=due, interval_jours=3.0,
            difficulty=5.0, stability=3.0,
            fsrs_state={"stability": 3.0},
            due_date=due, last_review=datetime.now(UTC),
            reps=2, lapses=0, state=1, avg_score=80.0,
        )
        items = await get_user_memory(db, 1, kinds=("concept",))
        assert len(items) == 1
        assert items[0].extra["total_reviews"] == 2
        assert items[0].extra["avg_score"] == pytest.approx(70.0)

    @pytest.mark.asyncio
    async def test_save_concept_missing_table_returns_false(self, db):
        """Table mastery absente → False, pas d'erreur."""
        import os
        import tempfile
        from datetime import UTC, datetime

        fd, path = tempfile.mkstemp(suffix=".db")
        os.close(fd)
        engine = create_async_engine(f"sqlite+aiosqlite:///{path}")
        async with engine.begin() as conn:
            await conn.exec_driver_sql(
                "CREATE TABLE users (id INTEGER PRIMARY KEY)"
            )
        factory = async_sessionmaker(engine, expire_on_commit=False)
        try:
            async with factory() as session:
                ok = await save_concept_card(
                    session, 1, "x", due_date=datetime.now(UTC),
                    prochaine_revision=datetime.now(UTC),
                )
                assert ok is False  # mastery_micro_concepts absente
        finally:
            await engine.dispose()
            os.unlink(path)
