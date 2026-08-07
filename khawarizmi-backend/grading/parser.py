"""grading/parser.py — Parsing tolérant de la réponse LLM (audit O7).

Stratégies, dans l'ordre :
    native_json  — mode JSON natif provider activé : le contenu DOIT être du
                   JSON pur (json.loads direct). Ne devrait quasi jamais
                   échouer ; si c'est le cas, on retombe sur les suivantes.
    direct       — texte libre qui est quand même du JSON (comportement actuel)
    fence        — extraction ```json ... ``` (markdown)
    regex        — premier { au dernier } (JSON tronqué/bavard)
    partial      — bloc { ... } englobant par profondeur
    failed       — aucune stratégie n'a abouti

Métrique : parse_strategy_total{strategy} — Counter in-process + log
structuré. Objectif O7 : native_json > 95 % sur les providers JSON-capables ;
si native_json < 90 % sur un provider, c'est un bug d'intégration ou un
fournisseur qui ne respecte pas son contrat (alerte).
"""

from __future__ import annotations

import json
import logging
import re
from typing import Any

logger = logging.getLogger("khawarizmi.grading_parser")

_PARSE_STATS: dict[str, int] = {}


def record_parse_strategy(strategy: str) -> None:
    """Incrémente parse_strategy_total{strategy} et logge au format métrique."""
    _PARSE_STATS[strategy] = _PARSE_STATS.get(strategy, 0) + 1
    logger.info(
        f"parse_strategy_total{{strategy={strategy}}} | total={_PARSE_STATS[strategy]}"
    )


def parse_stats() -> dict[str, int]:
    """Snapshot des compteurs de stratégies de parsing (tests / dashboard)."""
    return dict(_PARSE_STATS)


_FENCE_RE = re.compile(r"```(?:json)?\s*[\r\n]+(.+?)[\r\n]+\s*```", re.DOTALL)


def parse_correction_response(
    raw: str | None,
    *,
    json_mode_used: bool = False,
) -> tuple[dict[str, Any] | None, str]:
    """Parse la réponse LLM, retourne (dict | None, strategy).

    json_mode_used=True : la sortie a été demandée en JSON natif provider —
    le contenu est normalement du JSON pur ; on tente native_json en premier.
    """
    if not raw:
        return None, "failed"

    # Stratégie 0 — JSON natif provider
    if json_mode_used:
        try:
            result = json.loads(raw.strip())
            if isinstance(result, dict):
                return result, "native_json"
        except (json.JSONDecodeError, ValueError):
            pass  # ne devrait quasi jamais arriver — on ne crashe pas

    # Stratégie 1 — parse direct (texte libre qui est quand même du JSON)
    try:
        result = json.loads(raw.strip())
        if isinstance(result, dict):
            return result, "direct"
    except (json.JSONDecodeError, ValueError):
        pass

    # Stratégie 2 — fences markdown
    fence = _FENCE_RE.search(raw)
    if fence:
        try:
            result = json.loads(fence.group(1).strip())
            if isinstance(result, dict):
                return result, "fence"
        except (json.JSONDecodeError, ValueError):
            pass

    # Stratégie 3 — premier { au dernier } (tolérant JSON tronqué)
    start = raw.find("{")
    end = raw.rfind("}")
    if start != -1 and end != -1 and end > start:
        try:
            result = json.loads(raw[start:end + 1])
            if isinstance(result, dict):
                return result, "regex"
        except (json.JSONDecodeError, ValueError):
            pass

    # Stratégie 4 — bloc { ... } englobant (profondeur)
    depth = 0
    start_idx: int | None = None
    for i, ch in enumerate(raw):
        if ch == "{":
            start_idx = i if start_idx is None else start_idx
            depth += 1
        elif ch == "}":
            depth -= 1
            if depth == 0 and start_idx is not None:
                try:
                    result = json.loads(raw[start_idx:i + 1])
                    if isinstance(result, dict):
                        return result, "partial"
                except (json.JSONDecodeError, ValueError):
                    start_idx = None

    return None, "failed"
