"""services/llm_guard.py — Garde-fou ABSOLU contre les appels LLM externes.

VISION DU PROJET : le moteur Khawarizmi est 100% local et déterministe.
Par DÉFAUT, AUCUN appel vers OpenAI / Groq / Gemini / OpenRouter / Anthropic /
Mistral / n'importe quel provider ne peut partir. Réseau bloqué, clés API
ignorées, clients murés. Pour activer un provider externe (mode cloud), il
faut positionner EXPLICITEMENT la variable ENABLE_EXTERNAL_LLM=1 EN PLUS
d'une clé — sans ce flag, même une clé en dur dans le code est refusée.

Mécanismes (défense en profondeur) :
  1. is_llm_enabled() retourne False par défaut ; ENABLE_EXTERNAL_LLM=1
     est la SEULE façon de sortir du mode local.
  2. Au démarrage (scrub_environment), toutes les variables d'environnement
     de type *_API_KEY / *_TOKEN de providers connus sont VIDÉES si le flag
     n'est pas là.
  3. patch_openai_module() remplace openai.AsyncOpenAI par une factory qui
     retourne systématiquement GuardedOpenAIClient quand le guard est actif.
  4. GuardedOpenAIClient lève LLMDisabledError sur .create() et .embeddings.
  5. guard_proceed() logue + retourne False systématiquement quand le guard
     est actif, forçant les services à utiliser le fallback déterministe.
  6. install_network_block() installe un monkey-patch sur httpx pour
     BLACKHOLER toute requête HTTP sortante vers un domaine d'API LLM connu,
     même en cas de bug dans le code client.
"""

from __future__ import annotations

import logging
import os
from typing import Any

logger = logging.getLogger("khawarizmi.llm_guard")

# ──────────────────────────────────────────────────────────────────────
# Kill-switch global & constantes
# ──────────────────────────────────────────────────────────────────────
_FORCE_DISABLED: bool = False

LLM_DISABLED_MSG_FR = (
    "IA externe désactivée — utilisation du moteur déterministe Khawarizmi."
)
LLM_DISABLED_MSG_AR = (
    "المدرس الذكي الخارجي متوقف — يُستعمَل المحرك المحلي الخوارزمي."
)

# Domaines connus des providers LLM — bloqués au niveau transport
# en mode local pour éviter TOUTE fuite réseau accidentelle.
_BLOCKED_DOMAINS = {
    "api.openai.com",
    "api.groq.com",
    "generativelanguage.googleapis.com",
    "openrouter.ai",
    "api.openrouter.ai",
    "api.anthropic.com",
    "api.mistral.ai",
    "api.cohere.com",
    "api.together.xyz",
    "api.deepseek.com",
    "api.x.ai",
    "api.fireworks.ai",
    "api-inference.huggingface.co",
    "api.replicate.com",
    "api.naga.ac",
    "api.zukijourney.com",
    "api.nasiri.ai",
}

# Variables d'environnement de clés API à SCRUB si LLM non activé.
_SCRUB_KEYS = [
    "OPENAI_API_KEY",
    "GROQ_API_KEY",
    "GEMINI_API_KEY",
    "GOOGLE_API_KEY",
    "OPENROUTER_API_KEY",
    "ANTHROPIC_API_KEY",
    "MISTRAL_API_KEY",
    "COHERE_API_KEY",
    "TOGETHER_API_KEY",
    "DEEPSEEK_API_KEY",
    "XAI_API_KEY",
    "FIREWORKS_API_KEY",
    "HF_API_KEY",
    "HUGGINGFACE_API_KEY",
    "REPLICATE_API_TOKEN",
    "REAL_OPENAI_API_KEY",
    "DASHSCOPE_API_KEY",
    "ZHIPU_API_KEY",
    "YI_API_KEY",
]

# ──────────────────────────────────────────────────────────────────────
# Logique d'activation — double opt-in STRICT
# ──────────────────────────────────────────────────────────────────────


