"""Transparence de la boussole FSRS et de l'indicateur mémoire."""
import pytest

from services.orientation_service import calculer_orientation
from tests.test_orientation_roadmap import _roadmap
from tests.test_orientation_service import SequencedDb


@pytest.mark.asyncio
async def test_roadmap_declares_single_memory_source_and_non_prediction_scope():
    result = await _roadmap([])

    assert len(result["unites"]) == 11
    assert [unit["num"] for unit in result["unites"]] == list(range(1, 12))
    assert result["memory"] == {
        "source": "mastery_micro_concepts",
        "items_count": 0,
        "scope": "memory_indicator_not_bac_prediction",
        "message_ar": "تُحسب البوصلة من ذاكرة FSRS الموحدة؛ هي مؤشر مراجعة وليست تنبؤا بعلامة البكالوريا.",
        "message_fr": "Boussole calculée depuis la mémoire FSRS unifiée : indicateur de révision, pas prédiction de note au Bac.",
    }
    assert result["prochain_objectif"]["href"].startswith("/")


@pytest.mark.asyncio
async def test_orientation_labels_stability_value_as_uncalibrated_memory_indicator():
    db = SequencedDb([[], [], [], [], [], []])
    result = await calculer_orientation(db, "1")

    assert result["prediction_bac"] is None
    assert result["prediction_scope"] == "memory_indicator_not_bac_prediction"
    assert "Pas assez de données mémoire" in result["prediction_message"]
