#!/usr/bin/env python3
"""Batch final — FINAL BAC (V4-V6) + KHELIFA1 (V07-V15) GPU DPI 36."""
import json
import sys
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))
from services.ocr import get_volume_processor

K1 = r"C:\Users\zakaria\Documents\projet khawarizmi A\LIVRES SCOLAIRES\ANALES SCIENCES\LIVRES ANNALES SVT BAC\DOSSIER ANNALES KHELIFA\KHELIFA 1\VOLUMES_KHELIFA1"
FB = r"C:\Users\zakaria\Documents\projet khawarizmi A\LIVRES SCOLAIRES\ANALES SCIENCES\LIVRES ANNALES SVT BAC\DOSSIER ANNALES KHELIFA\FINAL BAC\VOLUMES_FINALBAC"
OUT = ROOT / "data" / "annales_workspace" / "OCR_PROD"
LOG = ROOT / "data" / "batch_final_log.json"


def process(name, pdf, dpi):
    sp = OUT / name / "summary.json"
    if sp.exists():
        j = json.loads(sp.read_text(encoding="utf-8"))
        return {"volume": name, "status": "skipped", "pages": j["pages_processed"]}
    t0 = time.time()
    try:
        p = get_volume_processor(dpi=dpi, enable_hocr=True, use_gpu=True)
        s = p.process_volume(pdf)
        r = s.to_dict()
        r["elapsed_sec"] = round(time.time() - t0, 1)
        return r
    except Exception as e:
        return {"volume": name, "status": "error", "error": str(e), "elapsed_sec": round(time.time() - t0, 1)}


results = []
# FINALBAC V4-V6
for v in range(4, 7):
    n = f"FINALBAC_VOLUME_{v}"
    pdf = Path(FB) / f"{n}.pdf"
    print(f"[FB] {n}...")
    r = process(n, pdf, 140)
    results.append(r)
    print(f"  {'OK' if 'total_pages' in r else 'FAIL'}: {r}")
    json.dump(results, open(LOG, "w", encoding="utf-8"), ensure_ascii=False, indent=2)

# KHELIFA1 V07-V15
for v in range(7, 16):
    n = f"KHELIFA1_VOLUME_{v:02d}"
    pdf = Path(K1) / f"{n}.pdf"
    print(f"[K1] {n} (DPI 36)...")
    r = process(n, pdf, 36)
    results.append(r)
    print(f"  {'OK' if 'total_pages' in r else 'FAIL'}: {r}")
    json.dump(results, open(LOG, "w", encoding="utf-8"), ensure_ascii=False, indent=2)

tp = sum(r.get("pages_processed", 0) for r in results if "pages_processed" in r)
tc = sum(r.get("total_characters", 0) for r in results if "total_characters" in r)
print(f"\nDONE: {len(results)} vols, {tp}p, {tc}ch")
