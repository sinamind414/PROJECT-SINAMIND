"""tests/test_tracing.py — Traces OpenTelemetry (audit S2.4).

- Import paresseux : no-op si la dépendance est absente (aucune erreur).
- Spans réels : le pipeline et le chatbot émettent des spans (vérifié via
  InMemorySpanExporter — provider configuré UNE FOIS, module-scope, car
  OTel interdit de remplacer le TracerProvider global).
- Les hooks (trace_step, set_span_attribute, record_exception) ne lèvent
  jamais, même sans tracer configuré.
"""

import pytest

from grading import tracing
from grading.tracing import is_enabled, record_exception, set_span_attribute, trace_step


class TestNoOp:
    def test_trace_step_without_tracer(self, monkeypatch):
        """Sans tracer configuré (get_tracer → None) : pas d'erreur."""
        monkeypatch.setattr(tracing, "get_tracer", lambda: None)
        with trace_step("test.step", {"a": 1}):
            pass  # ne doit pas lever

    def test_set_attribute_without_enabled(self, monkeypatch):
        monkeypatch.setattr(tracing, "_ENABLED", False)
        set_span_attribute("k", "v")  # ne doit pas lever

    def test_record_exception_without_enabled(self, monkeypatch):
        monkeypatch.setattr(tracing, "_ENABLED", False)
        record_exception(ValueError("boom"))  # ne doit pas lever


# ── Tracer OTel mocké (module-scope) ────────────────────────────────
# On ne configure pas le provider global : get_tracer est mocké avec un
# exporter mémoire, isolé et sans thread/log de console.

@pytest.fixture(scope="module")
def otel_exporter():
    """Mocke get_tracer → tracer lié à InMemorySpanExporter."""
    if not is_enabled():
        yield None
        return
    from opentelemetry.sdk.trace import TracerProvider
    from opentelemetry.sdk.trace.export import SimpleSpanProcessor
    from opentelemetry.sdk.trace.export.in_memory_span_exporter import (
        InMemorySpanExporter,
    )

    exporter = InMemorySpanExporter()
    provider = TracerProvider()
    provider.add_span_processor(SimpleSpanProcessor(exporter))
    tracer = provider.get_tracer("khawarizmi-test")

    original = tracing.get_tracer
    tracing.get_tracer = lambda: tracer  # type: ignore[method-assign]
    try:
        yield exporter
    finally:
        tracing.get_tracer = original  # type: ignore[method-assign]


@pytest.mark.skipif(not is_enabled(), reason="opentelemetry absent")
class TestRealSpans:
    def test_trace_step_creates_span(self, otel_exporter):
        otel_exporter.clear()
        with trace_step("test.etape", {"cle": "valeur"}):
            pass
        spans = otel_exporter.get_finished_spans()
        assert len(spans) == 1
        assert spans[0].name == "test.etape"
        assert spans[0].attributes["cle"] == "valeur"

    def test_pipeline_emits_spans(self, otel_exporter):
        """Le pipeline complet émet des spans grading.sanity + grading.savoir."""
        import asyncio
        from unittest.mock import MagicMock

        from grading.pipeline import evaluate_answer_v2_pipeline

        async def llm_mock(**kwargs):
            resp = MagicMock()
            resp.choices = [MagicMock()]
            resp.choices[0].message.content = (
                '{"score": 75, "errors": [], "feedback": "f", "grade": "acquis"}'
            )
            resp.choices[0].finish_reason = "stop"
            resp._khawarizmi_json_mode = True
            resp._khawarizmi_provider = "primary"
            resp._khawarizmi_model = "test"
            return resp

        otel_exporter.clear()
        asyncio.run(evaluate_answer_v2_pipeline(
            question_id=1, verb_slug="analyse", score_max=8,
            student_answer="الاستنساخ يتم في النواة والترجمة في الهيولى",
            model_answer="modèle", question_prompt="حلل",
            question_skill="analyse", llm_call=llm_mock,
            primary_client=MagicMock(), primary_model="test",
            use_v2_prompt=True,
        ))
        spans = otel_exporter.get_finished_spans()
        names = {s.name for s in spans}
        assert "grading.sanity" in names
        assert "grading.savoir" in names

    def test_chatbot_emits_span(self, otel_exporter):
        import asyncio
        from unittest.mock import AsyncMock, MagicMock, patch

        from services.chatbot_orchestrator import handle_chatbot_message

        async def run():
            await handle_chatbot_message(
                "ما هو دور ADN؟", {}, 1, AsyncMock(), MagicMock(), mode="quick"
            )

        with patch("services.chatbot_handlers.get_semantic_cache",
                   new=AsyncMock(return_value=None)), \
             patch("services.chatbot_handlers.call_llm",
                   new=AsyncMock(return_value="réponse")), \
             patch("services.chatbot_handlers.calculer_orientation",
                   new=AsyncMock(return_value={})), \
             patch("services.chatbot_handlers.rag_search",
                   new=AsyncMock(return_value=[])), \
             patch("services.chatbot_engagement_service.record_chat_interaction",
                   new=AsyncMock()):
            otel_exporter.clear()
            asyncio.run(run())

        spans = otel_exporter.get_finished_spans()
        names = {s.name for s in spans}
        assert "chatbot.handle" in names
