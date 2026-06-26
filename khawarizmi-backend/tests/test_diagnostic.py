"""Tests Diagnostic Avancé — Semaine 3"""

from methodology.diagnostic import (
    detect_verb_confusion,
    detect_error_profiles,
    calculate_methodology_maturity,
    generate_diagnostic_report,
    diagnose_methodology_level,
)


class TestDetectVerbConfusion:
    def test_confusion_detected(self):
        assert detect_verb_confusion(
            "وضّح في نص علمي كيف يتم التركيب الضوئي", "صف"
        ) is True

    def test_no_confusion(self):
        assert detect_verb_confusion(
            "صف خصائص الخلية النباتية", "صف"
        ) is False


class TestDetectErrorProfiles:
    def test_detects_weak_structure(self):
        r = detect_error_profiles(
            verb="وضّح في نص علمي",
            task_type="complex",
            structure={"structure_score": 4, "has_conclusion": False},
            doc_usage={"usage_quality": "good"},
            student_answer="réponse courte",
        )
        ids = [p["id"] for p in r]
        assert "weak_structure" in ids
        assert "no_conclusion" in ids

    def test_detects_poor_document_usage(self):
        r = detect_error_profiles(
            verb="أثبت",
            task_type="complex",
            structure={"structure_score": 12, "has_conclusion": True},
            doc_usage={"usage_quality": "none"},
            student_answer="test",
        )
        ids = [p["id"] for p in r]
        assert "poor_document_usage" in ids

    def test_no_errors_simple(self):
        r = detect_error_profiles(
            verb="صف",
            task_type="simple",
            structure={"structure_score": 0, "has_conclusion": False},
            doc_usage={"usage_quality": "good"},
            student_answer="réponse correcte",
        )
        assert len(r) == 0


class TestCalculateMethodologyMaturity:
    def test_beginner(self):
        r = calculate_methodology_maturity(
            [{"structure_score": 2}, {"structure_score": 4}]
        )
        assert r["level"] == "Débutant"

    def test_expert(self):
        r = calculate_methodology_maturity(
            [{"structure_score": 16}, {"structure_score": 14}, {"structure_score": 15}]
        )
        assert r["level"] == "Expert"

    def test_empty(self):
        r = calculate_methodology_maturity([])
        assert r["level"] == "Débutant"
        assert r["score"] == 0


class TestGenerateDiagnosticReport:
    def test_full_report(self):
        r = generate_diagnostic_report(
            verb="وضّح في نص علمي",
            task_type="complex",
            structure={"structure_score": 4, "has_intro": True, "has_development": False, "has_conclusion": False},
            doc_usage={"usage_quality": "none"},
            student_answer="réponse test",
            previous_answers=[],
        )
        assert r["verb"] == "وضّح في نص علمي"
        assert r["task_type"] == "complex"
        assert len(r["error_profiles"]) > 0
        assert "maturity_level" in r
        assert "recommendations" in r


class TestDiagnoseMethodologyLevel:
    def test_existing_pipeline(self):
        r = diagnose_methodology_level([
            {"score": 8, "max_score": 10, "verb": "صف", "task_type": "simple",
             "structure_score": 0, "feedback": {"weaknesses": ["Bonne structure"]}}
        ])
        assert r["level"] in ("beginner", "intermediate", "advanced", "expert")
        assert "level_label" in r
