"""
tests/test_document_analysis_v2.py

Tests d'intégration pour la route v2 du correcteur :
POST /api/document-analysis/evaluate-v2
"""

from unittest.mock import patch

import pytest

from tests.conftest import MockAsyncExecResult


@pytest.mark.asyncio
async def test_evaluate_v2_requires_auth(client):
    """Sans JWT → 401."""
    resp = await client.post(
        "/api/document-analysis/evaluate-v2",
        json={
            "scenario_id": "ch1-scenario1",
            "chapter_slug": "ch1_les_relations",
            "answers": [
                {"verb_slug": "analyse", "answer": "نلاحظ من وثيقة...", "question_id": "q1"}
            ],
        },
    )
    assert resp.status_code == 401


@pytest.mark.asyncio
async def test_evaluate_v2_scenario_not_found(client, auth_headers):
    """Scénario introuvable → 404."""
    # Par défaut, MockAsyncSession.execute() retourne MockAsyncExecResult() vide.
    resp = await client.post(
        "/api/document-analysis/evaluate-v2",
        json={
            "scenario_id": "scenario-nonexistent",
            "chapter_slug": "ch1_les_relations",
            "answers": [
                {"verb_slug": "analyse", "answer": "نلاحظ من وثيقة...", "question_id": "q1"}
            ],
        },
        headers=auth_headers,
    )
    assert resp.status_code == 404
    assert "Scénario introuvable" in resp.text


@pytest.mark.asyncio
async def test_evaluate_v2_success(client, auth_headers):
    """Route evaluate-v2 répond avec succès si DB + evaluateur mockés."""

    # 1. Préparer les données DB mockées
    scenario_row = {"id": 101, "context_ar": "السياق العام للتحليل"}
    document_row = {"title_ar": "وثيقة 1", "caption_ar": "منحنى تغيرات", "data": {}, "sort_order": 1}
    session_row = {"id": 999}
    question_row = {
        "id": "q1",
        "verb_slug": "analyse",
        "prompt_ar": "حلل الوثيقة",
        "skill_ar": "تحليل وثيقة",
        "model_answer_ar": "الإجابة النموذجية الصحيحة",
        "learning_focus_ar": "التحليل المنهجي",
    }

    from tests.conftest import MockAsyncSession
    original_execute = MockAsyncSession.execute

    # Custom execute pour renvoyer nos lignes mockées selon la requête
    async def mock_execute(self, statement, *args, **kwargs):
        sql = str(statement)
        if "da_scenarios" in sql:
            return MockAsyncExecResult([scenario_row])
        elif "da_documents" in sql:
            return MockAsyncExecResult([document_row])
        elif "da_sessions" in sql:
            return MockAsyncExecResult([session_row])
        elif "da_questions" in sql:
            return MockAsyncExecResult([question_row])
        elif "da_answers" in sql or "da_fsrs" in sql:
            return MockAsyncExecResult([{"id": 1}])
        return await original_execute(self, statement, *args, **kwargs)

    # 2. Mock du correcteur v2
    mock_eval_res = {
        "source": "llm",
        "score": 6,
        "score_max": 8,
        "percentage": 75,
        "highlights": [
            {"start": 0, "end": 5, "type": "good_element", "message_ar": "عنصر صحيح"}
        ],
        "matched_criteria": ["تقديم الوثيقة"],
        "unmatched_criteria": [],
        "feedback_ar": "تعليق ممتاز",
        "advice_ar": "نصيحة",
        "confidence": 0.9,
    }

    with (
        patch("tests.conftest.MockAsyncSession.execute", new=mock_execute),
        patch(
            "routes.document_analysis_v2.evaluate_answer_v2_with_retry",
            return_value=mock_eval_res,
        ) as mock_eval,
    ):
        resp = await client.post(
            "/api/document-analysis/evaluate-v2",
            json={
                "scenario_id": "ch1-scenario1",
                "chapter_slug": "ch1_les_relations",
                "answers": [
                    {
                        "verb_slug": "analyse",
                        "answer": "نلاحظ من خلال الوثيقة أن التغيرات واضحة",
                        "question_id": "q1",
                    }
                ],
            },
            headers=auth_headers,
        )

        assert resp.status_code == 200
        data = resp.json()
        assert data["session_id"] == "999"
        assert data["score_global"] == 6
        assert data["percentage"] == 75
        assert len(data["evaluations"]) == 1

        eval1 = data["evaluations"][0]
        assert eval1["question_id"] == "q1"
        assert eval1["verb_slug"] == "analyse"
        assert eval1["score"] == 6
        assert eval1["score_max"] == 8
        assert eval1["percentage"] == 75
        assert len(eval1["highlights"]) == 1
        assert eval1["highlights"][0]["type"] == "good_element"
        assert eval1["feedback_ar"] == "تعليق ممتاز"

        # Le correcteur v2 a bien été appelé avec les bons arguments.
        # Contrat S2.1c : le PIPELINE (evaluate_answer_v2_pipeline) appelle le
        # legacy (evaluate_answer_v2_with_retry) en construisant l'appel
        # complet : verb_slug/score_max/model_answer + precomputed_sanity.
        mock_eval.assert_called_once()
        kwargs_called = mock_eval.call_args.kwargs
        assert kwargs_called["scenario_context"] == "السياق العام للتحليل"
        assert kwargs_called["student_answer"] == "نلاحظ من خلال الوثيقة أن التغيرات واضحة"
        assert kwargs_called["verb_slug"] == "analyse"
        assert kwargs_called["score_max"] == 7
        assert kwargs_called["precomputed_sanity"] == (True, "ok", "")


