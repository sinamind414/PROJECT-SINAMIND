# -*- coding: utf-8 -*-
"""
2. split_chapters.py - Découpage semi-automatique par chapitre via mots-clés
Usage:
    python split_chapters.py --input "extracted_pages.json"
"""

import json
import argparse
from pathlib import Path

# Dictionnaire de classification copié depuis normalize_sciences.py pour cohérence
CHAPITRES_SVT = {
    "ch1_proteines": {
        "label": "تركيب البروتين (Synthèse des protéines)",
        "keywords": ["ARNm", "ADN", "ريبوزوم", "استنساخ", "ترجمة", "نيوكليوتيد", "رامزة", "شفرة وراثية", "بوليميراز"]
    },
    "ch2_structure": {
        "label": "العلاقة بين البنية والوظيفة (Structure et fonction)",
        "keywords": ["حمض أميني", "رابطة ببتيدية", "بنية فراغية", "PHi", "أمفوتير", "هجرة كهربائية", "جذر", "حمض ببتيدي"]
    },
    "ch3_enzymes": {
        "label": "النشاط الإنزيمي (Activité enzymatique)",
        "keywords": ["إنزيم", "موقع فعال", "ركيزة", "تحفيز", "نوعية", "درجة حرارة", "pH", "مثبط", "الموقع الفعال"]
    },
    "ch4_immunite": {
        "label": "دور البروتينات في الدفاع عن الذات (Immunologie)",
        "keywords": ["CMH", "HLA", "LT", "LB", "جسم مضاد", "مستضد", "بالعة", "VIH", "استجابة مناعية", "خلايا لمفاوية"]
    },
    "ch5_nerveux": {
        "label": "دور البروتينات في الاتصال العصبي (Communication nerveuse)",
        "keywords": ["كمون", "مشبك", "سيالة عصبية", "استقطاب", "Na+", "K+", "ACh", "GABA", "مبلغ عصبي"]
    },
    "ch6_photosynthese": {
        "label": "آليات تحويل الطاقة الضوئية (Photosynthèse)",
        "keywords": ["تركيب ضوئي", "يخضور", "تيالكويد", "كالفن", "NADPH", "RuDP", "APG", "صانعة خضراء"]
    },
    "ch7_respiration": {
        "label": "آليات تحويل الطاقة الكيميائية (Respiration)",
        "keywords": ["تنفس خلوي", "ميتوكوندري", "كريبس", "ATP", "تحلل سكري", "فسفرة تأكسدية", "NADH", "حمض بيروفيك"]
    }
}

def classer_page(text: str) -> str:
    """Détermine à quel chapitre appartient une page en fonction du nombre de mots-clés trouvés."""
    if not text:
        return "page_vide_ou_image"

    scores = {ch: 0 for ch in CHAPITRES_SVT}
    
    # Compter l'occurrence de chaque mot-clé
    for ch, info in CHAPITRES_SVT.items():
        for keyword in info["keywords"]:
            # Recherche simple (sensible ou insensible selon le mot-clé)
            if keyword.lower() in text.lower():
                scores[ch] += text.lower().count(keyword.lower())

    # Trouver le chapitre avec le score maximal
    if max(scores.values()) == 0:
        return "ch_inconnu" # Pas de mots-clés trouvés

    return max(scores, key=scores.get)

def split_by_chapters(input_json: Path, output_json: Path):
    if not input_json.exists():
        print(f"[ERROR] Le fichier d'entrée est introuvable : {input_json}")
        return False

    with open(input_json, "r", encoding="utf-8") as f:
        pages_data = json.load(f)

    print(f"[2/5] Découpage en cours sur {len(pages_data)} pages...")

    # Dictionnaires pour stocker les résultats
    chapters_content = {ch: [] for ch in CHAPITRES_SVT}
    chapters_content["ch_inconnu"] = []
    chapters_content["page_vide_ou_image"] = []

    stats = {ch: 0 for ch in chapters_content}

    for page_info in pages_data:
        p_num = page_info["page"]
        p_text = page_info["text"]
        
        chap_id = classer_page(p_text)
        
        if p_text:
            # Structurer le texte avec le numéro de page d'origine pour traçabilité
            formatted_text = f"--- [PAGE {p_num}] ---\n{p_text}\n"
            chapters_content[chap_id].append(formatted_text)
        
        stats[chap_id] += 1

    # Concaténer le texte de chaque chapitre en une seule chaîne
    final_output = {}
    for ch, texts in chapters_content.items():
        if texts:
            final_output[ch] = "\n".join(texts)

    # Afficher le résumé de la classification
    print("\n[STATS] RÉSULTAT DU DÉCOUPAGE PAR CHAPITRE :")
    for chap_id, count in stats.items():
        if count > 0:
            label = CHAPITRES_SVT.get(chap_id, {}).get("label", chap_id)
            print(f"  - {label} : {count} pages affectées")

    with open(output_json, "w", encoding="utf-8") as f:
        json.dump(final_output, f, ensure_ascii=False, indent=2)

    print(f"\n[SUCCESS] Découpage terminé ! Fichier écrit dans : {output_json.name}")
    return True

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Étape 2 : Découpage semi-automatique du texte par chapitre SVT")
    parser.add_argument("--input", default="extracted_pages.json", help="JSON des pages extraites")
    parser.add_argument("--output", default="chapters_text.json", help="JSON de sortie structuré par chapitre")
    args = parser.parse_args()

    split_by_chapters(Path(args.input), Path(args.output))
