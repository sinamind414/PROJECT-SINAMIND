"""grading/metrics.py — Métriques du pipeline de correction (audit S2.1c).

Compteurs in-process + logs structurés au format labelisé. Le cache wrapper
(grading/cache.py) conserve ses propres compteurs cache (grading_cache_stats) ;
les métriques de SOURCE de notation vivent ici (appelées par le pipeline).

- grading_source_total{source, verb_slug} : d'où vient la note finale
  (local_savoir, llm, llm_v2, sanity, cached_evaluation…). Objectif prod :
  ratio local_savoir / total > 15 % après activation [1-2 verbes], corrélé
  négativement à llm_tokens_total.
"""

from __future__ import annotations

import logging
from typing import Any

logger = logging.getLogger("khawarizmi.grading_metrics")

_grading_sources: dict[str, int] = {}
_grading_sources_by_verb: dict[str, dict[str, int]] = {}


def record_grading_source(source: str, verb_slug: str) -> None:
    """Compteur de source de notation (local_savoir, cache, llm, sanity…)."""
    _grading_sources[source] = _grading_sources.get(source, 0) + 1
    verb_map = _grading_sources_by_verb.setdefault(verb_slug, {})
    verb_map[source] = verb_map.get(source, 0) + 1
    logger.info(
        f"grading_source_total{{source={source},verb={verb_slug}}} "
        f"| total={_grading_sources[source]}"
    )
    # S2.3 : alimente aussi Prometheus (no-op si dépendance absente)
    from grading.observability import record_grading_source as _prom_record

    _prom_record(source, verb_slug)


def grading_source_stats() -> dict[str, Any]:
    """Snapshot des compteurs de sources (tests / dashboard)."""
    return {
        "total": dict(_grading_sources),
        "by_verb": {v: dict(m) for v, m in _grading_sources_by_verb.items()},
    }
