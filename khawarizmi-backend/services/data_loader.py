"""
services/data_loader.py
SINGLE SOURCE OF TRUTH for all educational data.

From now on, this is the ONLY place that should load programme, annales, lexique.
"""

import json
import logging
from pathlib import Path
from typing import Any

logger = logging.getLogger("khawarizmi.data_loader")

DATA_ROOT = Path(__file__).parent.parent / "data"
OFFICIAL_DIR = DATA_ROOT / "official"


class DataLoader:
    def __init__(self, data_dir: str | None = None):
        self.data_dir = Path(data_dir) if data_dir else DATA_ROOT
        self._programme_canonical: dict = {}
        self._loaded_from = {}

    def load_canonical_programme(self) -> dict[str, Any]:
        """Load the new official canonical programme (preferred)."""
        candidates = [
            OFFICIAL_DIR / "programme_svt_3as_canonical.json",
            self.data_dir / "official" / "programme_svt_3as_canonical.json",
        ]

        for path in candidates:
            if path.exists():
                with open(path, encoding="utf-8") as f:
                    data = json.load(f)
                self._programme_canonical = data
                self._loaded_from["programme"] = str(path)
                logger.info(f"✅ Loaded CANONICAL programme from {path}")
                return data

        # Temporary fallback (will be removed later)
        old_path = self.data_dir / "programme_sciences_3as.json"
        if old_path.exists():
            logger.warning("⚠️ FALLBACK: Using OLD programme_sciences_3as.json")
            with open(old_path, encoding="utf-8") as f:
                data = json.load(f)
            self._programme_canonical = data
            self._loaded_from["programme"] = str(old_path) + " (DEPRECATED)"
            return data

        logger.error("❌ No programme found (canonical or legacy) — returning empty dict")
        self._programme_canonical = {}
        return {}

    def get_programme(self) -> dict:
        if not self._programme_canonical:
            self.load_canonical_programme()
        return self._programme_canonical

    def get_data_foundation_report(self) -> dict:
        """Rich diagnostic report for debug endpoint."""
        prog = self.get_programme()

        total_mc = 0
        chapters = 0
        if prog and "domaines" in prog:
            for d in prog.get("domaines", []):
                for ch in d.get("chapitres", []):
                    chapters += 1
                    total_mc += len(ch.get("micro_concepts", []))

        return {
            "programme": {
                "source": self._loaded_from.get("programme"),
                "version": prog.get("metadata", {}).get("version") if prog else None,
                "total_micro_concepts": total_mc,
                "total_chapters": chapters,
                "status": "CANONICAL" if "official" in str(self._loaded_from.get("programme", "")) else "LEGACY",
            },
            "migration": {"phase": "deep_foundation"},
        }

    def get_loading_report(self) -> dict:
        """Loading report for engine initialization."""
        self.get_programme()
        return {
            "loaded_from": dict(self._loaded_from),
            "micro_concepts_count": sum(
                len(ch.get("micro_concepts", []))
                for d in self._programme_canonical.get("domaines", [])
                for ch in d.get("chapitres", [])
            )
            if self._programme_canonical and "domaines" in self._programme_canonical
            else 0,
        }


# Singleton
_loader_instance = None


def get_data_loader(data_dir: str | None = None) -> DataLoader:
    global _loader_instance
    if _loader_instance is None:
        _loader_instance = DataLoader(data_dir)
    return _loader_instance
