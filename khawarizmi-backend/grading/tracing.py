"""grading/tracing.py — Traces distribuées OpenTelemetry (audit S2.4).

Import PAESSEUX d'opentelemetry : si la dépendance est absente, toutes les
fonctions deviennent des no-op (le système ne casse pas — cohérent avec
grading/observability.py pour Prometheus).

Instrumentation MANUELLE (spans autour des étapes clés) plutôt que
l'instrumentation automatique FastAPI : plus robuste, testable, et
n'ajoute pas de dépendances lourdes (instrumentation-*).

Configuration par env (standards OTel) :
    OTEL_SERVICE_NAME  (défaut "khawarizmi-backend")
    OTEL_EXPORTER_OTLP_ENDPOINT — si absent, ConsoleSpanExporter (logs)

Usage :
    with trace_step("grading.llm", {"verb": "analyse"}):
        ...
"""

from __future__ import annotations

import logging
import os
from collections.abc import Iterator
from contextlib import contextmanager
from typing import Any

logger = logging.getLogger("khawarizmi.tracing")

# ── Import paresseux (no-op si opentelemetry absent) ─────────────────

try:
    from opentelemetry import trace as _otel_trace
    from opentelemetry.sdk.resources import Resource
    from opentelemetry.sdk.trace import TracerProvider
    from opentelemetry.sdk.trace.export import (
        BatchSpanProcessor,
        ConsoleSpanExporter,
    )

    _ENABLED = True
except Exception:  # pragma: no cover — dépendance optionnelle
    _ENABLED = False
    _otel_trace = None

_tracer = None


def is_enabled() -> bool:
    return _ENABLED


def get_tracer():
    """Retourne le tracer du service (initialisé une fois)."""
    global _tracer
    if not _ENABLED:
        return None
    if _tracer is not None:
        return _tracer
    try:
        service_name = os.environ.get("OTEL_SERVICE_NAME", "khawarizmi-backend")
        provider = TracerProvider(resource=Resource.create({"service.name": service_name}))
        # Exporter : OTLP si endpoint configuré, sinon console (logs)
        endpoint = os.environ.get("OTEL_EXPORTER_OTLP_ENDPOINT")
        if endpoint:
            from opentelemetry.exporter.otlp.proto.http.trace_exporter import (
                OTLPSpanExporter,
            )

            provider.add_span_processor(BatchSpanProcessor(OTLPSpanExporter(endpoint=endpoint)))
        else:
            provider.add_span_processor(BatchSpanProcessor(ConsoleSpanExporter()))
        _otel_trace.set_tracer_provider(provider)
        _tracer = _otel_trace.get_tracer("khawarizmi")
    except Exception as e:
        logger.warning(f"tracing: init OTel échoué ({e}) — traces désactivées")
        _tracer = None
    return _tracer


@contextmanager
def trace_step(name: str, attributes: dict[str, Any] | None = None) -> Iterator[None]:
    """Ouvre un span nommé (no-op si OTel absent)."""
    tracer = get_tracer()
    if tracer is None:
        yield
        return
    with tracer.start_as_current_span(name, attributes=attributes or {}):
        yield


def set_span_attribute(key: str, value: Any) -> None:
    """Ajoute un attribut au span courant (no-op si absent)."""
    if not _ENABLED or _otel_trace is None:
        return
    try:
        span = _otel_trace.get_current_span()
        if span is not None and span.is_recording():
            span.set_attribute(key, value)
    except Exception:
        pass


def record_exception(exc: Exception) -> None:
    """Enregistre une exception sur le span courant (no-op si absent)."""
    if not _ENABLED or _otel_trace is None:
        return
    try:
        span = _otel_trace.get_current_span()
        if span is not None and span.is_recording():
            span.record_exception(exc)
    except Exception:
        pass
