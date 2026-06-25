"""
Tests du module Methodology Evaluator V2
"""
import sys
sys.path.insert(0, ".")
import pytest
import asyncio
from methodology.verb_database import get_verb, get_all_verbs, get_complex_verbs, get_simple_verbs
from methodology.task_classifier import classify_task
from methodology.text_structure_validator import validate_text_structure
from methodology.feedback_generator import generate_feedback
from methodology.diagnostic import diagnose_methodology_level, ERROR_PROFILES
from methodology.evaluator import evaluate_methodology
from methodology.flashcard_templates import get_all_flashcards
from methodology.mindmap_templates import get_all_mindmaps, generate_methodology_mindmap
from schemas.methodology import VerbInfo, MethodologyEvaluationResult


class TestVerbDatabase:
    def test_get_verb_found(self):
        v = get_verb("\u0648\u0636\u0651\u062d \u0641\u064a \u0646\u0635 \u0639\u0644\u0645\u064a")
        assert v is not None
        assert v["type"] == "complex"

    def test_get_verb_not_found(self):
        v = get_verb("texte sans verbe")
        assert v is None

    def test_get_all_verbs_count(self):
        verbs = get_all_verbs()
        assert len(verbs) >= 20

    def test_complex_verbs_count(self):
        cv = get_complex_verbs()
        assert len(cv) >= 8

    def test_simple_verbs_count(self):
        sv = get_simple_verbs()
        assert len(sv) >= 8


class TestTaskClassifier:
    def test_simple_task(self):
        assert classify_task("\u0635\u0641 \u0627\u0644\u0634\u0643\u0644") == "simple"

    def test_complex_task_verb(self):
        assert classify_task("\u0648\u0636\u0651\u062d \u0641\u064a \u0646\u0635 \u0639\u0644\u0645\u064a") == "complex"

    def test_complex_task_keyword(self):
        assert classify_task("\u062d\u0644\u0644 \u0627\u0644\u0646\u062a\u0627\u0626\u062c") == "complex"

    def test_complex_task_context(self):
        assert classify_task("\u0627\u0642\u062a\u0631\u062d \u0641\u0631\u0636\u064a\u0629") == "complex"


class TestTextStructureValidator:
    def test_complete_structure(self):
        r = validate_text_structure("\u0645\u0642\u062f\u0645\u0629: ... \u0646\u062c\u062f \u0623\u0646 ... \u0646\u0633\u062a\u0646\u062a\u062c")
        assert r["has_intro"]
        assert r["has_development"]
        assert r["has_conclusion"]
        assert r["structure_score"] == 16

    def test_no_structure(self):
        r = validate_text_structure("juste une phrase")
        assert r["structure_score"] == 0
        assert not r["has_intro"]

    def test_partial_structure(self):
        r = validate_text_structure("\u0645\u0642\u062f\u0645\u0629: ... \u0646\u0633\u062a\u0646\u062a\u062c")
        assert r["has_intro"]
        assert r["has_conclusion"]
        assert r["structure_score"] == 8


class TestFeedbackGenerator:
    def test_feedback_complex_generated(self):
        v = get_verb("\u0648\u0636\u0651\u062d \u0641\u064a \u0646\u0635 \u0639\u0644\u0645\u064a")
        fb = generate_feedback(
            verb_info=v,
            task_type="complex",
            student_answer="r\u00e9ponse courte",
            structure_score=4,
            doc_usage_quality="weak",
        )
        assert fb["score"] >= 0
        assert fb["max_score"] == 20
        assert len(fb["weaknesses"]) > 0

    def test_feedback_structure_awarded(self):
        v = get_verb("\u0648\u0636\u0651\u062d \u0641\u064a \u0646\u0635 \u0639\u0644\u0645\u064a")
        fb = generate_feedback(
            verb_info=v,
            task_type="complex",
            student_answer="longue reponse avec introduction developpement conclusion complete",
            structure_score=16,
            doc_usage_quality="excellent",
        )
        assert fb["score"] > 0
        assert len(fb["strengths"]) > 0


class TestDiagnostic:
    def test_error_profiles_exist(self):
        assert len(ERROR_PROFILES) >= 8

    def test_diagnostic_debutant(self):
        diag = diagnose_methodology_level([
            {"score": 2, "max_score": 20, "feedback": {"weaknesses": ["Absence de structure", "Pas de verbe"]}}
        ])
        assert diag["level"] == "beginner"

    def test_diagnostic_expert(self):
        diag = diagnose_methodology_level([
            {"score": 18, "max_score": 20, "feedback": {"weaknesses": []}}
        ])
        assert diag["level"] == "expert"


class TestEvaluator:
    @pytest.mark.asyncio
    async def test_evaluate_complex(self):
        result = await evaluate_methodology(
            context="Test contexte",
            instruction="\u0648\u0636\u0651\u062d \u0641\u064a \u0646\u0635 \u0639\u0644\u0645\u064a",
            student_answer="\u0645\u0642\u062f\u0645\u0629 ... \u0646\u062c\u062f \u0623\u0646 ... \u0646\u0633\u062a\u0646\u062a\u062c",
        )
        assert result["verb"] == "\u0648\u0636\u0651\u062d \u0641\u064a \u0646\u0635 \u0639\u0644\u0645\u064a"
        assert result["score"] >= 0
        assert "task_type" in result
        assert "structure" in result
        assert "document_usage" in result
        assert "feedback" in result

    @pytest.mark.asyncio
    async def test_evaluate_simple(self):
        result = await evaluate_methodology(
            context="Test",
            instruction="\u0635\u0641 \u0627\u0644\u0634\u0643\u0644",
            student_answer="description d\u00e9taill\u00e9e",
        )
        assert result["task_type"] == "simple"


class TestFlashcards:
    def test_flashcards_count(self):
        cards = get_all_flashcards()
        assert len(cards) >= 15

    def test_flashcards_structure(self):
        for card in get_all_flashcards():
            assert "card_id" in card
            assert "front" in card
            assert "back" in card


class TestMindmaps:
    def test_mindmaps_count(self):
        mms = get_all_mindmaps()
        assert len(mms) >= 5

    def test_mindmap_by_id(self):
        mm = generate_methodology_mindmap(map_id="mm_01")
        assert mm is not None
        assert len(mm["nodes"]) > 5


class TestSchemas:
    def test_verb_info_schema(self):
        vi = VerbInfo(arabic="test", type="complex", max_score=15)
        assert vi.arabic == "test"
        assert vi.type == "complex"

    def test_evaluation_result_schema(self):
        er = MethodologyEvaluationResult(verb="test")
        assert er.score == 0
        assert er.structure.structure_score == 0
