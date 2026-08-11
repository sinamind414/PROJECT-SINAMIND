"""Contrat de la boussole complète et preuves issues des producteurs réels."""

from __future__ import annotations

from dataclasses import dataclass, field

import pytest

from services.chapter_identity import normalize_chapter_id
from services.orientation_roadmap import (
    BAC_THRESHOLD,
    COVERAGE_THRESHOLD,
    KNOWLEDGE_THRESHOLD,
    PARCOURS,
    _official_chapters,
    calculer_roadmap,
)
from services.units import DOMAINS, PHASES


@dataclass
class FakeItem:
    chapter: str
    stability: float = 0.0
    kind: str = "concept"
    item_id: str = ""
    attempts: int = 0
    last_score: int | None = None
    fsrs_state: dict = field(default_factory=dict)


def _concepts(chapter: str, stability: float = 10.0) -> list[FakeItem]:
    count = len(_official_chapters()[chapter]["essential_concepts"])
    return [
        FakeItem(chapter=chapter, stability=stability, item_id=f"{chapter}:c{index}", fsrs_state={"reps": 1})
        for index in range(count)
    ]


def _bac(chapter: str, score: int = BAC_THRESHOLD) -> FakeItem:
    return FakeItem(
        chapter=chapter,
        kind="verb_chapter",
        item_id=f"analyse::{chapter}",
        attempts=1,
        last_score=score,
    )


async def _roadmap(monkeypatch, items: list[FakeItem]):
    async def fake_get_user_memory(db, user_id, kinds=("concept",)):
        return items

    monkeypatch.setattr("services.orientation_roadmap.get_user_memory", fake_get_user_memory)
    return await calculer_roadmap(None, 1)


def test_catalogue_unique_3_domaines_11_unites_22_phases():
    assert len(DOMAINS) == 3
    assert len(PARCOURS) == 11
    assert len(PHASES) == 22
    assert len({unit["roadmap_id"] for unit in PARCOURS}) == 11
    assert len({phase["slug"] for phase in PHASES}) == 22
    assert sum(len(unit["phases"]) for unit in PARCOURS) == 22
    assert PARCOURS[0]["chapter_id"] == "ch1_proteines"
    assert [unit["domain_id"] for unit in PARCOURS] == ["d1"] * 5 + ["d2"] * 3 + ["d3"] * 3


@pytest.mark.parametrize(
    ("historical", "canonical"),
    [
        ("ch_structure", "ch_structure_proteines"),
        ("ch_nerveux", "ch4_nerveux"),
        ("ch5_photosynthese", "ch_photosynthese"),
        ("d2-u2-c4-fermentation", "ch_respiration"),
        ("phase22_chapitres_43_44", "ch_structures_geologiques"),
        ("Les ondes sismiques", "ch_structure_terre"),
        ("u10", "ch_structure_terre"),
    ],
)
def test_normalisation_historique(historical, canonical):
    assert normalize_chapter_id(historical) == canonical


def test_normalisation_refuse_identite_ambigue():
    assert normalize_chapter_id("Tectonique") is None
    assert normalize_chapter_id("zzz_inconnu") is None


@pytest.mark.asyncio
async def test_debutant_commence_unite_1_phase_1(monkeypatch):
    roadmap = await _roadmap(monkeypatch, [])

    assert len(roadmap["unites"]) == 11
    assert roadmap["phases_total"] == 22
    assert roadmap["unite_active"] == "u1"
    assert roadmap["unites"][0]["statut"] == "active"
    assert all(unit["statut"] == "locked" for unit in roadmap["unites"][1:])
    assert roadmap["prochain_objectif"]["kind"] == "lesson"
    assert roadmap["prochain_objectif"]["phase"]["slug"] == "phase1_chapitres_1_2"
    assert "الوحدة 1" in roadmap["coach"]["ar"]


@pytest.mark.asyncio
async def test_connaissance_sans_bac_ne_termine_pas_unite(monkeypatch):
    items = _concepts("ch1_proteines")
    roadmap = await _roadmap(monkeypatch, items)
    first = roadmap["unites"][0]

    assert first["knowledge"] == 100
    assert first["coverage"] == 100
    assert first["bac_validated"] is False
    assert first["statut"] == "active"
    assert roadmap["prochain_objectif"]["kind"] == "bac_validation"
    assert roadmap["prochain_objectif"]["href"].startswith("/document-analysis/chapters/d1-u1-")


@pytest.mark.asyncio
async def test_validation_reelle_unite_1_debloque_unite_2(monkeypatch):
    items = _concepts("ch1_proteines") + [
        _bac("d1-u1-c5-synthese-du-gene-a-la-proteine", score=76)
    ]
    roadmap = await _roadmap(monkeypatch, items)

    assert roadmap["unites"][0]["statut"] == "done"
    assert roadmap["unites"][0]["validation_complete"] is True
    assert roadmap["unites"][1]["statut"] == "active"
    assert roadmap["unite_active"] == "u2"


@pytest.mark.asyncio
async def test_unite_2_reste_verrouillee_si_unite_1_non_validee(monkeypatch):
    items = _concepts("ch_structure_proteines") + [_bac("ch_structure", score=90)]
    roadmap = await _roadmap(monkeypatch, items)

    assert roadmap["unites"][1]["validation_complete"] is True
    assert roadmap["unites"][1]["statut"] == "locked"
    assert roadmap["unite_active"] == "u1"


@pytest.mark.asyncio
async def test_seuils_independants(monkeypatch):
    chapter = "ch1_proteines"
    count = len(_official_chapters()[chapter]["essential_concepts"])
    items = _concepts(chapter)[: max(1, count // 2)] + [_bac(chapter, score=100)]
    roadmap = await _roadmap(monkeypatch, items)
    unit = roadmap["unites"][0]

    assert unit["coverage"] < COVERAGE_THRESHOLD
    assert unit["knowledge"] < KNOWLEDGE_THRESHOLD
    assert unit["bac_validated"] is True
    assert unit["statut"] == "active"
    assert roadmap["prochain_objectif"]["kind"] == "lesson"


@pytest.mark.asyncio
async def test_parcours_complet_envoie_vers_annales(monkeypatch):
    items: list[FakeItem] = []
    for unit in PARCOURS:
        chapter = unit["chapter_id"]
        items.extend(_concepts(chapter))
        items.append(_bac(chapter, score=85))

    roadmap = await _roadmap(monkeypatch, items)

    assert all(unit["statut"] == "done" for unit in roadmap["unites"])
    assert roadmap["unite_active"] is None
    assert roadmap["units_done"] == 11
    assert roadmap["prochain_objectif"]["kind"] == "annales"
    assert roadmap["prochain_objectif"]["href"] == "/annales"


@pytest.mark.asyncio
async def test_route_roadmap_http(client, auth_headers):
    response = await client.get("/api/orientation/roadmap", headers=auth_headers)

    assert response.status_code == 200, response.text
    payload = response.json()
    assert len(payload["domains"]) == 3
    assert len(payload["unites"]) == 11
    assert payload["phases_total"] == 22
    assert payload["unite_active"] == "u1"
    assert payload["prochain_objectif"]["kind"] == "lesson"
