"""Tests de la boussole pédagogique unité par unité."""

from __future__ import annotations

from dataclasses import dataclass

import pytest

from services.orientation_roadmap import (
    PARCOURS,
    SEUIL_DONE,
    _chapter_to_id,
    calculer_roadmap,
)


@dataclass
class FakeItem:
    chapter: str
    stability: float


NB_CONCEPTS = {
    "ch_respiration": 7,
    "ch_photosynthese": 4,
    "ch_bilan_energetique": 4,
    "ch1_proteines": 8,
    "ch_structure_proteines": 5,
    "ch2_enzymes": 5,
    "ch4_nerveux": 4,
    "ch3_immunite": 6,
    "ch_tectonique_plaques": 5,
    "ch_structure_terre": 4,
    "ch_banies_geologiques": 5,
}


def _concepts(chapter: str, stability: float) -> list[FakeItem]:
    return [FakeItem(chapter, stability) for _ in range(NB_CONCEPTS[chapter])]


async def _roadmap(monkeypatch, items: list[FakeItem]):
    async def fake_get_user_memory(db, user_id, kinds=("concept",)):
        return items

    monkeypatch.setattr(
        "services.orientation_roadmap.get_user_memory",
        fake_get_user_memory,
    )
    return await calculer_roadmap(None, 1)


def test_parcours_5_unites_ordonnees():
    assert len(PARCOURS) == 5
    assert [unit["num"] for unit in PARCOURS] == [1, 2, 3, 4, 5]
    assert all(unit["chapitres"] for unit in PARCOURS)


def test_chapter_alias_resolution():
    assert _chapter_to_id("ch_respiration") == "ch_respiration"
    assert _chapter_to_id("Respiration cellulaire") == "ch_respiration"
    assert _chapter_to_id("Photosynthèse") == "ch_photosynthese"
    assert _chapter_to_id("التركيب الضوئي") == "ch_photosynthese"
    assert _chapter_to_id("zzz_inconnu") is None


@pytest.mark.asyncio
async def test_debutant_tout_verrouille_sauf_unite_1(monkeypatch):
    roadmap = await _roadmap(monkeypatch, [])
    units = roadmap["unites"]

    assert units[0]["statut"] == "active"
    assert all(unit["statut"] == "locked" for unit in units[1:])
    assert units[1]["verrouille_par"] == "u1"
    assert roadmap["unite_active"] == "u1"
    assert roadmap["prochain_objectif"]["num"] == 1
    assert roadmap["coach"]["tone"] == "focus"
    assert "unité 1" in roadmap["coach"]["fr"]
    assert "الوحدة 1" in roadmap["coach"]["ar"]


@pytest.mark.asyncio
async def test_unite_1_maitrisee_debloque_unite_2(monkeypatch):
    items: list[FakeItem] = []
    for chapter in (
        "ch_respiration",
        "ch_photosynthese",
        "ch_bilan_energetique",
    ):
        items.extend(_concepts(chapter, 10.0))

    roadmap = await _roadmap(monkeypatch, items)
    units = roadmap["unites"]

    assert units[0]["statut"] == "done"
    assert units[0]["maitrise"] == 100
    assert units[1]["statut"] == "active"
    assert units[2]["statut"] == "locked"
    assert roadmap["unite_active"] == "u2"
    assert roadmap["prochain_objectif"]["num"] == 2


@pytest.mark.asyncio
async def test_unite_1_partielle_reste_active(monkeypatch):
    items = _concepts("ch_respiration", 10.0)
    roadmap = await _roadmap(monkeypatch, items)
    units = roadmap["unites"]

    assert units[0]["statut"] == "active"
    assert 0 < units[0]["maitrise"] < SEUIL_DONE
    assert units[1]["statut"] == "locked"
    assert roadmap["unite_active"] == "u1"
    assert roadmap["coach"]["tone"] == "progress"


@pytest.mark.asyncio
async def test_chapitre_faible_identifie(monkeypatch):
    items: list[FakeItem] = []
    for chapter in (
        "ch_respiration",
        "ch_photosynthese",
        "ch_bilan_energetique",
    ):
        items.extend(_concepts(chapter, 10.0))
    items.extend(_concepts("ch1_proteines", 10.0))

    roadmap = await _roadmap(monkeypatch, items)
    weakest = roadmap["prochain_objectif"]["chapitre_faible"]

    assert roadmap["unite_active"] == "u2"
    assert weakest["id"] == "ch_structure_proteines"
    assert weakest["maitrise"] == 0
    assert weakest["href"] == (
        "/lecons-sciences-experimentales/phase3_chapitres_5_6"
    )


@pytest.mark.asyncio
async def test_tout_maitrise_coach_felicitation(monkeypatch):
    items: list[FakeItem] = []
    for unit in PARCOURS:
        for chapter in unit["chapitres"]:
            items.extend(_concepts(chapter, 10.0))

    roadmap = await _roadmap(monkeypatch, items)

    assert all(unit["statut"] == "done" for unit in roadmap["unites"])
    assert roadmap["unite_active"] is None
    assert roadmap["coach"]["tone"] == "success"
    assert roadmap["prochain_objectif"]["href"] == "/annales"


@pytest.mark.asyncio
async def test_route_roadmap_http(client, auth_headers):
    response = await client.get(
        "/api/orientation/roadmap",
        headers=auth_headers,
    )

    assert response.status_code == 200, response.text
    payload = response.json()
    assert len(payload["unites"]) == 5
    assert payload["unite_active"] == "u1"
