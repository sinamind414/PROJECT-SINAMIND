"""Tests complets Methodology Evaluator V2 — Semaine 8"""

from fastapi.testclient import TestClient

from main import app

client = TestClient(app)


def test_methodology_evaluator_complex_verb():
    """Test verbe complexe : وضّح"""
    payload = {
        "context": "Document sur la photosynthese",
        "instruction": "وضّح في نص علمي كيف يتم التركيب الضوئي",
        "student_answer": "مقدمة: التركيب الضوئي هو... عرض: يتم ذلك عبر... خاتمة: إذن...",
        "documents": []
    }
    response = client.post("/api/evaluate/methodology", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert data["verb"] == "وضّح في نص علمي"
    assert data["task_type"] == "complex"


def test_methodology_evaluator_simple_verb():
    """Test verbe simple : صف"""
    payload = {
        "context": "",
        "instruction": "صف خصائص الخلية النباتية",
        "student_answer": "الخلية النباتية تحتوي على جدار خلوي",
        "documents": []
    }
    response = client.post("/api/evaluate/methodology", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert data["verb"] == "صف"
    assert data["task_type"] == "simple"


def test_methodology_evaluator_missing_verb():
    """Test verbe inconnu"""
    payload = {
        "context": "",
        "instruction": "Fais quelque chose",
        "student_answer": "Reponse",
        "documents": []
    }
    response = client.post("/api/evaluate/methodology", json=payload)
    assert response.status_code == 200
    assert response.json()["verb"] == "unknown"


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
    """Pipeline complet : evaluate (vivant) -> bac-blanc (GEL 404) -> action-plan (GEL 404)."""
    eval_payload = {
        "context": "Test pipeline",
        "instruction": "وضّح في نص علمي",
        "student_answer": "مقدمة: probleme... عرض: explication... خاتمة: synthese...",
        "documents": []
    }
    r = client.post("/api/evaluate/methodology", json=eval_payload)
    assert r.status_code == 200
    assert r.json()["task_type"] == "complex"

    # GEL 2026-08-17 : bac_blanc_intelligent retiré du registre → 404
    r2 = client.post("/api/bac-blanc/feedback", json=eval_payload)
    assert r2.status_code == 404

    r3 = client.post("/api/bac-blanc/action-plan", json=eval_payload)
    assert r3.status_code == 404
