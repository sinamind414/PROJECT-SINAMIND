# PHASE 02 — Créer le Data Loader (Single Source of Truth)

## Fichier à créer

Chemin :
```
khawarizmi-backend/services/data_loader.py
```

## Contenu complet du fichier

```python
"""
services/data_loader.py
SINGLE SOURCE OF TRUTH for all educational data.

From now on, this is the ONLY place that should load programme, annales, lexique.
"""

import json
import logging
from pathlib import Path
from typing import Dict, Any, Optional

logger = logging.getLogger("khawarizmi.data_loader")

DATA_ROOT = Path(__file__).parent.parent / "data"
OFFICIAL_DIR = DATA_ROOT / "official"

class DataLoader:
    def __init__(self, data_dir: Optional[str] = None):
        self.data_dir = Path(data_dir) if data_dir else DATA_ROOT
        self._programme_canonical: Dict = {}
        self._loaded_from = {}

    def load_canonical_programme(self) -> Dict[str, Any]:
        """Load the new official canonical programme (preferred)."""
        candidates = [
            OFFICIAL_DIR / "programme_svt_3as_canonical.json",
            self.data_dir / "official" / "programme_svt_3as_canonical.json",
        ]
        
        for path in candidates:
            if path.exists():
                with open(path, "r", encoding="utf-8") as f:
                    data = json.load(f)
                self._programme_canonical = data
                self._loaded_from["programme"] = str(path)
                logger.info(f"✅ Loaded CANONICAL programme from {path}")
                return data
        
        # Temporary fallback (will be removed later)
        old_path = self.data_dir / "programme_sciences_3as.json"
        if old_path.exists():
            logger.warning("⚠️ FALLBACK: Using OLD programme_sciences_3as.json")
            with open(old_path, "r", encoding="utf-8") as f:
                data = json.load(f)
            self._programme_canonical = data
            self._loaded_from["programme"] = str(old_path) + " (DEPRECATED)"
            return data
        
        raise FileNotFoundError("No programme found (canonical or legacy)")

    def get_programme(self) -> Dict:
        if not self._programme_canonical:
            self.load_canonical_programme()
        return self._programme_canonical

    def get_data_foundation_report(self) -> Dict:
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
                "status": "CANONICAL" if "official" in str(self._loaded_from.get("programme", "")) else "LEGACY"
            },
            "migration": {
                "phase": "deep_foundation"
            }
        }

# Singleton
_loader_instance = None

def get_data_loader(data_dir: Optional[str] = None) -> DataLoader:
    global _loader_instance
    if _loader_instance is None:
        _loader_instance = DataLoader(data_dir)
    return _loader_instance
```

**Fin de la Phase 2.** Confirme avant de passer à la Phase 3.