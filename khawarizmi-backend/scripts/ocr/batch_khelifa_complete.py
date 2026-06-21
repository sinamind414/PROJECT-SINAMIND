#!/usr/bin/env python3
"""Batch GPU OCR for all remaining KHELIFA + FINAL BAC volumes."""
import json
import sys
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from services.ocr import get_volume_processor

DATA_DIR = r"C:\Users\zakaria\Documents\projet khawarizmi A\LIVRES SCOLAIRES\ANALES SCIENCES\LIVRES ANNALES SVT BAC\DOSSIER ANNALES KHELIFA"
OCR_PROD = ROOT / "data" / "annales_workspace" / "OCR_PROD"
LOG_FILE = ROOT / "data" / "batch_complete_log.json"

# All volumes to process: [(name, pdf_path), ...]
volumes = []

# KHELIFA 1 (volumes 01-15)
k1_dir = Path(DATA_DIR) / "KHELIFA 1" / "VOLUMES_KHELIFA1"
for v in range(1, 16):
    n = f"{v:02d}"
    name = f"KHELIFA1_VOLUME_{n}"
    pdf = k1_dir / f"{name}.pdf"
    volumes.append((name, pdf))

# FINAL BAC (volumes 1-6)
fb_dir = Path(DATA_DIR) / "FINAL BAC" / "VOLUMES_FINALBAC"
for v in range(1, 7):
    name = f"FINALBAC_VOLUME_{v}"
    pdf = fb_dir / f"{name}.pdf"
    volumes.append((name, pdf))

results = []
for name, pdf in volumes:
    summary_path = OCR_PROD / name / "summary.json"
    if summary_path.exists():
        j = json.loads(summary_path.read_text(encoding="utf-8"))
        print(f"[SKIP] {name} already done ({j['pages_processed']}/{j['total_pages']}p)")
        results.append({"volume": name, "status": "skipped", "pages": j['pages_processed']})
        continue

    if not pdf.exists():
        print(f"[MISS] {name} not found: {pdf}")
        results.append({"volume": name, "status": "missing", "error": str(pdf)})
        continue

    print(f"\n{'='*60}")
    print(f"[START] {name} — {pdf.parent.name}")
    t0 = time.time()
    try:
        proc = get_volume_processor(dpi=96, enable_hocr=True, use_gpu=True)
        summary = proc.process_volume(pdf)
        elapsed = round(time.time() - t0, 1)
        row = summary.to_dict()
        row["elapsed_sec"] = elapsed
        results.append(row)
        msg = f"[DONE]  {name}: {row['pages_processed']}/{row['total_pages']}p, {row['total_characters']}ch, conf={row['avg_confidence']}, {elapsed}s"
        print(msg)
        with open(LOG_FILE, "w", encoding="utf-8") as f:
            json.dump(results, f, ensure_ascii=False, indent=2)
    except Exception as e:
        elapsed = round(time.time() - t0, 1)
        results.append({"volume": name, "status": "failed", "error": str(e), "elapsed_sec": elapsed})
        print(f"[FAIL]  {name}: {e} (after {elapsed}s)")
        with open(LOG_FILE, "w", encoding="utf-8") as f:
            json.dump(results, f, ensure_ascii=False, indent=2)

total_p = sum(r.get("pages_processed", 0) for r in results if "pages_processed" in r)
total_c = sum(r.get("total_characters", 0) for r in results if "total_characters" in r)
total_t = sum(r.get("elapsed_sec", 0) for r in results)
print(f"\n{'='*60}")
print(f"BATCH COMPLETE — {len(volumes)} volumes, {total_p} pages, {total_c} chars, {total_t:.0f}s")
print(f"Log: {LOG_FILE}")
