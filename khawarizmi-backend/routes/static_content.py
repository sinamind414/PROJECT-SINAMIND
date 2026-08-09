"""routes/static_content.py — Préchargement des contenus statiques pédagogiques.

Charge en mémoire (cache module) les contenus statiques utilisés par les
endpoints : l'essentiel BAC (mission du jour) et les cours markdown du
programme. Évite les lectures disque répétées et réduit la latence au
premier appel.
"""
from __future__ import annotations

import json
import logging
from pathlib import Path
from typing import Any

logger = logging.getLogger("khawarizmi.static_content")

_BACKEND = Path(__file__).resolve().parent.parent
_DATA = _BACKEND / "data"

_cache: dict[str, Any] = {}


def preload_static_cache() -> int:
    """Précharge les contenus statiques. Retourne le nombre d'éléments chargés."""
    global _cache
    loaded = 0

    essentials = _DATA / "essential" / "bac_essentials.json"
    if essentials.exists():
        try:
            _cache["bac_essentials"] = json.loads(essentials.read_text(encoding="utf-8"))
            loaded += 1
        except (json.JSONDecodeError, OSError) as exc:
            logger.warning("bac_essentials.json illisible : %s", exc)

    courses_dir = _DATA / "courses"
    if courses_dir.exists():
        for path in sorted(courses_dir.glob("*.md")):
            try:
                _cache[f"course:{path.stem}"] = path.read_text(encoding="utf-8")
                loaded += 1
            except OSError as exc:
                logger.warning("cours illisible %s : %s", path.name, exc)

    logger.info("Contenus statiques préchargés : %d", loaded)
    return loaded


def get_static_content(name: str) -> Any | None:
    """Retourne un contenu préchargé (bac_essentials, course:<stem>)."""
    return _cache.get(name)
