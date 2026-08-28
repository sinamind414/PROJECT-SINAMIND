"""S17 — quota /api/grade. Hors grade() (P7). Vide / cache / defer ne consomment pas."""

from __future__ import annotations


def should_count_quota(*, sanity_code: str, from_cache: bool) -> bool:
    """True seulement si une vraie note sanity==ok vient d'être calculée."""
    if from_cache:
        return False
    return sanity_code == "ok"
