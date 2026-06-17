# -*- coding: utf-8 -*-
"""
extract_khelifa.py - Ingestion automatique du livre Ahmed Amin Khelifa dans annales_sciences_3as.json
Usage:
    python extract_khelifa.py --api-key YOUR_API_KEY --page 15 (Test sur une seule page)
    python extract_khelifa.py --api-key YOUR_API_KEY (Lancement de l'extraction complète)
"""

import os
import io
import sys
import json
import time
import shutil
import sys
import argparse
from pathlib import Path
from PIL import Image
from dotenv import load_dotenv

sys.stdout.reconfigure(encoding='utf-8')

# Charger les variables d'environnement
load_dotenv(Path(__file__).parent / 'khawarizmi-backend' / '.env')
load_dotenv()

# Chemins des fichiers
DEFAULT_PDF_PATH = Path("LIVRES SCOLAIRES/ANALES SCIENCES/ANALES SCIENCE DEATILLE/Ahmed amin khelifa version 2 parte 1.pdf")
DEFAULT_DB_PATH = Path("annales_sciences_3as.json")
CHECKPOINT_PATH = Path("khelifa_checkpoint.json")

PROMPT = """
Analyse cette page d'un livre de sciences naturelles (SVT) de niveau terminale (Baccalauréat Algérien).
Identifie si la page contient des questions, des exercices, ou des sujets d'évaluation avec leurs réponses ou corrections.
Si oui, extrais les exercices et leurs questions correspondantes.

Pour chaque exercice identifié, génère un objet JSON suivant la structure :
{
  "exercice_id": "Un identifiant unique pour l'exercice, ex: khelifa_p[page]_ex[index]",
  "thematique": "Thème ou titre de l'exercice en arabe (ex: المناعة, تركيب البروتين, الاتصال العصبي, النشاط الإنزيمي)",
  "chapitre_id": "Identifiant du chapitre parmi: ch1_proteines, ch2_structure, ch3_enzymes, ch4_immunite, ch5_nerveux, ch6_photosynthese, ch7_respiration",
  "points": 5,
  "questions": [
    {
      "question_id": "q1",
      "texte": "Le texte de la question en Arabe, tel qu'écrit dans le livre",
      "reponse_attendue": "La réponse ou la correction correspondante de la question en Arabe",
      "concept_cle": "Le concept clé scientifique en Arabe (ex: فيروس السيدا, الاستنساخ, الموقع الفعال, كمون العمل)",
      "pattern_recherche": "3 à 5 mots clés essentiels en arabe séparés par des virgules (ex: أسيتيل كولين, مشبك, قنوات فولطية)"
    }
  ],
  "documents_annexes": [
    {
      "type": "tableau",
      "description": "Brève description en Arabe du tableau ou dessin",
      "box_2d": [ymin, xmin, ymax, xmax]
    }
  ]
}

Les valeurs dans `box_2d` doivent être des entiers entre 0 et 1000 représentant les coordonnées de la boîte englobante de l'image ou du tableau (0 en haut à gauche, 1000 en bas à droite). Si aucun tableau ou dessin n'est présent dans l'exercice, retourne une liste vide pour `documents_annexes`. Le type peut être "tableau", "dessin", ou "graphe".

Retourne STRICTEMENT un tableau JSON (liste) contenant les exercices trouvés sur cette page.
Si la page ne contient aucune question/exercice ou correction pertinente, retourne [].
N'inclus aucune balise de code comme ```json ... ```, retourne uniquement le texte JSON brut.
"""

def valider_exercice_schema(ex: dict) -> bool:
    """Valide sommairement le schéma d'un exercice."""
    champs_ex = {"exercice_id", "thematique", "chapitre_id", "questions"}
    champs_q = {"question_id", "texte", "reponse_attendue", "concept_cle", "pattern_recherche"}
    
    if not isinstance(ex, dict) or not champs_ex.issubset(ex.keys()):
        return False
    if not isinstance(ex["questions"], list):
        return False
    for q in ex["questions"]:
        if not isinstance(q, dict) or not champs_q.issubset(q.keys()):
            return False
    return True

