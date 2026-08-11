"""Round-trip SQLite : routes réelles → FSRS → boussole réelle."""

from __future__ import annotations

import os
import tempfile

import pytest
from sqlalchemy import text
from sqlalchemy.ext.asyncio import async_sessionmaker, create_async_engine

from routes.document_analysis import reviser_da
from routes.flashcards import soumettre_qcm_drill, soumettre_resultat_drill
from routes.orientation import roadmap_eleve
from schemas.document_analysis import DaReviewRequest
from schemas.flashcard import QcmSubmitRequest, ScheduleRequest

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
CREATE TABLE users (
    id INTEGER PRIMARY KEY,
    fsrs_config TEXT
);
CREATE TABLE question_concept_map (
    question_id TEXT,
    micro_concept TEXT,
    weight REAL
);
CREATE TABLE concept_prerequisites (
    concept_id TEXT,
    prerequisite_id TEXT
);
"""


@pytest.fixture
async def sqlite_db():
    fd, path = tempfile.mkstemp(suffix=".db")
    os.close(fd)
    engine = create_async_engine(f"sqlite+aiosqlite:///{path}")
    async with engine.begin() as connection:
        for statement in DDL.strip().split(";"):
            if statement.strip():
                await connection.exec_driver_sql(statement.strip() + ";")
        await connection.exec_driver_sql("INSERT INTO users (id) VALUES (42)")
    factory = async_sessionmaker(engine, expire_on_commit=False)
    try:
        async with factory() as session:
            yield session
    finally:
        await engine.dispose()
        os.unlink(path)


@pytest.mark.asyncio
async def test_routes_productrices_alimentent_la_boussole(sqlite_db):
    from main import state
    from services.scheduler import KhawarizmiScheduler

    user = {"id": 42, "plan": "free"}
    state.scheduler = KhawarizmiScheduler()

    # Flux historique /api/drill/result : l'identité transmise par le frontend
    # est normalisée et conservée même lors d'un ON CONFLICT ultérieur.
    response = await soumettre_resultat_drill(
        ScheduleRequest(
            micro_concept_id="protein-route-proof",
            score_percent=92,
            chapter="ch1_synthese_proteines",
        ),
        current_user=user,
        db=sqlite_db,
    )
    assert response["stability"] > 0
    await soumettre_resultat_drill(
        ScheduleRequest(
            micro_concept_id="protein-route-proof",
            score_percent=88,
            chapter="ch_proteines",
        ),
        current_user=user,
        db=sqlite_db,
    )

    # Flux QCM réellement utilisé par /drill/u1 : la correction locale est
    # une évaluation FSRS, pas une simple carte pending sans chapitre.
    qcm_response = await soumettre_qcm_drill(
        QcmSubmitRequest(qcm_id="qcm_01", selected_idx=1),
        current_user=user,
        db=sqlite_db,
    )
    assert qcm_response["correct"] is True
    assert qcm_response["next_review_date"] is not None

    # Producteur BAC réel : un slug méthodologique est regroupé sous la même
    # unité canonique, avec tentative et score vérifiables.
    bac_response = await reviser_da(
        DaReviewRequest(
            verb_slug="analyse",
            chapter_slug="d1-u1-c3-transcription-de-linformation-genetique-au-niveau-de-ladn",
            rating=3,
            score_percentage=78,
        ),
        current_user=user,
        db=sqlite_db,
    )
    assert bac_response["rating"] == 3

    raw = await sqlite_db.execute(
        text(
            "SELECT source, chapter, last_score, attempts "
            "FROM mastery_micro_concepts WHERE user_id = :uid ORDER BY source"
        ),
        {"uid": user["id"]},
    )
    rows = raw.fetchall()
    assert {row[1] for row in rows} == {"ch1_proteines"}
    bac_row = next(row for row in rows if row[0] == "verb_chapter")
    assert bac_row[2] == 78
    assert bac_row[3] == 1

    roadmap = await roadmap_eleve(current_user=user, db=sqlite_db)
    first = roadmap["unites"][0]
    assert first["concepts_seen"] == 2
    assert first["knowledge"] > 0
    assert first["bac_score"] == 78
    assert first["bac_attempts"] == 1
    # Une seule notion couverte ne suffit pas : l'unité suivante reste fermée.
    assert first["statut"] == "active"
    assert roadmap["unites"][1]["statut"] == "locked"
    assert roadmap["prochain_objectif"]["kind"] == "lesson"
