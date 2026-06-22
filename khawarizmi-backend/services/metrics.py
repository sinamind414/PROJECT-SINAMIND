"""Métriques d'observabilité — logs JSON structurés.

Instrumente le pipeline chat/tuteur pour mesurer :
- Latence par étape (embedding, RAG, LLM, cache)
- Tokens consommés (input, output, total)
- Cache hit/miss rate
- Fallback activation

Usage :
    from services.metrics import MetricsCollector

    mc = MetricsCollector(user_id="42", endpoint="/api/tuteur")
    mc.start("embedding")
    # ... embedding ...
    mc.end("embedding")

    mc.start("rag")
    # ... RAG ...
    mc.end("rag")

    mc.set("tokens_input", 150)
    mc.set("tokens_output", 80)
    mc.set("cache_hit", False)

    mc.flush()  # Log JSON structuré
"""

import json
import time
import logging
from typing import Dict, Optional

logger = logging.getLogger("khawarizmi.metrics")


class MetricsCollector:
    """Collecte des métriques pour une requête unique."""

    def __init__(self, user_id: str, endpoint: str):
        self.user_id = user_id
        self.endpoint = endpoint
        self._timers: Dict[str, float] = {}
        self._durations: Dict[str, float] = {}
        self._metrics: Dict[str, any] = {}
        self._start_total = time.perf_counter()

    def start(self, step: str) -> None:
        """Démarre le chronomètre pour une étape."""
        self._timers[step] = time.perf_counter()

    def end(self, step: str) -> None:
        """Arrête le chronomètre pour une étape et enregistre la durée (ms)."""
        if step in self._timers:
            duration_ms = (time.perf_counter() - self._timers[step]) * 1000
            self._durations[step] = round(duration_ms, 2)
            del self._timers[step]
        else:
            logger.warning(f"MetricsCollector.end('{step}') sans start() correspondant")

    def set(self, key: str, value: any) -> None:
        """Enregistre une métrique arbitraire (tokens, cache_hit, etc.)."""
        self._metrics[key] = value

    def flush(self) -> Dict:
        """Log les métriques en JSON structuré et retourne le dict.

        Format de sortie (log JSON) :
        {
          "endpoint": "/api/tuteur",
          "user_id": "42",
          "total_ms": 3450.5,
          "steps": {"embedding": 22.1, "rag": 45.3, "llm": 3200.0},
          "tokens_input": 150,
          "tokens_output": 80,
          "tokens_total": 230,
          "cache_hit": false,
          "fallback_active": false,
          "timestamp": "2026-06-22T20:30:00"
        }
        """
        total_ms = round((time.perf_counter() - self._start_total) * 1000, 2)

        # Calculer tokens_total si input + output présents
        tokens_in = self._metrics.get("tokens_input", 0)
        tokens_out = self._metrics.get("tokens_output", 0)
        if tokens_in or tokens_out:
            self._metrics["tokens_total"] = tokens_in + tokens_out

        report = {
            "endpoint": self.endpoint,
            "user_id": self.user_id,
            "total_ms": total_ms,
            "steps": self._durations,
            **self._metrics,
        }

        # Log JSON structuré (une ligne = une entrée parsable)
        logger.info(f"METRICS|{json.dumps(report, ensure_ascii=False)}")
        return report


# ── Compteurs globaux (cache hit rate, fallback rate) ────────────────────────

_global_counters = {
    "chat_total": 0,
    "chat_cache_hit": 0,
    "chat_fallback": 0,
    "tuteur_total": 0,
    "tuteur_cache_hit": 0,
    "tuteur_fallback": 0,
}


def record_request(endpoint: str, cache_hit: bool, fallback: bool) -> None:
    """Enregistre une requête pour les compteurs globaux."""
    prefix = "chat" if "chat" in endpoint else "tuteur"
    _global_counters[f"{prefix}_total"] += 1
    if cache_hit:
        _global_counters[f"{prefix}_cache_hit"] += 1
    if fallback:
        _global_counters[f"{prefix}_fallback"] += 1


def get_global_stats() -> Dict:
    """Retourne les statistiques globales (pour /health ou monitoring)."""
    stats = {}
    for prefix in ["chat", "tuteur"]:
        total = _global_counters[f"{prefix}_total"]
        hits = _global_counters[f"{prefix}_cache_hit"]
        fb = _global_counters[f"{prefix}_fallback"]
        stats[prefix] = {
            "total_requests": total,
            "cache_hits": hits,
            "cache_hit_rate": round(hits / total, 3) if total > 0 else 0.0,
            "fallback_count": fb,
            "fallback_rate": round(fb / total, 3) if total > 0 else 0.0,
        }
    return stats
