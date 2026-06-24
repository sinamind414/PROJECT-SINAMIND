#!/usr/bin/env python3
"""GPU Batch OCR - EasyOCR + RTX 3060"""

from __future__ import annotations

import logging
from pathlib import Path

PDF_DIR = Path(
    r"C:\Users\zakaria\Documents\projet khawarizmi A\LIVRES SCOLAIRES\ANALES SCIENCES\LIVRES ANNALES SVT BAC\DOSSIER ANNALES KHELIFA"
)
OUTPUT_BASE = Path(r"C:\Users\zakaria\Documents\PROJET KHAWARIZMI IA\khawarizmi-backend\data\ocr_gpu_output")
MAX_DIM = 1600
SEP = "=" * 70
LOG = logging.getLogger("gpu_batch_ocr")
