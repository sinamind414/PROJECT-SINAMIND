"""tests/test_orientation_roadmap.py — Boussole : parcours unité par unité.

Vérifie :
- le calcul de maîtrise par unité (Σ min(stability,10) / (10 × nb concepts)) ;
- les statuts done / active / locked avec verrouillage séquentiel strict
  (l'unité N reste locked tant que N-1 < 80 %) ;
- l'unité active = première non-maîtrisée ;
- le chapitre le plus faible de l'unité active ;
- les messages coach FR/AR (débutant / en cours / tout terminé).
"""

from __future__ import annotations

import pytest
from dataclasses import dataclass

from services.orientation_roadmap import (
    PARCOURS,
    SEUIL_DONE,
    _chapter_to_id,
    calculer_roadmap,
)


@dataclass
class FakeItem:
    """Item mémoire simulé (chapter + stability)."""

    chapter: str
    stability: float


async def _roadmap(items: list[FakeItem]):
    """Mocke get_user_memory (importé dans le module) et calcule la roadmap."""
    import services.orientation_roadmap as mod

    async def fake_get_user_memory(db, user_id, kinds=("concept",)):
        return items

    original = mod.get_user_memory
    mod.get_user_memory = fake_get_user_memory
    try:
        return await calculer_roadmap(None, 1)
    finally:
        mod.get_user_memory = original


def test_parcours_5_unites_ordonnees():
    assert len(PARCOURS) == 5
    assert [u["num"] for u in PARCOURS] == [1, 2, 3, 4, 5]
    # toutes les unités ont des chapitres du programme
    for u in PARCOURS:
        assert u["chapitres"], f"unité {u['id']} sans chapitres"


def test_chapter_alias_resolution():
    # slugs du programme
    assert _chapter_to_id("ch_respiration") == "ch_respiration"
    # nom français (normalisé, sans accents)
    assert _chapter_to_id("Respiration cellulaire") == "ch_respiration"
    assert _chapter_to_id("Photosynthèse") == "ch_photosynthese"
    # inconnu
    assert _chapter_to_id("zzz_inconnu") is None


@pytest.mark.asyncio
async def test_debutant_tout_verrouille_sauf_unite_1():
    """Aucune mémoire → unité 1 active, les autres locked, message débutant."""
    r = await _roadmap([])
    unites = r["unites"]
    assert unites[0]["statut"] == "active"
    assert all(u["statut"] == "locked" for u in unites[1:])
    assert unites[1]["verrouille_par"] == "u1"
    assert r["unite_active"] == "u1"
    assert r["prochain_objectif"]["num"] == 1
    assert r["coach"]["tone"] == "focus"
    assert "unité 1" in r["coach"]["fr"] or "l'unité 1" in r["coach"]["fr"]
    assert r["coach"]["ar"]


NB_CONCEPTS = {
    "ch_respiration": 7, "ch_photosynthese": 4, "ch_bilan_energetique": 4,
    "ch1_proteines": 8, "ch_structure_proteines": 5, "ch2_enzymes": 5,
    "ch4_nerveux": 4, "ch3_immunite": 6,
    "ch_tectonique_plaques": 5, "ch_structure_terre": 4, "ch_banies_geologiques": 5,
}


def _concepts(chapitre: str, stability: float) -> list[FakeItem]:
    return [FakeItem(chapitre, stability) for _ in range(NB_CONCEPTS[chapitre])]


@pytest.mark.asyncio
async def test_unite_1_maitrisee_debloque_unite_2():
    """U1 à 100 % (tous les concepts stability ≥ 10) → U1 done, U2 active."""
    items = []
    # respiration : 7 concepts, photosynthèse : 4, bilan : 4 → 15 concepts
    for ch in ("ch_respiration", "ch_photosynthese", "ch_bilan_energetique"):
        items.extend(_concepts(ch, 10.0))
    r = await _roadmap(items)
    unites = r["unites"]
    assert unites[0]["statut"] == "done"
    assert unites[0]["maitrise"] == 100
    assert unites[1]["statut"] == "active"
    assert unites[2]["statut"] == "locked"
    assert r["unite_active"] == "u2"
    assert r["prochain_objectif"]["num"] == 2
    assert r["coach"]["tone"] == "focus" or r["coach"]["tone"] == "progress"


@pytest.mark.asyncio
async def test_unite_1_partielle_reste_active():
    """U1 à 50 % → U1 active (pas done), U2 locked (verrouillage strict)."""
    # respiration à moitié : stability 10 sur la moitié des concepts ≈ 50 %
    items = _concepts("ch_respiration", 10.0) + _concepts("ch_respiration", 0.0)
    r = await _roadmap(items)
    unites = r["unites"]
    assert unites[0]["statut"] == "active"
    assert 0 < unites[0]["maitrise"] < SEUIL_DONE
    assert unites[1]["statut"] == "locked"
    assert r["unite_active"] == "u1"


@pytest.mark.asyncio
async def test_chapitre_faible_identifie():
    """Dans l'unité active, le chapitre le plus faible est renvoyé."""
    # U2 (protéines) : ch1_proteines 8 concepts, ch_structure 5, ch2_enzymes 5
    items = _concepts("ch1_proteines", 10.0) + _concepts("ch_structure_proteines", 0.0)
    # U1 done pour débloquer U2
    for ch in ("ch_respiration", "ch_photosynthese", "ch_bilan_energetique"):
        items.extend(_concepts(ch, 10.0))
    r = await _roadmap(items)
    assert r["unite_active"] == "u2"
    faible = r["prochain_objectif"]["chapitre_faible"]
    assert faible["id"] == "ch_structure_proteines"
    assert faible["maitrise"] == 0
    assert faible["href"].startswith("/lecons-sciences-experimentales/")


@pytest.mark.asyncio
async def test_tout_maitrise_coach_felicitation():
    """Toutes les unités à 100 % → tout done, coach félicitations, href annales."""
    items = []
    for u in PARCOURS:
        for ch in u["chapitres"]:
            items.extend(_concepts(ch, 10.0))
    r = await _roadmap(items)
    assert all(u["statut"] == "done" for u in r["unites"])
    assert r["unite_active"] is None
    assert r["coach"]["tone"] == "success"
    assert r["prochain_objectif"]["href"] == "/annales"


@pytest.mark.asyncio
async def test_route_roadmap_http(client, auth_headers):
    """La route HTTP renvoie le parcours (5 unités) avec auth valide."""
    resp = await client.get("/api/orientation/roadmap", headers=auth_headers)
    assert resp.status_code == 200, resp.text[:200]
    data = resp.json()
    assert len(data["unites"]) == 5
    assert data["unite_active"] in ["u1", "u2", "u3", "u4", "u5", None]
    assert "coach" in data
    assert "prochain_objectif" in data