import sys
import argparse
import json
import re
import time
import os
from pathlib import Path
from dotenv import load_dotenv

# Configurer l'encodage pour Windows
sys.stdout.reconfigure(encoding='utf-8')

from segmentation import process_pdf_segmentation
from ocr_arabe import ocr_all_text_zones
from structuration import structure_all_pages, structure_single_page, merge_cross_page_exercises


def main():
    parser = argparse.ArgumentParser(description="Khawarizmi IA — PDF → JSON structuré")
    parser.add_argument("--pdf", required=True, help="Chemin vers le PDF")
    parser.add_argument("--output", default="./output_pipeline", help="Dossier de sortie")
    parser.add_argument("--dpi", type=int, default=200, help="DPI pour la conversion")
    parser.add_argument("--ocr-backend", default="easyocr", choices=["easyocr"])
    parser.add_argument("--skip-segmentation", action="store_true")
    parser.add_argument("--skip-ocr", action="store_true")
    parser.add_argument("--continuity", action="store_true",
                        help="Activer la détection et fusion des exercices multi-pages")
    parser.add_argument("--page", type=int)
    args = parser.parse_args()

    # Chargement .env — ordre correct
    load_dotenv()
    load_dotenv(Path(__file__).parent / 'khawarizmi-backend' / '.env', override=False)
    
    gemini_key = os.environ.get("GEMINI_API_KEY")
    if not gemini_key:
        print("[ERREUR] GEMINI_API_KEY introuvable dans l'environnement.")
        sys.exit(1)

    # Vérifier que le PDF existe
    pdf_path = Path(args.pdf)
    if not pdf_path.exists():
        print(f"[ERREUR] PDF introuvable : {args.pdf}")
        sys.exit(1)

    output_dir = Path(args.output)
    output_dir.mkdir(parents=True, exist_ok=True)

    start_page = args.page if args.page is not None else 0
    end_page   = args.page if args.page is not None else None

    print(f"""
    {'='*45}
       KHAWARIZMI IA - Pipeline PDF
    {'='*45}
      PDF    : {pdf_path.name:<28}
      Sortie : {str(output_dir):<28}
      Page   : {str(args.page or 'toutes'):<28}
    {'='*45}
    """)

    # ── Étape 1 : Segmentation ─────────────────────────────
    if not args.skip_segmentation:
        print("=" * 60)
        print("ETAPE 1/4 : Segmentation visuelle")
        print("=" * 60)
        t0 = time.time()
        process_pdf_segmentation(
            args.pdf, str(output_dir),
            start_page=start_page, end_page=end_page, dpi=args.dpi
        )
        
        # Vérification
        zones_dir = output_dir / "text_zones"
        if not zones_dir.exists() or not any(zones_dir.iterdir()):
            print("[ERREUR] Segmentation n'a produit aucune zone de texte")
            sys.exit(1)
        print(f"[OK] Segmentation terminee en {time.time()-t0:.0f}s\n")
    else:
        print("[SKIP] Etape 1 ignoree\n")

    # ── Étape 2 : OCR ──────────────────────────────────────
    ocr_cache = output_dir / "ocr_results.json"

    if not args.skip_ocr:
        print("=" * 60)
        print(f"ETAPE 2/4 : OCR arabe ({args.ocr_backend})")
        print("=" * 60)
        t0 = time.time()
        ocr_results = ocr_all_text_zones(
            str(output_dir / "text_zones"),
            backend=args.ocr_backend
        )
        
        if not ocr_results:
            print("[ERREUR] OCR n'a produit aucun resultat")
            sys.exit(1)
            
        with open(ocr_cache, "w", encoding="utf-8") as f:
            json.dump(ocr_results, f, ensure_ascii=False, indent=2)
        print(f"[OK] OCR termine : {len(ocr_results)} zones - {time.time()-t0:.0f}s\n")
    else:
        print("[SKIP] Etape 2 ignoree")
        if not ocr_cache.exists():
            print(f"[ERREUR] Cache OCR introuvable : {ocr_cache}")
            sys.exit(1)
        with open(ocr_cache, "r", encoding="utf-8") as f:
            ocr_results = json.load(f)
        print(f"  Charge {len(ocr_results)} resultats depuis le cache\n")

    # Filtrage page unique
    if args.page is not None:
        prefix = f"page{args.page:04d}_"
        ocr_results = {k: v for k, v in ocr_results.items() if k.startswith(prefix)}
        print(f"  Filtre page {args.page} : {len(ocr_results)} zones conservees\n")

    # ── Étape 3 : Structuration Gemini ─────────────────────
    print("=" * 60)
    print("ETAPE 3/4 : Structuration JSON via Gemini")
    print("=" * 60)
    t0 = time.time()
    
    output_json_name = (
        f"exercices_page_{args.page}.json"
        if args.page is not None
        else "exercices_structures.json"
    )
    
    if args.continuity:
        print("  [CONTINUITY] Mode continuite active : traitement sequentiel avec contexte")
        exercises = process_pages_with_continuity(
            ocr_results=ocr_results,
            figures_dir=str(output_dir / "figures"),
            api_key=gemini_key,
            output_file=str(output_dir / output_json_name)
        )
    else:
        exercises = structure_all_pages(
            ocr_results=ocr_results,
            figures_dir=str(output_dir / "figures"),
            api_key=gemini_key,
            output_file=str(output_dir / output_json_name)
        )
    print(f"[OK] Structuration terminee en {time.time()-t0:.0f}s\n")

    # ── Étape 4 : Rapport ──────────────────────────────────
    if args.continuity and isinstance(exercises, dict):
        # Format du pipeline continuité : {"total_exercises": N, "pages_processed": M, "exercises": [...]}
        total_exercises = exercises.get("total_exercises", 0)
        pages_count = exercises.get("pages_processed", 0)
        all_page_data = exercises.get("exercises", [])
        errors = sum(1 for p in all_page_data if isinstance(p, dict) and p.get("status") == "error")
    else:
        # Format original : liste de pages
        pages_count = len(exercises)
        total_exercises = sum(
            len(page.get("exercises", []))
            for page in exercises
            if isinstance(page.get("exercises"), list)
        )
        errors = sum(1 for page in exercises if page.get("status") == "error")
    
    fig_pattern = (
        f"page{args.page:04d}_*.png"
        if args.page is not None
        else "*.png"
    )
    total_figures = len(list((output_dir / "figures").glob(fig_pattern)))
    status_str = "[OK]" if errors == 0 else "[WARN]"

    print(f"""
    {'='*45}
    {status_str}  RESUME DE L'EXTRACTION
    {'='*45}
      Pages traitees    : {pages_count:>6}
      Exercices extraits: {total_exercises:>6}
      Figures extraites : {total_figures:>6}
      Erreurs Gemini    : {errors:>6}
      Fichier JSON      : {output_json_name:<20}
    {'='*45}
    """)
    
    if errors > 0:
        print(f"[WARN] {errors} pages ont echoue. Relancer avec --skip-ocr pour les pages concernees.")
    
    return 0


