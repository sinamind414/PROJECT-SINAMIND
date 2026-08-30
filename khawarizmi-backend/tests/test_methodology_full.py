"""Tests complets Methodology Evaluator V2 — Semaine 8

Évaluateur LLM GELÉ : /api/evaluate/methodology = grade_or_none (0 LLM),
auth requise + 422 ungraded sans Rubric L0 (réaligné S36, audit 2026-08-30 F8).
"""

from fastapi.testclient import TestClient

from deps import get_current_user
from main import app
from services.rubric_store import load

client = TestClient(app)


def _auth_on():
    app.dependency_overrides[get_current_user] = lambda: {
        "id": 1, "email": "test@khawarizmi.dz", "plan": "free",
    }


def _auth_off():
    app.dependency_overrides.pop(get_current_user, None)


def test_methodology_evaluator_complex_verb():
    """GEL : sans Rubric L0 → 422 ungraded (avant : 200 + task_type complex)."""
    _auth_on()
    try:
        payload = {
            "instruction": "وضّح في نص علمي كيف يتم التركيب الضوئي",
            "student_answer": "مقدمة: التركيب الضوئي هو... عرض: خاتمة:",
            "documents": [],
        }
        response = client.post("/api/evaluate/methodology", json=payload)
        assert response.status_code == 422
        assert response.json()["code"] == "ungraded"
    finally:
        _auth_off()


def test_methodology_evaluator_simple_verb():
    """GEL : avec Rubric L0 → 200 to_verb_eval, 0 LLM (avant : 200 + verb صف)."""
    _auth_on()
    try:
        packed = load("manhadjiya-yeast-analyse")
        assert packed is not None
        payload = {
            "question_id": "manhadjiya-yeast-analyse",
            "student_answer": packed.rubric.model_answer,
        }
        response = client.post("/api/evaluate/methodology", json=payload)
        assert response.status_code == 200
        data = response.json()
        assert data["source"] == "local_rubric"
        assert data["verb_slug"] == "analyse"
        assert data["method_percent"] == 100
    finally:
        _auth_off()


def test_methodology_evaluator_missing_verb():
    """GEL : sans token → 401 (avant : 200 + verb unknown). S36 auth."""
    response = client.post("/api/evaluate/methodology", json={"student_answer": "x"})
    assert response.status_code == 401


def test_diagnostic_report():
    """Test du rapport de diagnostic"""
    payload = {
        "verb": "وضّح في نص علمي",
        "task_type": "complex",
        "structure": {"structure_score": 12, "has_intro": True, "has_development": True, "has_conclusion": True},
        "doc_usage": {"usage_quality": "good"},
        "student_answer": "Reponse complete",
        "previous_answers": []
    }
    response = client.post("/api/diagnostic/report", json=payload)
    assert response.status_code == 200


def test_tutor_explain_mode():
    """GEL 2026-08-17 : routes/tutor.py retiré du registre (audit endpoints
    morts) → 404. Avant le gel : 200 + champ « explanation »."""
    payload = {
        "instruction": "وضّح في نص علمي",
        "mode": "explain"
    }
    response = client.post("/api/tutor/methodology", json=payload)
    assert response.status_code == 404


def test_tutor_correct_mode():
    """GEL : idem → 404 (avant : 200)."""
    payload = {
        "instruction": "وضّح في نص علمي",
        "student_answer": "Ma reponse",
        "mode": "correct"
    }
    response = client.post("/api/tutor/methodology", json=payload)
    assert response.status_code == 404


def test_tutor_diagnose_mode():
    """GEL : idem → 404 (avant : 200)."""
    payload = {
        "instruction": "وضّح في نص علمي",
        "student_answer": "Ma reponse",
        "mode": "diagnose"
    }
    response = client.post("/api/tutor/methodology", json=payload)
    assert response.status_code == 404


def test_bac_blanc_feedback():
    """GEL : routes/bac_blanc_intelligent.py retiré du registre → 404 (avant : 200)."""
    payload = {
        "context": "Test",
        "instruction": "وضّح في نص علمي",
        "student_answer": "Introduction... Developpement... Conclusion...",
        "documents": []
    }
    response = client.post("/api/bac-blanc/feedback", json=payload)
    assert response.status_code == 404


def test_bac_blanc_action_plan():
    """GEL : idem → 404 (avant : 200)."""
    payload = {
        "context": "Test",
        "instruction": "وضّح في نص علمي",
        "student_answer": "Introduction... Developpement... Conclusion...",
        "documents": []
    }
    response = client.post("/api/bac-blanc/action-plan", json=payload)
    assert response.status_code == 404


def test_mindmap_dynamic():
    """GEL : routes/mindmap_methodology.py retiré du registre → 404 (avant : 200)."""
    payload = {"verb": "وضّح في نص علمي"}
    response = client.post("/api/mindmap/methodology/dynamic", json=payload)
    assert response.status_code == 404


def test_mindmap_static():
    """GEL : idem → 404 (avant : 200 + payload)."""
    response = client.get("/api/mindmap/methodology/static/structure_texte_scientifique")
    assert response.status_code == 404


def test_full_methodology_pipeline():
    """Pipeline complet : evaluate (vivant, 0 LLM) -> bac-blanc (GEL 404) -> action-plan (GEL 404)."""
    packed = load("manhadjiya-yeast-analyse")
    assert packed is not None
    eval_payload = {
        "question_id": "manhadjiya-yeast-analyse",
        "student_answer": packed.rubric.model_answer,
    }
    _auth_on()
    try:
        r = client.post("/api/evaluate/methodology", json=eval_payload)
    finally:
        _auth_off()
    assert r.status_code == 200
    assert r.json()["source"] == "local_rubric"

    # GEL 2026-08-17 : bac_blanc_intelligent retiré du registre → 404
    r2 = client.post("/api/bac-blanc/feedback", json=eval_payload)
    assert r2.status_code == 404

    r3 = client.post("/api/bac-blanc/action-plan", json=eval_payload)
    assert r3.status_code == 404
