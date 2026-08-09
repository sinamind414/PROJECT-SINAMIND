"""tests/test_correction_output_schema.py — Schémas JSON natifs (audit O7).

- Les schémas sont structurellement valides (mini-validateur, jsonschema
  n'est pas une dépendance du projet)
- Le schéma v2 (PROD) correspond au format DEMANDÉ par le prompt v2
  (score 0-100 / errors / feedback / grade) — pas au contrat public v1
  (divergence documentée : conflit avec le mapping v2→v1 sinon)
- Le schéma v1 est aligné sur les types RÉELS du code (highlights.type,
  dominant_error_code) — pas les valeurs fantaisistes du plan
"""

import json

from grading.schemas.correction_output import (
    _DOMINANT_ERROR_CODES,
    _HIGHLIGHT_TYPES,
    CORRECTION_V1_JSON_SCHEMA,
    CORRECTION_V2_JSON_SCHEMA,
    assert_json_schema_valid,
)


class TestSchemaValidity:
    def test_v1_schema_produces_valid_contract(self):
        assert_json_schema_valid(CORRECTION_V1_JSON_SCHEMA)

    def test_v2_schema_produces_valid_contract(self):
        assert_json_schema_valid(CORRECTION_V2_JSON_SCHEMA)

    def test_schemas_are_json_serializable(self):
        json.dumps(CORRECTION_V1_JSON_SCHEMA)
        json.dumps(CORRECTION_V2_JSON_SCHEMA)

    def test_strict_compatibility_required_or_nullable(self):
        """OpenAI strict:true : tout champ déclaré doit être required OU
        nullable (["T", "null"]) — jamais d'union sans null."""
        def _is_nullable(item: dict) -> bool:
            t = item.get("type")
            return isinstance(t, list) and "null" in t

        for schema in (CORRECTION_V1_JSON_SCHEMA, CORRECTION_V2_JSON_SCHEMA):
            props = schema["properties"]
            req = set(schema["required"])
            for name, item in props.items():
                assert name in req or _is_nullable(item), (
                    f"{name}: ni required ni nullable (strict OpenAI)"
                )

            def _check_items(item: dict, path: str) -> None:
                if item.get("type") == "object":
                    sub_props = item["properties"]
                    sub_req = set(item.get("required", []))
                    for name, sub in sub_props.items():
                        assert name in sub_req or _is_nullable(sub), (
                            f"{path}.{name}: ni required ni nullable"
                        )
                        _check_items(sub, f"{path}.{name}")
                elif item.get("type") == "array":
                    _check_items(item["items"], f"{path}[]")

            for name, item in props.items():
                _check_items(item, name)

    def test_v1_optionals_are_nullable(self):
        """confidence / advice_ar sont optionnels (plan O7) → nullable."""
        props = CORRECTION_V1_JSON_SCHEMA["properties"]
        assert "confidence" not in CORRECTION_V1_JSON_SCHEMA["required"]
        assert "advice_ar" not in CORRECTION_V1_JSON_SCHEMA["required"]
        assert props["confidence"]["type"] == ["number", "null"]
        assert props["advice_ar"]["type"] == ["string", "null"]


class TestV2SchemaMatchesPromptV2:
    """Le schéma natif doit matcher le format du prompt v2 (PROD)."""

    def test_v2_has_v2_format_not_v1(self):
        props = CORRECTION_V2_JSON_SCHEMA["properties"]
        # Format demandé par prompts/correction_prompt_v2.py SYSTEM_PROMPT_AR
        assert set(props) == {"score", "errors", "feedback", "grade"}
        assert "highlights" not in props
        assert "matched_criteria" not in props

    def test_v2_score_is_0_100(self):
        score = CORRECTION_V2_JSON_SCHEMA["properties"]["score"]
        assert score["maximum"] == 100  # le prompt v2 demande score 0-100

    def test_v2_grade_enum(self):
        grade = CORRECTION_V2_JSON_SCHEMA["properties"]["grade"]
        assert grade["enum"] == ["retenir", "acquis", "maîtrisé"]

    def test_v2_errors_items(self):
        items = CORRECTION_V2_JSON_SCHEMA["properties"]["errors"]["items"]
        assert set(items["properties"]) == {"line", "type", "detail", "fix"}


class TestV1SchemaAlignedWithCode:
    """Le schéma v1 doit utiliser les types RÉELS de correction_v2.py."""

    def test_highlight_types_match_validate_highlights(self):
        # _validate_highlights (correction_v2.py) n'accepte que ces types ;
        # le plan listait ["error","missing","good","partial"] — FAUX vs code.
        items = CORRECTION_V1_JSON_SCHEMA["properties"]["highlights"]["items"]
        assert items["properties"]["type"]["enum"] == _HIGHLIGHT_TYPES
        assert set(_HIGHLIGHT_TYPES) == {
            "gibberish", "off_topic", "missing_link", "wrong_formulation",
            "irrelevant", "good_element",
        }
        assert "error" not in _HIGHLIGHT_TYPES

    def test_dominant_error_codes_match_code(self):
        # Schemas/evaluation_v2.py DominantErrorCode : 13 valeurs réelles
        prop = CORRECTION_V1_JSON_SCHEMA["properties"]["dominant_error_code"]
        assert prop["enum"] == _DOMINANT_ERROR_CODES
        assert "server_error" in _DOMINANT_ERROR_CODES  # absent du plan (8 valeurs)
