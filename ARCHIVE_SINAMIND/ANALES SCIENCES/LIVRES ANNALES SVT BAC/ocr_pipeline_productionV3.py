#!/usr/bin/env python3
"""
OCR PIPELINE PRODUCTION — Thin CLI for the modular backend
Version: 3.0 — 2026-06-20

This is the ONLY entry point you should use to run OCR.

It delegates all logic to services/ocr/VolumeProcessor.

Usage:
    python scripts/ocr/ocr_pipeline_production.py \
        data/ANNALES_SVT_BAC_ALGERIE/KHELIFA_1/VOLUMES_KHELIFA1/KHELIFA1_VOLUME_05.pdf \
        --dpi 140 --parallel --max-workers 3
"""

import argparse
import json
import sys
from pathlib import Path

# Make sure we can import from project root
ROOT = Path(__file__).resolve().parents[3]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from services.ocr import get_volume_processor


def main():
    parser = argparse.ArgumentParser(
        description="Production OCR Pipeline (Arabic + French) — Modular Backend"
    )
    parser.add_argument("pdf", help="Path to PDF volume")
    parser.add_argument("--dpi", type=int, default=140)
    parser.add_argument("--psm", type=int, default=3)
    parser.add_argument("--oem", type=int, default=1)
    parser.add_argument("--retries", type=int, default=2)
    parser.add_argument("--parallel", action="store_true", help="Enable multiprocessing")
    parser.add_argument("--max-workers", type=int, default=2)
    parser.add_argument("--no-hocr", action="store_true", help="Disable hOCR output")

    args = parser.parse_args()

    pdf_path = Path(args.pdf).resolve()
    if not pdf_path.exists():
        print(f"❌ ERROR: PDF not found: {pdf_path}", file=sys.stderr)
        sys.exit(1)

    print(f"🚀 Starting OCR Production for: {pdf_path.name}")
    print(f"   DPI={args.dpi} | Parallel={args.parallel} | hOCR={not args.no_hocr}")

    processor = get_volume_processor(
        dpi=args.dpi,
        psm=args.psm,
        oem=args.oem,
        retries=args.retries,
        use_parallel=args.parallel,
        max_workers=args.max_workers,
        enable_hocr=not args.no_hocr,
    )

    try:
        summary = processor.process_volume(pdf_path, use_parallel=args.parallel)
        print("\n" + "=" * 60)
        print(json.dumps(summary.to_dict(), indent=2, ensure_ascii=False))
        print("=" * 60)
        print(f"\n✅ OCR completed successfully.")
        print(f"   Bundle: {summary.bundle_dir}")
    except Exception as e:
        print(f"❌ OCR failed: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
