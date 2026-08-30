"""Tests /api/evaluate/methodology — GELÉ (0 LLM, grade() seul juge).

Réaligné S36 (audit 2026-08-30 F8) : l'ancien évaluateur LLM (verb/task_type)
a été remplacé par grade_or_none → ces tests verrouillent le contrat as-built :
auth requise, 422 ungraded sans Rubric L0, to_verb_eval sinon, même quota
que /api/grade. Avant le gel : 200 + champs « verb » / « task_type ».
"""

from fastapi.testclient import TestClient

from deps import get_current_user
from main import app
from services.rubric_store import load

client = TestClient(app)


def _auth(payload: dict) -> dict:
    return payload


def _with_auth(override_user=True):
    """Active la surcharge d'auth pour les tests (nettoyée en finally)."""
    if override_user:
        app.dependency_overrides[get_current_user] = lambda: {
            "id": 1,
            "email": "test@khawarizmi.dz",
            "plan": "free",
        }


def _clear_auth() -> None:
    app.dependency_overrides.pop(get_current_user, None)


def _l0_payload() -> dict:
    packed = load("manhadjiya-yeast-analyse")
    assert packed is not None
    return {
        "question_id": "manhadjiya-yeast-analyse",
        "student_answer": packed.rubric.model_answer,
    }


def test_methodology_requires_auth():
    """S36 : sans token → 401 (avant : surface anonyme)."""
    response = client.post("/api/evaluate/methodology", json=_l0_payload())
    assert response.status_code == 401


def test_methodology_with_rubric_returns_verb_eval():
    """Avec question_id L0 → 200, to_verb_eval (0 LLM), pas de verb/task_type."""
    _with_auth()
    try:
        response = client.post("/api/evaluate/methodology", json=_l0_payload())
        assert response.status_code == 200
        data = response.json()
        assert data["source"] == "local_rubric"
        assert data["verb_slug"] == "analyse"
        assert data["method_percent"] == 100
        assert "banner_ar" in data
        assert "ليست علامة بكالوريا رسمية" in data["banner_ar"]
        # l'ancien contrat LLM est bien mort
        assert "verb" not in data
        assert "task_type" not in data
    finally:
        _clear_auth()


def test_methodology_without_question_id_ungraded():
    """Sans question_id → 422 ungraded (jamais 0, jamais fallback regex)."""
    _with_auth()
    try:
        response = client.post(
            "/api/evaluate/methodology",
            json={"student_answer": "الغلوكوز مادة أيض"},
        )
        assert response.status_code == 422
        data = response.json()
        assert data["code"] == "ungraded"
        assert data["status"] == 422
    finally:
        _clear_auth()


def test_methodology_unknown_question_id_ungraded():
    """Question_id inconnu → 422 ungraded, pas de note inventée."""
    _with_auth()
    try:
        response = client.post(
            "/api/evaluate/methodology",
            json={"question_id": "verb:analyse", "student_answer": "نلاحظ ارتفاع"},
        )
        assert response.status_code == 422
        assert response.json()["code"] == "ungraded"
    finally:
        _clear_auth()


def test_methodology_wires_shared_quota():
    """S36 : même budget que /api/grade — décision pure + application partagée."""
    from pathlib import Path

    src = (
        Path(__file__).resolve().parent.parent / "routes" / "methodology.py"
    ).read_text(encoding="utf-8")
    assert "get_current_user" in src
    assert "should_count_quota" in src
    assert "enforce_evaluate_quota" in src
