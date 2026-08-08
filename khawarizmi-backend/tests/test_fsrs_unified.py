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
    clear_pending_concept,
    get_concept_state,
    get_concept_states,
    get_concept_stats,
    get_concept_stats_by_chapter,
    get_due_items,
    get_user_memory,
    memory_summary,
    save_concept_card,
    save_concept_review,
    save_concept_update,
    save_concept_update_existing,
    tag_pending_concept,
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
    source TEXT DEFAULT 'concept',
    item_key TEXT,
    avg_pct REAL,
    total_users INTEGER,
    updated_at DATETIME,
    UNIQUE(user_id, micro_concept_id),
    UNIQUE(user_id, concept_id)
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


class TestEvaluationRichHelpers:
    @pytest.mark.asyncio
    async def test_get_concept_states_batch(self, db):
        """Batch par concept_id : retourne des Cards hydratées ou vierges."""
        from datetime import UTC, datetime, timedelta

        from fsrs import Card

        due = datetime.now(UTC) + timedelta(days=2)
        await save_concept_update(
            db, 1, "c1", chapter="ch1",
            due=due, interval_jours=2.0,
            difficulty=5.0, stability=2.5,
            fsrs_state={"stability": 2.5, "difficulty": 5.0, "reps": 3},
        )
        states = await get_concept_states(db, 1, ["c1", "absent"])
        assert set(states) == {"c1", "absent"}
        assert isinstance(states["c1"], Card)
        assert states["c1"].stability == 2.5
        # reps n'existe pas sur la Card fsrs (l'ancien code utilisait
        # hasattr comme garde) — seuls les champs présents sont hydratés
        if hasattr(states["c1"], "reps"):
            assert states["c1"].reps == 3
        assert isinstance(states["absent"], Card)
        # Card() vierge : stability None (l'ancien code retournait Card() aussi)
        assert states["absent"].stability is None

    @pytest.mark.asyncio
    async def test_save_concept_update_roundtrip(self, db):
        from datetime import UTC, datetime, timedelta

        due = datetime.now(UTC) + timedelta(days=5)
        ok = await save_concept_update(
            db, 1, "c2", chapter="ch2",
            due=due, interval_jours=5.0,
            difficulty=4.0, stability=3.0,
            fsrs_state={"stability": 3.0, "reps": 1},
            pending_eval=False,
        )
        assert ok is True
        items = await get_user_memory(db, 1, kinds=("concept",))
        assert len(items) == 1
        assert items[0].item_id == "c2"
        assert items[0].stability == 3.0
        assert items[0].chapter == "ch2"

    @pytest.mark.asyncio
    async def test_save_concept_update_conflict_on_concept_id(self, db):
        """Deux concepts partageant le même concept_id → un seul upsert
        (ON CONFLICT user_id+concept_id — le schéma réel l'exige)."""
        from datetime import UTC, datetime, timedelta

        due = datetime.now(UTC) + timedelta(days=1)
        # micro_concept_id différent, concept_id identique (c_id = c3)
        await save_concept_update(
            db, 1, "c3", chapter="ch1",
            due=due, interval_jours=1.0, difficulty=5.0, stability=1.0,
            fsrs_state={"stability": 1.0},
        )
        await save_concept_update(
            db, 1, "c3", chapter="ch1",
            due=due, interval_jours=2.0, difficulty=5.0, stability=2.0,
            fsrs_state={"stability": 2.0},
        )
        items = await get_user_memory(db, 1, kinds=("concept",))
        assert len(items) == 1
        assert items[0].stability == 2.0  # écrasé par le 2e

    @pytest.mark.asyncio
    async def test_tag_pending_concept(self, db):
        ok = await tag_pending_concept(db, 1, "c_pending", "ch3")
        assert ok is True
        # Lire l'état : pending_real_evaluation doit être TRUE
        from sqlalchemy import text

        res = await db.execute(
            text("SELECT pending_real_evaluation FROM mastery_micro_concepts WHERE concept_id = 'c_pending'")
        )
        row = res.fetchone()
        assert row is not None
        assert bool(row[0]) is True

    @pytest.mark.asyncio
    async def test_missing_table_returns_false(self, db):
        import os
        import tempfile

        fd, path = tempfile.mkstemp(suffix=".db")
        os.close(fd)
        engine = create_async_engine(f"sqlite+aiosqlite:///{path}")
        async with engine.begin() as conn:
            await conn.exec_driver_sql("CREATE TABLE users (id INTEGER PRIMARY KEY)")
        factory = async_sessionmaker(engine, expire_on_commit=False)
        try:
            async with factory() as session:
                assert await save_concept_update(
                    session, 1, "x", chapter="ch",
                    due=None, interval_jours=1.0, difficulty=1.0,
                    stability=1.0, fsrs_state={},
                ) is False
                assert await tag_pending_concept(session, 1, "x", "ch") is False
        finally:
            await engine.dispose()
            os.unlink(path)


