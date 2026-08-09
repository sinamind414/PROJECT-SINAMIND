"""tests/test_grading_post_validate.py — Post-validation (audit S2.1e).

- validate_highlights : clamp, types invalides → irrelevant, start>=end filtré
- normalize_unmatched : strings et dicts
- compute_dominant_error_code : sanity, all_correct, off_topic, methodology
- build_sanity_result / build_error_result : formats complets
- finalize_result : pourcentage, dominant auto, remédiation, hashes,
  parse_status ok/recovered, llm_raw JAMAIS exposé
- Parité : evaluate_answer_v2 (LLM mocké) passe par finalize_result (les
  tests existants test_correction_v2 le garantissent — ici, vérification
  du format directement).
"""


from grading.post_validate import (
    build_error_result,
    build_sanity_result,
    clamp,
    compute_dominant_error_code,
    finalize_result,
    normalize_unmatched,
    validate_highlights,
)


class TestValidateHighlights:
    def test_valid_highlight_passes(self):
        out = validate_highlights(
            [{"start": 0, "end": 5, "type": "good_element", "message_ar": "bien"}],
            "réponse élève",
        )
        assert out == [{"start": 0, "end": 5, "type": "good_element",
                        "message_ar": "bien"}]

    def test_invalid_type_defaults_to_irrelevant(self):
        out = validate_highlights(
            [{"start": 0, "end": 5, "type": "scientific_error", "message_ar": "x"}],
            "réponse élève",
        )
        assert out[0]["type"] == "irrelevant"

    def test_clamped_to_bounds(self):
        out = validate_highlights(
            [{"start": -5, "end": 999, "type": "good_element", "message_ar": ""}],
            "abcde",
        )
        assert out[0]["start"] == 0
        assert out[0]["end"] == 5

    def test_start_ge_end_filtered(self):
        out = validate_highlights(
            [{"start": 5, "end": 5, "type": "good_element", "message_ar": ""}],
            "abcde",
        )
        assert out == []

    def test_non_dict_and_non_int_filtered(self):
        out = validate_highlights(
            [{"start": "x", "end": 2, "type": "good_element", "message_ar": ""},
             "not a dict"],
            "abcde",
        )
        assert out == []


class TestNormalizeUnmatched:
    def test_strings_to_dicts(self):
        out = normalize_unmatched(["critère A", "critère B"])
        assert out == [
            {"criterion": "critère A", "why_ar": "", "from_model_answer": ""},
            {"criterion": "critère B", "why_ar": "", "from_model_answer": ""},
        ]

    def test_dicts_preserved(self):
        out = normalize_unmatched(
            [{"criterion": "c", "why_ar": "w", "from_model_answer": "f"}]
        )
        assert out == [{"criterion": "c", "why_ar": "w", "from_model_answer": "f"}]


class TestComputeDominantErrorCode:
    def test_sanity_first(self):
        assert compute_dominant_error_code([], [], "gibberish", 0, 4) == "gibberish"

    def test_all_correct(self):
        assert compute_dominant_error_code([], [], "ok", 4, 4) == "all_correct"

    def test_off_topic(self):
        hs = [{"type": "off_topic"}]
        assert compute_dominant_error_code(hs, [], "ok", 1, 4) == "off_topic"

    def test_missing_link_is_methodology(self):
        hs = [{"type": "missing_link"}]
        assert compute_dominant_error_code(hs, [], "ok", 1, 4) == "methodology_error"

    def test_unmatched_is_methodology(self):
        assert compute_dominant_error_code([], [{"criterion": "c"}], "ok", 1, 4) \
            == "methodology_error"

    def test_partial_correct(self):
        assert compute_dominant_error_code([], [], "ok", 2, 4) == "partial_correct"

    def test_unknown(self):
        assert compute_dominant_error_code([], [], "ok", 4, 4) == "all_correct"


