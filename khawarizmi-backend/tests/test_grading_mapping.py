"""tests/test_grading_mapping.py — Mapping v2 → v1 (audit O7, point 2).

Le JSON natif provider garantit une structure parfaite (errors = liste,
score = entier 0-100) : le mapping v2→v1 doit la gérer sans garde de
réparation devenue morte, et produire un contrat v1 correct.
"""


from grading.mapping import map_v2_to_v1

NATIVE_V2 = {
    "score": 75,
    "errors": [
        {"line": "DNA", "type": "scientific_error",
         "detail": "خطأ في تحديد القواعد", "fix": "A-T, G-C"},
    ],
    "feedback": "إجابة جزئية",
    "grade": "partial_correct",
}


class TestMapV2ToV1:
    def test_score_scaled_to_bareme(self):
        fields = map_v2_to_v1(NATIVE_V2, score_max=4, student_answer="réponse")
        assert fields["score"] == 3  # 75 * 4 / 100 = 3
        assert fields["source"] == "llm_v2"

    def test_errors_mapped_to_highlights_and_unmatched(self):
        fields = map_v2_to_v1(NATIVE_V2, score_max=4, student_answer="réponse")
        assert len(fields["highlights"]) == 1
        h = fields["highlights"][0]
        assert h["start"] == 0
        assert h["end"] == len("réponse")  # tout le texte surligné (pas de positions v2)
        assert h["type"] == "wrong_formulation"
        assert fields["unmatched"][0]["criterion"] == "scientific_error"

    def test_dominant_error_code_type_aware(self):
        """Amélioration O7 : une erreur scientifique → scientific_error
        (remédiation contenu), plus le fallback aveugle methodology_error."""
        fields = map_v2_to_v1(NATIVE_V2, score_max=4, student_answer="réponse")
        assert fields["dominant_error_code"] == "scientific_error"

    def test_dominant_fallback_methodology(self):
        v2 = {"score": 50, "errors": [{"type": "structure"}],
              "feedback": "f", "grade": "acquis"}
        fields = map_v2_to_v1(v2, score_max=4, student_answer="réponse")
        assert fields["dominant_error_code"] == "methodology_error"

    def test_dominant_all_correct_when_no_errors(self):
        v2 = {"score": 100, "errors": [], "feedback": "f", "grade": "maîtrisé"}
        fields = map_v2_to_v1(v2, score_max=4, student_answer="réponse")
        assert fields["dominant_error_code"] == "all_correct"

    def test_grade_maps_to_advice_not_error_code(self):
        """Le plan supposait grade → dominant_error_code ; le code réel mappe
        grade → advice_ar (dominant dérivé des errors/score)."""
        v2 = {"score": 75, "errors": [{"type": "scientific_error"}],
              "feedback": "f", "grade": "acquis"}
        fields = map_v2_to_v1(v2, score_max=4, student_answer="réponse")
        assert fields["advice_ar"] == "جيد، لكن يمكنك التعمق أكثر"
        assert fields["dominant_error_code"] == "scientific_error"

    def test_empty_errors_and_zero_score_insufficient(self):
        v2 = {"score": 0, "errors": [], "feedback": "", "grade": "retenir"}
        fields = map_v2_to_v1(v2, score_max=4, student_answer="réponse")
        assert fields["score"] == 0
        assert fields["dominant_error_code"] == "insufficient"

    def test_score_clamped(self):
        v2 = {"score": 120, "errors": [], "feedback": "f", "grade": "maîtrisé"}
        fields = map_v2_to_v1(v2, score_max=4, student_answer="réponse")
        assert fields["score"] == 4

    def test_perfect_native_json_end_to_end_shape(self):
        """Le contrat v1 produit est complet (champs requis par la suite)."""
        fields = map_v2_to_v1(NATIVE_V2, score_max=7, student_answer="الاستنساخ يتم في النواة")
        for key in ("score", "highlights", "matched", "unmatched", "feedback_ar",
                    "advice_ar", "confidence", "source", "dominant_error_code"):
            assert key in fields, key
        assert isinstance(fields["feedback_ar"], str)
        assert 0.0 <= fields["confidence"] <= 1.0