class TestDrillQueueSupport:
    @pytest.mark.asyncio
    async def test_pending_flag_exposed_in_extra(self, db):
        """drill_queue lit pending_real_evaluation via extra — vérifié."""

        await tag_pending_concept(db, 1, "c_pend", "ch1")
        items = await get_user_memory(db, 1, kinds=("concept",))
        assert len(items) == 1
        assert items[0].extra["pending_real_evaluation"] is True

    @pytest.mark.asyncio
    async def test_due_date_exposed_in_extra(self, db):
        from datetime import UTC, datetime, timedelta

        due = datetime.now(UTC) + timedelta(days=1)
        await save_concept_update(
            db, 1, "c_due", chapter="ch1",
            due=due, interval_jours=1.0, difficulty=5.0, stability=1.0,
            fsrs_state={"stability": 1.0},
        )
        items = await get_user_memory(db, 1, kinds=("concept",))
        assert items[0].extra["due_date"] is not None
        # NB : le due principal (normalisé) vient de prochaine_revision, qui
        # est NULL ici — le due_date réel est exposé dans extra (drill_queue
        # lit cette colonne). Les deux cohabitent comme dans le schéma réel.


class TestAnalyticsHelpers:
    @pytest.mark.asyncio
    async def test_get_concept_stats(self, db):
        from datetime import UTC, datetime, timedelta

        due = datetime.now(UTC) + timedelta(days=1)
        await save_concept_update(
            db, 1, "c1", chapter="ch1", due=due, interval_jours=1.0,
            difficulty=5.0, stability=2.0, fsrs_state={"stability": 2.0},
        )
        await save_concept_update(
            db, 1, "c2", chapter="ch1", due=due, interval_jours=1.0,
            difficulty=5.0, stability=12.0, fsrs_state={"stability": 12.0},
        )
        await save_concept_update(
            db, 1, "c3", chapter="ch2", due=due, interval_jours=1.0,
            difficulty=5.0, stability=4.0, fsrs_state={"stability": 4.0},
        )
        stats = await get_concept_stats(db, 1)
        assert stats["total"] == 3
        assert stats["mastered"] == 1  # stability > 10
        assert stats["avg_stability"] == 6.0  # (2+12+4)/3 = 6

    @pytest.mark.asyncio
    async def test_get_concept_stats_by_chapter(self, db):
        from datetime import UTC, datetime, timedelta

        due = datetime.now(UTC) + timedelta(days=1)
        await save_concept_update(
            db, 1, "c1", chapter="ch1", due=due, interval_jours=1.0,
            difficulty=5.0, stability=2.0, fsrs_state={"stability": 2.0},
        )
        await save_concept_update(
            db, 1, "c2", chapter="ch1", due=due, interval_jours=1.0,
            difficulty=5.0, stability=4.0, fsrs_state={"stability": 4.0},
        )
        await save_concept_update(
            db, 1, "c3", chapter="ch2", due=due, interval_jours=1.0,
            difficulty=5.0, stability=6.0, fsrs_state={"stability": 6.0},
        )
        by_chapter = await get_concept_stats_by_chapter(db, 1)
        assert set(by_chapter) == {"ch1", "ch2"}
        assert by_chapter["ch1"]["nb_concepts"] == 2
        assert by_chapter["ch1"]["avg_stability"] == 3.0  # (2+4)/2
        assert by_chapter["ch2"]["avg_stability"] == 6.0


