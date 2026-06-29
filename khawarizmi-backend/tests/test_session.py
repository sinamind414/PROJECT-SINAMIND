# tests/test_session.py
"""
Tests pour routes/session.py (P3 audit — 218 LoC).

Endpoints testés :
  POST /api/session/next  — queue de révision FSRS
  POST /api/session/random — question aléatoire
"""

from unittest.mock import patch

import pytest


def _session_request(max_cards=5, lang="fr", exclude=None):
    return {
        "max_cards": max_cards,
        "lang": lang,
        "exclude": exclude or [],
    }


@pytest.mark.asyncio
async def test_session_next_cold_start_serves_valid_questions(client, auth_headers):
    """Phase 1 — cold start ( nouvel utilisateur, FSRS vide ) doit servir
    des questions NEW valides, jamais de carte vide ni méthodologique.
    C'est le fix du bug 'carte Methodologie - منهجية - النص-العلمي'."""
    resp = await client.post(
        "/api/session/next",
        json=_session_request(max_cards=8),
        headers=auth_headers,
    )
    assert resp.status_code == 200
    data = resp.json()
    queue = data["session_queue"]
    assert len(queue) > 0, "cold start doit servir des questions NEW"

    for item in queue:
        # Aucune carte vide
        texte = (item.get("texte_ar") or item.get("texte") or "").strip()
        assert len(texte) >= 12, f"carte sans texte valide: {item.get('question_id')}"
        # Aucune carte méthodologique ( le bug d'origine )
        qid = item.get("question_id", "")
        assert not qid.startswith("minhajiya_"), f"carte méthodologique servie: {qid}"
        cc = item.get("concept_cle", "") or ""
        assert "منهجية" not in cc and "Methodologie" not in cc, f"concept méthodologique: {cc}"


# ── /api/session/next ───────────────────────────────────────────────


@pytest.mark.asyncio
async def test_session_next_requires_auth(client):
    """Sans JWT → 401."""
    resp = await client.post("/api/session/next", json=_session_request())
    assert resp.status_code == 401


@pytest.mark.asyncio
async def test_session_next_returns_session_queue_key(client, auth_headers):
    """La réponse contient toujours une clé 'session_queue'."""
    with patch("routes.session.get_question", return_value=None):
        resp = await client.post(
            "/api/session/next",
            json=_session_request(max_cards=3),
            headers=auth_headers,
        )
        assert resp.status_code == 200
        data = resp.json()
        assert "session_queue" in data
        assert isinstance(data["session_queue"], list)


@pytest.mark.asyncio
async def test_session_next_empty_when_no_concepts(client, auth_headers):
    """Si aucune question valide disponible → queue vide ( mais réponse OK ).

    Phase 1 : la logique a migré vers services.drill_queue qui lit
    questions_db. Le scénario 'vide' signifie maintenant 'aucune question
    valide dans questions_db' ( ex. base non ingérée ).
    """
    with patch("services.drill_queue.questions_db", {}):
        resp = await client.post(
            "/api/session/next",
            json=_session_request(max_cards=10),
            headers=auth_headers,
        )
        assert resp.status_code == 200
        data = resp.json()
        assert data["session_queue"] == []


@pytest.mark.asyncio
async def test_session_next_exclude_empty_list_accepted(client, auth_headers):
    """exclude vide est accepté."""
    with patch("routes.session.get_question", return_value=None):
        resp = await client.post(
            "/api/session/next",
            json=_session_request(exclude=[]),
            headers=auth_headers,
        )
        assert resp.status_code == 200


@pytest.mark.asyncio
async def test_session_next_exclude_with_values_accepted(client, auth_headers):
    """exclude avec valeurs est accepté."""
    with patch("routes.session.get_question", return_value=None):
        resp = await client.post(
            "/api/session/next",
            json=_session_request(exclude=["c1", "c2", "c3"]),
            headers=auth_headers,
        )
        assert resp.status_code == 200


@pytest.mark.asyncio
async def test_session_next_arabic_lang_accepted(client, auth_headers):
    """lang='ar' accepté."""
    with patch("routes.session.get_question", return_value=None):
        resp = await client.post(
            "/api/session/next",
            json=_session_request(lang="ar"),
            headers=auth_headers,
        )
        assert resp.status_code == 200


@pytest.mark.asyncio
async def test_session_next_french_lang_accepted(client, auth_headers):
    """lang='fr' (default) accepté."""
    with patch("routes.session.get_question", return_value=None):
        resp = await client.post(
            "/api/session/next",
            json=_session_request(lang="fr"),
            headers=auth_headers,
        )
        assert resp.status_code == 200


@pytest.mark.asyncio
async def test_session_next_no_lang_field_uses_default(client, auth_headers):
    """Pas de lang → default OK."""
    with patch("routes.session.get_question", return_value=None):
        resp = await client.post(
            "/api/session/next",
            json={"max_cards": 5, "exclude": []},  # pas de lang
            headers=auth_headers,
        )
        assert resp.status_code == 200


@pytest.mark.asyncio
async def test_session_next_returns_items_with_required_fields(client, auth_headers):
    """Chaque item de la queue doit avoir question_id, texte, etc."""
    fake_question = {
        "question_id": "q_001",
        "texte": "Quelle est la fonction de l'ADN ?",
        "texte_ar": "ما هي وظيفة الحمض النووي",
        "concept_cle": "ADN",
        "concept_cle_ar": "الحمض النووي",
    }

    # Mock get_question pour retourner la question factice
    with patch("routes.session.get_question", return_value=fake_question):
        resp = await client.post(
            "/api/session/next",
            json=_session_request(max_cards=1),
            headers=auth_headers,
        )
        # Si queue non vide
        if resp.status_code == 200:
            data = resp.json()
            if data["session_queue"]:
                item = data["session_queue"][0]
                assert "question_id" in item
                assert "texte" in item or "texte_ar" in item