def merge_checkpoint_to_db(db_path: Path, checkpoint_data: list):
    """Fusionne les exercices extraits du checkpoint dans le fichier principal."""
    if not checkpoint_data:
        print("[INFO] Aucun exercice dans le checkpoint à fusionner.")
        return

    print(f"[MERGE] Fusion de {len(checkpoint_data)} exercices dans {db_path}...")
    
    # 1. Charger la DB
    if db_path.exists():
        with open(db_path, "r", encoding="utf-8") as f:
            db_data = json.load(f)
    else:
        db_data = []

    # 2. Trouver ou créer le sujet
    sujet_id = "ahmed_amin_khelifa_v2_part1"
    sujet = None
    for s in db_data:
        if s.get("sujet_id") == sujet_id:
            sujet = s
            break

    if not sujet:
        sujet = {
            "sujet_id": sujet_id,
            "annee": 2024,
            "filiere": "Sciences Expérimentales",
            "titre": "Ahmed Amin Khelifa V2 - Partie 1",
            "exercices": []
        }
        db_data.append(sujet)

    # Indexer les exercices existants pour éviter les doublons
    existants = {ex["exercice_id"] for ex in sujet["exercices"]}
    
    ajoutes = 0
    pour_ajout = []
    for ex in checkpoint_data:
        if not valider_exercice_schema(ex):
            print(f"[WARNING] Exercice ignoré (format invalide) : {ex.get('exercice_id')}")
            continue
            
        if ex["exercice_id"] in existants:
            # Remplacer ou ignorer ? On ignore pour l'instant
            print(f"[SKIP] Exercice déjà présent dans la DB : {ex['exercice_id']}")
            continue
            
        pour_ajout.append(ex)
        existants.add(ex["exercice_id"])
        ajoutes += 1

    sujet["exercices"].extend(pour_ajout)

    # 3. Créer un backup de la DB
    backup_path = db_path.with_suffix(f'.backup_{int(time.time())}.json')
    if db_path.exists():
        shutil.copy2(db_path, backup_path)
        print(f"[BACKUP] Sauvegarde créée : {backup_path.name}")

    # 4. Sauvegarder la DB mise à jour
    with open(db_path, "w", encoding="utf-8") as f:
        json.dump(db_data, f, ensure_ascii=False, indent=2)

    print(f"[MERGE SUCCESS] {ajoutes} exercices ont été fusionnés. Total exercices pour Khelifa : {len(sujet['exercices'])}")

