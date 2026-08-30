"""POST /api/document-analysis/evaluate-v2 — gelé vers grade() (S6).

Les tests LLM/L2 d'origine sont caducs. Auth + 404 restent.
"""

import pytest


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
