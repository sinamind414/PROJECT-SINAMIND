"""Récompenses serveur — le client n'envoie JAMAIS un delta libre (T3)."""

from __future__ import annotations

# Liste FERMÉE action → points/XP. Modifier = revue humaine.
REWARD_ACTIONS: dict[str, int] = {
    "start": 10,
    "daily": 5,
    "exercise": 15,
    "lesson": 20,
    "review": 10,
    "streak": 10,
    "combo": 10,
}


class UnknownRewardAction(ValueError):
    """Action hors whitelist."""


def delta_for_action(action: str) -> int:
    key = (action or "").strip().lower()
    if key not in REWARD_ACTIONS:
        raise UnknownRewardAction(key)
    return REWARD_ACTIONS[key]
