"""Tests complets Methodology Evaluator V2 — Semaine 8"""

import pytest
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
    """Test du tuteur en mode explication"""
    payload = {
        "instruction": "وضّح في نص علمي",
        "mode": "explain"
    }
    response = client.post("/api/tutor/methodology", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert "explanation" in data


def test_tutor_correct_mode():
    """Test du tuteur en mode correction"""
    payload = {
        "instruction": "وضّح في نص علمي",
        "student_answer": "Ma reponse",
        "mode": "correct"
    }
    response = client.post("/api/tutor/methodology", json=payload)
    assert response.status_code == 200


def test_tutor_diagnose_mode():
    """Test du tuteur en mode diagnostic"""
    payload = {
        "instruction": "وضّح في نص علمي",
        "student_answer": "Ma reponse",
        "mode": "diagnose"
    }
    response = client.post("/api/tutor/methodology", json=payload)
    assert response.status_code == 200


def test_bac_blanc_feedback():
    """Test du feedback Bac Blanc Intelligent"""
    payload = {
        "context": "Test",
        "instruction": "وضّح في نص علمي",
        "student_answer": "Introduction... Developpement... Conclusion...",
        "documents": []
    }
    response = client.post("/api/bac-blanc/feedback", json=payload)
    assert response.status_code == 200


def test_bac_blanc_action_plan():
    """Test du plan d'action personnalise"""
    payload = {
        "context": "Test",
        "instruction": "وضّح في نص علمي",
        "student_answer": "Introduction... Developpement... Conclusion...",
        "documents": []
    }
    response = client.post("/api/bac-blanc/action-plan", json=payload)
    assert response.status_code == 200


def test_mindmap_dynamic():
    """Test de la mindmap dynamique"""
    payload = {"verb": "وضّح في نص علمي"}
    response = client.post("/api/mindmap/methodology/dynamic", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert data["generated"] is True
    assert len(data["root"]["children"]) == 3


def test_mindmap_static():
    """Test de la mindmap statique"""
    response = client.get("/api/mindmap/methodology/static/structure_texte_scientifique")
    assert response.status_code == 200
    assert response.json()["id"] == "mm_structure"


def test_full_methodology_pipeline():
    """Test du pipeline complet : evaluate -> bac-blanc -> action-plan"""
    eval_payload = {
        "context": "Test pipeline",
        "instruction": "وضّح في نص علمي",
        "student_answer": "مقدمة: probleme... عرض: explication... خاتمة: synthese...",
        "documents": []
    }
    r = client.post("/api/evaluate/methodology", json=eval_payload)
    assert r.status_code == 200
    assert r.json()["task_type"] == "complex"

    r2 = client.post("/api/bac-blanc/feedback", json=eval_payload)
    assert r2.status_code == 200

    r3 = client.post("/api/bac-blanc/action-plan", json=eval_payload)
    assert r3.status_code == 200
