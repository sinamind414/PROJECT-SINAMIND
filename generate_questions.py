# -*- coding: utf-8 -*-
"""
3. generate_questions.py - Génération de questions avec GPT-4o ou Gemini (Supervisé)
Usage:
    python generate_questions.py --input "chapters_text.json"
"""

import os
import json
import argparse
from pathlib import Path
from dotenv import load_dotenv

# Charger les variables d'environnement
load_dotenv(Path(__file__).parent / 'khawarizmi-backend' / '.env')
load_dotenv()

SYSTEM_PROMPT = """
Tu es un professeur de Sciences Naturelles (SVT) du secondaire en Algérie, expert dans la préparation du Baccalauréat (Filière Sciences Expérimentales).
Ta tâche est de lire ce document textuel extrait d'un manuel d'exercices SVT (en Arabe) et d'en extraire/générer des questions d'exercices structurées en JSON.

Pour chaque exercice ou question identifié dans le texte, génère un objet JSON suivant ce schéma :
{
  "exercice_id": "Un identifiant unique basé sur le chapitre et un numéro, ex: ex_[chapitre_id]_1",
  "thematique": "Thématique globale de l'exercice en Arabe (ex: تركيب البروتين, استجابة مناعية خلطية, الاتصال العصبي)",
  "chapitre_id": "L'ID du chapitre (fourni dans le contexte)",
  "points": 5, // Score de l'exercice (5, 7, ou 8 points)
  "questions": [
    {
      "question_id": "q1",
      "texte": "La question scientifique en arabe telle qu'extraite ou formulée de manière claire",
      "reponse_attendue": "La réponse modèle attendue en arabe (détaillée et scientifiquement rigoureuse pour le Bac Algérien)",
      "concept_cle": "Le micro-concept testé par cette question en arabe (ex: استنساخ, موقع فعال, إفراز الأسيتيل كولين)",
      "pattern_recherche": "3 à 5 mots clés indispensables en arabe séparés par des virgules (ex: بوليميراز, نيوكليوتيدات, روابط هيدروجينية)"
    }
  ]
}

Règles de génération :
- Le contenu scientifique doit être extrait fidèlement du texte fourni.
- Les réponses attendues doivent être de haute qualité et rigoureuses.
- Les pattern_recherche doivent contenir des termes techniques cruciaux pour le matching automatique.
- Retourne STRICTEMENT une liste JSON : [ {exercice_1}, {exercice_2}, ... ]
- N'inclus aucune explication en dehors du JSON, pas de code block Markdown ```json ... ```, uniquement du texte JSON brut.
"""

def generate_via_openai(api_key: str, model_name: str, chapter_id: str, text: str) -> list:
    from openai import OpenAI
    client = OpenAI(api_key=api_key)
    
    print(f"  -> Appel OpenAI ({model_name}) pour {chapter_id}...")
    user_prompt = f"Voici le texte brut pour le chapitre ID '{chapter_id}'. Génère les questions au format JSON :\n\n{text}"
    
    response = client.chat.completions.create(
        model=model_name,
        messages=[
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": user_prompt}
        ],
        temperature=0.3,
        response_format={"type": "json_object"}
    )
    
    res_text = response.choices[0].message.content.strip()
    # Si le modèle renvoie une structure englobante (ex: {"exercices": [...]})
    data = json.loads(res_text)
    if isinstance(data, dict) and "exercices" in data:
        return data["exercices"]
    elif isinstance(data, dict) and len(data) == 1 and isinstance(list(data.values())[0], list):
        return list(data.values())[0]
    return data if isinstance(data, list) else [data]

def generate_via_gemini(api_key: str, model_name: str, chapter_id: str, text: str) -> list:
    import google.generativeai as genai
    genai.configure(api_key=api_key)
    model = genai.GenerativeModel(model_name)
    
    print(f"  -> Appel Gemini ({model_name}) pour {chapter_id}...")
    user_prompt = f"Voici le texte brut pour le chapitre ID '{chapter_id}'. Génère les questions au format JSON :\n\n{text}"
    
    # Fusionner le prompt système et le texte
    response = model.generate_content([SYSTEM_PROMPT, user_prompt])
    res_text = response.text.strip()
    
    if res_text.startswith("```json"):
        res_text = res_text[7:-3].strip()
    elif res_text.startswith("```"):
        res_text = res_text[3:-3].strip()
        
    data = json.loads(res_text)
    if isinstance(data, dict) and "exercices" in data:
        return data["exercices"]
    elif isinstance(data, dict) and len(data) == 1 and isinstance(list(data.values())[0], list):
        return list(data.values())[0]
    return data if isinstance(data, list) else [data]