def main():
    parser = argparse.ArgumentParser(description="Extracteur SVT - Livre Ahmed Amin Khelifa")
    parser.add_argument("--api-key", help="Clé API Gemini (Google AI Studio)")
    parser.add_argument("--pdf", default=str(DEFAULT_PDF_PATH), help="Chemin vers le PDF")
    parser.add_argument("--db", default=str(DEFAULT_DB_PATH), help="Chemin vers annales_sciences_3as.json")
    parser.add_argument("--page", type=int, help="Page unique à extraire pour tester (1-indexed)")
    parser.add_argument("--start-page", type=int, default=1, help="Page de début pour l'extraction complète")
    parser.add_argument("--end-page", type=int, help="Page de fin pour l'extraction complète")
    parser.add_argument("--merge-only", action="store_true", help="Fusionner uniquement le checkpoint existant sans appeler l'API")
    args = parser.parse_args()

    pdf_path = Path(args.pdf)
    db_path = Path(args.db)

    # 1. Mode fusion uniquement
    if args.merge_only:
        if not CHECKPOINT_PATH.exists():
            print("[ERROR] Aucun checkpoint trouvé pour la fusion.")
            sys.exit(1)
        with open(CHECKPOINT_PATH, "r", encoding="utf-8") as f:
            cp = json.load(f)
        merge_checkpoint_to_db(db_path, cp.get("data", []))
        sys.exit(0)

    # Charger la clé API
    api_key = args.api_key or os.environ.get("GEMINI_API_KEY") or os.environ.get("GOOGLE_API_KEY")
    if not api_key:
        print("[ERROR] Clé API Gemini introuvable.")
        print("Spécifie-la avec --api-key ou renseigne GEMINI_API_KEY dans ton fichier .env")
        sys.exit(1)

    # Importer les dépendances après validation de la clé
    try:
        import fitz
        import google.generativeai as genai
    except ImportError as e:
        print(f"[ERROR] Dépendances manquantes : {e}")
        print("Exécute: pip install pymupdf google-generativeai pillow python-dotenv")
        sys.exit(1)

    # Configuration Gemini
    genai.configure(api_key=api_key)
    # Utilisation du modèle recommandé pour la vision & l'arabe
    model = genai.GenerativeModel('gemini-2.5-flash-lite')

    # Ouvrir le PDF
    if not pdf_path.exists():
        print(f"[ERROR] PDF introuvable : {pdf_path}")
        sys.exit(1)

    print(f"[INFO] Ouverture du PDF : {pdf_path.name}")
    doc = fitz.open(pdf_path)
    total_pages = len(doc)
    print(f"[INFO] Nombre de pages : {total_pages}")

    # 2. Mode Test (Page unique)
    if args.page:
        page_idx = args.page - 1
        if page_idx < 0 or page_idx >= total_pages:
            print(f"[ERROR] Page invalide. Doit être entre 1 et {total_pages}")
            sys.exit(1)
            
        print(f"[TEST] Traitement de la page test {args.page}...")
        page = doc.load_page(page_idx)
        pix = page.get_pixmap(dpi=75) # DPI réduit pour économiser les tokens
        img_bytes = pix.tobytes("jpeg")
        img = Image.open(io.BytesIO(img_bytes))
        
        try:
            start_time = time.time()
            response = model.generate_content([PROMPT, img])
            elapsed = time.time() - start_time
            text_res = response.text.strip()
            
            # Nettoyer d'éventuelles balises markdown générées
            if text_res.startswith("```json"):
                text_res = text_res[7:-3].strip()
            elif text_res.startswith("```"):
                text_res = text_res[3:-3].strip()
                
            page_data = json.loads(text_res)
            
            images_dir = Path("images_extraites")
            images_dir.mkdir(exist_ok=True)
            img_width, img_height = img.size

            if isinstance(page_data, list):
                for ex in page_data:
                    if "documents_annexes" in ex:
                        for idx, doc_annexe in enumerate(ex["documents_annexes"]):
                            if "box_2d" in doc_annexe and isinstance(doc_annexe["box_2d"], list) and len(doc_annexe["box_2d"]) == 4:
                                ymin, xmin, ymax, xmax = doc_annexe["box_2d"]
                                left = (xmin / 1000) * img_width
                                top = (ymin / 1000) * img_height
                                right = (xmax / 1000) * img_width
                                bottom = (ymax / 1000) * img_height
                                
                                try:
                                    cropped_img = img.crop((left, top, right, bottom))
                                    img_filename = f"{ex.get('exercice_id', 'test')}_doc{idx+1}.jpg"
                                    img_filepath = images_dir / img_filename
                                    cropped_img.save(img_filepath)
                                    doc_annexe["image_path"] = str(img_filepath)
                                    del doc_annexe["box_2d"]
                                except Exception as e:
                                    print(f"  -> Erreur recadrage image test : {e}")
            print(f"[TEST SUCCESS] Temps de réponse : {elapsed:.2f}s")
            print(json.dumps(page_data, ensure_ascii=False, indent=2))
            
            # Sauvegarder dans un fichier test temporaire
            test_out = Path(f"khelifa_page_{args.page}_test.json")
            with open(test_out, "w", encoding="utf-8") as f:
                json.dump(page_data, f, ensure_ascii=False, indent=2)
            print(f"[TEST] Données enregistrées dans {test_out}")
            
            print("[INFO] Pour fusionner ce test à la DB, relance avec --merge-only après avoir copié les données.")
            
        except Exception as e:
            print(f"[TEST ERROR] Erreur lors du traitement de la page {args.page} : {e}")
            if 'response' in locals() and hasattr(response, 'text'):
                print("Réponse brute de l'API :", response.text)
        return

    # 3. Extraction complète avec Checkpoint
    checkpoint = {"processed_pages": [], "data": []}
    if CHECKPOINT_PATH.exists():
        try:
            with open(CHECKPOINT_PATH, "r", encoding="utf-8") as f:
                checkpoint = json.load(f)
            print(f"[CHECKPOINT] Reprise détectée. {len(checkpoint['processed_pages'])} pages déjà traitées.")
        except Exception as e:
            print(f"[WARNING] Impossible de lire le checkpoint, création d'un nouveau : {e}")

    start_p = args.start_page
    end_p = args.end_page if args.end_page else total_pages

    print(f"[START] Lancement de l'extraction des pages {start_p} à {end_p}...")
    
    try:
        for p in range(start_p, end_p + 1):
            page_idx = p - 1
            if page_idx in checkpoint["processed_pages"]:
                continue
                
            print(f"[{p}/{end_p}] Traitement de la page {p}...")
            page = doc.load_page(page_idx)
            pix = page.get_pixmap(dpi=75) # DPI réduit pour économiser les tokens
            img_bytes = pix.tobytes("jpeg")
            img = Image.open(io.BytesIO(img_bytes))
            
            # Appel API
            retry_count = 0
            success = False
            while retry_count < 3 and not success:
                try:
                    response = model.generate_content([PROMPT, img])
                    text_res = response.text.strip()
                    
                    if text_res.startswith("```json"):
                        text_res = text_res[7:-3].strip()
                    elif text_res.startswith("```"):
                        text_res = text_res[3:-3].strip()
                        
                    if text_res:
                        page_data = json.loads(text_res)
                        
                        images_dir = Path("images_extraites")
                        images_dir.mkdir(exist_ok=True)
                        img_width, img_height = img.size

                        if isinstance(page_data, list):
                            # Ajouter la page de provenance pour traçabilité
                            for ex in page_data:
                                ex["source_page"] = p
                                if "documents_annexes" in ex:
                                    for idx, doc_annexe in enumerate(ex["documents_annexes"]):
                                        if "box_2d" in doc_annexe and isinstance(doc_annexe["box_2d"], list) and len(doc_annexe["box_2d"]) == 4:
                                            ymin, xmin, ymax, xmax = doc_annexe["box_2d"]
                                            left = (xmin / 1000) * img_width
                                            top = (ymin / 1000) * img_height
                                            right = (xmax / 1000) * img_width
                                            bottom = (ymax / 1000) * img_height
                                            
                                            try:
                                                cropped_img = img.crop((left, top, right, bottom))
                                                img_filename = f"{ex.get('exercice_id', f'p{p}_inconnu')}_doc{idx+1}.jpg"
                                                img_filepath = images_dir / img_filename
                                                cropped_img.save(img_filepath)
                                                doc_annexe["image_path"] = str(img_filepath)
                                                del doc_annexe["box_2d"]
                                            except Exception as e:
                                                print(f"  -> Erreur recadrage image page {p} : {e}")

                            checkpoint["data"].extend(page_data)
                            print(f"  -> {len(page_data)} exercices trouvés.")
                        success = True
                    else:
                        print("  -> Page vide ou sans exercice.")
                        success = True # Considéré comme traité
                except json.JSONDecodeError:
                    print("  -> Erreur de format JSON retourné. Nouvel essai...")
                    retry_count += 1
                    time.sleep(2)
                except Exception as e:
                    print(f"  -> Erreur d'appel API : {e}. Nouvel essai...")
                    retry_count += 1
                    time.sleep(5)
            
            if success:
                checkpoint["processed_pages"].append(page_idx)
                # Sauvegarde du checkpoint en écriture sécurisée
                with open(CHECKPOINT_PATH, "w", encoding="utf-8") as f:
                    json.dump(checkpoint, f, ensure_ascii=False, indent=2)
            else:
                print(f"[WARNING] Échec de la page {p} après 3 tentatives. Passage à la page suivante.")

            # Respect du Rate Limit de l'API Gratuite pour 2.5 Flash Lite (10 RPM)
            # Pause de 7.5 secondes pour éviter le dépassement de quota par minute
            time.sleep(7.5)

        # Extraction terminée, fusionner dans la DB principale
        print("\n[SUCCESS] Extraction terminée !")
        merge_checkpoint_to_db(db_path, checkpoint["data"])
        
        # Archiver le checkpoint au lieu de le supprimer
        archive_path = CHECKPOINT_PATH.with_name(f"khelifa_checkpoint_done_{int(time.time())}.json")
        CHECKPOINT_PATH.rename(archive_path)
        print(f"[CLEANUP] Checkpoint archivé sous : {archive_path.name}")

    except KeyboardInterrupt:
        print("\n[INTERRUPT] Script interrompu par l'utilisateur. Progression sauvegardée dans le checkpoint.")
        print("Tu peux relancer le script à tout moment pour reprendre.")

if __name__ == "__main__":
    main()
