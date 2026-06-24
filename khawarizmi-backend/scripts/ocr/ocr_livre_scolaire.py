#!/usr/bin/env python3
"""
OCR LIVRE SCOLAIRE SVT 3AS — GPU RTX 3060 / EasyOCR
"""

import json
import logging
import sys
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))

from services.ocr import get_volume_processor
from services.ocr.bundle import BundleManager

PDF_PATH = r"C:\Users\zakaria\Documents\projet khawarizmi A\LIVRES SCOLAIRES\LIVRE SCOLAIRE SCIENCE BAC\livre_scolaire_3as_sciences_se.pdf"
OUT_DIR = ROOT / "data" / "ocr_livre_scolaire"


def main():
    pdf = Path(PDF_PATH)
    if not pdf.exists():
        print(f"ERROR: PDF not found: {pdf}")
        sys.exit(1)

    print("=" * 60)
    print("OCR LIVRE SCOLAIRE SVT 3AS — GPU RTX 3060")
    print(f"PDF: {pdf.name} ({pdf.stat().st_size // 1024 // 1024} MB)")
    print(f"Output: {OUT_DIR}")
    logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
    print("=" * 60)

    import fitz

    doc = fitz.open(str(pdf))
    total_pages = doc.page_count
    doc.close()
    print(f"Total pages: {total_pages}")
    t0 = time.time()
    last_log = [t0]

    def progress_cb(info):
        now = time.time()
        if now - last_log[0] >= 30:
            elapsed = now - t0
            rate = info["page"] / elapsed * 60
            remaining = (total_pages - info["page"]) / rate * 60 if rate > 0 else 0
            print(
                f"  [{info['progress']:.0f}%] page {info['page']}/{total_pages} — {rate:.1f} p/min — ~{remaining:.0f}s remaining"
            )
            last_log[0] = now

    processor = get_volume_processor(
        dpi=140,
        enable_hocr=True,
        use_gpu=True,
    )
    summary = processor.process_volume(pdf, resume=True, progress_callback=progress_cb)
    elapsed = round(time.time() - t0, 1)

    print(f"\n{'=' * 60}")
    print(f"OCR COMPLETE — {elapsed}s")
    print(json.dumps(summary.to_dict(), ensure_ascii=False, indent=2))
    print(f"{'=' * 60}")

    bundle = BundleManager(pdf)
    ocr_txt = bundle.export_combined_txt(suffix=".ocr_livre_scolaire.txt")
    print(f"Combined text → {ocr_txt}")

    summary_out = OUT_DIR / "summary.json"
    summary_out.parent.mkdir(parents=True, exist_ok=True)
    summary_out.write_text(
        json.dumps(summary.to_dict(), ensure_ascii=False, indent=2),
        encoding="utf-8",
    )
    print(f"Summary → {summary_out}")


if __name__ == "__main__":
    main()
