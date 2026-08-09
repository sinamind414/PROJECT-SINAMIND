"""tests/test_llm_providers.py — Capacités JSON par provider (audit O7).

- Dispatch par capacité déclarée, jamais de flag global
- Un provider "none" ne reçoit JAMAIS response_format
- Gemini (endpoint OpenAI-compatible) → json_object, pas de schéma forcé
- Le provider primaire est auto-détecté par la clé (gsk_/AIza*/openai)
"""

from dataclasses import dataclass

from services.llm_providers import (
    PROVIDER_CAPS,
    ProviderCapabilities,
    apply_json_mode,
    caps_for,
    primary_json_mode,
    should_use_json_mode,
)

_SCHEMA = {
    "type": "object",
    "properties": {"score": {"type": "integer"}},
    "required": ["score"],
}


@dataclass
class _FakeCfg:
    """Config minimale pour tester la détection primary par clé."""

    OPENAI_API_KEY: str = ""
    json_mode_providers: list = None  # None = défaut (aucun provider activé)

    def __post_init__(self):
        if self.json_mode_providers is None:
            self.json_mode_providers = []


class TestCapsFor:
    def test_unknown_provider_is_none(self):
        assert caps_for("Provider inconnu").json_mode == "none"

    def test_cloudflare_is_none(self):
        # Prudent : non validé empiriquement → jamais de response_format
        assert caps_for("Cloudflare GLM-5.2").json_mode == "none"

    def test_zenmux_and_nara_are_none(self):
        assert caps_for("ZenMux GLM-5.2").json_mode == "none"
        assert caps_for("NaraRouter").json_mode == "none"

    def test_gemini_is_json_object(self):
        # Endpoint OpenAI-compatible de Gemini : response_format json_object
        assert caps_for("Gemini 2.5 Flash").json_mode == "json_object"

    def test_openai_is_json_schema(self):
        assert caps_for("OpenAI gpt-4o-mini").json_mode == "json_schema"

    def test_zai_is_json_object(self):
        assert caps_for("GLM-4.7").json_mode == "json_object"


class TestPrimaryJsonMode:
    def test_groq_key(self):
        assert primary_json_mode(_FakeCfg("gsk_abc123")) == "groq"

    def test_gemini_key(self):
        assert primary_json_mode(_FakeCfg("AIzaSyBogusKey")) == "gemini"

    def test_openai_default(self):
        assert primary_json_mode(_FakeCfg("sk-proj-123")) == "openai"
        assert primary_json_mode(_FakeCfg("")) == "openai"


class TestShouldUseJsonMode:
    def test_capable_and_enabled(self):
        cfg = _FakeCfg(json_mode_providers=["openai"])
        assert should_use_json_mode("OpenAI gpt-4o-mini", cfg) is True

    def test_capable_not_enabled(self):
        assert should_use_json_mode("OpenAI gpt-4o-mini", _FakeCfg()) is False

    def test_none_capability_never_enabled(self):
        cfg = _FakeCfg(json_mode_providers=["cloudflare"])
        assert should_use_json_mode("Cloudflare GLM-5.2", cfg) is False

    def test_primary_resolved_by_key(self):
        cfg = _FakeCfg("AIzaSyX", json_mode_providers=["gemini"])
        assert should_use_json_mode("primary", cfg) is True
        cfg2 = _FakeCfg("AIzaSyX", json_mode_providers=["openai"])
        assert should_use_json_mode("primary", cfg2) is False


class TestApplyJsonMode:
    def test_no_schema_no_change(self):
        kwargs: dict = {"model": "m"}
        cfg = _FakeCfg(json_mode_providers=["openai"])
        assert apply_json_mode(kwargs, "OpenAI gpt-4o-mini", None, cfg) is False
        assert "response_format" not in kwargs

    def test_provider_without_json_mode_no_response_format(self):
        """Acceptation O7 : un provider sans JSON mode ne reçoit jamais
        response_format (il renverrait un 400 ou l'ignorerait)."""
        for name in ("Cloudflare GLM-5.2", "ZenMux GLM-5.2", "NaraRouter", "Inconnu"):
            kwargs: dict = {"model": "m"}
            assert apply_json_mode(kwargs, name, _SCHEMA) is False
            assert "response_format" not in kwargs, name

    def test_openai_json_schema(self):
        kwargs: dict = {"model": "m"}
        cfg = _FakeCfg(json_mode_providers=["openai"])
        applied = apply_json_mode(kwargs, "OpenAI gpt-4o-mini", _SCHEMA, cfg)
        assert applied is True
        rf = kwargs["response_format"]
        assert rf["type"] == "json_schema"
        assert rf["json_schema"]["name"] == "correction_output"
        assert rf["json_schema"]["strict"] is True
        assert rf["json_schema"]["schema"] is _SCHEMA

    def test_groq_json_object(self):
        kwargs: dict = {"model": "m"}
        applied = apply_json_mode(kwargs, "groq", _SCHEMA, _FakeCfg("gsk_x", json_mode_providers=["groq"]))
        assert applied is True
        assert kwargs["response_format"] == {"type": "json_object"}
        # json_object ne valide pas le schéma → pas de schéma envoyé
        assert "schema" not in kwargs["response_format"]

    def test_gemini_json_object_no_schema(self):
        """Piège Gemini neutralisé : l'endpoint OpenAI-compatible reçoit
        json_object — le schéma n'est pas envoyé, donc aucun champ optionnel
        n'est forcé/inventé (contrairement à response_schema du SDK Google)."""
        kwargs: dict = {"model": "gemini-2.5-flash"}
        cfg = _FakeCfg(json_mode_providers=["gemini"])
        applied = apply_json_mode(kwargs, "Gemini 2.5 Flash", _SCHEMA, cfg)
        assert applied is True
        assert kwargs["response_format"] == {"type": "json_object"}

    def test_primary_dispatch_by_key(self):
        kwargs: dict = {"model": "m"}
        # primary avec clé Groq → json_object
        cfg = _FakeCfg("gsk_x", json_mode_providers=["groq"])
        assert apply_json_mode(kwargs, "primary", _SCHEMA, cfg) is True
        assert kwargs["response_format"] == {"type": "json_object"}


class TestProviderCapsTable:
    def test_table_has_expected_keys(self):
        for key in ("openai", "groq", "gemini", "zai", "cloudflare", "zenmux", "nara"):
            assert key in PROVIDER_CAPS
            assert isinstance(PROVIDER_CAPS[key], ProviderCapabilities)
