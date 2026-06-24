#!/usr/bin/env python3
"""
Batch runner : applique ocr_pipeline_production.py à tous les volumes KHELIFA 1 & 2.

DEPRECATED : Utiliser `scripts/ocr/batch_khelifa_complete.py`.
Backend modulaire services/ocr/*. Conserve pour compatibilite.

Usage :
  python scripts/batch_khelifa_ocr.py                        # les 30 volumes
  python scripts/batch_khelifa_ocr.py --serie 1               # KHELIFA 1 only
  python scripts/batch_khelifa_ocr.py --serie 2 --start 6 --end 10
  python scripts/batch_khelifa_ocr.py --resume
"""

from __future__ import annotations

import argparse
import logging
import subprocess
import sys
from pathlib import Path

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    datefmt="%H:%M:%S",
)
log = logging.getLogger("batch_khelifa")

BASE = Path(__file__).resolve().parent.parent
SCRIPT = BASE / "scripts" / "ocr_pipeline_production.py"
OCR_OUT_DIR = BASE / "data" / "ocr_production"
KHELIFA_BASE = BASE / "data" / "ANNALES_SVT_BAC_ALGERIE"

# Map each volume PDF to its output text file for resume detection
VOLUME_PATTERNS = {
    1: (KHELIFA_BASE / "KHELIFA_1" / "VOLUMES_KHELIFA1", "KHELIFA1_VOLUME_{:02d}.pdf", "khelifa1_volume{:02d}"),
    2: (KHELIFA_BASE / "KHELIFA_2" / "VOLUMES_KHELIFA2", "KHELIFA2_VOLUME_{:02d}.pdf", "khelifa2_volume{:02d}"),
}


def build_parser() -> argparse.ArgumentParser:
    ap = argparse.ArgumentParser(description="Batch OCR KHELIFA 1 & 2")
    ap.add_argument("--serie", type=int, choices=[1, 2], default=None, help="Série (1 ou 2, défaut: les deux)")
    ap.add_argument("--start", type=int, default=1, help="Premier volume (défaut: 1)")
    ap.add_argument("--end", type=int, default=15, help="Dernier volume (défaut: 15)")
    ap.add_argument("--dpi", type=int, default=150, help="DPI (défaut: 150)")
    ap.add_argument("--workers", type=int, default=2, help="Workers parallèles par PDF (défaut: 2)")
    ap.add_argument("--resume", action="store_true", help="Ignorer les volumes déjà traités")
    ap.add_argument("--pdf-mode", choices=["auto", "ocr", "text"], default="ocr", help="Mode PDF (défaut: ocr)")
    return ap


def volume_done(out_dir: Path, stem: str) -> bool:
    """Vérifie si un volume a déjà été traité."""
    txt_file = out_dir / f"{stem}.ocr.txt"
    bundle_state = out_dir / f"{stem}.ocr.txt.bundle" / "run.state.json"
    if not txt_file.exists():
        return False
    return bundle_state.exists()


def run_batch(args: argparse.Namespace) -> None:
    OCR_OUT_DIR.mkdir(parents=True, exist_ok=True)
    series_to_run = [args.serie] if args.serie else [1, 2]

    for serie in series_to_run:
        pdf_dir, pdf_pattern, output_stem_pattern = VOLUME_PATTERNS[serie]
        if not pdf_dir.exists():
            log.warning("Dossier introuvable : %s", pdf_dir)
            continue

        for vol in range(args.start, args.end + 1):
            pdf_path = pdf_dir / pdf_pattern.format(vol)
            if not pdf_path.exists():
                log.warning("Fichier introuvable : %s", pdf_path.name)
                continue

            stem = output_stem_pattern.format(vol)

            if args.resume and volume_done(OCR_OUT_DIR, stem):
                log.info("Volume déjà traité (skip) : %s", stem)
                continue

            out_txt = OCR_OUT_DIR / f"{stem}.ocr.txt"
            log.info("=" * 70)
            log.info("OCR : KHELIFA %d Volume %d → %s", serie, vol, out_txt.name)
            log.info("=" * 70)

            cmd = [
                sys.executable,
                str(SCRIPT),
                str(pdf_path),
                "--workers",
                str(args.workers),
                "--dpi",
                str(args.dpi),
                "--out-dir",
                str(OCR_OUT_DIR),
                "--lang",
                "ara+fra",
                "--pdf-mode",
                args.pdf_mode,
                "--suffix",
                ".ocr.txt",
                "--timeout",
                "120",
            ]

            result = subprocess.run(cmd, capture_output=True, text=True)
            if result.returncode != 0:
                log.error("ÉCHEC KHELIFA %d Volume %d : %s", serie, vol, result.stderr[-500:])
                log.error("stdout: %s", result.stdout[-500:])
                continue

            log.info("Terminé : %s", out_txt.name)

    log.info("=== BATCH TERMINÉ ===")

    total = 0
    for f in sorted(OCR_OUT_DIR.glob("*.ocr.txt")):
        size = f.stat().st_size
        total += size
        log.info("  %s (%d chars)", f.name, size)

    log.info("Total : %d volumes, %d chars", len(list(OCR_OUT_DIR.glob("*.ocr.txt"))), total)


def main() -> None:
    parser = build_parser()
    args = parser.parse_args()
    run_batch(args)


if __name__ == "__main__":
    main()
