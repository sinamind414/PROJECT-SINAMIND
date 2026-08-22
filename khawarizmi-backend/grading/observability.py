"""grading/observability.py — Métriques Prometheus (audit S2.3).

Expose les métriques du pipeline et du chatbot au format Prometheus
(/metrics/prometheus). Import PAESSEUX de prometheus_client : si la
dépendance est absente, toutes les fonctions deviennent des no-op (le
système ne casse pas).

Métriques exposées (labels à cardinalité bornée : verb ~15, provider ~7,
strategy ~6, result ~5, step ~5) :
- grading_source_total{source, verb}        — d'où vient la note finale
- parse_strategy_total{strategy, provider}  — stratégies de parsing (O7)
- correction_cache_ops_total{result, verb}  — opérations du cache (C2)
- grading_pipeline_events_total{event}      — sanity_reject / savoir_promoted /
                                             l2_fallback / llm_error / llm_ok
- grading_llm_latency_seconds               — histogramme latence LLM
- chatbot_messages_total{intent, type}      — messages classés
- chatbot_step_duration_ms{step}            — histogramme étapes chatbot
"""

from __future__ import annotations

import logging
from typing import Any

logger = logging.getLogger("khawarizmi.observability")

# ── Import paresseux (no-op si prometheus-client absent) ─────────────

try:
    from prometheus_client import (
        Counter,
        Gauge,
        Histogram,
        generate_latest,
    )

    _ENABLED = True
except Exception:  # pragma: no cover — dépendance optionnelle
    _ENABLED = False
    Counter = Gauge = Histogram = generate_latest = None  # type: ignore[assignment,misc]


def is_enabled() -> bool:
    return _ENABLED


# ── Définition des métriques (une seule fois à l'import) ─────────────

if _ENABLED:
    _grading_source = Counter(
        "grading_source_total",
        "Source de la note finale (local_savoir, llm, sanity…)",
        ["source", "verb"],
    )
    _parse_strategy = Counter(
        "parse_strategy_total",
        "Stratégie de parsing de la réponse LLM",
        ["strategy", "provider"],
    )
    _cache_ops = Counter(
        "correction_cache_ops_total",
        "Opérations du cache de correction",
        ["result", "verb"],
    )
    _pipeline_events = Counter(
        "grading_pipeline_events_total",
        "Événements du pipeline de correction",
        ["event"],
    )
    _llm_latency = Histogram(
        "grading_llm_latency_seconds",
        "Latence de l'appel LLM (secondes)",
        buckets=(0.1, 0.5, 1.0, 2.0, 5.0, 10.0, 20.0, 30.0, float("inf")),
    )
    _chatbot_messages = Counter(
        "chatbot_messages_total",
        "Messages chatbot classés",
        ["intent", "type"],
    )
    _chatbot_step = Histogram(
        "chatbot_step_duration_ms",
        "Durée des étapes chatbot (ms)",
        ["step"],
        buckets=(5, 20, 50, 100, 250, 500, 1000, 3000, float("inf")),
    )
    # Budget LLM (G0-3) : coût du jour UTC + état de coupure.
    _llm_budget_cost = Gauge(
        "llm_budget_day_cost_usd",
        "Coût LLM externe du jour UTC (USD)",
    )
    _llm_budget_killed = Gauge(
        "llm_budget_auto_killed",
        "1 = LLM externe coupé (budget journalier dépassé)",
    )
    _llm_budget_kills = Counter(
        "llm_budget_kills_total",
        "Nombre de coupures budget (BUDGET_KILL)",
    )
else:  # pragma: no cover — no-op
    _grading_source = _parse_strategy = _cache_ops = _pipeline_events = None
    _llm_latency = _chatbot_messages = _chatbot_step = None
    _llm_budget_cost = _llm_budget_killed = _llm_budget_kills = None


# ── Fonctions d'enregistrement (no-op si désactivé) ──────────────────

def record_grading_source(source: str, verb: str) -> None:
    if _ENABLED:
        _grading_source.labels(source=source, verb=verb).inc()


def record_parse_strategy(strategy: str, provider: str) -> None:
    if _ENABLED:
        _parse_strategy.labels(strategy=strategy, provider=provider).inc()


def record_cache_op(result: str, verb: str) -> None:
    if _ENABLED:
        _cache_ops.labels(result=result, verb=verb).inc()


def record_pipeline_event(event: str) -> None:
    if _ENABLED:
        _pipeline_events.labels(event=event).inc()


def observe_llm_latency(seconds: float) -> None:
    if _ENABLED and seconds >= 0:
        _llm_latency.observe(seconds)


def record_chatbot_message(intent: str, resp_type: str) -> None:
    if _ENABLED:
        _chatbot_messages.labels(intent=intent, type=resp_type).inc()


def observe_chatbot_step(step: str, duration_ms: float) -> None:
    if _ENABLED and duration_ms >= 0:
        _chatbot_step.labels(step=step).observe(duration_ms)


def observe_llm_budget(day_cost_usd: float, auto_killed: bool) -> None:
    """État du budget LLM (G0-3) — appelé par services/llm_budget."""
    if _ENABLED:
        _llm_budget_cost.set(day_cost_usd)
        _llm_budget_killed.set(1.0 if auto_killed else 0.0)


def record_budget_kill() -> None:
    """Une coupure budget (BUDGET_KILL) a eu lieu (G0-3)."""
    if _ENABLED:
        _llm_budget_kills.inc()


def metrics_text() -> str:
    """Texte Prometheus (format exposition) — vide si désactivé."""
    if not _ENABLED:
        return ""
    return generate_latest().decode("utf-8")


def metrics_summary() -> dict[str, Any]:
    """Snapshot JSON des compteurs (dashboard interne / tests)."""
    if not _ENABLED:
        return {"enabled": False}
    from prometheus_client import REGISTRY

    out: dict[str, Any] = {"enabled": True}
    # NB : metric.name est le nom de BASE (le suffixe _total est ajouté à
    # l'exposition pour les counters) — on filtre sur les noms de base.
    for metric in REGISTRY.collect():
        if metric.name in ("grading_source", "parse_strategy",
                           "correction_cache_ops",
                           "grading_pipeline_events",
                           "chatbot_messages",
                           "llm_budget_cost", "llm_budget_killed",
                           "llm_budget_kills"):
            samples: dict[str, float] = {}
            for s in metric.samples:
                # Ignorer le sample *_created (gauge timestamp) — seule la
                # VALEUR du compteur nous intéresse.
                if s.name.endswith("_created"):
                    continue
                key = ",".join(f"{k}={v}" for k, v in s.labels.items()) or "none"
                samples[key] = s.value
            out[metric.name] = samples
    return out
