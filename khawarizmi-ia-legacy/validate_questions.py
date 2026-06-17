# -*- coding: utf-8 -*-
"""
4. validate_questions.py - Validation manuelle et interactive des exercices générés
Usage:
    python validate_questions.py --input "generated_questions.json"
"""

import json
import os
import sys
import argparse
from pathlib import Path

def print_separator():
    print("\n" + "═" * 70 + "\n")

def safe_print(text):
    """Affiche le texte de manière compatible avec la console Windows."""
    try:
        print(text)
    except UnicodeEncodeError:
        # Fallback pour cp1252 si nécessaire
        sys.stdout.buffer.write((text + '\n').encode('utf-8', errors='replace'))

def interactive_review(input_json: Path, output_json: Path):
    if not input_json.exists():
        print(f"[ERROR] Fichier d'entrée introuvable : {input_json}")
        return False

    with open(input_json, "r", encoding="utf-8") as f:
        exercises = json.load(f)

    if not exercises:
        print("[INFO] Aucun exercice à valider.")
        return True

    print_separator()
    print("      KHAWARIZMI IA — VALIDATION DES EXERCICES SVT")
    print(f"      ({len(exercises)} exercices chargés pour relecture)")
    print_separator()
    print("Instructions :")
    print("  [v] : Valider l'exercice (l'ajouter à la liste de sortie)")
    print("  [d] : Supprimer / Rejeter l'exercice")
    print("  [e] : Modifier une question de l'exercice")
    print("  [q] : Sauvegarder et quitter le script de validation")
    print_separator()

    validated_exercises = []

    for idx, ex in enumerate(exercises):
        validated = False
        while not validated:
            print(f"\n({idx + 1}/{len(exercises)}) Exercice ID : {ex.get('exercice_id')}")
            safe_print(f"Chapitre ID  : {ex.get('chapitre_id')}")
            safe_print(f"Thématique   : {ex.get('thematique')}")
            safe_print(f"Points       : {ex.get('points')}")
            print("Questions :")
            
            for q_idx, q in enumerate(ex.get("questions", [])):
                print(f"  --- Question {q_idx + 1} ({q.get('question_id')}) ---")
                safe_print(f"    Texte             : {q.get('texte')}")
                safe_print(f"    Réponse attendue  : {q.get('reponse_attendue')}")
                safe_print(f"    Concept clé       : {q.get('concept_cle')}")
                safe_print(f"    Mots clés requis  : {q.get('pattern_recherche')}")

            print_separator()
            choice = input("Choix [v / d / e / q] : ").strip().lower()

            if choice == 'v':
                validated_exercises.append(ex)
                print("✅ Exercice validé.")
                validated = True
            elif choice == 'd':
                print("❌ Exercice supprimé.")
                validated = True
            elif choice == 'q':
                # Sauvegarder ce qui a été validé et quitter
                with open(output_json, "w", encoding="utf-8") as f:
                    json.dump(validated_exercises, f, ensure_ascii=False, indent=2)
                print(f"\n[INFO] Validation interrompue. {len(validated_exercises)} exercices sauvegardés dans {output_json.name}.")
                sys.exit(0)
            elif choice == 'e':
                # Menu d'édition
                print("\n--- Modification de l'exercice ---")
                new_theme = input(f"Nouvelle thématique [{ex.get('thematique')}] : ").strip()
                if new_theme:
                    ex['thematique'] = new_theme
                    
                new_points = input(f"Nouveau barème [{ex.get('points')}] : ").strip()
                if new_points:
                    try:
                        ex['points'] = int(new_points)
                    except ValueError:
                        print("Valeur invalide pour les points, conservée.")
                
                for q_idx, q in enumerate(ex.get("questions", [])):
                    print(f"\nModification de la Question {q_idx + 1} :")
                    new_text = input(f"  Nouveau texte [{q.get('texte')}] : ").strip()
                    if new_text:
                        q['texte'] = new_text
                        
                    new_rep = input(f"  Nouvelle réponse [{q.get('reponse_attendue')}] : ").strip()
                    if new_rep:
                        q['reponse_attendue'] = new_rep
                        
                    new_concept = input(f"  Nouveau concept clé [{q.get('concept_cle')}] : ").strip()
                    if new_concept:
                        q['concept_cle'] = new_concept
                        
                    new_pattern = input(f"  Nouveau pattern recherche [{q.get('pattern_recherche')}] : ").strip()
                    if new_pattern:
                        q['pattern_recherche'] = new_pattern
                        
                print("\nExercice modifié. Réaffichage pour vérification.")
            else:
                print("Choix invalide. Veuillez entrer v, d, e ou q.")

    with open(output_json, "w", encoding="utf-8") as f:
        json.dump(validated_exercises, f, ensure_ascii=False, indent=2)

    print_separator()
    print(f"[SUCCESS] Relecture terminée. {len(validated_exercises)} exercices validés enregistrés dans : {output_json.name}")
    print_separator()
    return True

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Étape 4 : Validation interactive des questions SVT générées")
    parser.add_argument("--input", default="generated_questions.json", help="JSON brut d'entrée")
    parser.add_argument("--output", default="validated_questions.json", help="Fichier JSON des questions validées")
    args = parser.parse_args()

    # Configuration de l'encodage d'E/S du terminal sous Windows
    # pour pouvoir taper et lire de l'arabe sans crash
    if sys.platform == "win32":
        import io
        sys.stdin = io.TextIOWrapper(sys.stdin.buffer, encoding='utf-8')
        sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

    interactive_review(Path(args.input), Path(args.output))
