"""
append_annales.py — Ingestion sécurisée dans le corpus BAC
Usage : python append_annales.py
"""

import json
import os
import sys
import shutil
from pathlib import Path
from datetime import datetime

# ═══ CONFIGURATION ══════════════════════════════════════════════

# Résolution dynamique — fonctionne partout (Windows, Linux, Docker)
DATA_DIR = Path(
    os.environ.get('KHAWARIZMI_DATA_DIR')
    or Path(__file__).parent.parent
)
FILEPATH = DATA_DIR / 'annales_maths_3as.json'


# ═══ VALIDATION ═════════════════════════════════════════════════

CHAMPS_REQUIS_SUJET = {'id', 'annee', 'filiere', 'questions'}
CHAMPS_REQUIS_QUESTION = {'id', 'texte', 'micro_concept_id'}

def valider_sujet(sujet: dict) -> list:
    """Retourne la liste des erreurs de structure."""
    erreurs = []

    manquants = CHAMPS_REQUIS_SUJET - set(sujet.keys())
    if manquants:
        erreurs.append(f"Champs manquants dans le sujet : {manquants}")

    if 'questions' in sujet:
        for i, q in enumerate(sujet['questions']):
            manquants_q = CHAMPS_REQUIS_QUESTION - set(q.keys())
            if manquants_q:
                erreurs.append(
                    f"Question {i} ({q.get('id','?')}) : "
                    f"champs manquants {manquants_q}"
                )

    return erreurs


# ═══ INGESTION SÉCURISÉE ════════════════════════════════════════