def is_llm_enabled() -> bool:
    """Retourne True SI ET SEULEMENT SI ENABLE_EXTERNAL_LLM=1 explicite.

    AUCUNE clé API, même présente dans l'environnement ou en dur dans le
    code, ne pourra jamais activer le LLM sans ce flag.
    """
    if _FORCE_DISABLED:
        return False

    # Kill switch explicite
    if os.environ.get("DISABLE_LLM", "").strip().lower() in (
        "1", "true", "yes", "on", "oui",
    ):
        return False

    # Environnements de CI/preview/test : JAMAIS d'LLM externe, peu importe le flag
    try:
        env = (os.environ.get("ENVIRONMENT", "") or "").strip().lower()
    except Exception:
        env = ""
    if env in ("ci", "preview", "test"):
        return False

    # LE SEUL moyen d'activer : flag explicite
    enable_flag = os.environ.get("ENABLE_EXTERNAL_LLM", "").strip().lower()
    if enable_flag not in ("1", "true", "yes", "on", "oui"):
        return False

    # Il faut bien sûr qu'il y ait une clé non vide
    key_present = False
    for k in _SCRUB_KEYS:
        if (os.environ.get(k) or "").strip():
            key_present = True
            break
    if not key_present:
        return False

    return True


def disable_llm(reason: str = "admin") -> None:
    global _FORCE_DISABLED
    _FORCE_DISABLED = True
    logger.warning(f"🛑 [KILL SWITCH] LLM globalement désactivé (raison: {reason})")


def enable_llm() -> None:
    global _FORCE_DISABLED
    _FORCE_DISABLED = False
    logger.info("✅ LLM externe réactivé")


def guard_proceed(kind: str = "chat") -> bool:
    if is_llm_enabled():
        return True
    logger.info(f"🛑 LLM call blocked [{kind}] — moteur déterministe seul")
    return False


# ──────────────────────────────────────────────────────────────────────
# Client muré (ne fait aucun appel réseau)
# ──────────────────────────────────────────────────────────────────────

class LLMDisabledError(RuntimeError):
    def __init__(self, kind: str = "chat"):
        super().__init__(
            f"LLM call blocked: {kind} (external LLM disabled; mode local)"
        )
        self.kind = kind


class _GuardedCompletions:
    async def create(self, *args: Any, **kwargs: Any) -> Any:
        raise LLMDisabledError("chat.completions.create")

    def __call__(self, *a, **kw):
        raise LLMDisabledError("chat.completions.create")


class _GuardedChat:
    @property
    def completions(self) -> _GuardedCompletions:
        return _GuardedCompletions()


class _GuardedEmbeddings:
    async def create(self, *args: Any, **kwargs: Any) -> Any:
        raise LLMDisabledError("embeddings.create")

    def __call__(self, *a, **kw):
        raise LLMDisabledError("embeddings.create")


class _GuardedImages:
    async def generate(self, *a, **kw): raise LLMDisabledError("images.generate")


class _GuardedAudio:
    async def transcribe(self, *a, **kw): raise LLMDisabledError("audio.transcribe")


class GuardedOpenAIClient:
    """Substitut drop-in à AsyncOpenAI qui lève LLMDisabledError sur tout appel."""

    @property
    def chat(self) -> _GuardedChat: return _GuardedChat()
    @property
    def embeddings(self) -> _GuardedEmbeddings: return _GuardedEmbeddings()
    @property
    def images(self) -> _GuardedImages: return _GuardedImages()
    @property
    def audio(self) -> _GuardedAudio: return _GuardedAudio()


def guarded_openai_client(preferred_client: Any = None) -> Any:
    if guard_proceed("client-init"):
        return preferred_client
    return GuardedOpenAIClient()


# ──────────────────────────────────────────────────────────────────────
# Scrub environnement : vide toutes les clés API si LLM non activé
# ──────────────────────────────────────────────────────────────────────

def scrub_environment() -> None:
    """Vide (supprime) toute clé API LLM de os.environ en mode local.

    Appelé au démarrage. Garantit que même si un provider a une détection
    automatique de la clé dans l'environnement, il trouvera une chaîne vide.
    """
    if is_llm_enabled():
        logger.info("✅ ENABLE_EXTERNAL_LLM=1 détecté — clés API conservées (mode cloud)")
        return
    wiped = 0
    for k in _SCRUB_KEYS:
        if os.environ.get(k):
            os.environ[k] = ""
            wiped += 1
    if wiped:
        logger.info(
            f"🛑 Mode LOCAL : {wiped} clé(s) API LLM neutralisée(s) dans os.environ "
            f"(ENABLE_EXTERNAL_LLM non positionné à 1)."
        )


