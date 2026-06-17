# normalize_sciences.py — VERSION FINALE

import json
import re
import sys
from pathlib import Path

# Configure stdout and stderr to use UTF-8 to prevent UnicodeEncodeError on Windows
if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8')
if hasattr(sys.stderr, 'reconfigure'):
    sys.stderr.reconfigure(encoding='utf-8')


# ─── CONSTANTES ───────────────────────────────────────────────

CHAPITRES = {
    "ch1_proteines": {
        "label": "تركيب البروتين",
        "keywords": [
            "ARNm", "ADN", "ريبوزوم", "استنساخ", "ترجمة",
            "نيوكليوتيد", "رامزة", "شفرة وراثية", "بوليميراز",
            "synthèse", "transcription", "traduction"
        ]
    },
    "ch2_structure": {
        "label": "العلاقة بين البنية والوظيفة",
        "keywords": [
            "حمض أميني", "رابطة ببتيدية", "بنية فراغية",
            "PHi", "أمفوتير", "هجرة كهربائية", "جذر",
            "acide aminé", "liaison peptidique", "structure"
        ]
    },
    "ch3_enzymes": {
        "label": "النشاط الإنزيمي",
        "keywords": [
            "إنزيم", "موقع فعال", "ركيزة", "تحفيز",
            "نوعية", "درجة حرارة", "pH", "مثبط",
            "enzyme", "substrat", "catalyse", "inhibiteur"
        ]
    },
    "ch4_immunite": {
        "label": "دور البروتينات في الدفاع عن الذات",
        "keywords": [
            "CMH", "HLA", "LT", "LB", "جسم مضاد",
            "مستضد", "بالعة", "VIH", "استجابة مناعية",
            "anticorps", "antigène", "immunité", "lymphocyte",
            "الدفاع عن الذات", "مناعة"
        ]
    },
    "ch5_nerveux": {
        "label": "دور البروتينات في الاتصال العصبي",
        "keywords": [
            "كمون", "مشبك", "سيالة عصبية", "استقطاب",
            "Na+", "K+", "ACh", "GABA", "برفورين",
            "potentiel", "synapse", "neurone", "influx"
        ]
    },
    "ch6_photosynthese": {
        "label": "آليات تحويل الطاقة الضوئية",
        "keywords": [
            "تركيب ضوئي", "يخضور", "تيالكويد", "كالفن",
            "NADPH", "RuDP", "APG", "صانعة خضراء",
            "photosynthèse", "chlorophylle", "Calvin", "thylakoid"
        ]
    },
    "ch7_respiration": {
        "label": "آليات تحويل الطاقة الكيميائية",
        "keywords": [
            "تنفس خلوي", "ميتوكوندري", "كريبس", "ATP",
            "تحلل سكري", "فسفرة تأكسدية", "NADH", "حمض بيروفيك",
            "respiration", "mitochondrie", "Krebs", "glycolyse"
        ]
    },
}

BLOOM_VERBES = {
    5: ["حوصل", "اقترح", "أعط تفسيرا", "فسّر", "استخلص"],
    4: ["قارن", "ميّز", "فرّق", "استنتج", "رتّب", "أثبت"],
    3: ["احسب", "طبّق", "صنّف", "أنجز", "لوّن", "صف"],
    2: ["اشرح", "علّل", "وضّح", "بيّن", "استخرج"],
    1: ["عرّف", "اذكر", "عدّد", "سطّر", "سمّ", "ما هي", "ما هو"],
}

SUJETS_METHODOLOGIE = {
    "minhajiya_", "minhajiya_RES", "minhajiya_RESUM",
    "minhajiya_ملخص"
}

CHAPITRE_MAP = {
    "ch1_proteines": "ch1_proteines",
    "ch_structure": "ch2_structure",
    "ch2_structure": "ch2_structure",
    "ch2_enzymes": "ch3_enzymes",
    "ch3_enzymes": "ch3_enzymes",
    "ch3_immunite": "ch4_immunite",
    "ch4_immunite": "ch4_immunite",
    "ch_nerveux": "ch5_nerveux",
    "ch5_nerveux": "ch5_nerveux",
    "ch6_photosynthese": "ch6_photosynthese",
    "ch_energie": "ch6_photosynthese",
    "ch7_respiration": "ch7_respiration",
    "ch_geologie": "ch_inconnu",
}

# ─── FONCTIONS ────────────────────────────────────────────────

def detecter_chapitre(texte: str) -> str:
    """Détecte le chapitre depuis le texte d'une question."""
    texte_lower = texte.lower()
    scores = {ch: 0 for ch in CHAPITRES}
    for ch, data in CHAPITRES.items():
        for kw in data["keywords"]:
            if kw.lower() in texte_lower:
                scores[ch] += 1
    best = max(scores, key=scores.get)
    return best if scores[best] > 0 else "ch_inconnu"

def detecter_bloom(texte: str) -> dict:
    """Détecte le niveau cognitif Bloom depuis le texte."""
    for niveau in sorted(BLOOM_VERBES.keys(), reverse=True):
        for verbe in BLOOM_VERBES[niveau]:
            if verbe in texte:
                return {
                    "niveau": niveau,
                    "verbe_detecte": verbe,
                    "label": {
                        5: "التأليف",
                        4: "التحليل",
                        3: "التطبيق",
                        2: "الفهم",
                        1: "التذكر"
                    }[niveau]
                }
    return {"niveau": 1, "verbe_detecte": None, "label": "التذكر"}