class TestReconciliationHelpers:
    @pytest.mark.asyncio
    async def test_save_concept_update_existing_updates_only(self, db):
        """UPDATE sans création : un concept absent n'est pas créé."""
        from datetime import UTC, datetime, timedelta

        due = datetime.now(UTC) + timedelta(days=3)
        # UPDATE sur un concept inexistant → aucune ligne affectée
        ok = await save_concept_update_existing(
            db, 1, "absent", due=due, interval_jours=3.0,
            difficulty=5.0, stability=2.0, fsrs_state={"stability": 2.0},
        )
        assert ok is True  # pas d'erreur
        items = await get_user_memory(db, 1, kinds=("concept",))
        assert len(items) == 0  # rien créé

    @pytest.mark.asyncio
    async def test_save_concept_update_existing_updates_pending(self, db):
        """Un concept pending → UPDATE le réconcilie (pending=FALSE)."""
        from datetime import UTC, datetime, timedelta

        await tag_pending_concept(db, 1, "c_rec", "ch1")
        due = datetime.now(UTC) + timedelta(days=3)
        await save_concept_update_existing(
            db, 1, "c_rec", due=due, interval_jours=3.0,
            difficulty=5.0, stability=2.0, fsrs_state={"stability": 2.0},
        )
        items = await get_user_memory(db, 1, kinds=("concept",))
        assert len(items) == 1
        assert items[0].extra["pending_real_evaluation"] is False  # réconcilié
        assert items[0].stability == 2.0

    @pytest.mark.asyncio
    async def test_clear_pending_concept(self, db):
        await tag_pending_concept(db, 1, "c_clr", "ch1")
        assert await clear_pending_concept(db, 1, "c_clr") is True
        items = await get_user_memory(db, 1, kinds=("concept",))
        assert items[0].extra["pending_real_evaluation"] is False

    @pytest.mark.asyncio
    async def test_clear_pending_missing_table(self, db):
        import os
        import tempfile

        fd, path = tempfile.mkstemp(suffix=".db")
        os.close(fd)
        engine = create_async_engine(f"sqlite+aiosqlite:///{path}")
        async with engine.begin() as conn:
            await conn.exec_driver_sql("CREATE TABLE users (id INTEGER PRIMARY KEY)")
        factory = async_sessionmaker(engine, expire_on_commit=False)
        try:
            async with factory() as session:
                assert await clear_pending_concept(session, 1, "x") is False
        finally:
            await engine.dispose()
            os.unlink(path)


class TestUnifiedProvenance:
    @pytest.mark.asyncio
    async def test_source_and_item_key_exposed(self, db):
        """La vue consolidée expose la provenance (source/item_key) —
        la fusion physique (migration 033) rend les lignes verb_chapter /
        verb_action visibles via get_user_memory."""
        from sqlalchemy import text

        # Simuler des lignes fusionnées (migration 033)
        async with db.begin():
            # NB : '::' dans un text() SQLAlchemy est un bind param → échappé
            # avec text("...") + bindparams explicites (ou concaténation)
            await db.execute(text("""
                INSERT INTO mastery_micro_concepts
                    (user_id, micro_concept_id, concept_id, chapter,
                     stability, source, item_key)
                VALUES
                    (1, 'vc_analyse_ch1', 'vc_analyse_ch1', 'ch1', 2.5,
                     'verb_chapter', :key_vc),
                    (1, 'va_interpret', 'va_interpret', NULL, 3.0,
                     'verb_action', 'interpret')
            """), {"key_vc": "analyse::ch1"})

        items = await get_user_memory(db, 1)  # tous les kinds (provenance)
        assert len(items) == 2
        # item_id = item_key (le lecteur mastery-first l'utilise directement)
        by_id = {i.item_id: i for i in items}
        assert "analyse::ch1" in by_id
        assert by_id["analyse::ch1"].stability == 2.5
        assert by_id["analyse::ch1"].kind == "verb_chapter"
        assert by_id["interpret"].kind == "verb_action"
        assert by_id["interpret"].item_id == "interpret"


