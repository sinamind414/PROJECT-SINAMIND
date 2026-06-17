# -*- coding: utf-8 -*-
"""
auto_ingest_pdf.py — Automatisation complète du traitement des PDF (pages individuelles)
- Extrait la page du PDF sous forme d'image WebP haute définition (300 DPI)
- Envoie l'image à Gemini 2.5 Flash pour extraire les questions en JSON
- Associe automatiquement l'image générée aux exercices dans le JSON
- Injecte les exercices dans la base de données principale (annales_sciences_3as.json)
- Lance automatiquement le normalisateur pour reconstruire le corpus

Usage :
    1. Déposez vos PDF de pages dans le dossier 'import_pdf/'
    2. Lancez le script : python auto_ingest_pdf.py
"""

import os
import re
import sys
import json
import time
import shutil
import subprocess
from pathlib import Path
import fitz  # PyMuPDF
from PIL import Image
from dotenv import load_dotenv
import google.generativeai as genai

# Helper function for safe print to windows consoles
def safe_print(text):
    try:
        print(text)
    except UnicodeEncodeError:
        try:
            sys.stdout.buffer.write((text + "\n").encode("utf-8", errors="replace"))
        except Exception:
            # Fallback to pure ascii stripping
            print(text.encode("ascii", errors="ignore").decode("ascii"))

# ─── CONFIGURATION DES DOSSIERS ────────────────────────────────
IMPORT_DIR = Path("import_pdf")
PROCESSED_DIR = Path("processed_pdf")
DB_PATH = Path("annales_sciences_3as.json")
SUBJECT_ID = "ahmed_amin_khelifa_v2_part1"
SUBJECT_TITLE = "Ahmed Amin Khelifa V2 - Partie 1"

# Dossiers pour stocker les images WebP (les deux destinations possibles)
IMAGE_OUT_ROOT = Path("assets/images/khelifa")
IMAGE_OUT_FRONTEND = Path("khawarizmi-frontend/public/assets/images/khelifa")

# ─── CHARGEMENT DE LA CLÉ GEMINI ────────────────────────────────
# Essaye de charger .env depuis le backend ou le dossier courant
for env_path in [Path("khawarizmi-backend/.env"), Path(".env")]:
    if env_path.exists():
        load_dotenv(env_path)
        break

api_key = os.environ.get("GEMINI_API_KEY") or os.environ.get("GOOGLE_API_KEY")
if not api_key:
    safe_print("[ERROR] Cle API Gemini introuvable dans le fichier .env.")
    safe_print("Veuillez configurer GEMINI_API_KEY dans votre fichier .env.")
    sys.exit(1)

genai.configure(api_key=api_key)

# Prompt pour Gemini 2.5 Flash
SYSTEM_INSTRUCTION = """Tu es un professeur de Sciences Naturelles (SVT) de Terminale en Algérie, expert du Baccalauréat (Filière Sciences Expérimentales).
Analyse la page fournie du livre d'exercices d'Ahmed Amin Khelifa pour en extraire les exercices scientifiques de SVT et leurs corrections correspondantes.

Pour chaque exercice détecté dans le document, tu dois associer ses questions à leurs réponses/corrections respectives et générer un tableau JSON.

Voici le schéma JSON strict que tu dois respecter :
[
  {
    "exercice_id": "khelifa_p{page_num}_ex{index}",
    "thematique": "Thématique globale de l'exercice en Arabe (ex: تركيب البروتين, استجابة مناعية خلطية, الاتصال العصبي, النشاط الإنزيمي)",
    "chapitre_id": "L'identifiant exact du chapitre (choisir UNIQUEMENT parmi la liste ci-dessous)",
    "points": 5, // Barème de l'exercice (généralement 5, 7 ou 8 points)
    "questions": [
      {
        "question_id": "q1",
        "texte": "Le texte exact de la question en Arabe, tel qu'il apparaît dans le livre",
        "reponse_attendue": "La réponse/correction détaillée de la question en Arabe (rigoureuse pour le Bac Algérien)",
        "concept_cle": "Le concept scientifique clé testé par cette question en Arabe (ex: استنساخ, موقع فعال, إفراز الأسيتيل كولين)",
        "pattern_recherche": "3 à 5 mots clés indispensables en Arabe séparés par des virgules pour la notation automatique (ex: بوليميراز, نيوكليوتيدات, روابط هيدروجينية)"
      }
    ]
  }
]

### Liste stricte des chapitre_id valides :
- "ch1_proteines" : تركيب البروتين (Synthèse des protéines)
- "ch2_structure" : العلاقة بين بنية ووظيفة البروتين (Structure et fonction des protéines)
- "ch3_enzymes" : النشاط الإنزيمي (Activité enzymatique)
- "ch4_immunite" : دور البروتينات في الدفاع عن الذات (Immunité)
- "ch5_nerveux" : دور البروتينات في الاتصال العصبي (Communication nerveuse)
- "ch6_photosynthese" : آليات تحويل الطاقة الضوئية (Photosynthèse)
- "ch7_respiration" : آليات تحويل الطاقة الكيميائية (Respiration)

### Règles importantes :
1. Le texte des questions, des réponses attendues, de la thématique, du concept clé et des mots-clés de recherche doit être rédigé en arabe scientifique de haute qualité.
2. Si le document contient des exercices sans correction immédiate, rédige toi-même la correction modèle standard du Baccalauréat algérien.
3. Utilise la notation LaTeX pour les formules chimiques et symboles scientifiques si nécessaire, par exemple ($\\alpha$) ou ($H^+$) ou ($-COOH$).
4. N'inclus aucune explication avant ou après le JSON. Retourne uniquement le texte JSON brut (sans balises markdown ```json).
"""

