#!/usr/bin/env python3
"""
auto_tagger.py
Script d'aide au tagging automatique des questions avec les 42 micro-concepts.

Utilisation :
    python auto_tagger.py "texte de la question"
    python auto_tagger.py --batch questions.txt
    python auto_tagger.py --batch questions.txt --output tagged.json
"""

import argparse
import json
from pathlib import Path

BASE = Path(__file__).parent.parent.parent
REF_PATH = BASE / "data" / "official" / "micro_concepts_reference.json"

# Charger les micro-concepts
try:
    with open(REF_PATH, encoding="utf-8") as f:
        MICRO_CONCEPTS = json.load(f)["micro_concepts"]
except FileNotFoundError:
    print(f"[ERREUR] Fichier non trouvé : {REF_PATH}")
    MICRO_CONCEPTS = []

# Mapping de mots-clés (à enrichir au fil du temps)
KEYWORD_MAP = {
    # Synthèse des protéines
    "transcription": "mc_prot_01",
    "استنساخ": "mc_prot_01",
    "نسخ": "mc_prot_01",
    "arn polymérase": "mc_prot_01",
    "traduction": "mc_prot_02",
    "ترجمة": "mc_prot_02",
    "code génétique": "mc_prot_03",
    "الشفرة الوراثية": "mc_prot_03",
    "arn messager": "mc_prot_04",
    "الرنا الرسول": "mc_prot_04",
    "arnm": "mc_prot_04",
    "arn de transfert": "mc_prot_05",
    "الرنا الناقل": "mc_prot_05",
    "ribosome": "mc_prot_06",
    "ريبوزوم": "mc_prot_06",
    "initiation": "mc_prot_07",
    "élongation": "mc_prot_08",
    # Structure
    "structure primaire": "mc_struc_01",
    "structure secondaire": "mc_struc_02",
    "hélice": "mc_struc_02",
    "feuillet": "mc_struc_02",
    "structure tertiaire": "mc_struc_03",
    "structure quaternaire": "mc_struc_04",
    "structure-fonction": "mc_struc_05",
    # Enzymes
    "site actif": "mc_enz_01",
    "الموقع الفعال": "mc_enz_01",
    "spécificité": "mc_enz_02",
    "vitesse": "mc_enz_03",
    "température": "mc_enz_04",
    "ph": "mc_enz_04",
    "inhibition": "mc_enz_05",
    # Immunité
    "lymphocyte b": "mc_imm_01",
    "lymphocyte t": "mc_imm_02",
    "anticorps": "mc_imm_03",
    "الأجسام المضادة": "mc_imm_03",
    "réponse humorale": "mc_imm_04",
    "réponse cellulaire": "mc_imm_05",
    "mémoire immunitaire": "mc_imm_06",
    # Nerveux
    "potentiel de repos": "mc_nerv_01",
    "كمون الراحة": "mc_nerv_01",
    "potentiel d'action": "mc_nerv_02",
    "synapse": "mc_nerv_03",
    "neurotransmetteur": "mc_nerv_04",
    # Photosynthèse
    "chloroplaste": "mc_photo_01",
    "phase lumineuse": "mc_photo_02",
    "cycle de calvin": "mc_photo_03",
    "كالفن": "mc_photo_03",
    # Respiration
    "mitochondrie": "mc_resp_01",
    "glycolyse": "mc_resp_02",
    "cycle de krebs": "mc_resp_03",
    "chaîne respiratoire": "mc_resp_04",
    "fermentation": "mc_resp_05",
    # Tectonique
    "structure interne": "mc_tec_01",
    "plaques tectoniques": "mc_tec_02",
    "الصفائح": "mc_tec_02",
    "divergence": "mc_tec_03",
    "convergence": "mc_tec_03",
    "subduction": "mc_tec_04",
    "dorsale": "mc_tec_04",
    "sismicité": "mc_tec_05",
    "volcanisme": "mc_tec_05",
}


def suggest_micro_concepts(text: str, top_k: int = 3) -> list[dict]:
    """Retourne les meilleurs micro-concepts pour un texte donné."""
    if not text or not MICRO_CONCEPTS:
        return []

    text_lower = text.lower()
    scores = {}

    for mc in MICRO_CONCEPTS:
        score = 0
        mc_id = mc["id"]

        if mc_id.lower() in text_lower:
            score += 100

        for keyword, mapped_id in KEYWORD_MAP.items():
            if keyword in text_lower and mapped_id == mc_id:
                score += 30

        if mc.get("nom_fr", "").lower() in text_lower:
            score += 15
        if mc.get("nom_ar", "") in text:
            score += 20

        if score > 0:
            scores[mc_id] = {"mc": mc, "score": score}

    sorted_results = sorted(scores.values(), key=lambda x: x["score"], reverse=True)[:top_k]

    return [
        {
            "id": r["mc"]["id"],
            "nom_fr": r["mc"].get("nom_fr", ""),
            "nom_ar": r["mc"].get("nom_ar", ""),
            "score": r["score"],
        }
        for r in sorted_results
    ]


def process_batch(input_path: Path, output_path: Path | None = None) -> list[dict]:
    """Traite un fichier texte (une question par ligne)."""
    results = []
    with open(input_path, encoding="utf-8") as f:
        lines = [line.strip() for line in f if line.strip() and not line.startswith("#")]

    for i, line in enumerate(lines, 1):
        suggestions = suggest_micro_concepts(line)
        result = {
            "line": i,
            "texte": line,
            "suggested_micro_concept_id": suggestions[0]["id"] if suggestions else None,
            "suggestions": suggestions,
        }
        results.append(result)

    if output_path:
        with open(output_path, "w", encoding="utf-8") as f:
            json.dump(results, f, ensure_ascii=False, indent=2)
        print(f"✅ Résultats sauvegardés dans : {output_path}")

    return results


def main():
    parser = argparse.ArgumentParser(description="Auto-tagger pour les 42 micro-concepts")
    parser.add_argument("text", nargs="?", help="Texte d'une question")
    parser.add_argument("--batch", help="Fichier texte avec une question par ligne")
    parser.add_argument("--output", help="Fichier de sortie JSON (pour --batch)")

    args = parser.parse_args()

    if args.batch:
        process_batch(Path(args.batch), Path(args.output) if args.output else None)
    elif args.text:
        suggestions = suggest_micro_concepts(args.text)
        print(f"\nQuestion : {args.text}\n")
        if suggestions:
            for s in suggestions:
                print(f"  → {s['id']} ({s['nom_fr']}) — score: {s['score']}")
        else:
            print("Aucune suggestion trouvée.")
    else:
        parser.print_help()


if __name__ == "__main__":
    main()