class TestMasteryFirstBascule:
    """S3 finale : les lectures verb_chapter/verb_action lisent d'abord les
    lignes FUSIONNÉES (source dans mastery), avec fallback sur les tables
    héritées si aucune ligne fusionnée."""

    @pytest.mark.asyncio
    async def test_verb_chapter_reads_fused_rows(self, db):
        from sqlalchemy import text

        # Ligne fusionnée (migration 033) — source='verb_chapter'
        async with db.begin():
            await db.execute(text("""
                INSERT INTO mastery_micro_concepts
                    (user_id, micro_concept_id, concept_id, chapter,
                     stability, source, item_key)
                VALUES
                    (1, 'vc_analyse_ch1', 'vc_analyse_ch1', 'ch1', 4.5,
                     'verb_chapter', :key)
            """), {"key": "analyse::ch1"})
        # Table da_fsrs absente du fixture → fallback impossible → la
        # lecture doit venir de mastery
        items = await get_user_memory(db, 1, kinds=("verb_chapter",))
        assert len(items) == 1
        assert items[0].item_id == "analyse::ch1"
        assert items[0].stability == 4.5
        assert items[0].chapter == "ch1"
        assert items[0].extra["verb_slug"] == "analyse"

    @pytest.mark.asyncio
    async def test_verb_chapter_falls_back_to_legacy(self):
        """Fallback UNIQUEMENT si la table mastery est ABSENTE (prod avant
        033) : da_fsrs est alors la source."""
        import os
        import tempfile

        fd, path = tempfile.mkstemp(suffix=".db")
        os.close(fd)
        engine = create_async_engine(f"sqlite+aiosqlite:///{path}")
        async with engine.begin() as conn:
            # da_fsrs seulement (PAS mastery — fallback requis)
            await conn.exec_driver_sql("""
                CREATE TABLE da_fsrs (
                    id INTEGER PRIMARY KEY, user_id TEXT, verb_slug TEXT,
                    chapter_slug TEXT, stability REAL, difficulty REAL,
                    fsrs_state TEXT DEFAULT '{}', prochaine_revision DATETIME,
                    interval_jours REAL, last_score INTEGER,
                    attempts INTEGER, last_review DATETIME,
                    UNIQUE(user_id, verb_slug, chapter_slug)
                )
            """)
            await conn.exec_driver_sql(
                "INSERT INTO da_fsrs (user_id, verb_slug, chapter_slug, "
                "stability, last_score) VALUES ('1', 'analyse', 'ch1', 2.5, 75)"
            )
        factory = async_sessionmaker(engine, expire_on_commit=False)
        try:
            async with factory() as session:
                items = await get_user_memory(session, 1, kinds=("verb_chapter",))
                assert len(items) == 1
                assert items[0].item_id == "analyse::ch1"
                assert items[0].stability == 2.5
                assert items[0].last_score == 75
        finally:
            await engine.dispose()
            os.unlink(path)

    @pytest.mark.asyncio
    async def test_verb_action_reads_fused_rows(self, db):
        from sqlalchemy import text

        async with db.begin():
            await db.execute(text("""
                INSERT INTO mastery_micro_concepts
                    (user_id, micro_concept_id, concept_id, stability,
                     avg_pct, total_users, source, item_key)
                VALUES
                    (1, 'va_interpret', 'va_interpret', 3.5, 60, 10,
                     'verb_action', 'interpret')
            """))
        items = await get_user_memory(db, 1, kinds=("verb_action",))
        assert len(items) == 1
        assert items[0].item_id == "interpret"
        assert items[0].stability == 3.5
        assert items[0].extra["avg_pct"] == 60
        assert items[0].extra["total_users"] == 10