async def test_evaluate_v2_cache_contract(client, auth_headers):
    """Audit C2 — la route passe au wrapper grading_cache les composants
    de la clé (question_id, verb_slug, score_max, student_answer, model_id)
    et le correcteur en tant qu'evaluate_fn. Le wrapper est mocké ici :
    on vérifie le CONTRAT d'appel de la route, pas le cache (testé ailleurs)."""
    from unittest.mock import AsyncMock

    from config import get_settings

    scenario_row = {"id": 101, "context_ar": "السياق العام للتحليل"}
    document_row = {"title_ar": "وثيقة 1", "caption_ar": "منحنى تغيرات", "data": {}, "sort_order": 1}
    session_row = {"id": 999}
    question_row = {
        "id": "q1",
        "verb_slug": "analyse",
        "prompt_ar": "حلل الوثيقة",
        "skill_ar": "تحليل وثيقة",
        "model_answer_ar": "الإجابة النموذجية الصحيحة",
        "learning_focus_ar": "التحليل المنهجي",
    }

    from tests.conftest import MockAsyncSession

    original_execute = MockAsyncSession.execute

    async def mock_execute(self, statement, *args, **kwargs):
        sql = str(statement)
        if "da_scenarios" in sql:
            return MockAsyncExecResult([scenario_row])
        elif "da_documents" in sql:
            return MockAsyncExecResult([document_row])
        elif "da_sessions" in sql:
            return MockAsyncExecResult([session_row])
        elif "da_questions" in sql:
            return MockAsyncExecResult([question_row])
        elif "da_answers" in sql or "da_fsrs" in sql or "correction_audit" in sql:
            return MockAsyncExecResult([])
        # users (auth), etc. → comportement par défaut de la session mockée
        return await original_execute(self, statement, *args, **kwargs)

    mock_eval_res = {
        "source": "llm",
        "score": 6,
        "score_max": 8,
        "percentage": 75,
        "highlights": [],
        "matched_criteria": [],
        "unmatched_criteria": [],
        "feedback_ar": "تعليق",
        "advice_ar": "",
        "confidence": 0.9,
    }

    with (
        patch("tests.conftest.MockAsyncSession.execute", new=mock_execute),
        patch(
            "routes.document_analysis_v2.evaluate_with_cache",
            new=AsyncMock(return_value=mock_eval_res),
        ) as mock_cache,
    ):
        resp = await client.post(
            "/api/document-analysis/evaluate-v2",
            json={
                "scenario_id": "ch1-scenario1",
                "chapter_slug": "ch1_les_relations",
                "answers": [
                    {
                        "verb_slug": "analyse",
                        "answer": "نلاحظ من خلال الوثيقة أن التغيرات واضحة",
                        "question_id": "q1",
                    }
                ],
            },
            headers=auth_headers,
        )

        assert resp.status_code == 200
        mock_cache.assert_called_once()
        call_kwargs = mock_cache.call_args.kwargs
        # Composants de la clé C2 — présents à l'appel du wrapper
        assert call_kwargs["question_id"] == "q1"
        assert call_kwargs["verb_slug"] == "analyse"
        assert call_kwargs["score_max"] == 7  # VERB_RULES analyse (2+2+2+1)
        assert call_kwargs["student_answer"] == "نلاحظ من خلال الوثيقة أن التغيرات واضحة"
        assert call_kwargs["model_id"] == get_settings().openai_model
        # S2.1c : le wrapper reçoit le PIPELINE comme evaluate_fn et le
        # legacy (retry) comme evaluate_legacy — le wrapper ne fait que
        # cacher, le pipeline orchestre (sanity → savoir → legacy).
        from routes.document_analysis_v2 import (
            evaluate_answer_v2_pipeline,
            evaluate_answer_v2_with_retry,
        )
        assert call_kwargs["evaluate_fn"] is evaluate_answer_v2_pipeline
        assert call_kwargs["evaluate_legacy"] is evaluate_answer_v2_with_retry
        # La copie normalisée + la version de prompt v2 partent au pipeline
        assert call_kwargs["use_v2_prompt"] is True
