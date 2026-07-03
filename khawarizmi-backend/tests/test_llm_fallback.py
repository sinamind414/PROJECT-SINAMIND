"""tests/test_llm_fallback.py — 10 tests pour le fallback LLM et JSON parser.

Couvre :
- parse_llm_json : brut, markdown, tronqué, invalide → erreur
- _call_with_fallback : succès direct, validateur OK, validateur KO → fallback,
  tous échouent → RuntimeError, rate limit → fallback
"""

from __future__ import annotations

from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from services.llm import _call_with_fallback
from services.llm_parser import parse_llm_json

# ═══════════════════════════════════════════════════════════════════════
# parse_llm_json (4 tests)
# ═══════════════════════════════════════════════════════════════════════


class TestParseLLMJson:
    def test_plain_json(self):
        raw = '{"score": 4, "ok": true}'
        assert parse_llm_json(raw) == {"score": 4, "ok": True}

    def test_markdown_fence(self):
        raw = '```json\n{"score": 4}\n```'
        assert parse_llm_json(raw) == {"score": 4}

    def test_raw_with_extra_text_and_repairable_object(self):
        raw = 'Voici le résultat:\n{"score": 4, "ok": true} texte après'
        result = parse_llm_json(raw)
        assert result == {"score": 4, "ok": True}

    def test_malformed_unrepairable_raises(self):
        raw = '{"score": 4, "items": [1, 2, 3}'  # } avant ]
        with pytest.raises(ValueError, match="non-JSON"):
            parse_llm_json(raw)

    def test_empty_raises(self):
        with pytest.raises(ValueError, match="vide"):
            parse_llm_json("")

    def test_garbage_raises(self):
        with pytest.raises(ValueError, match="non-JSON"):
            parse_llm_json("pas du json du tout")


# ═══════════════════════════════════════════════════════════════════════
# _call_with_fallback (6 tests)
# ═══════════════════════════════════════════════════════════════════════


def _make_llm_response(content: str) -> MagicMock:
    response = MagicMock()
    response.choices = [MagicMock()]
    response.choices[0].message.content = content
    return response


class TestCallWithFallback:
    @pytest.mark.asyncio
    async def test_primary_success(self):
        client = AsyncMock()
        client.chat.completions.create = AsyncMock(
            return_value=_make_llm_response('{"score": 4}')
        )
        result = await _call_with_fallback(
            messages=[{"role": "user", "content": "test"}],
            primary_client=client,
            primary_model="test-model",
        )
        assert result.choices[0].message.content == '{"score": 4}'
        assert result._khawarizmi_provider == "primary"

    @pytest.mark.asyncio
    async def test_validator_passes(self):
        client = AsyncMock()
        client.chat.completions.create = AsyncMock(
            return_value=_make_llm_response('{"score": 4}')
        )

        def validator(raw: str) -> bool:
            return '"score"' in raw

        result = await _call_with_fallback(
            messages=[{"role": "user", "content": "test"}],
            primary_client=client,
            primary_model="test-model",
            response_validator=validator,
        )
        assert result.choices[0].message.content == '{"score": 4}'

    @pytest.mark.asyncio
    async def test_validator_rejects_triggers_fallback(self):
        """Si le validateur rejette le contenu primaire, le fallback est tenté.
        Sans fallback valide, une RuntimeError est levée."""
        primary = AsyncMock()
        primary.chat.completions.create = AsyncMock(
            return_value=_make_llm_response("pas du JSON")
        )

        def validator(raw: str) -> bool:
            return raw.strip().startswith("{")

        with patch.object(
            __import__("services.llm", fromlist=["get_settings"]),
            "get_settings",
            return_value=MagicMock(
                GEMINI_API_KEY="test",
                gemini_base_url="https://generativelanguage.googleapis.com",
                gemini_model="gemini-2.5-flash",
                CLOUDFLARE_API_TOKEN="test",
                cloudflare_base_url="https://api.cloudflare.com",
                cloudflare_model="glm-5.2",
                CLOUDFLARE_ACCOUNT_ID="test",
                ZAI_API_KEY=None,
                ZENMUX_API_KEY=None,
                NARA_API_KEY=None,
                OPENAI_FALLBACK_API_KEY=None,
                REAL_OPENAI_API_KEY=None,
            ),
        ), pytest.raises(RuntimeError, match="Tous les providers"):
            await _call_with_fallback(
                messages=[{"role": "user", "content": "test"}],
                primary_client=primary,
                primary_model="test-model",
                response_validator=validator,
            )

        primary.chat.completions.create.assert_awaited_once()

    @pytest.mark.asyncio
    async def test_rate_limit_triggers_fallback_and_fails(self):
        """Rate limit (429) sur le primaire → fallback ; sans fallback valide → erreur."""
        primary = AsyncMock()
        primary.chat.completions.create = AsyncMock(
            side_effect=Exception("Error code: 429 - Rate limit")
        )

        with patch.object(
            __import__("services.llm", fromlist=["get_settings"]),
            "get_settings",
            return_value=MagicMock(
                GEMINI_API_KEY="test",
                gemini_base_url="https://generativelanguage.googleapis.com",
                gemini_model="gemini-2.5-flash",
                CLOUDFLARE_API_TOKEN=None,
                ZAI_API_KEY=None,
                ZENMUX_API_KEY=None,
                NARA_API_KEY=None,
                OPENAI_FALLBACK_API_KEY=None,
                REAL_OPENAI_API_KEY=None,
            ),
        ), pytest.raises(RuntimeError, match="Tous les providers"):
            await _call_with_fallback(
                messages=[{"role": "user", "content": "test"}],
                primary_client=primary,
                primary_model="test-model",
            )

    @pytest.mark.asyncio
    async def test_non_rate_limit_error_bubbles(self):
        """Erreur non-rate-limit (401) remonte sans fallback."""
        primary = AsyncMock()
        primary.chat.completions.create = AsyncMock(
            side_effect=Exception("Error code: 401 - Invalid API key")
        )

        with pytest.raises(Exception, match="401"):
            await _call_with_fallback(
                messages=[{"role": "user", "content": "test"}],
                primary_client=primary,
                primary_model="test-model",
            )

    @pytest.mark.asyncio
    async def test_quota_triggers_fallback(self):
        """'quota exhausted' est classé comme rate-limit et déclenche le fallback."""
        primary = AsyncMock()
        primary.chat.completions.create = AsyncMock(
            side_effect=Exception("quota exhausted for this model")
        )

        with patch.object(
            __import__("services.llm", fromlist=["get_settings"]),
            "get_settings",
            return_value=MagicMock(
                GEMINI_API_KEY=None,
                CLOUDFLARE_API_TOKEN=None,
                ZAI_API_KEY=None,
                ZENMUX_API_KEY=None,
                NARA_API_KEY=None,
                OPENAI_FALLBACK_API_KEY=None,
                REAL_OPENAI_API_KEY=None,
            ),
        ), pytest.raises(RuntimeError, match="Tous les providers"):
            await _call_with_fallback(
                messages=[{"role": "user", "content": "test"}],
                primary_client=primary,
                primary_model="test-model",
            )
