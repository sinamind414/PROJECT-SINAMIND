"""
test_simulateur.py — Simulateur du moteur pédagogique Khawarizmi
Usage : python test_simulateur.py
        KHAWARIZMI_DATA_DIR=/path/to/data python test_simulateur.py
"""

import os
import sys
import json
from pathlib import Path
from services.khawarizmi_engine import KhawarizmiTutor

# ═══ HELPERS ════════════════════════════════════════════════════

def safe_print(text: str):
    """Affichage UTF-8 robuste (Windows + Arabic)."""
    try:
        sys.stdout.buffer.write(text.encode('utf-8') + b'\n')
        sys.stdout.buffer.flush()
    except Exception:
        print(text)


def valider_input(student_input: str) -> tuple[bool, str]:
    if not student_input or not student_input.strip():
        return False, "L'input de l'élève est vide."
    if len(student_input) > 5000:
        return False, "L'input est trop long (max 5000 caractères)."
    if len(student_input.strip()) < 5:
        return False, "L'input est trop court pour être une réponse."
    return True, ""


def compter_questions(annales: dict) -> int:
    """
    Compte les questions dans les deux structures JSON possibles.
    Structure A : sujet.questions (liste plate)
    Structure B : sujet.exercices[].questions (hiérarchique)
    """
    total = 0
    for sujet in annales.get('sujets', []):
        # Structure A
        total += len(sujet.get('questions', []))
        # Structure B
        for ex in sujet.get('exercices', []):
            total += len(ex.get('questions', []))
            total += len(ex.get('sous_questions', []))
    return total


def resoudre_data_dir() -> str:
    """
    Résolution du data_dir dans l'ordre de priorité :
    1. Variable d'environnement KHAWARIZMI_DATA_DIR
    2. Dossier parent (structure projet standard)
    3. Dossier data/ local
    """
    # Priorité 1
    data_dir = os.environ.get('KHAWARIZMI_DATA_DIR')
    if data_dir:
        return data_dir

    # Priorité 2 : dossier parent du fichier actuel
    parent = Path(__file__).parent.parent.resolve()
    if (parent / 'programme_maths_3as.json').exists():
        return str(parent)

    # Priorité 3 : sous-dossier data/
    local_data = Path(__file__).parent / 'data'
    return str(local_data)


# ═══ SCÉNARIOS ══════════════════════════════════════════════════

SCENARIOS = [
    {
        'nom':         'Probabilités — Somme ≠ 1 (TYPE_3)',
        'sujet_id':    'BAC_MATH_2024_SC_S1_EX4',
        'question_id': 'Q3_b',
        'input': (
            "J'ai fait le tableau, pour P(X=0) je trouve 1/35, "
            "P(X=1) = 12/35, P(X=2) = 15/35, P(X=3) = 6/35. "
            "Mais je sais pas si c'est bon."
        ),
        'erreur_attendue': 'TYPE_3',
        # Vérification : 1+12+15+6 = 34 ≠ 35 → manque 1/35
    },
    {
        'nom':         'Récurrence — Hérédité oubliée (TYPE_4)',
        'sujet_id':    'BAC_MATH_2024_SC_S1_EX1',
        'question_id': 'Q1',
        'input': (
            "Pour n=0 on a U0=1 donc c'est vrai. "
            "Ensuite on suppose que Un est entre 0 et 1. "
            "La limite est 1 donc c'est bon."
        ),
        'erreur_attendue': 'TYPE_4',
        # Vérification : oublie l'étape d'hérédité
    },
]


# ═══ MAIN ════════════════════════════════════════════════════════

