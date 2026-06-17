# -*- coding: utf-8 -*-
"""
5. inject_to_db.py - Injection des exercices validés dans la base de données principale
Usage:
    python inject_to_db.py --input "validated_questions.json"
"""

import json
import os
import time
import shutil
import subprocess
import argparse
from pathlib import Path

DEFAULT_DB_PATH = Path("annales_sciences_3as.json")

def inject_exercises(input_json: Path, db_path: Path, sujet_id: str, sujet_titre: str, overwrite: bool = False):
    if not input_json.exists():
        print(f"[ERROR] Fichier d'entrée introuvable : {input_json}")
        return False

    with open(input_json, "r", encoding="utf-8") as f:
        validated_exercises = json.load(f)

    if not validated_exercises:
        print("[INFO] Aucun exercice à injecter.")
        return True

    print(f"[5/5] Ingestion de {len(validated_exercises)} exercices dans {db_path.name}...")

    # 1. Charger la base existante
    if db_path.exists():
        with open(db_path, "r", encoding="utf-8") as f:
            db_data = json.load(f)
    else:
        db_data = []

    # 2. Trouver ou créer le sujet
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
            "titre": sujet_titre,
            "exercices": []
        }
        db_data.append(sujet)
        print(f"[INFO] Nouveau sujet créé dans la DB : {sujet_titre}")

    # Indexer pour éviter les doublons ou remplacer
    existants = {ex["exercice_id"]: idx for idx, ex in enumerate(sujet["exercices"])}

    ajoutes = 0
    remplaces = 0
    for ex in validated_exercises:
        ex_id = ex.get("exercice_id")
        if ex_id in existants:
            if overwrite:
                idx = existants[ex_id]
                sujet["exercices"][idx] = ex
                print(f"[OVERWRITE] Exercice mis à jour : {ex_id}")
                remplaces += 1
            else:
                print(f"[SKIP] Doublon détecté, exercice déjà présent : {ex_id}")
            continue

        sujet["exercices"].append(ex)
        existants[ex_id] = len(sujet["exercices"]) - 1
        ajoutes += 1

    if ajoutes == 0 and remplaces == 0:
        print("[INFO] Tous les exercices sont déjà présents. DB inchangée.")
        return True

    # 3. Créer une sauvegarde de sécurité
    backup_path = db_path.with_suffix(f'.backup_inject_{int(time.time())}.json')
    if db_path.exists():
        shutil.copy2(db_path, backup_path)
        print(f"[BACKUP] Sauvegarde créée : {backup_path.name}")

    # 4. Enregistrer la DB mise à jour
    with open(db_path, "w", encoding="utf-8") as f:
        json.dump(db_data, f, ensure_ascii=False, indent=2)

    print(f"[SUCCESS] {ajoutes} exercice(s) injecté(s) et {remplaces} remplacé(s) avec succès !")
    print(f"[INFO] Nombre total d'exercices pour ce sujet : {len(sujet['exercices'])}")

    # 5. Lancer le normalisateur
    print("\n[STATS] Lancement du normalisateur pour synchroniser les corpus...")
    try:
        import sys
        # Forcer l'encodage UTF-8 pour le subprocess sous Windows
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
            print("[NORMALISATION SUCCESS]")
            sys.stdout.buffer.write(result.stdout.encode('utf-8', errors='replace'))
        else:
            print("[NORMALISATION ERROR] Le normalisateur a échoué :")
            sys.stderr.buffer.write(result.stderr.encode('utf-8', errors='replace'))
    except Exception as e:
        print(f"[WARNING] Impossible de lancer le normalisateur automatiquement : {e}")
        print("          Pensez à lancer manuellement: python normalize_sciences.py")

    return True

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Étape 5 : Ingestion des exercices dans la DB et normalisation")
    parser.add_argument("--input", default="validated_questions.json", help="JSON d'entrée validé")
    parser.add_argument("--db", default=str(DEFAULT_DB_PATH), help="Chemin vers annales_sciences_3as.json")
    parser.add_argument("--sujet-id", default="ahmed_amin_khelifa_v2_part1", help="ID du sujet cible")
    parser.add_argument("--sujet-titre", default="Ahmed Amin Khelifa V2 - Partie 1", help="Titre du sujet cible")
    parser.add_argument("--overwrite", action="store_true", help="Remplacer les exercices si l'ID existe déjà")
    args = parser.parse_args()

    inject_exercises(Path(args.input), Path(args.db), args.sujet_id, args.sujet_titre, args.overwrite)
