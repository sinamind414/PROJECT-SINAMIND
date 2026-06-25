#!/usr/bin/env python3
"""Batch GPU OCR pour tous les volumes KHELIFA2 restants."""
import json
import sys
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from services.ocr import get_volume_processor
from services.ocr.bundle import BundleManager

BASE = ROOT / "data" / "ANNALES_SVT_BAC_ALGERIE" / "KHELIFA_2" / "VOLUMES_KHELIFA2"
LOG_FILE = ROOT / "data" / "ocr_batch_log.json"
OCR_PROD = ROOT / "data" / "annales_workspace" / "OCR_PROD"

results = []
for v in range(1, 16):
    num = f"{v:02d}"
    name = f"KHELIFA2_VOLUME_{num}"
    summary_path = OCR_PROD / name / "summary.json"
    if summary_path.exists():
        print(f"[SKIP] {name} already done")
        continue

    pdf = BASE / f"{name}.pdf"
    if not pdf.exists():
        print(f"[MISS] {pdf}")
        continue

    print(f"\n{'=' * 60}")
    print(f"[START] {name}")
    t0 = time.time()
    try:
        proc = get_volume_processor(dpi=140, enable_hocr=True, use_gpu=True)
        summary = proc.process_volume(pdf)
        bundle = BundleManager(pdf)
        ocr_txt = bundle.export_combined_txt()
        elapsed = round(time.time() - t0, 1)
        row = summary.to_dict()
        row["elapsed_sec"] = elapsed
        results.append(row)
        print(f"[DONE] {name}: {row['pages_processed']}/{row['total_pages']}p, {row['total_characters']}ch, conf={row['avg_confidence']}, {elapsed}s")
        print(f"       Text bundle → {ocr_txt.name}")
    except Exception as e:
        elapsed = round(time.time() - t0, 1)
        results.append({"volume": name, "error": str(e), "elapsed_sec": elapsed})
        print(f"[FAIL] {name}: {e}")

LOG_FILE.parent.mkdir(parents=True, exist_ok=True)
LOG_FILE.write_text(json.dumps(results, ensure_ascii=False, indent=2), encoding="utf-8")
print(f"\n{'=' * 60}")
print(f"BATCH COMPLETE — {len(results)} volumes processed")
print(f"Log: {LOG_FILE}")