def main():

    # ── Header ─────────────────────────────────────────────────
    safe_print("=" * 60)
    safe_print("   KHAWARIZMI — SIMULATEUR PÉDAGOGIQUE")
    safe_print("=" * 60)

    # ── Résolution data_dir ────────────────────────────────────
    data_dir = resoudre_data_dir()
    safe_print(f"[DIR] Data dir : {data_dir}")

    if not os.path.exists(data_dir):
        safe_print(f"[ERREUR] Dossier introuvable : {data_dir}")
        safe_print("   Définis KHAWARIZMI_DATA_DIR dans ton .env")
        sys.exit(1)

    # ── Chargement ─────────────────────────────────────────────
    safe_print("[WAIT] Chargement de la base de données...")
    try:
        tutor = KhawarizmiTutor(data_dir=data_dir)
    except FileNotFoundError as e:
        safe_print(f"[ERREUR] Fichier JSON manquant : {e}")
        sys.exit(1)
    except Exception as e:
        safe_print(f"[ERREUR] Chargement échoué : {e}")
        sys.exit(1)

    # ── Statistiques ───────────────────────────────────────────
    nb_chapitres    = len(tutor.programme_maths.get('chapitres', []))
    nb_sujets       = len(tutor.annales_maths.get('sujets', []))
    nb_questions    = compter_questions(tutor.annales_maths)
    nb_micro_concepts = len(tutor._index_micro_concepts)

    safe_print(f"[OK] {nb_chapitres} chapitres chargés")
    safe_print(f"[OK] {nb_sujets} sujets BAC chargés")
    safe_print(f"[OK] {nb_questions} questions indexées")
    safe_print(f"[OK] {nb_micro_concepts} micro-concepts indexés")
    safe_print("-" * 60)

    # ── Scénarios ──────────────────────────────────────────────
    for i, scenario in enumerate(SCENARIOS, 1):

        safe_print(f"\n{'='*60}")
        safe_print(f"   SCÉNARIO {i} : {scenario['nom']}")
        safe_print(f"{'='*60}")
        safe_print(f"[SUJET]    {scenario['sujet_id']}")
        safe_print(f"[QUESTION] {scenario['question_id']}")
        safe_print(f"[RÉPONSE]  {scenario['input']}")

        # Validation input
        is_valid, err_msg = valider_input(scenario['input'])
        if not is_valid:
            safe_print(f"[ERREUR] Input invalide : {err_msg}")
            continue

        # Pré-analyse sans IA
        safe_print("\n[PROCESS] Pré-analyse (sans IA)...")
        pre_analyse = tutor.pre_analyser_sans_ia(
            scenario['sujet_id'],
            scenario['question_id'],
            scenario['input']
        )

        if pre_analyse:
            erreur_ok = pre_analyse['type_erreur'] == scenario.get('erreur_attendue')
            safe_print(f"   → {pre_analyse['diagnostic']}")
            safe_print(f"   → Type détecté : {pre_analyse['type_erreur']} "
                      f"({'✅' if erreur_ok else '❌ attendu: ' + scenario.get('erreur_attendue', '?')})")
            safe_print(f"   → Économie : {pre_analyse.get('economie_tokens', 0)} tokens")
        else:
            safe_print("   → Aucune erreur détectée par pré-analyse")

        # Construction prompt
        safe_print("\n[PROMPT] Construction du prompt socratique...")
        try:
            prompt = tutor.build_system_prompt(
                sujet_id      = scenario['sujet_id'],
                question_id   = scenario['question_id'],
                student_input = scenario['input'],
                pre_analyse   = pre_analyse,
            )
            safe_print(f"   → {len(prompt)} caractères générés")
            safe_print(f"\n--- APERÇU (400 chars) ---")
            safe_print(prompt[:400] + "...")

        except ValueError as e:
            safe_print(f"[ERREUR] Introuvable : {e}")
            continue

        # Appel IA optionnel
        _appel_ia_optionnel(prompt, scenario['input'])

    safe_print(f"\n{'='*60}")
    safe_print("   FIN DES TESTS — Pipeline opérationnel ✅")
    safe_print(f"{'='*60}")


def _appel_ia_optionnel(prompt: str, student_input: str):
    """Appel OpenAI si clé API valide disponible."""
    api_key = os.environ.get('OPENAI_API_KEY', '')

    # Validation clé API plus robuste
    if not api_key or len(api_key) < 20 or api_key in ('sk-...', 'METTRE_TA_CLE_ICI'):
        safe_print(
            "\n[INFO] Appel IA ignoré — Définis OPENAI_API_KEY "
            "dans .env pour tester l'appel réel."
        )
        return

    safe_print("\n[IA] Appel OpenAI en cours...")
    try:
        from openai import OpenAI
        client = OpenAI(api_key=api_key)

        response = client.chat.completions.create(
            model           = 'gpt-4o-mini',
            messages        = [
                {'role': 'system', 'content': prompt},
                {'role': 'user',   'content': student_input}
            ],
            temperature     = 0.2,
            max_tokens      = 500,
            response_format = {'type': 'json_object'},
        )

        content = response.choices[0].message.content
        safe_print("\n[IA] Réponse Khawarizmi (JSON) :")
        safe_print("-" * 40)

        # Pretty print JSON
        try:
            parsed = json.loads(content)
            safe_print(json.dumps(parsed, ensure_ascii=False, indent=2))
        except json.JSONDecodeError:
            safe_print(content)

        safe_print("-" * 40)
        safe_print(
            f"[MÉTRIQUES] "
            f"tokens={response.usage.total_tokens} | "
            f"coût≈${response.usage.total_tokens * 0.00000015:.6f}"
        )

    except Exception as e:
        safe_print(f"[ERREUR] Appel OpenAI échoué : {e}")


if __name__ == "__main__":
    main()
