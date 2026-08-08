"""routes/observability.py — Exposition Prometheus (audit S2.3).

- GET /metrics/prometheus : texte Prometheus (format d'exposition) — les
  métriques du pipeline (grading_source, parse_strategy, cache ops,
  événements, latence LLM) et du chatbot (messages, étapes). Vide (200)
  si prometheus-client est absent (mode no-op).

Note : /metrics (JSON gamification) est déjà utilisé par routes/phase6.py —
le path /metrics/prometheus évite le conflit.
"""

from __future__ import annotations

from fastapi import APIRouter
from fastapi.responses import PlainTextResponse

from grading.observability import metrics_text

router = APIRouter(tags=["Observabilité"])


@router.get("/metrics/prometheus")
async def prometheus_metrics() -> PlainTextResponse:
    """Métriques au format Prometheus (scrape endpoint)."""
    return PlainTextResponse(
        metrics_text(),
        media_type="text/plain; version=0.0.4; charset=utf-8",
    )