class TestBuildSanityResult:
    def test_format_complete(self):
        r = build_sanity_result(sanity_code="empty", message_ar="msg",
                                score_max=4, student_answer="")
        assert r["source"] == "sanity"
        assert r["score"] == 0 and r["score_max"] == 4
        assert r["parse_status"] == "not_called"
        assert r["dominant_error_code"] == "empty"
        assert r["provider"] == "none" and r["model"] == "none"
        assert r["highlights"] == []  # vide → pas de surlignage

    def test_gibberish_highlights_full_text(self):
        r = build_sanity_result(sanity_code="gibberish", message_ar="msg",
                                score_max=4, student_answer="AZERTY")
        assert r["highlights"] == [{
            "start": 0, "end": 6, "type": "gibberish", "message_ar": "msg",
        }]
        assert r["student_answer_hash"]  # hash RGPD présent


class TestBuildErrorResult:
    def test_llm_raw_present_internal(self):
        r = build_error_result(score_max=4, error_message="boom",
                               llm_raw='{"score": 3}', student_answer="réponse")
        assert r["source"] == "llm_error"
        assert r["parse_status"] == "failed"
        assert r["dominant_error_code"] == "server_error"
        assert r["llm_raw"] == '{"score": 3}'  # debug interne uniquement
        assert r["llm_raw_hash"]  # hash présent
        assert r["student_answer_hash"]


class TestFinalizeResult:
    def _base(self, **over):
        params = {
            "source": "llm",
            "score": 6,
            "score_max": 8,
            "highlights": [],
            "matched": ["a"],
            "unmatched": [],
            "feedback_ar": "f",
            "advice_ar": "",
            "confidence": 0.8,
            "provider": "p",
            "model": "m",
            "finish_reason": "stop",
            "prompt_hash": "h",
            "student_answer": "réponse",
            "llm_raw": '{"score": 75}',
            "verb_slug": "analyse",
        }
        params.update(over)
        return params

    def test_basic_result(self):
        r = finalize_result(**self._base())
        assert r["source"] == "llm"
        assert r["score"] == 6 and r["score_max"] == 8
        assert r["percentage"] == 75
        assert r["parse_status"] == "ok"  # source == "llm"
        assert r["matched_criteria"] == ["a"]
        assert r["success"] == ["a"]
        # score 6 < 8, unmatched vide, pas de highlights → partial_correct
        assert r["dominant_error_code"] == "partial_correct"
        assert r["student_answer_hash"]
        assert r["llm_raw_hash"]
        assert "llm_raw" not in r  # JAMAIS exposé
        assert "remediation" in r  # clé toujours présente (dict | None)

    def test_parse_status_recovered_for_v2(self):
        r = finalize_result(**self._base(source="llm_v2"))
        assert r["parse_status"] == "recovered"

    def test_dominant_error_code_passed_through(self):
        r = finalize_result(**self._base(dominant_error_code="scientific_error"))
        assert r["dominant_error_code"] == "scientific_error"

    def test_dominant_error_code_auto(self):
        r = finalize_result(**self._base(
            score=2, score_max=8,
            unmatched=[{"criterion": "c", "why_ar": "", "from_model_answer": ""}],
        ))
        assert r["dominant_error_code"] == "methodology_error"

    def test_missing_and_errors_mapping(self):
        r = finalize_result(**self._base(
            unmatched=[{"criterion": "c", "why_ar": "w", "from_model_answer": "f"}],
        ))
        assert r["missing"] == [{"expected": "c", "why_ar": "w", "from_model_answer": "f"}]
        assert r["errors"] == [{"criterion": "c", "why_ar": "w", "from_model_answer": "f"}]

    def test_percentage_zero_when_score_max_zero(self):
        r = finalize_result(**self._base(score_max=0, score=0))
        assert r["percentage"] == 0


class TestClamp:
    def test_clamp(self):
        assert clamp(5, 0, 4) == 4
        assert clamp(-1, 0, 4) == 0
        assert clamp(3, 0, 4) == 3
