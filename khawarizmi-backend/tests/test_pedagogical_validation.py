import pytest

from services.pedagogical_validation import grading_validation_status


def test_synthetic_golden_never_claims_human_validation():
    status = grading_validation_status()
    assert status["annotation_type"] == "synthetic_keyword_based"
    assert status["human_validated"] is False
    assert status["scope"] == "formative_only"
    assert "non certificatives" in status["message_fr"]


@pytest.mark.asyncio
async def test_legacy_document_corrector_is_not_mounted(client, auth_headers):
    response = await client.post(
        "/api/document-analysis/evaluate",
        headers=auth_headers,
        json={"scenario_id": "x", "answers": []},
    )
    assert response.status_code in {404, 405}