def ajouter_sujets(nouveaux_sujets: list, filepath: Path = FILEPATH) -> bool:
    """
    Ajoute des sujets au corpus avec :
    - Détection des doublons
    - Validation de structure
    - Backup automatique avant écriture
    """

    # ── 1. Charger le fichier existant ──────────────────────────
    if not filepath.exists():
        print(f"[ERREUR] Fichier introuvable : {filepath}")
        return False

    with open(filepath, 'r', encoding='utf-8') as f:
        data = json.load(f)

    ids_existants = {s['id'] for s in data.get('sujets', [])}
    print(f"[INFO] Corpus actuel : {len(ids_existants)} sujets")

    # ── 2. Valider + filtrer les doublons ───────────────────────
    a_ajouter = []
    for sujet in nouveaux_sujets:
        sujet_id = sujet.get('id', 'SANS_ID')

        # Vérifier doublons
        if sujet_id in ids_existants:
            print(f"[SKIP] Doublon ignoré : {sujet_id}")
            continue

        # Valider structure
        erreurs = valider_sujet(sujet)
        if erreurs:
            print(f"[ERREUR] Sujet {sujet_id} invalide :")
            for e in erreurs:
                print(f"   → {e}")
            continue

        a_ajouter.append(sujet)
        print(f"[OK] Sujet validé : {sujet_id}")

    if not a_ajouter:
        print("[INFO] Aucun nouveau sujet à ajouter.")
        return True

    # ── 3. Backup avant écriture ────────────────────────────────
    backup_path = filepath.with_suffix(
        f'.backup_{datetime.now().strftime("%Y%m%d_%H%M%S")}.json'
    )
    shutil.copy2(filepath, backup_path)
    print(f"[BACKUP] Sauvegarde créée : {backup_path.name}")

    # ── 4. Ajouter et sauvegarder ───────────────────────────────
    data['sujets'].extend(a_ajouter)

    with open(filepath, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

    print(f"\n[SUCCÈS] {len(a_ajouter)} sujet(s) ajouté(s)")
    print(f"[INFO] Total corpus : {len(data['sujets'])} sujets")

    # Compter les questions totales
    nb_questions = sum(len(s.get('questions', [])) for s in data['sujets'])
    print(f"[INFO] Total questions : {nb_questions}")

    return True


# ═══ DONNÉES À INJECTER ═════════════════════════════════════════

NOUVEAUX_SUJETS = [

    {
        "id":             "BAC_MATH_2024_SC_S1_EX2",
        "source":         "Annales - TVI et Limites",
        "annee":          2024,
        "filiere":        "Sciences Expérimentales",
        "session":        "Principale",
        "sujet":          1,
        "exercice":       2,
        "theme_principal":"CHAP_MATH_02",
        "points":         7.0,
        "enonce": (
            "On considère la fonction f définie sur R "
            "par f(x) = (x - 1)e^x + 1."
        ),
        "questions": [
            {
                "id":                    "Q1_a",
                "texte":                 "Calculer la limite de f en -infini.",
                "points":                0.5,
                "micro_concept_id":      "MC_FONC_03",
                "diagnostic_erreur_cible":"ERR_CC_EXEC_01",
                "note_pedagogique": (
                    "Vérifie si l'élève reconnaît la croissance comparée "
                    "x*e^x → 0 en -infini."
                ),
            },
            {
                "id":                    "Q1_b",
                "texte":                 "Calculer la limite de f en +infini.",
                "points":                0.5,
                "micro_concept_id":      "MC_FONC_03",
                "diagnostic_erreur_cible":"ERR_CC_METH_01",
                "note_pedagogique":      "Limite +infini * +infini.",
            },
            {
                "id":                    "Q2_a",
                "texte":                 "Montrer que f'(x) = x*e^x.",
                "points":                1.0,
                "micro_concept_id":      "MC_FONC_05",
                "diagnostic_erreur_cible":"ERR_DERIV_EXEC_01",
                "note_pedagogique":      "Dérivée du produit (u'v + uv').",
            },
            {
                "id":                    "Q2_b",
                "texte": (
                    "Étudier le signe de f'(x) et dresser "
                    "le tableau de variations."
                ),
                "points":                1.0,
                "micro_concept_id":      "MC_FONC_06",
                "diagnostic_erreur_cible":"ERR_TAB_METH_01",
                "note_pedagogique":      "L'élève doit justifier e^x > 0.",
            },
            {
                "id":                    "Q3",
                "texte": (
                    "Montrer que f(x) = 0 admet une unique solution "
                    "alpha dans [-1.5; -1.2]."
                ),
                "points":                1.0,
                "micro_concept_id":      "MC_FONC_04",
                "diagnostic_erreur_cible":"ERR_TVI_METH_01",
                "note_pedagogique": (
                    "3 mots-clés : Continue, Strictement décroissante, "
                    "f(-1.5)*f(-1.2) < 0."
                ),
            },
        ],
    },

    {
        "id":             "BAC_MATH_2024_SC_S1_EX3",
        "source":         "Annales - Nombres Complexes",
        "annee":          2024,
        "filiere":        "Sciences Expérimentales",
        "session":        "Principale",
        "sujet":          1,
        "exercice":       3,
        "theme_principal":"CHAP_MATH_03",
        "points":         5.0,
        "enonce": (
            "Plan complexe repère orthonormé direct. "
            "zA = -1+i, zB = 2+2i, zC = 1-2i."
        ),
        "questions": [
            {
                "id":                    "Q1",
                "texte":                 "Résoudre dans C : z^2 - 4z + 13 = 0.",
                "points":                1.0,
                "micro_concept_id":      "MC_COMP_04",
                "diagnostic_erreur_cible":"ERR_EQ2_CONC_01",
                "note_pedagogique": (
                    "Si Delta < 0, rappeler que dans C "
                    "on remplace - par i^2."
                ),
            },
            {
                "id":                    "Q2_a",
                "texte": (
                    "Calculer (zC - zA)/(zB - zA) "
                    "sous forme algébrique."
                ),
                "points":                1.0,
                "micro_concept_id":      "MC_COMP_01",
                "diagnostic_erreur_cible":"ERR_ALG_METH_01",
                "note_pedagogique":      "Utilisation du conjugué.",
            },
            {
                "id":                    "Q2_b",
                "texte":                 "Déduire la nature du triangle ABC.",
                "points":                1.0,
                "micro_concept_id":      "MC_COMP_06",
                "diagnostic_erreur_cible":"ERR_RAP_METH_01",
                "note_pedagogique": (
                    "Module = 1 → isocèle. "
                    "Passer en forme trigonométrique."
                ),
            },
            {
                "id":                    "Q3",
                "texte": (
                    "Rotation R de centre A et d'angle -Pi/2 : "
                    "écriture complexe."
                ),
                "points":                1.0,
                "micro_concept_id":      "MC_COMP_07",
                "diagnostic_erreur_cible":"ERR_TRANS_EXEC_01",
                "note_pedagogique":      "e^(-i Pi/2) = -i.",
            },
        ],
    },
]


# ═══ EXÉCUTION ════════════════════════════════════════════════════

if __name__ == "__main__":
    print("=" * 55)
    print("  KHAWARIZMI — INGESTION CORPUS MATHS")
    print("=" * 55)
    print(f"[DIR] {FILEPATH}")

    succes = ajouter_sujets(NOUVEAUX_SUJETS)
    sys.exit(0 if succes else 1)
