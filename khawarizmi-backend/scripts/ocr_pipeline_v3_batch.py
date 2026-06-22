#!/usr/bin/env python3
"""
OCR Pipeline v3 — Batch GPU (RTX 3060 + EasyOCR + CUDA)

Detecte tous les volumes PDF manquants ou incomplets dans OCR_PROD
et lance l'OCR avec acceleration GPU.

Usage :
    python scripts/ocr_pipeline_v3_batch.py
    python scripts/ocr_pipeline_v3_batch.py --force          # re-OCR tous
    python scripts/ocr_pipeline_v3_batch.py --volumes KHELIFA1_VOLUME_09 KHELIFA1_VOLUME_10
    python scripts/ocr_pipeline_v3_batch.py --dry-run        # liste seulement
"""

import argparse
import json
import logging
import sys
import time
from pathlib import Path
from datetime import datetime, timezone

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from services.ocr.config import get_config

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    datefmt="%H:%M:%S",
)
logger = logging.getLogger("ocr_v3_batch")

config = get_config()

PDF_BASE = ROOT / "data" / "ANNALES_SVT_BAC_ALGERIE"
OCR_BASE = config.ocr_output_base

# Structure des dossiers PDF
PDF_DIRS = {
    "KHELIFA1": PDF_BASE / "KHELIFA_1" / "VOLUMES_KHELIFA1",
    "KHELIFA2": PDF_BASE / "KHELIFA_2" / "VOLUMES_KHELIFA2",
    "FINALBAC": PDF_BASE / "FINAL_BAC" / "VOLUMES_FINALBAC",
    "MORAFIK": PDF_BASE / "SCIENCES_MORAFIK" / "VOLUMES_MORAFIK",
}


def utc_now_iso() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat()


def list_all_pdf_volumes() -> list:
    """Liste tous les volumes PDF disponibles avec leur chemin."""
    volumes = []
    for prefix, pdf_dir in PDF_DIRS.items():
        if not pdf_dir.exists():
            logger.warning("Dossier PDF introuvable : %s", pdf_dir)
            continue
        for pdf in sorted(pdf_dir.glob("*.pdf")):
            volumes.append(pdf)
    return volumes


def check_ocr_status(volume_name: str) -> str:
    """Retourne le statut OCR : 'ok', 'partial', 'absent'."""
    bundle = OCR_BASE / volume_name
    if not bundle.exists():
        return "absent"

    summary_path = bundle / "summary.json"
    pages_txt_dir = bundle / "pages_txt"

    if summary_path.exists():
        return "ok"

    if pages_txt_dir.exists():
        txt_files = list(pages_txt_dir.glob("page_*.txt"))
        if txt_files:
            return "partial"

    return "absent"


def get_ocr_page_count(volume_name: str) -> int:
    """Retourne le nombre de pages OCR deja traitees."""
    pages_txt_dir = OCR_BASE / volume_name / "pages_txt"
    if not pages_txt_dir.exists():
        return 0
    return len(list(pages_txt_dir.glob("page_*.txt")))


def detect_missing_volumes(force: bool = False, volume_filter: list = None) -> list:
    """Detecte les volumes necessitant un OCR."""
    all_pdfs = list_all_pdf_volumes()
    missing = []

    for pdf_path in all_pdfs:
        volume_name = pdf_path.stem

        if volume_filter and volume_name not in volume_filter:
            continue

        status = check_ocr_status(volume_name)

        if force:
            missing.append((pdf_path, "forced"))
        elif status == "absent":
            missing.append((pdf_path, "absent"))
        elif status == "partial":
            missing.append((pdf_path, "partial"))

    return missing


def run_ocr_volume(pdf_path: Path, use_gpu: bool = True, dpi: int = 200) -> dict:
    """Lance l'OCR sur un volume avec le backend GPU ou Tesseract."""
    from services.ocr.volume_processor import get_volume_processor

    logger.info("Demarrage OCR : %s (GPU=%s, DPI=%d)", pdf_path.name, use_gpu, dpi)

    processor = get_volume_processor(
        dpi=dpi,
        use_gpu=use_gpu,
        enable_hocr=False,
        use_parallel=False,
    )

    start = time.perf_counter()
    summary = processor.process_volume(pdf_path, resume=True)
    elapsed = time.perf_counter() - start

    # Export du texte combine
    try:
        from services.ocr.bundle import BundleManager
        bundle = BundleManager(pdf_path)
        ocr_txt = bundle.export_combined_txt()
        logger.info("Texte combine exporte : %s", ocr_txt.name)
    except Exception as e:
        logger.warning("Export texte combine echoue : %s", e)

    result = summary.to_dict()
    result["elapsed_seconds"] = round(elapsed, 1)
    result["processed_at"] = utc_now_iso()

    return result


