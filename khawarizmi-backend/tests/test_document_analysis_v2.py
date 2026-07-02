"""
tests/test_document_analysis_v2.py

Tests d'intégration pour la route v2 du correcteur :
POST /api/document-analysis/evaluate-v2
"""

from unittest.mock import AsyncMock, patch

import pytest

from tests.conftest import MockAsyncExecResult, MockRow


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
            "routes.document_analysis_v2.evaluate_answer_v2",
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

        # Le correcteur v2 a bien été appelé avec les bons arguments
        mock_eval.assert_called_once()
        kwargs_called = mock_eval.call_args.kwargs
        assert kwargs_called["scenario_context"] == "السياق العام للتحليل"
        assert kwargs_called["verb_slug"] == "analyse"
        assert kwargs_called["student_answer"] == "نلاحظ من خلال الوثيقة أن التغيرات واضحة"
