"""S17/S22 — décision quota (PURE, 0 I/O). Hors grade() (P7).

Vide / cache / stop sanity / 422 ne consomment pas.
defer consomme (B4) : le pipeline a tourné. G7 reste defer ≠ 0.
L'application du quota (limiter, HTTP 429) vit dans rate_limit.enforce_evaluate_quota.
"""

from __future__ import annotations

_COUNTABLE = frozenset({"ok", "defer"})


def should_count_quota(*, sanity_code: str, from_cache: bool) -> bool:
    """True si une note a été calculée (ok ou defer). Cache = 0."""
    if from_cache:
        return False
    return sanity_code in _COUNTABLE
