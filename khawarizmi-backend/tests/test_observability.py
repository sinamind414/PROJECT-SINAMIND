"""tests/test_observability.py — Observabilité Prometheus (audit S2.3).

- Les compteurs s'incrémentent et apparaissent dans le texte Prometheus.
- La route /metrics/prometheus répond 200 text/plain.
- Mode no-op si la dépendance est absente (monkeypatch _ENABLED=False) :
  aucune erreur, texte vide.
- Les hooks du pipeline/parser/cache alimentent Prometheus (via les
  fonctions existantes record_*).
"""


import pytest

from grading import cache as grading_cache
from grading import metrics as grading_metrics
from grading import parser as grading_parser
from grading.observability import (
    is_enabled,
    metrics_summary,
    metrics_text,
    observe_llm_latency,
    record_cache_op,
    record_chatbot_message,
    record_grading_source,
    record_parse_strategy,
    record_pipeline_event,
)

pytestmark = pytest.mark.skipif(
    not is_enabled(), reason="prometheus-client absent"
)


class TestObservabilityModule:
    def test_enabled(self):
        assert is_enabled() is True

    def test_record_grading_source_appears_in_text(self):
        before = metrics_text()
        record_grading_source("local_savoir", "analyse")
        after = metrics_text()
        assert "grading_source_total" in after
        assert after != before or "local_savoir" in after

    def test_all_counters_in_summary(self):
        record_parse_strategy("native_json", "primary")
        record_cache_op("hit", "analyse")
        record_pipeline_event("llm_ok")
        record_chatbot_message("sos_concept", "socratique")
        summary = metrics_summary()
        assert summary["enabled"] is True
        # NB : metric.name est le nom de BASE (le _total est ajouté à l'expo)
        assert "grading_source" in summary
        assert "parse_strategy" in summary
        assert "correction_cache_ops" in summary
        assert "grading_pipeline_events" in summary
        assert "chatbot_messages" in summary

    def test_observe_llm_latency(self):
        # Ne doit pas lever (histogramme)
        observe_llm_latency(0.5)
        observe_llm_latency(-1)  # négatif ignoré
        assert "grading_llm_latency_seconds" in metrics_text()

    def test_noop_when_disabled(self, monkeypatch):
        """Mode no-op : aucune erreur, texte vide."""
        import grading.observability as obs

        monkeypatch.setattr(obs, "_ENABLED", False)
        assert obs.metrics_text() == ""
        assert obs.metrics_summary() == {"enabled": False}
        obs.record_grading_source("llm", "analyse")  # ne doit pas lever
        obs.observe_llm_latency(1.0)
        obs.record_chatbot_message("x", "y")


class TestHooks:
    def _value(self, metric_name: str, label: str) -> float:
        """Valeur d'un compteur Prometheus par (nom de base, label)."""
        summary = metrics_summary()
        samples = summary.get(metric_name, {})
        return samples.get(label, 0.0)

    def test_grading_metrics_hook_feeds_prometheus(self):
        """record_grading_source (grading/metrics.py) alimente Prometheus."""
        label = "source=llm_v2,verb=interpret"
        before = self._value("grading_source", label)
        grading_metrics.record_grading_source("llm_v2", "interpret")
        after = self._value("grading_source", label)
        assert after >= before + 1

    def test_parser_hook_feeds_prometheus(self):
        label = "strategy=fence,provider=groq"
        before = self._value("parse_strategy", label)
        grading_parser.record_parse_strategy("fence", "groq")
        after = self._value("parse_strategy", label)
        assert after >= before + 1

    def test_cache_hook_feeds_prometheus(self):
        label = "result=miss,verb=analyse"
        before = self._value("correction_cache_ops", label)
        grading_cache._record("miss", "analyse")
        after = self._value("correction_cache_ops", label)
        assert after >= before + 1


class TestRoute:
    @pytest.mark.asyncio
    async def test_metrics_route_returns_text(self, client):
        resp = await client.get("/metrics/prometheus")
        assert resp.status_code == 200
        assert "text/plain" in resp.headers["content-type"]
        assert "grading_source_total" in resp.text

    @pytest.mark.asyncio
    async def test_metrics_route_does_not_conflict_with_gamification(self, client):
        """/metrics n'est PAS le path Prometheus (pas de conflit de route) :
        il répond autre chose (404 ici — phase6 non monté dans le test) et
        surtout PAS le texte Prometheus."""
        resp = await client.get("/metrics")
        assert resp.status_code != 200 or "grading_source_total" not in resp.text