def process_pages_with_continuity(
    ocr_results: dict,
    figures_dir: str,
    api_key: str,
    output_file: str
):
    """
    Traite les pages dans l'ordre en passant le contexte de fin
    de page à la page suivante, puis fusionne les exercices multi-pages.
    """
    # Trier les pages dans l'ordre
    def extract_page_num(item):
        m = re.search(r'page(\d+)', item[0])
        return int(m.group(1)) if m else 0

    sorted_pages = sorted(ocr_results.items(), key=extract_page_num)

    all_pages_data = []
    prev_page_ending = None

    for page_key, ocr_text in sorted_pages:
        m = re.search(r'page(\d+)', page_key)
        page_num = int(m.group(1)) if m else 0

        print(f"  [Page {page_num}] Structuration...", end=" ")

        try:
            page_data = structure_single_page(
                ocr_text=ocr_text,
                page_number=page_num,
                figures_dir=figures_dir,
                api_key=api_key,
                prev_page_ending=prev_page_ending
            )

            all_pages_data.append(page_data)

            # Préparer le contexte pour la page suivante
            exercises = page_data.get("exercises", [])
            if exercises and not exercises[-1].get("is_complete", True):
                prev_page_ending = exercises[-1].get("texte", "")[-300:]
                print(f"incomplet -> contexte transmis")
            else:
                prev_page_ending = None
                print("[OK]")

        except Exception as e:
            print(f"[ERREUR] {e}")
            all_pages_data.append({
                "page_number": page_num,
                "exercises": [],
                "status": "error",
                "error": str(e)
            })
            prev_page_ending = None

    # Fusionner les exercices multi-pages
    print("\n[MERGE] Fusion des exercices multi-pages...")
    all_exercises = merge_cross_page_exercises(all_pages_data)

    # Sauvegarder
    result = {
        "total_exercises": len(all_exercises),
        "pages_processed": len(all_pages_data),
        "exercises": all_exercises
    }

    with open(output_file, "w", encoding="utf-8") as f:
        json.dump(result, f, ensure_ascii=False, indent=2)

    print(f"[DONE] {len(all_exercises)} exercices sauvegardes dans {output_file}")
    return all_pages_data


if __name__ == "__main__":
    sys.exit(main())