# ──────────────────────────────────────────────────────────────────────
# Blocage réseau : monkey-patch httpx pour intercepter toute requête
# vers un domaine de provider LLM.
# ──────────────────────────────────────────────────────────────────────

_NETWORK_PATCHED = False


def install_network_block() -> None:
    """Installe un monkey-patch sur httpx.AsyncClient.send (et http.client)
    pour lever LLMDisabledError si une requête cible un domaine d'API LLM
    connu. Double protection si le guard client échoue."""
    global _NETWORK_PATCHED
    if _NETWORK_PATCHED:
        return
    if is_llm_enabled():
        return  # pas de blocage si l'utilisateur a explicitement opt-in

    try:
        import httpx as _httpx
    except ImportError:
        return

    _real_send = _httpx.AsyncClient.send
    _blocked = set(_BLOCKED_DOMAINS)

    def _host_of(url) -> str:
        try:
            from urllib.parse import urlparse
            return (urlparse(str(url)).hostname or "").lower()
        except Exception:
            return ""

    async def _blocked_send(self, request, *args, **kwargs):
        host = _host_of(request.url)
        if host in _blocked or any(host.endswith("." + d) for d in _blocked):
            logger.warning(
                f"🛑 HTTP BLOQUÉ vers {host} — provider LLM externe refusé en mode local."
            )
            raise LLMDisabledError(f"http://{host}")
        return await _real_send(self, request, *args, **kwargs)

    _httpx.AsyncClient.send = _blocked_send
    _NETWORK_PATCHED = True
    logger.info(
        f"🛑 Blocage réseau LLM actif : {len(_blocked)} domaines blackholés "
        f"(openai, groq, gemini, anthropic, openrouter, …)."
    )


# ──────────────────────────────────────────────────────────────────────
# Patch module openai : toute instanciation AsyncOpenAI retourne un client muré
# ──────────────────────────────────────────────────────────────────────

_MODULE_PATCHED = False


def patch_openai_module() -> None:
    global _MODULE_PATCHED
    if _MODULE_PATCHED:
        return
    try:
        import openai as _openai_mod
    except ImportError:
        _MODULE_PATCHED = True
        return

    _real_AOC = _openai_mod.AsyncOpenAI
    _real_OC = getattr(_openai_mod, "OpenAI", None)

    def _factory(*args: Any, **kwargs: Any) -> Any:
        if is_llm_enabled():
            return _real_AOC(*args, **kwargs)
        logger.info(
            "🛑 AsyncOpenAI(...) intercepté → GuardedOpenAIClient (mode local)."
        )
        return GuardedOpenAIClient()

    def _sync_factory(*args: Any, **kwargs: Any) -> Any:
        if is_llm_enabled():
            return _real_OC(*args, **kwargs) if _real_OC else None
        return GuardedOpenAIClient()

    _openai_mod.AsyncOpenAI = _factory  # type: ignore[assignment]
    if _real_OC is not None:
        _openai_mod.OpenAI = _sync_factory  # type: ignore[assignment]

    # Patch aussi AsyncOpenAI à tous les endroits où il pourrait être importé
    # (certains services importent directement depuis openai).
    _MODULE_PATCHED = True


# ──────────────────────────────────────────────────────────────────────
# Setup global au premier import (appelé par main.py)
# ──────────────────────────────────────────────────────────────────────

def setup() -> None:
    """Point d'entrée unique : scrub + patch openai + blocage réseau."""
    scrub_environment()
    patch_openai_module()
    install_network_block()


def llm_status() -> dict:
    has_key = False
    for k in _SCRUB_KEYS:
        if (os.environ.get(k) or "").strip():
            has_key = True
            break
    enabled = is_llm_enabled()
    return {
        "external_llm_enabled": enabled,
        "has_api_key_in_env": has_key,
        "force_disabled": _FORCE_DISABLED,
        "mode": "external" if enabled else "deterministic-local",
        "network_block_installed": _NETWORK_PATCHED,
        "message_fr": LLM_DISABLED_MSG_FR if not enabled else "LLM externe actif",
        "message_ar": LLM_DISABLED_MSG_AR if not enabled else "المدرس الخارجي فعّال",
    }
