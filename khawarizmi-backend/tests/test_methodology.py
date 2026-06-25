"""Tests Methodology Evaluator V2 — Semaine 1"""

import pytest
from fastapi.testclient import TestClient
from main import app

client = TestClient(app)


def test_methodology_endpoint_complex_verb():
    """Test verbe complexe : وضّح في نص علمي"""
    payload = {
        "context": "Document sur la photosynthèse",
        "instruction": "وضّح في نص علمي كيف يتم التركيب الضوئي",
        "student_answer": "مقدمة: التركيب الضوئي هو عملية... عرض: يتم ذلك عبر... خاتمة: إذن التركيب الضوئي ضروري.",
        "documents": [],
    }
    response = client.post("/api/evaluate/methodology", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert data["verb"] == "وضّح في نص علمي"
    assert data["task_type"] == "complex"
    assert "structure" in data


def test_methodology_endpoint_simple_verb():
    """Test verbe simple : صف"""
    payload = {
        "context": "",
        "instruction": "صف خصائص الخلية النباتية",
        "student_answer": "الخلية النباتية تحتوي على جدار خلوي وبلاستيدات خضراء",
        "documents": [],
    }
    response = client.post("/api/evaluate/methodology", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert data["verb"] == "صف"
    assert data["task_type"] == "simple"


def test_methodology_missing_verb():
    """Test quand aucun verbe n'est reconnu"""
    payload = {
        "context": "",
        "instruction": "Fais quelque chose de bizarre",
        "student_answer": "Réponse quelconque",
        "documents": [],
    }
    response = client.post("/api/evaluate/methodology", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert data["verb"] == "unknown"
