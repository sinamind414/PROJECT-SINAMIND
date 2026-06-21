#!/usr/bin/env python3
"""
OCR PIPELINE PRODUCTION - Thin CLI for the modular backend
Version: 3.1 - 2026-06-21 - GPU + Batch support
"""

import argparse
import json
import logging
import os
import sys
import time
from pathlib import Path
from typing import List, Optional

# fix Windows cp1252 console for emojis
if sys.platform == "win32":
    sys.stdout.reconfigure(encoding="utf-8")
    os.environ["PYTHONIOENCODING"] = "utf-8"

SCRIPT_DIR = Path(__file__).resolve().parent
BACKEND_DIR = SCRIPT_DIR / "khawarizmi-backend"
if (BACKEND_DIR / "services" / "ocr").exists():
    if str(BACKEND_DIR) not in sys.path:
        sys.path.insert(0, str(BACKEND_DIR))
elif str(SCRIPT_DIR) not in sys.path:
    sys.path.insert(0, str(SCRIPT_DIR))

from services.ocr import get_volume_processor

LOG = logging.getLogger("ocr_production")


def setup_logging(verbose: bool = False) -> None:
    LOG.setLevel(logging.DEBUG if verbose else logging.INFO)
    LOG.handlers.clear()
    LOG.propagate = False
    fmt = logging.Formatter("%(asctime)s [%(levelname)s] %(message)s", datefmt="%H:%M:%S")
    h = logging.StreamHandler(sys.stdout)
    h.setLevel(logging.DEBUG if verbose else logging.INFO)
    h.setFormatter(fmt)
    LOG.addHandler(h)


def discover_pdfs(directory: Path) -> List[Path]:
    pdfs = []
    for pdf in sorted(directory.rglob("*.pdf")):
        pdfs.append(pdf)
    return pdfs


def process_single(args) -> None:
    pdf_path = Path(args.pdf).resolve()
    if not pdf_path.exists():
        print("ERROR: PDF not found:", pdf_path, file=sys.stderr)
        sys.exit(1)

    print("Starting OCR for:", pdf_path.name)
    print("  DPI=%d | GPU=%s | Parallel=%s" % (args.dpi, args.use_gpu, args.parallel))

    processor = get_volume_processor(
        dpi=args.dpi,
        psm=args.psm,
        oem=args.oem,
        retries=args.retries,
        use_parallel=args.parallel,
        max_workers=args.max_workers,
        enable_hocr=not args.no_hocr,
        use_gpu=args.use_gpu,
    )

    try:
        summary = processor.process_volume(pdf_path, use_parallel=args.parallel)
        print("\n" + "=" * 60)
        print(json.dumps(summary.to_dict(), indent=2, ensure_ascii=False))
        print("=" * 60)
        print("OCR completed. Bundle:", summary.bundle_dir)
    except Exception as e:
        print("OCR failed:", e, file=sys.stderr)
        sys.exit(1)


def process_batch(args) -> None:
    directory = Path(args.pdf).resolve()
    if not directory.is_dir():
        print("ERROR: Not a directory:", directory, file=sys.stderr)
        sys.exit(1)

    pdfs = discover_pdfs(directory)
    if args.max_volumes:
        pdfs = pdfs[: args.max_volumes]

    if not pdfs:
        print("No PDFs found in directory.")
        sys.exit(1)

    print("Batch OCR - %d PDFs found in %s" % (len(pdfs), directory))
    print("  DPI=%d | GPU=%s" % (args.dpi, args.use_gpu))

    results = []
    total_start = time.perf_counter()

    for i, pdf_path in enumerate(pdfs, 1):
        print("\n--- [%d/%d] %s ---" % (i, len(pdfs), pdf_path.name))
        try:
            processor = get_volume_processor(
                dpi=args.dpi,
                psm=args.psm,
                oem=args.oem,
                retries=args.retries,
                use_parallel=False,
                max_workers=1,
                enable_hocr=not args.no_hocr,
                use_gpu=args.use_gpu,
            )
            vol_start = time.perf_counter()
            summary = processor.process_volume(pdf_path)
            duration = time.perf_counter() - vol_start
            results.append(summary)
            print("  Done - %d pages, %d chars, conf=%.1f, %.1fs" % (
                summary.total_pages, summary.total_characters, summary.avg_confidence, duration))
        except Exception as e:
            print("  Failed:", e)
            results.append(None)

    total_dur = time.perf_counter() - total_start
    total_chars = sum(r.total_characters for r in results if r)
    total_pages = sum(r.pages_processed for r in results if r)
    ok = sum(1 for r in results if r and r.errors == 0)
    err = sum(1 for r in results if r and r.errors > 0) + sum(1 for r in results if r is None)

    print("\n" + "=" * 60)
    print("BATCH SUMMARY")
    print("=" * 60)
    print("  Total PDFs:  %d" % len(results))
    print("  Successful:  %d" % ok)
    print("  With errors: %d" % err)
    print("  Pages done:  %d" % total_pages)
    print("  Chars:       %d" % total_chars)
    print("  Duration:    %.1fs (%.1f min)" % (total_dur, total_dur / 60))


def build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(description="Production OCR Pipeline (GPU + Batch)")
    p.add_argument("pdf", help="Path to PDF or directory for batch mode")
    p.add_argument("--dpi", type=int, default=200)
    p.add_argument("--psm", type=int, default=3)
    p.add_argument("--oem", type=int, default=1)
    p.add_argument("--retries", type=int, default=2)
    p.add_argument("--parallel", action="store_true", help="Enable multiprocessing")
    p.add_argument("--max-workers", type=int, default=2)
    p.add_argument("--no-hocr", action="store_true", help="Disable hOCR output")
    p.add_argument("--use-gpu", action="store_true", help="Use EasyOCR GPU backend")
    p.add_argument("--batch", action="store_true", help="Process directory of PDFs")
    p.add_argument("--max-volumes", type=int, default=None, help="Max PDFs in batch mode")
    p.add_argument("--verbose", action="store_true", help="Verbose logging")
    return p


def main():
    parser = build_parser()
    args = parser.parse_args()
    setup_logging(args.verbose)

    if args.batch:
        process_batch(args)
    else:
        process_single(args)


if __name__ == "__main__":
    main()
