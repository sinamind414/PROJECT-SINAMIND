"""Intégration des résultats de chapitre dans la mémoire FSRS unifiée."""
import os
import tempfile
from datetime import UTC, datetime

import pytest
from sqlalchemy.ext.asyncio import async_sessionmaker, create_async_engine

from services.fsrs_unified import get_user_memory, review_memory_from_score
from tests.test_fsrs_unified import DDL


@pytest.fixture
async def db():
    fd, path = tempfile.mkstemp(suffix=".db")
    os.close(fd)
    engine = create_async_engine(f"sqlite+aiosqlite:///{path}")
    async with engine.begin() as connection:
        for statement in DDL.strip().split(";"):
            if statement.strip():
                await connection.exec_driver_sql(statement.strip() + ";")
    factory = async_sessionmaker(engine, expire_on_commit=False)
    async with factory() as session:
        yield session
    await engine.dispose()
    os.unlink(path)


@pytest.mark.asyncio
async def test_review_uses_one_mastery_table_and_schedules_from_score(db):
    now = datetime(2026, 8, 22, 12, 0, tzinfo=UTC)
    chapter_slug = "d1-u1-c3-transcription-de-l-information-genetique-au-niveau-de-l-adn"

    chapter_review = await review_memory_from_score(
        db,
        1,
        "verb_chapter",
        item_id=f"extract::{chapter_slug}",
        chapter=chapter_slug,
        score_percent=20,
        now=now,
    )
    verb_review = await review_memory_from_score(
        db,
        1,
        "verb_action",
        item_id="extract",
        chapter=None,
        score_percent=40,
        now=now,
    )
    await db.commit()

    assert chapter_review["updated"] is True
    assert chapter_review["rating"] == "Again"
    assert verb_review["updated"] is True
    assert verb_review["rating"] == "Hard"
    assert chapter_review["next_review_at"]

    items = await get_user_memory(db, 1)
    assert {item.kind for item in items} == {"verb_chapter", "verb_action"}
    by_kind = {item.kind: item for item in items}
    assert by_kind["verb_chapter"].chapter == chapter_slug
    assert by_kind["verb_chapter"].last_score == 20
    assert by_kind["verb_action"].last_score == 40


@pytest.mark.asyncio
async def test_second_review_reuses_fsrs_state_and_increments_attempts(db):
    now = datetime(2026, 8, 22, 12, 0, tzinfo=UTC)
    item_id = "scientific-text::d2-u3-c1-les-transformations-energetiques-au-niveau-cellulaire"

    first = await review_memory_from_score(
        db,
        7,
        "verb_chapter",
        item_id=item_id,
        chapter=item_id.partition("::")[2],
        score_percent=55,
        now=now,
    )
    await db.commit()
    second = await review_memory_from_score(
        db,
        7,
        "verb_chapter",
        item_id=item_id,
        chapter=item_id.partition("::")[2],
        score_percent=95,
        now=now,
    )
    await db.commit()

    assert first["rating"] == "Hard"
    assert second["rating"] == "Easy"
    items = await get_user_memory(db, 7, kinds=("verb_chapter",))
    assert len(items) == 1
    assert items[0].attempts == 2
    assert items[0].last_score == 95
    assert items[0].fsrs_state["card_id"]
    assert items[0].due is not None