def est_methodologique(sujet_id: str) -> bool:
    """Identifie les documents méthodologiques."""
    return any(
        sujet_id.startswith(prefix)
        for prefix in SUJETS_METHODOLOGIE
    )

def normaliser_question(q: dict, sujet: dict, ex: dict) -> dict:
    """Transforme une question brute en format normalisé."""
    texte = q.get("texte", "")
    reponse = q.get("reponse_attendue", "")
    texte_complet = texte + " " + reponse

    chapitre_brut = ex.get("chapitre_id", "")
    chapitre = CHAPITRE_MAP.get(chapitre_brut, chapitre_brut)

    if chapitre in ("ch_minhajiya", "", "ch_inconnu"):
        chapitre = detecter_chapitre(texte_complet)

    bloom = detecter_bloom(texte)

    return {
        "id": f"{sujet['sujet_id']}_{ex['exercice_id']}_{q['question_id']}",
        "source": {
            "sujet_id": sujet.get("sujet_id"),
            "annee": sujet.get("annee"),
            "filiere": sujet.get("filiere"),
            "titre": sujet.get("titre"),
        },
        "chapitre_id": chapitre,
        "chapitre_label": CHAPITRES.get(chapitre, {}).get("label", ""),
        "bloom": bloom,
        "points": ex.get("points", 0),
        "enonce": texte,
        "reponse_attendue": reponse,
        "concept_cle": q.get("concept_cle", ""),
        "valide": len(texte_complet) > 10,
    }

def normaliser_corpus(input_path: str) -> dict:
    """Pipeline complet de normalisation."""

    with open(input_path, encoding="utf-8") as f:
        data = json.load(f)

    sujets = data if isinstance(data, list) else data.get("sujets", [])

    output = {
        "exercices_bac": [],
        "qr_atomiques": [],
        "resumes": [],
        "methodologie": [],
        "stats": {
            "total_sujets": len(sujets),
            "total_questions": 0,
            "par_chapitre": {ch: 0 for ch in CHAPITRES},
            "par_bloom": {i: 0 for i in range(1, 6)},
        }
    }
    
    # Initialize ch_inconnu stat
    output["stats"]["par_chapitre"]["ch_inconnu"] = 0

    for sujet in sujets:
        sujet_id = sujet.get("sujet_id", "")

        # Routing des documents
        if est_methodologique(sujet_id):
            if "ملخص" in sujet_id:
                destination = "resumes"
            elif "أخطاء" in sujet_id or "منهجية" in sujet_id:
                destination = "methodologie"
            else:
                destination = "methodologie"
        elif "أهم-الأسئلة" in sujet_id:
            destination = "qr_atomiques"
        else:
            destination = "exercices_bac"

        for ex in sujet.get("exercices", []):
            for q in ex.get("questions", []):
                nq = normaliser_question(q, sujet, ex)

                if not nq["valide"]:
                    continue

                output[destination].append(nq)
                output["stats"]["total_questions"] += 1

                ch = nq["chapitre_id"]
                if ch not in output["stats"]["par_chapitre"]:
                    output["stats"]["par_chapitre"][ch] = 0
                output["stats"]["par_chapitre"][ch] += 1

                bl = nq["bloom"]["niveau"]
                output["stats"]["par_bloom"][bl] += 1

    return output

def sauvegarder(output: dict, output_dir: str = "corpus/"):
    """Sauvegarde les 4 fichiers de sortie."""
    Path(output_dir).mkdir(exist_ok=True)

    fichiers = {
        "sciences_bac_exercices.json": output["exercices_bac"],
        "sciences_qr_atomiques.json":  output["qr_atomiques"],
        "sciences_resumes.json":        output["resumes"],
        "sciences_methodologie.json":   output["methodologie"],
    }

    for nom, contenu in fichiers.items():
        path = Path(output_dir) / nom
        with open(path, "w", encoding="utf-8") as f:
            json.dump(contenu, f, ensure_ascii=False, indent=2)
        print(f"✅ {nom} — {len(contenu)} entrées")

    # Stats
    print("\n📊 STATISTIQUES :")
    print(f"  Total questions : {output['stats']['total_questions']}")
    print("\n  Par chapitre :")
    for ch, n in output["stats"]["par_chapitre"].items():
        if n > 0:
            label = CHAPITRES.get(ch, {"label": "Inconnu"})["label"]
            print(f"    {ch} ({label}) : {n}")
    print("\n  Par niveau Bloom :")
    labels = {1:"التذكر",2:"الفهم",3:"التطبيق",4:"التحليل",5:"التأليف"}
    for n, count in output["stats"]["par_bloom"].items():
        if count > 0:
            print(f"    L{n} {labels[n]} : {count}")

# ─── MAIN ─────────────────────────────────────────────────────

if __name__ == "__main__":
    output = normaliser_corpus("annales_sciences_3as.json")
    sauvegarder(output)
