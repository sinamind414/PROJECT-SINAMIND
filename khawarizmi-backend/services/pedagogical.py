"""services/pedagogical.py — Bucket pédagogique partagé (audit O2 révisé).

Le seuil de stabilité FSRS qui décide entre « explication directe » (low) et
« relance socratique » (high) ne doit exister qu'à UN SEUL endroit — sinon la
clé de cache chatbot et les sélecteurs de prompt peuvent diverger (le bug de
la réserve B : deux élèves, même question, l'un reçoit une explication,
l'autre une relance — et le cache mélange les deux).

Invariant : stabilité ABSENTE ≡ 0.0 ≡ "low" (explication). Le namespace
"default" de la clé cache était du poids mort : le prompt tombait déjà sur
context.get("fsrs_stability", 0) = 0 → explication. Un seul namespace
désormais : "low" / "high".
"""

from __future__ import annotations

from typing import Literal

# Seuil unique : en dessous → concept faible → explication directe.
PEDAGOGICAL_STABILITY_THRESHOLD = 3.0

# Niveaux pédagogiques possibles — utilisés par la clé de cache ET les prompts.
PedagogicalLevel = Literal["low", "high"]


def pedagogical_bucket(context: dict) -> PedagogicalLevel:
    """Niveau pédagogique d'un contexte FSRS.

    low  = stabilité faible ou absente → explication directe
    high = concept stable → relance socratique / approfondissement
    """
    try:
        stability = float(context.get("fsrs_stability") or 0.0)
    except (TypeError, ValueError):
        stability = 0.0
    return (
        "low"
        if stability < PEDAGOGICAL_STABILITY_THRESHOLD
        else "high"
    )


def is_explication(context: dict) -> bool:
    """Alias sémantique pour les sélecteurs de prompt (orchestrateur, chat).

    Équivaut à l'ancien `stability is not None and stability < 3.0` avec le
    défaut `context.get("fsrs_stability", 0)` : clé absente → 0.0 → True.
    """
    return pedagogical_bucket(context) == "low"
