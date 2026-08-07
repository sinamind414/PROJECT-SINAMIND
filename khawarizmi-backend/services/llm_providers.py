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


def canonical_name(provider_name: str, cfg: Any = None) -> str:
    """Nom canonique (clé de PROVIDER_CAPS) d'un provider de la cascade.

    "primary" est résolu par la clé (cfg). Les noms réels ("Gemini 2.5 Flash",
    "Cloudflare GLM-5.2", "GLM-4.7", "ZenMux GLM-5.2", "NaraRouter",
    "OpenAI gpt-4o-mini") matchent par mots-clés. Inconnu → "none".
    """
    name = _normalize(provider_name)
    if name == "primary":
        return primary_json_mode(cfg)
    if "gemini" in name:
        return "gemini"
    if "groq" in name or "llama" in name:
        return "groq"
    if "cloudflare" in name:
        return "cloudflare"
    if "glm-4.7" in name or "zai" in name:
        return "zai"
    if "zenmux" in name:
        return "zenmux"
    if "nara" in name:
        return "nara"
    if "openai" in name or "gpt" in name:
        return "openai"
    return name if name in PROVIDER_CAPS else "none"


def caps_for(provider_name: str, cfg: Any = None) -> ProviderCapabilities:
    """Capacités du provider, résolues par nom canonique."""
    return PROVIDER_CAPS[canonical_name(provider_name, cfg)]


def should_use_json_mode(provider_name: str, cfg: Any = None) -> bool:
    """Le JSON natif est-il activé pour CE provider ?

    Deux conditions : le provider supporte le JSON mode (caps.json_mode !=
    "none") ET son nom canonique est dans la liste config json_mode_providers
    (défaut vide = aucun — activation progressive, rollback par provider).
    """
    caps = caps_for(provider_name, cfg)
    if caps.json_mode == "none":
        return False
    enabled = getattr(cfg, "json_mode_providers", None) or []
    return canonical_name(provider_name, cfg) in enabled


def apply_json_mode(
    call_kwargs: dict[str, Any],
    provider_name: str,
    json_schema: dict | None,
    cfg: Any = None,
) -> bool:
    """Injecte response_format dans call_kwargs si JSON natif ACTIVÉ pour ce
    provider (capacité + liste config). Fonction PURE — testable sans réseau.

    Retourne True si le mode JSON natif a été appliqué (pour tagger la
    réponse avec _khawarizmi_json_mode).

    - json_schema  → response_format={"type":"json_schema","json_schema":
                     {"name":"correction_output","strict":True,"schema":...}}
    - json_object  → response_format={"type":"json_object"}
                     (garantit du JSON valide, ne valide pas le schéma)
    - none / non activé → rien ajouté (le parser fallback fait le travail)
    """
    if json_schema is None:
        return False
    if not should_use_json_mode(provider_name, cfg):
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
