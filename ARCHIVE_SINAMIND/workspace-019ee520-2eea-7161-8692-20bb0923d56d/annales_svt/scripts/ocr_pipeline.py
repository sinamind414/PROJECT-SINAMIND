#!/usr/bin/env python3
"""
Pipeline OCR pour les annales SVT.
Convertit un PDF scanné en texte via PyMuPDF + Tesseract (ara+eng).

Usage:
    python3 ocr_pipeline.py <pdf_path> [--dpi 200] [--start 1] [--end 40]

Sortie: fichier .txt à côté du PDF avec le texte OCR de chaque page.
"""
import sys
import os
import subprocess
import tempfile
import argparse
from pathlib import Path

import fitz  # PyMuPDF


def ocr_pdf(pdf_path: str, dpi: int = 200, start: int = 1, end: int = None) -> str:
    doc = fitz.open(pdf_path)
    total = doc.page_count
    if end is None or end > total:
        end = total
    start = max(1, start)

    base = Path(pdf_path).stem
    out_path = Path(pdf_path).with_suffix(".ocr.txt")
    mat = fitz.Matrix(dpi / 72, dpi / 72)

    all_text = []
    for i in range(start - 1, end):
        page = doc[i]
        pix = page.get_pixmap(matrix=mat)

        # Save to temp file for tesseract
        with tempfile.NamedTemporaryFile(suffix=".png", delete=False) as tmp:
            tmp_path = tmp.name
            pix.save(tmp_path)

        # Run tesseract
        try:
            result = subprocess.run(
                ["tesseract", tmp_path, "-", "-l", "ara+eng", "--psm", "3"],
                capture_output=True, text=True, timeout=30
            )
            text = result.stdout.strip()
        except Exception as e:
            text = f"[OCR ERROR: {e}]"
        finally:
            os.unlink(tmp_path)

        header = f"\n{'='*70}\nPAGE {i+1}\n{'='*70}\n"
        all_text.append(header + text)
        print(f"  Page {i+1}/{end}: {len(text)} chars")

    doc.close()

    full_text = "\n".join(all_text)
    with open(out_path, "w", encoding="utf-8") as f:
        f.write(full_text)

    print(f"\n✅ OCR terminé: {out_path} ({len(full_text)} chars)")
    return str(out_path)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="OCR pipeline pour annales SVT")
    parser.add_argument("pdf_path", help="Chemin du PDF à traiter")
    parser.add_argument("--dpi", type=int, default=200, help="Résolution (défaut: 200)")
    parser.add_argument("--start", type=int, default=1, help="Page de début")
    parser.add_argument("--end", type=int, default=None, help="Page de fin")
    args = parser.parse_args()

    ocr_pdf(args.pdf_path, dpi=args.dpi, start=args.start, end=args.end)
