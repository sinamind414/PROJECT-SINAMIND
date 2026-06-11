# -*- coding: utf-8 -*-
"""
1. extract_pdf.py - Extraction de texte brut par page (sans IA)
Usage:
    python extract_pdf.py --pdf "LIVRES SCOLAIRES/ANALES SCIENCES/ANALES SCIENCE DEATILLE/1.pdf"
"""

import json
import argparse
from pathlib import Path
import fitz  # PyMuPDF

def extract_pdf_text(pdf_path: Path, output_json: Path):
    if not pdf_path.exists():
        print(f"[ERROR] Le fichier PDF est introuvable : {pdf_path}")
        return False

    print(f"[1/5] Ouverture du PDF : {pdf_path.name}")
    doc = fitz.open(pdf_path)
    total_pages = len(doc)
    print(f"[INFO] Nombre total de pages : {total_pages}")

    extracted_pages = []
    empty_pages = 0

    for page_idx in range(total_pages):
        page = doc.load_page(page_idx)
        text = page.get_text().strip()
        
        extracted_pages.append({
            "page": page_idx + 1,
            "text": text
        })
        
        if not text:
            empty_pages += 1

    # Alerte si le PDF est scanné sans OCR
    if empty_pages == total_pages:
        print("[WARNING] Attention ! Toutes les pages de ce PDF sont vides.")
        print("          Ce PDF est probablement un SCAN sans couche de texte.")
        print("          Tu dois d'abord l'OCRiser (ex: via Adobe Acrobat ou un outil en ligne) pour extraire son texte.")
    elif empty_pages > 0:
        print(f"[INFO] {empty_pages} page(s) vide(s) ou contenant uniquement des images détectée(s).")

    with open(output_json, "w", encoding="utf-8") as f:
        json.dump(extracted_pages, f, ensure_ascii=False, indent=2)

    print(f"[SUCCESS] Texte extrait sauvegardé dans : {output_json.name} ({len(extracted_pages)} pages écrites)")
    return True

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Étape 1 : Extraction de texte brut depuis un PDF")
    parser.add_argument("--pdf", required=True, help="Chemin vers le PDF d'entrée")
    parser.add_argument("--output", default="extracted_pages.json", help="Fichier JSON de sortie")
    args = parser.parse_args()

    extract_pdf_text(Path(args.pdf), Path(args.output))