def setup_directories():
    """Crée les dossiers requis s'ils n'existent pas."""
    IMPORT_DIR.mkdir(exist_ok=True)
    PROCESSED_DIR.mkdir(exist_ok=True)
    IMAGE_OUT_ROOT.mkdir(parents=True, exist_ok=True)
    IMAGE_OUT_FRONTEND.mkdir(parents=True, exist_ok=True)

def extract_page_number(filename: str) -> str:
    """Extrait le numéro de page à partir du nom du fichier."""
    # Cherche un numéro précédé d'un tiret de soulignement ou à la fin (ex: parte 1_231)
    match = re.search(r"(\d+)(?:\.pdf)?$", filename, re.IGNORECASE)
    if match:
        return match.group(1)
    # Autre tentative
    match = re.search(r"_(\d+)", filename)
    if match:
        return match.group(1)
    return "inconnu"

def pdf_page_to_webp(pdf_path: Path, page_num_str: str) -> Path:
    """Convertit la première page du PDF en image WebP haute qualité."""
    safe_print(f"[CONVERT] Conversion de {pdf_path.name} en WebP...")
    with fitz.open(pdf_path) as doc:
        page = doc[0]  # On prend la première page
        
        # Rendu à 300 DPI pour une netteté maximale des textes et graphiques
        zoom = 300 / 72  # 72 points par pouce par défaut
        mat = fitz.Matrix(zoom, zoom)
        pix = page.get_pixmap(matrix=mat)
    
    # Save as temporary PNG
    temp_png_path = Path(f"temp_page_{page_num_str}.png")
    pix.save(str(temp_png_path))
    
    # Save as WebP in both destinations using Pillow
    image_basename = f"khelifa_p{page_num_str}.webp"
    with Image.open(temp_png_path) as img:
        for dest_dir in [IMAGE_OUT_ROOT, IMAGE_OUT_FRONTEND]:
            img.save(dest_dir / image_basename, "WEBP", quality=80)
            
    # Clean up temporary PNG
    if temp_png_path.exists():
        temp_png_path.unlink()
        
    safe_print(f"   Image sauvegardee : assets/images/khelifa/{image_basename}")
    return IMAGE_OUT_ROOT / image_basename

def call_gemini_ocr(image_path: Path, page_num_str: str) -> list:
    """Appelle l'API Gemini 2.5 Flash avec l'image pour extraire le JSON."""
    safe_print(f"[GEMINI] Analyse de l'image par Gemini 2.5 Flash...")
    model = genai.GenerativeModel("gemini-2.5-flash")
    
    # Chargement de l'image via Pillow
    img = Image.open(image_path)
    
    prompt = SYSTEM_INSTRUCTION.replace("{page_num}", page_num_str)
    
    response = model.generate_content([img, prompt])
    
    # Extraction et nettoyage du JSON
    raw_text = response.text.strip()
    
    # Nettoyage d'éventuels blocs de code markdown
    if raw_text.startswith("```"):
        raw_text = re.sub(r"^```[a-zA-Z]*\n", "", raw_text)
        raw_text = re.sub(r"\n```$", "", raw_text)
    
    raw_text = raw_text.strip()
    
    try:
        # Essai de parsing direct
        exercises = json.loads(raw_text)
    except json.JSONDecodeError:
        # Essai de réparation des antislashs LaTeX (ex: \alpha -> \\alpha)
        fixed_text = re.sub(r'\\([a-zA-Z])', r'\\\\\1', raw_text)
        try:
            exercises = json.loads(fixed_text)
        except json.JSONDecodeError as e:
            safe_print(f"[ERROR] Impossible de parser le JSON retourne par Gemini.")
            safe_print(f"   Brut recu :\n{raw_text}\n")
            raise e
            
    if not isinstance(exercises, list):
        exercises = [exercises]
    return exercises

