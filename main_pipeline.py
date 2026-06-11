import sys
import argparse
import json
import time
import os
from pathlib import Path
from dotenv import load_dotenv

# Configurer l'encodage pour Windows
sys.stdout.reconfigure(encoding='utf-8')

from segmentation import process_pdf_segmentation
from ocr_arabe import ocr_all_text_zones
from structuration import structure_all_pages


def main():
    parser = argparse.ArgumentParser(description="Khawarizmi IA — PDF → JSON structuré")
    parser.add_argument("--pdf", required=True, help="Chemin vers le PDF")
    parser.add_argument("--output", default="./output_pipeline", help="Dossier de sortie")
    parser.add_argument("--dpi", type=int, default=200, help="DPI pour la conversion")
    parser.add_argument("--ocr-backend", default="easyocr",
                        choices=["easyocr"],
                        help="Moteur OCR à utiliser")
    parser.add_argument("--skip-segmentation", action="store_true",
                        help="Passer l'étape 1 si déjà faite")
    parser.add_argument("--skip-ocr", action="store_true",
                        help="Passer l'étape 2 si déjà faite")
    parser.add_argument("--page", type=int, help="Numéro d'une page spécifique à tester")
    args = parser.parse_args()

    load_dotenv(Path(__file__).parent / 'khawarizmi-backend' / '.env')
    load_dotenv()
    gemini_key = os.environ.get("GEMINI_API_KEY")

    if not gemini_key:
        print("Erreur : Clé GEMINI_API_KEY introuvable dans l'environnement.")
        sys.exit(1)

    output_dir = Path(args.output)
    output_dir.mkdir(parents=True, exist_ok=True)

    start_page = args.page if args.page is not None else 0
    end_page = args.page if args.page is not None else None

    # ═══════════════════════════════════════════════════════
    # ÉTAPE 1 : Segmentation visuelle (LOCAL)
    # ═══════════════════════════════════════════════════════
    if not args.skip_segmentation:
        print("=" * 60)
        print("ÉTAPE 1/4 : Segmentation visuelle des pages")
        print("=" * 60)
        t0 = time.time()
        process_pdf_segmentation(args.pdf, str(output_dir), start_page=start_page, end_page=end_page, dpi=args.dpi)
        print(f"⏱ Segmentation terminée en {time.time()-t0:.0f}s\n")
    else:
        print("⏭ Étape 1 ignorée (--skip-segmentation)\n")

    # ═══════════════════════════════════════════════════════
    # ÉTAPE 2 : OCR arabe local
    # ═══════════════════════════════════════════════════════
    ocr_cache = output_dir / "ocr_results.json"

    if not args.skip_ocr:
        print("=" * 60)
        print(f"ÉTAPE 2/4 : OCR arabe ({args.ocr_backend})")
        print("=" * 60)
        t0 = time.time()
        ocr_results = ocr_all_text_zones(
            str(output_dir / "text_zones"),
            backend=args.ocr_backend
        )
        # Sauvegarder les résultats OCR pour ne pas refaire
        with open(ocr_cache, "w", encoding="utf-8") as f:
            json.dump(ocr_results, f, ensure_ascii=False, indent=2)
        print(f"⏱ OCR terminé en {time.time()-t0:.0f}s\n")
    else:
        print("⏭ Étape 2 ignorée (--skip-ocr)")
        with open(ocr_cache, "r", encoding="utf-8") as f:
            ocr_results = json.load(f)
        print(f"  Chargé {len(ocr_results)} résultats OCR depuis le cache\n")

    # Si on teste une seule page, on filtre les résultats OCR
    if args.page is not None:
        prefix = f"page{args.page:04d}_"
        ocr_results = {k: v for k, v in ocr_results.items() if k.startswith(prefix)}

    # ═══════════════════════════════════════════════════════
    # ÉTAPE 3 : Structuration par LLM texte
    # ═══════════════════════════════════════════════════════
    print("=" * 60)
    print("ÉTAPE 3/4 : Structuration JSON via Gemini (texte seul)")
    print("=" * 60)
    t0 = time.time()
    
    output_json_name = f"exercices_page_{args.page}.json" if args.page is not None else "exercices_structures.json"
    
    exercises = structure_all_pages(
        ocr_results=ocr_results,
        figures_dir=str(output_dir / "figures"),
        api_key=gemini_key,
        output_file=str(output_dir / output_json_name)
    )
    print(f"⏱ Structuration terminée en {time.time()-t0:.0f}s\n")

    # ═══════════════════════════════════════════════════════
    # ÉTAPE 4 : Rapport final
    # ═══════════════════════════════════════════════════════
    print("=" * 60)
    print("ÉTAPE 4/4 : Rapport final")
    print("=" * 60)

    total_exercises = sum(
        len(page.get("exercises", []))
        for page in exercises
        if isinstance(page.get("exercises"), list)
    )
    total_figures = len(list((output_dir / "figures").glob("*.png")))
    errors = sum(1 for page in exercises if page.get("status") == "error")

    print(f"""
    ╔══════════════════════════════════════╗
    ║       RÉSUMÉ DE L'EXTRACTION         ║
    ╠══════════════════════════════════════╣
    ║  Pages traitées : {len(exercises):>6}             ║
    ║  Exercices extraits : {total_exercises:>6}         ║
    ║  Figures sauvegardées : {total_figures:>6}         ║
    ║  Erreurs : {errors:>6}                    ║
    ║  Fichier : {output_json_name:<25} ║
    ╚══════════════════════════════════════╝
    """)


if __name__ == "__main__":
    main()
