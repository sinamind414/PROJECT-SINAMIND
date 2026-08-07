"""grading/schemas/correction_output.py — Schémas JSON natifs (audit O7).

⚠️ Divergence documentée vs plan d'audit : le schéma doit correspondre au
format de sortie DEMANDÉ PAR LE PROMPT, pas au contrat public v1. En prod la
route tourne avec `use_v2_prompt=True` → le prompt v2
(prompts/correction_prompt_v2.py, SYSTEM_PROMPT_AR) demande :

    {"score": 0-100, "errors": [{line, type, detail, fix}],
     "feedback": "...", "grade": "retenir | acquis | maîtrisé"}

Forcer le schéma v1 (score 0-score_max, highlights, matched_criteria…) avec le
prompt v2 créerait un conflit prompt↔schéma ET déclencherait le mapping v2→v1
de correction_v2.py (`use_v2_prompt and "errors" in parsed`) sur du v1 —
le score (0-7) serait réinterprété comme 0-100 → multiplié par score_max/100 →
note catastrophique silencieuse. Le schéma natif du prompt v2 est donc le
format v2 ; le mapping v2→v1 produit ensuite le contrat public inchangé.

`CORRECTION_V1_JSON_SCHEMA` (prompt v1, non utilisé en prod) est aligné sur les
types RÉELS du code — le plan listait highlights.type en
["error","missing","good","partial"] mais `_validate_highlights` de
correction_v2.py n'accepte que ["gibberish","off_topic","missing_link",
"wrong_formulation","irrelevant","good_element"] (autre valeur → normalisée en
"irrelevant", perte d'information). Idem dominant_error_code : enum complète
réelle (13 valeurs, pas 8).

Les deux schémas sont strict-compatibles (OpenAI `strict: true`) : chaque
champ déclaré est soit `required`, soit nullable (`["T", "null"]`) — jamais
un type union sans null.
"""

from __future__ import annotations

# ── Format v2 (PROD — prompt v2) ─────────────────────────────────────

CORRECTION_V2_JSON_SCHEMA: dict = {
    "type": "object",
    "properties": {
        "score": {"type": "integer", "minimum": 0, "maximum": 100},
        "errors": {
            "type": "array",
            "items": {
                "type": "object",
                "properties": {
                    "line": {"type": "string"},
                    "type": {"type": "string"},
                    "detail": {"type": "string"},
                    "fix": {"type": "string"},
                },
                "required": ["line", "type", "detail", "fix"],
                "additionalProperties": False,
            },
        },
        "feedback": {"type": "string"},
        "grade": {
            "type": "string",
            "enum": ["retenir", "acquis", "maîtrisé"],
        },
    },
    "required": ["score", "errors", "feedback", "grade"],
    "additionalProperties": False,
}

# ── Format v1 (prompt v1 — aligné sur les types réels du code) ───────

_HIGHLIGHT_TYPES = [
    "gibberish", "off_topic", "missing_link", "wrong_formulation",
    "irrelevant", "good_element",
]

_DOMINANT_ERROR_CODES = [
    "scientific_error", "methodology_error", "off_topic", "partial_correct",
    "all_correct", "insufficient", "gibberish", "too_short", "empty",
    "not_arabic", "repeated_chars", "server_error", "unknown",
]

CORRECTION_V1_JSON_SCHEMA: dict = {
    "type": "object",
    "properties": {
        "score": {"type": "integer", "minimum": 0},
        "matched_criteria": {"type": "array", "items": {"type": "string"}},
        "unmatched_criteria": {
            "type": "array",
            "items": {
                "type": "object",
                "properties": {
                    "criterion": {"type": "string"},
                    "why_ar": {"type": "string"},
                    "from_model_answer": {"type": "string"},
                },
                "required": ["criterion", "why_ar", "from_model_answer"],
                "additionalProperties": False,
            },
        },
        "highlights": {
            "type": "array",
            "items": {
                "type": "object",
                "properties": {
                    "start": {"type": "integer", "minimum": 0},
                    "end": {"type": "integer", "minimum": 0},
                    "type": {"type": "string", "enum": _HIGHLIGHT_TYPES},
                    "message_ar": {"type": "string"},
                },
                "required": ["start", "end", "type", "message_ar"],
                "additionalProperties": False,
            },
        },
        "feedback_ar": {"type": "string"},
        # Optionnels (plan O7 : ne pas forcer les modèles à les produire) —
        # déclarés NULLABLE pour rester compatibles avec OpenAI strict:true
        # (tout champ déclaré doit être required OU nullable).
        "advice_ar": {"type": ["string", "null"]},
        "confidence": {"type": ["number", "null"], "minimum": 0.0, "maximum": 1.0},
        "dominant_error_code": {
            "type": "string",
            "enum": _DOMINANT_ERROR_CODES,
        },
    },
    "required": [
        "score", "matched_criteria", "unmatched_criteria", "highlights",
        "feedback_ar", "dominant_error_code",
    ],
    "additionalProperties": False,
}

# ── Mini-validateur structurel (jsonschema n'est pas une dépendance) ─

_KNOWN_TYPES = {"string", "integer", "number", "boolean", "array", "object"}


def assert_json_schema_valid(schema: dict) -> None:
    """Valide structurellement un JSON Schema (équivalent raisonnable de
    jsonschema.Draft7Validator.check_schema, sans dépendance).

    Vérifie : type racine, properties dict, required ⊆ properties, types
    connus, enum listes non vides, schémas imbriqués récursivement.
    """
    assert isinstance(schema, dict), "schéma racine doit être un objet"
    assert schema.get("type") == "object", "schéma racine doit être type=object"
    properties = schema.get("properties")
    assert isinstance(properties, dict) and properties, "properties requis"
    required = schema.get("required", [])
    assert isinstance(required, list), "required doit être une liste"
    for name in required:
        assert name in properties, (
            f"champ required '{name}' absent des properties"
        )

    def _check_sub(sub: dict, path: str) -> None:
        t = sub.get("type")
        if isinstance(t, str):
            assert t in _KNOWN_TYPES, f"{path}: type inconnu '{t}'"
            if t == "array":
                items = sub.get("items")
                assert isinstance(items, dict), f"{path}: items requis"
                _check_sub(items, f"{path}.items")
            elif t == "object":
                sub_props = sub.get("properties")
                assert isinstance(sub_props, dict), f"{path}: properties requis"
                sub_req = sub.get("required", [])
                for name in sub_req:
                    assert name in sub_props, (
                        f"{path}: required '{name}' absent des properties"
                    )
                for name, item_schema in sub_props.items():
                    _check_sub(item_schema, f"{path}.properties.{name}")
        elif isinstance(t, list):
            # Type union — uniquement [T, "null"] (optionnel OpenAI strict)
            assert set(t) <= (set(_KNOWN_TYPES) | {"null"}), (
                f"{path}: union de types non supportée {t}"
            )
            assert "null" in t, f"{path}: union sans null non supportée"
        if "enum" in sub:
            assert isinstance(sub["enum"], list) and sub["enum"], (
                f"{path}: enum doit être une liste non vide"
            )

    for name, item_schema in properties.items():
        _check_sub(item_schema, f"properties.{name}")
