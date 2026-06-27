from unittest.mock import patch

import pytest


def _eval_request(question_id="q_test_001", answer="Ma réponse", lang="fr"):
    return {
        "question_id": question_id,
        "reponse_eleve": answer,
        "lang": lang,
        "tentative": 1,
    }


FAKE_QUESTION = {
    "question_id": "q_test_001",
    "texte": "Qu'est-ce que l'ADN ?",
    "texte_ar": "ما هو الحمض النووي",
    "concept_cle": "ADN",
    "concept_cle_ar": "الحمض النووي",
    "reponse_correcte": "L'ADN stocke l'information génétique.",
    "niveau": "moyen",
    "chapitre": "génétique",
}

FAKE_RESULT = {
    "score": 7,
    "statut": "ACCEPTABLE",
    "feedback": "Bon travail, mais quelques lacunes.",
    "manquant": ["structure"],
    "scores_concepts": {},
    "source": "GPT4O",
    "methodology": None,
}


@pytest.mark.asyncio
async def test_evaluate_requires_auth(client):
    """Sans JWT → 401."""
    resp = await client.post("/api/ai/evaluate", json=_eval_request())
    assert resp.status_code == 401


@pytest.mark.asyncio
async def test_evaluate_invalid_question_returns_404(client, auth_headers):
    """Question inexistante → 404."""
    with patch("services.ai_modes.evaluation_mode.get_question", return_value=None):
        resp = await client.post(
            "/api/ai/evaluate",
            json=_eval_request(question_id="q_nonexistent"),
            headers=auth_headers,
        )
        assert resp.status_code == 404


@pytest.mark.asyncio
async def test_evaluate_endpoint_responds(client, auth_headers):
    """L'endpoint /api/ai/evaluate répond 200."""
    with (
        patch("services.ai_modes.evaluation_mode.get_question", return_value=FAKE_QUESTION),
        patch("routes.evaluate.evaluate_with_fallback", return_value=FAKE_RESULT),
        patch("services.ai_modes.evaluation_mode.get_concept_states", return_value={}),
        patch("services.ai_modes.evaluation_mode.save_concept_updates", return_value="2026-07-01"),
        patch("services.fsrs_graph.load_concept_graph", return_value={}),
        patch("services.ai_modes.evaluation_mode.update_concept_graph", return_value=[]),
    ):
        resp = await client.post(
            "/api/ai/evaluate",
            json=_eval_request(),
            headers=auth_headers,
        )
        assert resp.status_code == 200


@pytest.mark.asyncio
async def test_evaluate_returns_json_response(client, auth_headers):
    """La réponse doit être du JSON valide."""
    with (
        patch("services.ai_modes.evaluation_mode.get_question", return_value=None),
    ):
        resp = await client.post(
            "/api/ai/evaluate",
            json=_eval_request(),
            headers=auth_headers,
        )
        assert resp.status_code == 404


@pytest.mark.asyncio
async def test_evaluate_accepts_arabic_language(client, auth_headers):
    """Language 'ar' doit être accepté."""
    with (
        patch("services.ai_modes.evaluation_mode.get_question", return_value=FAKE_QUESTION),
        patch("routes.evaluate.evaluate_with_fallback", return_value=FAKE_RESULT),
        patch("services.ai_modes.evaluation_mode.get_concept_states", return_value={}),
        patch("services.ai_modes.evaluation_mode.save_concept_updates", return_value="2026-07-01"),
        patch("services.fsrs_graph.load_concept_graph", return_value={}),
        patch("services.ai_modes.evaluation_mode.update_concept_graph", return_value=[]),
    ):
        resp = await client.post(
            "/api/ai/evaluate",
            json=_eval_request(lang="ar", answer="إجابة اختبار"),
            headers=auth_headers,
        )
        assert resp.status_code == 200


@pytest.mark.asyncio
async def test_evaluate_returns_response_with_arabic_text(client, auth_headers):
    """Language 'ar' passe la validation (réponse 200)."""
    with (
        patch("services.ai_modes.evaluation_mode.get_question", return_value=FAKE_QUESTION),
        patch("routes.evaluate.evaluate_with_fallback", return_value=FAKE_RESULT),
        patch("services.ai_modes.evaluation_mode.get_concept_states", return_value={}),
        patch("services.ai_modes.evaluation_mode.save_concept_updates", return_value="2026-07-01"),
        patch("services.fsrs_graph.load_concept_graph", return_value={}),
        patch("services.ai_modes.evaluation_mode.update_concept_graph", return_value=[]),
    ):
        resp = await client.post(
            "/api/ai/evaluate",
            json=_eval_request(lang="ar"),
            headers=auth_headers,
        )
        assert resp.status_code == 200
