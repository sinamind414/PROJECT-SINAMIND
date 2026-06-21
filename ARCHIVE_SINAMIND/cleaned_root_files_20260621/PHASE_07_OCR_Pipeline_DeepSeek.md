# PHASE 07 — OCR Pipeline Production (Modulaire)

**Projet** : SINAMIND / Khawarizmi Pro  
**Date** : 2026-06-20  
**Objectif** : Remplacer l'ancien script OCR monolithique par le **nouveau backend modulaire professionnel** (`services/ocr/`) et l'intégrer au pipeline canonique (DataLoader + 42 micro-concepts).

---

## RÈGLES ABSOLUES (à respecter à la lettre)

- Tout doit passer par `services/data_loader.py` (Single Source of Truth).
- Les sorties OCR doivent être directement consommables par `scripts/data_pipeline/integrate_ocr_bilan.py`.
- Utiliser **exactement** ces chemins :
  - `khawarizmi-backend/services/ocr/`
  - `khawarizmi-backend/scripts/ocr/ocr_pipeline_production.py`
- Activer `enable_hocr=True` (bounding boxes + vraie confiance par mot via TSV/hOCR).
- Ne jamais charger les anciens fichiers legacy (`annales_sciences_3as.json`, etc.).
- Qualité > Quantité. Code propre et modulaire.
- À la fin de cette phase, réponds **uniquement** par :  
  **"Phase 7 terminée"**

---

## ÉTAPE 1 : Créer l'architecture modulaire

Crée le dossier :
```
khawarizmi-backend/services/ocr/
```

### Fichier 1 : `config.py`

```python
from pathlib import Path
from dataclasses import dataclass

BASE_DIR = Path(__file__).resolve().parents[3]

@dataclass
class OCRConfig:
    tesseract_cmd: str = "tesseract"
    tesseract_langs: str = "ara+fra"
    default_dpi: int = 140
    default_psm: int = 3
    default_oem: int = 1
    default_retries: int = 2
    default_timeout: int = 180
    data_dir: Path = BASE_DIR / "data"
    annales_pdf_dir: Path = data_dir / "ANNALES_SVT_BAC_ALGERIE"
    ocr_output_base: Path = data_dir / "annales_workspace" / "OCR_PROD"
    enable_preprocessing: bool = True
    bundle_suffix: str = ".ocr_prod_full.txt"

config = OCRConfig()

def get_config():
    return config
```

### Fichier 2 : `models.py`

```python
from dataclasses import dataclass, field
from datetime import datetime
from typing import List, Optional, Dict, Any

@dataclass
class WordBox:
    text: str
    conf: float
    bbox: tuple

    def to_dict(self) -> Dict[str, Any]:
        return {"text": self.text, "conf": round(self.conf, 1), "bbox": self.bbox}

@dataclass
class PageResult:
    page: int
    text: str = ""
    char_count: int = 0
    confidence: float = 0.0
    status: str = "success"
    error: Optional[str] = None
    processing_time: float = 0.0
    words: List[WordBox] = field(default_factory=list)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "page": self.page,
            "text": self.text,
            "char_count": self.char_count,
            "confidence": round(self.confidence, 2),
            "status": self.status,
            "words": [w.to_dict() for w in self.words],
            "word_count": len(self.words)
        }

@dataclass
class VolumeSummary:
    volume: str
    pdf: str
    total_pages: int
    pages_processed: int
    errors: int
    total_characters: int
    avg_confidence: float
    quality_warning: str
    timestamp: str = field(default_factory=lambda: datetime.now().isoformat())
    bundle_dir: Optional[str] = None

    def to_dict(self) -> Dict[str, Any]:
        return {k: getattr(self, k) for k in self.__dataclass_fields__}
```

### Fichier 3 : `volume_processor.py`

