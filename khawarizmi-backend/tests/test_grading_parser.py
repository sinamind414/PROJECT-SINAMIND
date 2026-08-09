"""tests/test_grading_parser.py — Parsing tolérant (audit O7).

- native_json en tête quand le provider a répondu en mode JSON natif
- fallback tolérant conservé (direct → fence → regex → partial)
- compteur parse_strategy_total{strategy}
"""

import json

from grading.parser import parse_correction_response, parse_stats, record_parse_strategy

VALID = {
    "score": 5,
    "feedback": "إجابة متوسطة",
    "grade": "acquis",
}
VALID_RAW = json.dumps(VALID, ensure_ascii=False)


class TestParseStrategies:
    def test_native_json_strategy(self):
        """Acceptation O7 : contenu JSON pur + mode natif → native_json."""
        result, strategy = parse_correction_response(VALID_RAW, json_mode_used=True)
        assert strategy == "native_json"
        assert result["score"] == 5

    def test_direct_strategy_without_native_flag(self):
        """Sans mode natif, du JSON pur → direct."""
        result, strategy = parse_correction_response(VALID_RAW)
        assert strategy == "direct"
        assert result["score"] == 5

    def test_fallback_when_native_fails(self):
        """Acceptation O7 : le mode natif a échoué (contenu bavard) → la
        stratégie fence rattrape."""
        raw = "Voici la correction:\n```json\n" + VALID_RAW + "\n```\nfin"
        result, strategy = parse_correction_response(raw, json_mode_used=True)
        assert strategy == "fence"
        assert result["score"] == 5

    def test_fence_without_native_flag(self):
        raw = "```json\n" + VALID_RAW + "\n```"
        result, strategy = parse_correction_response(raw)
        assert strategy == "fence"

    def test_regex_first_last_brace(self):
        raw = "texte avant {" + VALID_RAW[1:-1] + "} texte après"
        result, strategy = parse_correction_response(raw)
        assert strategy == "regex"
        assert result["score"] == 5

    def test_partial_depth_block(self):
        """Cas où regex (premier { au dernier }) échoue mais depth rattrape :
        le span global est invalide (objets successifs + accolade ouverte),
        le premier bloc équilibré est récupéré."""
        raw = '{"a": 1} {"b": 2} {"c": 3'
        result, strategy = parse_correction_response(raw)
        assert strategy == "partial"
        assert result == {"a": 1}

    def test_failed(self):
        result, strategy = parse_correction_response("pas de json ici {")
        assert strategy == "failed"
        assert result is None

    def test_empty_is_failed(self):
        result, strategy = parse_correction_response("")
        assert strategy == "failed"
        assert result is None

    def test_non_dict_json_is_failed(self):
        # Un JSON valide mais non-objet (ex. liste) n'est pas une correction
        result, strategy = parse_correction_response("[1, 2, 3]", json_mode_used=True)
        assert strategy == "failed"
        assert result is None


class TestParseStats:
    def test_record_and_snapshot(self):
        before = parse_stats()
        record_parse_strategy("native_json")
        record_parse_strategy("native_json")
        record_parse_strategy("fence")
        after = parse_stats()
        assert after.get("native_json", 0) == before.get("native_json", 0) + 2
        assert after.get("fence", 0) == before.get("fence", 0) + 1
