#!/usr/bin/env python3
"""
OCR PIPELINE PRODUCTION — Thin CLI (Backend modulaire)
"""

import argparse
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
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
    parser.add_argument("--gpu", action="store_true", help="Use GPU-accelerated OCR (EasyOCR + CUDA)")
    args = parser.parse_args()

    pdf_path = Path(args.pdf).resolve()
    if not pdf_path.exists():
        print(f"ERROR: PDF not found: {pdf_path}")
        sys.exit(1)

    processor = get_volume_processor(
        dpi=args.dpi,
        use_parallel=args.parallel,
        max_workers=args.max_workers,
        enable_hocr=not args.no_hocr,
        use_gpu=args.gpu
    )

    summary = processor.process_volume(pdf_path, use_parallel=args.parallel)
    print(json.dumps(summary.to_dict(), indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()