```python
from pathlib import Path
from typing import Optional, Callable, List
import time
import logging

from .config import get_config
from .models import PageResult, VolumeSummary, WordBox
from .bundle import BundleManager

logger = logging.getLogger(__name__)
config = get_config()

class VolumeProcessor:
    def __init__(self, dpi=None, psm=None, oem=None, retries=None, enable_hocr=True):
        self.dpi = dpi or config.default_dpi
        self.psm = psm or config.default_psm
        self.oem = oem or config.default_oem
        self.retries = retries or config.default_retries
        self.enable_hocr = enable_hocr

    def process_volume(self, pdf_path: Path, progress_callback: Optional[Callable] = None) -> VolumeSummary:
        from .pdf_renderer import PDFRenderer
        from .preprocessor import ImagePreprocessor
        from .tesseract_ocr import TesseractOCR

        renderer = PDFRenderer(self.dpi)
        preprocessor = ImagePreprocessor()
        tesseract = TesseractOCR(self.psm, self.oem)
        bundle = BundleManager(pdf_path)

        total_pages = renderer.get_page_count(pdf_path)
        results: List[PageResult] = []
        errors = 0
        total_chars = 0
        confidences = []

        for i in range(total_pages):
            try:
                img = renderer.render_page(pdf_path, i)
                if not img: continue

                pre = preprocessor.preprocess(img)
                text, conf, words = tesseract.ocr_image(pre, return_hocr=self.enable_hocr)

                pr = PageResult(
                    page=i + 1,
                    text=text,
                    char_count=len(text),
                    confidence=conf,
                    words=[WordBox(w["text"], w["conf"], w["bbox"]) for w in (words or [])]
                )
                results.append(pr)
                total_chars += len(text)
                confidences.append(conf)

                bundle.write_page_text(i + 1, text)
                bundle.write_page_meta(pr)

                if progress_callback:
                    progress_callback({"page": i+1, "progress": round((i+1)/total_pages*100, 1)})

                preprocessor.cleanup(img)
            except Exception as e:
                errors += 1
                logger.error(f"Page {i+1} failed: {e}")

        avg = sum(confidences) / len(confidences) if confidences else 0
        summary = VolumeSummary(
            volume=pdf_path.stem,
            pdf=str(pdf_path),
            total_pages=total_pages,
            pages_processed=len(results),
            errors=errors,
            total_characters=total_chars,
            avg_confidence=round(avg, 2),
            quality_warning="None" if errors == 0 else "Check sequences",
            bundle_dir=str(bundle.get_bundle_path())
        )
        bundle.write_summary(summary)
        renderer.cleanup_temp(pdf_path)
        return summary

def get_volume_processor(**kwargs):
    return VolumeProcessor(**kwargs)
```

### Fichiers support à créer (implémentations fonctionnelles)

Crée aussi ces fichiers (versions fonctionnelles) :
- `pdf_renderer.py`
- `preprocessor.py`
- `tesseract_ocr.py` (avec support TSV + hOCR réel pour bounding boxes + confiance par mot)
- `bundle.py`
- `__init__.py`

**`__init__.py`** :
```python
from .volume_processor import get_volume_processor
from .config import get_config
from .models import VolumeSummary, PageResult

__all__ = ["get_volume_processor", "get_config", "VolumeSummary", "PageResult"]
```

---

## ÉTAPE 2 : Mettre à jour le CLI

**Fichier** : `khawarizmi-backend/scripts/ocr/ocr_pipeline_production.py`

Remplace **tout le contenu** par :

```python
#!/usr/bin/env python3
"""
OCR PIPELINE PRODUCTION — Thin CLI (Backend modulaire)
"""

import argparse
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from services.ocr import get_volume_processor

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("pdf")
    parser.add_argument("--dpi", type=int, default=140)
    parser.add_argument("--parallel", action="store_true")
    parser.add_argument("--max-workers", type=int, default=2)
    parser.add_argument("--no-hocr", action="store_true")
    args = parser.parse_args()

    pdf_path = Path(args.pdf).resolve()
    if not pdf_path.exists():
        print(f"❌ ERROR: PDF not found: {pdf_path}")
        sys.exit(1)

    processor = get_volume_processor(
        dpi=args.dpi,
        use_parallel=args.parallel,
        max_workers=args.max_workers,
        enable_hocr=not args.no_hocr
    )

    summary = processor.process_volume(pdf_path, use_parallel=args.parallel)
    print(json.dumps(summary.to_dict(), indent=2, ensure_ascii=False))

if __name__ == "__main__":
    main()
```

---

## ÉTAPE 3 : Mise à jour documentation

**Fichier** : `khawarizmi-backend/scripts/data_pipeline/README.md`

Ajoute à la fin du fichier :

```markdown
## OCR Production (Pipeline Modulaire)

Nouveau backend professionnel :

```bash
python scripts/ocr/ocr_pipeline_production.py \
  data/ANNALES_SVT_BAC_ALGERIE/KHELIFA_1/VOLUMES_KHELIFA1/KHELIFA1_VOLUME_05.pdf \
  --dpi 140
```

Puis intégrer dans le canonique :

```bash
python scripts/data_pipeline/integrate_ocr_bilan.py \
  --bilan-json data/annales_clean/questions_taggees.json
```
```

---

## Commande de validation

Une fois tout implémenté, teste avec :

```bash
python scripts/ocr/ocr_pipeline_production.py \
  data/ANNALES_SVT_BAC_ALGERIE/KHELIFA_1/VOLUMES_KHELIFA1/KHELIFA1_VOLUME_05.pdf \
  --dpi 120
```

Vérifie que :
- Le bundle est créé
- `avg_confidence` est réel (pas 65.0 fixe)
- Les `words` avec `bbox` apparaissent (si hOCR activé)

---

**Phase 7 terminée** (réponds uniquement par cette phrase quand c'est terminé)
