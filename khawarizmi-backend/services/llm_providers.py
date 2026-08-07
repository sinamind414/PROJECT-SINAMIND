"""services/llm_providers.py — Capacités déclarées par provider (audit O7).

Architecture : pas de flag global JSON_MODE — chaque provider déclare sa
capacité JSON native (json_schema / json_object / none). La cascade de
_llm_with_fallback peut passer d'un provider JSON-capable à un autre qui ne
l'est pas : le dispatch se fait par provider, au moment de chaque appel.

⚠️ Tous les providers sont appelés via le SDK AsyncOpenAI (même Gemini via son
endpoint OpenAI-compatible `generativelanguage.googleapis.com/v1beta/openai/`).
Donc pas de `generation_config.response_mime_type` ici : le mode JSON de Gemini
se déclare via `response_format={"type": "json_object"}` (supporté par
l'endpoint OpenAI-compat). Conséquence positive : le piège Gemini du plan
(response_schema force tous les champs déclarés) est neutralisé — json_object
garantit du JSON valide sans valider le schéma, donc aucun champ optionnel
inventé.

Valeurs prudentes (aucune clé réelle dans le sandbox → pas de test curl
possible) : les providers marqués "none" ne reçoivent JAMAIS response_format
(ils renverraient un 400 ou ignoreraient silencieusement). Ajustables dans
PROVIDER_CAPS après validation empirique en production.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Literal

JsonMode = Literal["json_schema", "json_object", "none"]


@dataclass(frozen=True)
class ProviderCapabilities:
    json_mode: JsonMode
    max_output_tokens: int = 4096
    supports_prefix_caching: bool = False  # pour C1 futur (prompt caching)


PROVIDER_CAPS: dict[str, ProviderCapabilities] = {
    "none": ProviderCapabilities("none", 4096, False),          # inconnus / non validés
    "openai": ProviderCapabilities("json_schema", 4096, True),
    "groq": ProviderCapabilities("json_object", 4096, False),
    "gemini": ProviderCapabilities("json_object", 8192, True),  # endpoint OpenAI-compat
    "zai": ProviderCapabilities("json_object", 4096, False),    # GLM-4.7 OpenAI-compatible
    "cloudflare": ProviderCapabilities("none", 2048, False),    # à valider empiriquement
    "zenmux": ProviderCapabilities("none", 4096, False),        # à valider empiriquement
    "nara": ProviderCapabilities("none", 4096, False),          # à valider empiriquement
}


def _normalize(name: str) -> str:
    return (name or "").strip().lower()


def primary_json_mode(cfg: Any) -> JsonMode:
    """Mode JSON du provider primaire, auto-détecté par la clé.

    Même logique que le docstring de llm.py : gsk_* → Groq, AIza* → Gemini,
    sinon OpenAI (gpt-4o-mini).
    """
    key = (cfg.OPENAI_API_KEY or "") if hasattr(cfg, "OPENAI_API_KEY") else ""
    if key.startswith("gsk_"):
        return "groq"
    if key.startswith("AIza"):
        return "gemini"
    return "openai"


def caps_for(provider_name: str, cfg: Any = None) -> ProviderCapabilities:
    """Capacités du provider, résolues par nom (matching mots-clés).

    "primary" est résolu par la clé (cfg). Les noms réels de la cascade
    ("Gemini 2.5 Flash", "Cloudflare GLM-5.2", "GLM-4.7", "ZenMux GLM-5.2",
    "NaraRouter", "OpenAI gpt-4o-mini") matchent par mots-clés.
    Inconnu → none (prudent : jamais de response_format non validé).
    """
    name = _normalize(provider_name)
    if name == "primary":
        return PROVIDER_CAPS[primary_json_mode(cfg)]

    if "gemini" in name:
        return PROVIDER_CAPS["gemini"]
    if "groq" in name or "llama" in name:
        return PROVIDER_CAPS["groq"]
    if "cloudflare" in name:
        return PROVIDER_CAPS["cloudflare"]
    if "glm-4.7" in name or "zai" in name:
        return PROVIDER_CAPS["zai"]
    if "zenmux" in name:
        return PROVIDER_CAPS["zenmux"]
    if "nara" in name:
        return PROVIDER_CAPS["nara"]
    if "openai" in name or "gpt" in name:
        return PROVIDER_CAPS["openai"]

    return PROVIDER_CAPS["none"]


def apply_json_mode(
    call_kwargs: dict[str, Any],
    provider_name: str,
    json_schema: dict | None,
    cfg: Any = None,
) -> bool:
    """Injecte response_format dans call_kwargs si le provider le supporte.

    Retourne True si le mode JSON natif a été appliqué (pour tagger la
    réponse avec _khawarizmi_json_mode). Fonction PURE — testable sans réseau.

    - json_schema  → response_format={"type":"json_schema","json_schema":
                     {"name":"correction_output","strict":True,"schema":...}}
    - json_object  → response_format={"type":"json_object"}
                     (garantit du JSON valide, ne valide pas le schéma)
    - none / inconnu → rien ajouté (le parser fallback fait le travail)
    """
    if json_schema is None:
        return False
    caps = caps_for(provider_name, cfg)
    if caps.json_mode == "json_schema":
        call_kwargs["response_format"] = {
            "type": "json_schema",
            "json_schema": {
                "name": "correction_output",
                "strict": True,
                "schema": json_schema,
            },
        }
        return True
    if caps.json_mode == "json_object":
        call_kwargs["response_format"] = {"type": "json_object"}
        return True
    return False
