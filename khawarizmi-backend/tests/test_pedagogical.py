"""tests/test_pedagogical.py — Bucket pédagogique partagé (audit O2 révisé).

Invariant : stabilité absente ≡ 0.0 ≡ "low" (explication) — la clé de cache
chatbot et les sélecteurs de prompt ne peuvent pas diverger (réserve B).
"""

from services.pedagogical import (
    PEDAGOGICAL_STABILITY_THRESHOLD,
    is_explication,
    pedagogical_bucket,
)


class TestPedagogicalBucket:
    def test_threshold_is_3(self):
        assert PEDAGOGICAL_STABILITY_THRESHOLD == 3.0

    def test_absent_stability_is_low(self):
        # Réserve B : le namespace "default" était du poids mort —
        # stabilité absente ≡ 0.0 ≡ low (explication).
        assert pedagogical_bucket({}) == "low"
        assert pedagogical_bucket({"chapitre": "ch1", "history": []}) == "low"

    def test_none_stability_is_low(self):
        assert pedagogical_bucket({"fsrs_stability": None}) == "low"

    def test_weak_concept_is_low(self):
        assert pedagogical_bucket({"fsrs_stability": 0.0}) == "low"
        assert pedagogical_bucket({"fsrs_stability": 2.9}) == "low"

    def test_stable_concept_is_high(self):
        assert pedagogical_bucket({"fsrs_stability": 3.0}) == "high"
        assert pedagogical_bucket({"fsrs_stability": 5.0}) == "high"

    def test_non_numeric_is_low(self):
        assert pedagogical_bucket({"fsrs_stability": "inconnu"}) == "low"


class TestIsExplication:
    def test_alias_matches_bucket(self):
        for ctx in ({}, {"fsrs_stability": 2.0}, {"fsrs_stability": 4.0}):
            assert is_explication(ctx) == (pedagogical_bucket(ctx) == "low")

    def test_absent_context_is_explication(self):
        # Comportement actuel de l'orchestrateur : clé absente → 0 → explication
        assert is_explication({}) is True