def main():
    parser = argparse.ArgumentParser(description="OCR Pipeline v3 — Batch GPU")
    parser.add_argument("--force", action="store_true",
                        help="Re-OCR tous les volumes meme ceux deja faits")
    parser.add_argument("--volumes", nargs="*", default=None,
                        help="Volumes specifiques a traiter (ex: KHELIFA1_VOLUME_09)")
    parser.add_argument("--dry-run", action="store_true",
                        help="Lister les volumes sans lancer l'OCR")
    parser.add_argument("--no-gpu", action="store_true",
                        help="Utiliser Tesseract CPU au lieu de EasyOCR GPU")
    parser.add_argument("--dpi", type=int, default=200,
                        help="DPI de rendu PDF (defaut: 200)")
    parser.add_argument("--output-report", default=None,
                        help="Chemin du rapport JSON de fin")
    args = parser.parse_args()

    use_gpu = not args.no_gpu

    print("=" * 70)
    print("OCR Pipeline v3 — Batch GPU (RTX 3060 + EasyOCR)")
    print("=" * 70)

    # Detection des volumes manquants
    missing = detect_missing_volumes(force=args.force, volume_filter=args.volumes)

    if not missing:
        print("\nTous les volumes ont deja un OCR complet.")
        return

    print(f"\n{len(missing)} volume(s) a traiter :\n")
    print(f"{'Volume':<30} {'Statut':<10} {'PDF (KB)':<12}")
    print("-" * 55)
    for pdf_path, status in missing:
        size_kb = round(pdf_path.stat().st_size / 1024)
        print(f"{pdf_path.stem:<30} {status:<10} {size_kb:<12}")

    if args.dry_run:
        print("\n[Dry-run] Aucun OCR lance.")
        return

    # Verification GPU
    if use_gpu:
        try:
            import torch
            if not torch.cuda.is_available():
                logger.warning("CUDA non disponible -> fallback Tesseract CPU")
                use_gpu = False
            else:
                gpu_name = torch.cuda.get_device_name(0)
                print(f"\nGPU detecte : {gpu_name}")
        except ImportError:
            logger.warning("PyTorch non installe -> fallback Tesseract CPU")
            use_gpu = False

    print(f"\nBackend : {'EasyOCR GPU' if use_gpu else 'Tesseract CPU'}")
    print(f"DPI     : {args.dpi}")
    print()

    # Traitement batch
    results = []
    total_start = time.perf_counter()

    for i, (pdf_path, status) in enumerate(missing, 1):
        print(f"\n[{i}/{len(missing)}] {pdf_path.name} (statut: {status})")
        print("-" * 70)

        try:
            result = run_ocr_volume(pdf_path, use_gpu=use_gpu, dpi=args.dpi)
            results.append(result)
            print(f"  Pages traitees : {result.get('pages_processed', 0)}/{result.get('total_pages', 0)}")
            print(f"  Erreurs        : {result.get('errors', 0)}")
            print(f"  Caracteres     : {result.get('total_characters', 0)}")
            print(f"  Confiance moy. : {result.get('avg_confidence', 0)}")
            print(f"  Temps          : {result.get('elapsed_seconds', 0)}s")
        except Exception as e:
            logger.error("Echec OCR %s : %s", pdf_path.name, e)
            results.append({
                "volume": pdf_path.stem,
                "error": str(e),
                "processed_at": utc_now_iso(),
            })

    total_elapsed = time.perf_counter() - total_start

    # Rapport final
    print("\n" + "=" * 70)
    print("RAPPORT FINAL")
    print("=" * 70)
    print(f"Volumes traites    : {len(results)}")
    print(f"Temps total        : {round(total_elapsed, 1)}s ({round(total_elapsed / 60, 1)} min)")

    ok_count = sum(1 for r in results if "error" not in r)
    err_count = sum(1 for r in results if "error" in r)
    total_pages = sum(r.get("pages_processed", 0) for r in results if "error" not in r)
    total_chars = sum(r.get("total_characters", 0) for r in results if "error" not in r)

    print(f"Succes             : {ok_count}")
    print(f"Echecs             : {err_count}")
    print(f"Total pages OCR    : {total_pages}")
    print(f"Total caracteres   : {total_chars}")

    # Rapport JSON
    report = {
        "generated_at": utc_now_iso(),
        "backend": "easyocr_gpu" if use_gpu else "tesseract_cpu",
        "dpi": args.dpi,
        "total_volumes": len(results),
        "success": ok_count,
        "failures": err_count,
        "total_pages_processed": total_pages,
        "total_characters": total_chars,
        "total_elapsed_seconds": round(total_elapsed, 1),
        "volumes": results,
    }

    report_path = Path(args.output_report or OCR_BASE / "ocr_v3_batch_report.json")
    report_path.parent.mkdir(parents=True, exist_ok=True)
    report_path.write_text(
        json.dumps(report, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )
    print(f"\nRapport sauvegarde : {report_path}")


if __name__ == "__main__":
    main()