"""Tests Couche 3 — Évaluation Intelligente (Semaine 2)"""

from methodology.text_structure_analyzer import analyze_text_structure
from methodology.document_usage_analyzer import analyze_document_usage_v2
from methodology.feedback_engine import generate_detailed_feedback
from methodology.evaluator import evaluate_methodology

import pytest


class TestTextStructureAnalyzer:
    def test_full_structure(self):
        r = analyze_text_structure(
            "مقدمة: المشكل يهدف لدراسة... عرض: من خلال الوثيقة نلاحظ... خاتمة: نستنتج أن..."
        )
        assert r["has_intro"] is True
        assert r["has_development"] is True
        assert r["has_conclusion"] is True
        assert r["structure_score"] == 16

    def test_no_structure(self):
        r = analyze_text_structure("جملة عادية فقط")
        assert r["structure_score"] == 0

    def test_partial_structure(self):
        r = analyze_text_structure(
            "عرض: لأن هذه النتيجة تبين أن... لذلك نستنتج"
        )
        assert r["has_intro"] is False
        assert r["has_development"] is True
        assert r["has_conclusion"] is True
        assert r["structure_score"] == 11


class TestDocumentUsageAnalyzerV2:
    def test_no_documents(self):
        r = analyze_document_usage_v2("réponse", [])
        assert r["usage_quality"] == "none"
        assert r["documents_used"] == 0

    def test_good_usage(self):
        docs = [{"id": "doc1", "key_element": "photosynthèse"}]
        r = analyze_document_usage_v2(
            "La photosynthèse selon le doc1", docs
        )
        assert r["documents_used"] >= 1
        assert r["usage_quality"] in ("good", "excellent")


class TestFeedbackEngine:
    def test_complex_missing_structure(self):
        fb = generate_detailed_feedback(
            verb="وضّح في نص علمي",
            task_type="complex",
            structure={"structure_score": 4, "has_intro": True, "has_development": False, "has_conclusion": False},
            doc_usage={"usage_quality": "none"},
        )
        assert "Introduction" in fb or "Développement" in fb or "Conclusion" in fb

    def test_simple_no_feedback(self):
        fb = generate_detailed_feedback(
            verb="صف",
            task_type="simple",
            structure={"structure_score": 16, "has_intro": True, "has_development": True, "has_conclusion": True},
            doc_usage={"usage_quality": "good"},
        )
        assert fb == "Réponse méthodologiquement correcte."


@pytest.mark.asyncio
class TestEvaluateMethodology:
    async def test_complex_verb(self):
        r = await evaluate_methodology(
            context="Document sur la photosynthèse",
            instruction="وضّح في نص علمي كيف يتم التركيب الضوئي",
            student_answer="مقدمة: التركيب الضوئي هو عملية... عرض: يتم ذلك عبر... خاتمة: إذن التركيب الضوئي ضروري.",
            documents=[],
        )
        assert r["verb"] == "وضّح في نص علمي"
        assert r["task_type"] == "complex"
        assert "structure" in r

    async def test_simple_verb(self):
        r = await evaluate_methodology(
            context="",
            instruction="صف خصائص الخلية النباتية",
            student_answer="الخلية النباتية تحتوي على جدار خلوي",
            documents=[],
        )
        assert r["verb"] == "صف"
        assert r["task_type"] == "simple"
