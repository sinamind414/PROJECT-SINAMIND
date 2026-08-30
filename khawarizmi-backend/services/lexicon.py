"""Lexique $lex: versionné (S5). Fichier git, pas un parseur de livre.

Lookup : fichier d'abord, puis _SYNONYMS (Savoir) pour les clés pas encore extraites.
Clé inconnue → liste vide (validate_rubrics FAIL).
"""

from __future__ import annotations

import json
from pathlib import Path

_BACKEND = Path(__file__).resolve().parent.parent
_LEX_PATH = _BACKEND / "data" / "lexicons" / "svt_terms.v1.json"

_file_cache: dict[str, list[str]] | None = None


def lexicon_path() -> Path:
    return _LEX_PATH


def reset_lexicon_cache() -> None:
    global _file_cache
    _file_cache = None


def _load_file() -> dict[str, list[str]]:
    global _file_cache
    if _file_cache is not None:
        return _file_cache
    if not _LEX_PATH.is_file():
        _file_cache = {}
        return _file_cache
    raw = json.loads(_LEX_PATH.read_text(encoding="utf-8"))
    terms = raw.get("terms") if isinstance(raw, dict) else None
    if not isinstance(terms, dict):
        raise RuntimeError(f"lexicon invalide: { _LEX_PATH }")
    out: dict[str, list[str]] = {}
    for k, v in terms.items():
        if isinstance(k, str) and isinstance(v, list):
            out[k] = [str(x) for x in v if x]
    _file_cache = out
    return _file_cache


def has_lex(key: str) -> bool:
    if key in _load_file():
        return True
    from services.savoir_corrector import _SYNONYMS

    return key in _SYNONYMS


def in_file(key: str) -> bool:
    return key in _load_file()


def synonyms(key: str) -> list[str]:
    """Synonymes pour $lex:key. Fichier > _SYNONYMS. Inconnu → []."""
    file_terms = _load_file().get(key)
    if file_terms:
        return list(file_terms)
    from services.savoir_corrector import _SYNONYMS

    return list(_SYNONYMS.get(key) or [])