def inject_exercises_to_db(new_exercises: list):
    """Injecte les exercices extraits dans la base de données annales_sciences_3as.json."""
    if not DB_PATH.exists():
        db_data = []
    else:
        with open(DB_PATH, "r", encoding="utf-8") as f:
            db_data = json.load(f)
            
    # Recherche du sujet cible
    sujet = None
    for s in db_data:
        if s.get("sujet_id") == SUBJECT_ID:
            sujet = s
            break
            
    if not sujet:
        sujet = {
            "sujet_id": SUBJECT_ID,
            "annee": 2024,
            "filiere": "Sciences Expérimentales",
            "titre": SUBJECT_TITLE,
            "exercices": []
        }
        db_data.append(sujet)
        safe_print(f"[INFO] Nouveau sujet cree : {SUBJECT_TITLE}")
        
    # Indexer pour éviter les doublons (on écrase si existant pour mise à jour)
    existants = {ex["exercice_id"]: idx for idx, ex in enumerate(sujet["exercices"])}
    
    ajoutes = 0
    remplaces = 0
    for ex in new_exercises:
        ex_id = ex.get("exercice_id")
        # Injection automatique des liens d'images (format liste + url simple pour compatibilité)
        img_url = f"assets/images/khelifa/{Path(ex['images'][0]).name}" if "images" in ex and ex["images"] else f"assets/images/khelifa/{ex_id.split('_ex')[0]}.webp"
        ex["images"] = [img_url]
        ex["image_url"] = img_url  # Double compatibilité
        
        if ex_id in existants:
            idx = existants[ex_id]
            sujet["exercices"][idx] = ex
            remplaces += 1
        else:
            sujet["exercices"].append(ex)
            existants[ex_id] = len(sujet["exercices"]) - 1
            ajoutes += 1
            
    # Sauvegarde de sécurité
    backup_path = DB_PATH.with_suffix(f'.backup_inject_{int(time.time())}.json')
    if DB_PATH.exists():
        shutil.copy2(DB_PATH, backup_path)
        
    # Enregistrement
    with open(DB_PATH, "w", encoding="utf-8") as f:
        json.dump(db_data, f, ensure_ascii=False, indent=2)
        
    safe_print(f"[SUCCESS] Base de donnees mise a jour : {ajoutes} ajoutes, {remplaces} remplaces.")
    safe_print(f"[INFO] Total exercices dans le sujet : {len(sujet['exercices'])}")

def run_normalizer():
    """Lance le script de normalisation."""
    safe_print("[NORMALIZE] Lancement de la normalisation du corpus...")
    env = os.environ.copy()
    env["PYTHONIOENCODING"] = "utf-8"
    
    result = subprocess.run(
        ["python", "normalize_sciences.py"],
        capture_output=True,
        text=True,
        env=env,
        encoding="utf-8"
    )
    if result.returncode == 0:
        safe_print("[NORMALIZE SUCCESS] Normalisation terminee et corpus synchronises.")
    else:
        safe_print("[NORMALIZE ERROR] Echec de la normalisation :")
        safe_print(result.stderr)

def main():
    setup_directories()
    
    pdf_files = list(IMPORT_DIR.glob("*.pdf"))
    if not pdf_files:
        safe_print("[INFO] Aucun fichier PDF trouve dans 'import_pdf/'.")
        safe_print("Veuillez y copier vos PDF de pages (ex: Ahmed amin khelifa version 2 parte 1_231.pdf) et relancer.")
        return
        
    safe_print(f"[START] Debut du traitement automatique pour {len(pdf_files)} fichiers...")
    
    for pdf_path in pdf_files:
        safe_print("\n" + "=" * 60)
        safe_print(f"Fichier : {pdf_path.name}")
        safe_print("=" * 60)
        
        # 1. Extraction du numéro de page
        page_num_str = extract_page_number(pdf_path.name)
        safe_print(f"Page detectee : {page_num_str}")
        
        try:
            # 2. Conversion PDF en image WebP
            image_path = pdf_page_to_webp(pdf_path, page_num_str)
            
            # 3. Extraction par Gemini 2.5 Flash
            exercises = call_gemini_ocr(image_path, page_num_str)
            safe_print(f"[SUCCESS] Extraction reussie : {len(exercises)} exercice(s) trouve(s).")
            
            # 4. Injection dans la base de données
            inject_exercises_to_db(exercises)
            
            # 5. Déplacement du PDF traité vers le dossier d'archives
            shutil.move(str(pdf_path), PROCESSED_DIR / pdf_path.name)
            safe_print(f"[ARCHIVE] PDF deplace vers {PROCESSED_DIR.name}/")
            
        except Exception as e:
            safe_print(f"[ERROR] Echec du traitement de {pdf_path.name} : {e}")
            
    # 6. Lancement final de la normalisation
    run_normalizer()
    safe_print("\n[FINISH] Tous les fichiers disponibles ont ete traites avec succes !")

if __name__ == "__main__":
    main()
