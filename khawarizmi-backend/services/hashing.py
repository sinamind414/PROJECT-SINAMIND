"""services/hashing.py — Hachage RGPD des réponses élèves.

Audit P0-4.2 : le SHA-256 simple est vulnérable aux dictionnaires (les réponses
arabes courtes ont un espace réduit). On utilise HMAC-SHA256 avec un pepper
serveur (SECRET_KEY) — sans le secret, impossible de brute-forcer.
"""
from __future__ import annotations

import hashlib
import hmac

from config import get_settings


def _pepper() -> bytes:
    cfg = get_settings()
    key = cfg.SECRET_KEY or "dev-only-key"
    return key.encode("utf-8")


def hash_answer(text: str) -> str:
    """HMAC-SHA256(pepper, text) — hexadécimal."""
    if not text:
        return ""
    return hmac.new(_pepper(), text.encode("utf-8"), hashlib.sha256).hexdigest()


def hash_text(text: str | None) -> str | None:
    if text is None:
        return None
    return hash_answer(text)