def generate_questions(input_json: Path, output_json: Path, force_model: str):
    if not input_json.exists():
        print(f"[ERROR] Fichier d'entrée introuvable : {input_json}")
        return False

    with open(input_json, "r", encoding="utf-8") as f:
        chapters_data = json.load(f)

    # 1. Sélection du fournisseur d'API
    openai_key = os.environ.get("OPENAI_API_KEY")
    gemini_key = os.environ.get("GEMINI_API_KEY") or os.environ.get("GOOGLE_API_KEY")

    provider = None
    api_key = None
    model_name = None

    if force_model:
        if "gpt" in force_model:
            provider = "openai"
            api_key = openai_key
            model_name = force_model
        else:
            provider = "gemini"
            api_key = gemini_key
            model_name = force_model
    else:
        # Choix automatique (OpenAI par défaut si configuré)
        if openai_key and openai_key != "ta_cle_openai":
            provider = "openai"
            api_key = openai_key
            model_name = "gpt-4o"
        elif gemini_key and gemini_key != "ta_cle_gemini":
            provider = "gemini"
            api_key = gemini_key
            model_name = "gemini-2.0-flash"

    if not provider or not api_key:
        print("[ERROR] Clé API introuvable ou configurée avec des placeholders.")
        print("        Veuillez renseigner OPENAI_API_KEY ou GEMINI_API_KEY dans le fichier .env")
        return False

    print(f"[3/5] Début de la génération via {provider.upper()} ({model_name})...")
    
    all_generated_exercises = []

    for chap_id, text in chapters_data.items():
        if chap_id in ("ch_inconnu", "page_vide_ou_image"):
            # On ignore les pages non classées
            continue
            
        print(f"\n📂 Traitement du chapitre : {chap_id} ({len(text)} caractères)...")
        
        # Limiter la taille pour éviter de dépasser les limites (ex: 20000 caractères par paquet)
        # Idéalement, diviser le texte s'il est trop grand
        max_chars = 30000
        text_chunks = [text[i:i+max_chars] for i in range(0, len(text), max_chars)]
        
        for idx, chunk in enumerate(text_chunks):
            if len(text_chunks) > 1:
                print(f"  * Partie {idx + 1}/{len(text_chunks)}")
            
            try:
                if provider == "openai":
                    exercises = generate_via_openai(api_key, model_name, chap_id, chunk)
                else:
                    exercises = generate_via_gemini(api_key, model_name, chap_id, chunk)
                
                # Suffixer les ID pour éviter les collisions si on a plusieurs blocs
                for i, ex in enumerate(exercises):
                    if len(text_chunks) > 1:
                        ex["exercice_id"] = f"{ex['exercice_id']}_pt{idx+1}_{i}"
                    all_generated_exercises.append(ex)
                    
                print(f"  ✅ {len(exercises)} exercice(s) généré(s) pour cette partie.")
            except Exception as e:
                print(f"  ❌ Erreur de génération pour le chapitre {chap_id} : {e}")

    with open(output_json, "w", encoding="utf-8") as f:
        json.dump(all_generated_exercises, f, ensure_ascii=False, indent=2)

    print(f"\n[SUCCESS] Génération terminée ! {len(all_generated_exercises)} exercice(s) brut(s) dans : {output_json.name}")
    return True

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Étape 3 : Génération automatique de questions via LLM")
    parser.add_argument("--input", default="chapters_text.json", help="JSON d'entrée structuré par chapitre")
    parser.add_argument("--output", default="generated_questions.json", help="Fichier JSON des questions brutes")
    parser.add_argument("--model", help="Forcer l'utilisation d'un modèle (ex: gpt-4o-mini ou gemini-2.0-flash)")
    args = parser.parse_args()

    generate_questions(Path(args.input), Path(args.output), args.model)
