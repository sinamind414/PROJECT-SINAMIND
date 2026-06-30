#!/usr/bin/env python3
"""
Test du moteur pédagogique optimisé — 5 cas BAC SVT
Mesure : taille prompt, qualité pédagogique, stabilité JSON.
"""
import json
import sys
import os
import time

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from services.khawarizmi_engine import get_tutor

DATA_DIR = os.path.join(os.path.dirname(__file__), "..", "data")

# ── Cas de test avec vrais IDs ─────────────────────────────
TEST_CASES = [
    {
        "name": "Cas 1 — Erreur de concept (protéines)",
        "sujet_id": "sujet_1_bac_blanc",
        "question_id": "q1_tableau",
        "student_input": "Les protéines sont des molécules qui servent à stocker l'énergie dans les cellules",
        "pre_analyse": None,
        "niveau_sm2": 2,
        "score_actuel": 5.0,
        "mode_force": None,
        "calendar_context": {
            "days_to_bac": 45,
            "phase": "Phase de consolidation",
            "user_stats": {"mastered": 12, "total": 25, "avg_stability": 1.5},
        },
    },
    {
        "name": "Cas 2 — Erreur de méthode (kowached)",
        "sujet_id": "sujet_1_bac_blanc",
        "question_id": "q1_reaction",
        "student_input": "Le test de Biuret donne une couleur violette car les protéines réagissent avec le cuivre",
        "pre_analyse": {
            "type_erreur": "TYPE_2",
            "message": "L'élève utilise un raisonnement séquentiel sans structure de document",
        },
        "niveau_sm2": 3,
        "score_actuel": 7.0,
        "mode_force": "FEYNMAN",
        "calendar_context": None,
    },
    {
        "name": "Cas 3 — Erreur d'exécution (cellule)",
        "sujet_id": "sujet_3_bac_blanc",
        "question_id": "q1_cycle_cellulaire",
        "student_input": "La mitose se déroule en 4 phases : prophase, métaphase, anaphase, télophase. L'ADN est répliqué pendant l'interphase.",
        "pre_analyse": {
            "type_erreur": "TYPE_3",
            "message": "Élément pertinent de l'analyse non utilisé, erreur de manipulation",
        },
        "niveau_sm2": 4,
        "score_actuel": 8.5,
        "mode_force": "ANNALES_COMPLEXES",
        "calendar_context": {
            "days_to_bac": 10,
            "phase": "Phase Sprint final",
            "user_stats": {"mastered": 18, "total": 22, "avg_stability": 2.0},
        },
    },
    {
        "name": "Cas 4 — Bon élève (ADN)",
        "sujet_id": "sujet_3_bac_blanc",
        "question_id": "q2_interpretation_adn",
        "student_input": "La transcription est le processus par lequel l'ADN est copié en ARNm. L'ARN polymérase se fixe sur le promoteur et synthétise l'ARNm complémentaire.",
        "pre_analyse": {
            "type_erreur": "TYPE_0",
            "message": "Réponse correcte — rien à signaler",
        },
        "niveau_sm2": 5,
        "score_actuel": 10.0,
        "mode_force": "RAPPEL_ACTIF",
        "calendar_context": {
            "days_to_bac": 2,
            "phase": "Phase Sprint final",
            "user_stats": {"mastered": 22, "total": 22, "avg_stability": 3.5},
        },
    },
    {
        "name": "Cas 5 — Élève fragile (révision)",
        "sujet_id": "revision_605_questions",
        "question_id": "q_46",
        "student_input": "euh... c'est quand l'ADN se réplique je crois",
        "pre_analyse": None,
        "niveau_sm2": 1,
        "score_actuel": 3.0,
        "mode_force": None,
        "calendar_context": {
            "days_to_bac": 60,
            "phase": "Phase Initiation",
            "user_stats": {"mastered": 3, "total": 15, "avg_stability": 0.5},
        },
    },
]


def count_tokens_approx(text: str) -> int:
    return len(text) // 4


def check_solution_leak(prompt: str) -> list:
    leaks = []
    for forbidden in [
        "SOLUTION OFFICIELLE",
        'json.dumps(question.get("solution"',
        "La bonne réponse est",
        "Réponse correcte :",
    ]:
        if forbidden in prompt:
            leaks.append(forbidden)
    return leaks


def check_pedagogical_quality(prompt: str) -> dict:
    checks = {
        "langue_arabe": "arabe" in prompt.lower() or "العربية" in prompt,
        "socratique": "question" in prompt.lower() or "SOCRATIQUE" in prompt,
        "minhajiya": "MINHAJIYA" in prompt or "ANALYSER" in prompt.upper(),
        "mode_pedagogique": "MODE PÉDAGOGIQUE" in prompt or "MODE PEDAGOGIQUE" in prompt,
        "contexte_bac": "BAC" in prompt,
        "micro_concept": "Micro-concept" in prompt,
        "type_erreur": "Type d'erreur" in prompt,
        "erreurs_frequentes": "ERREURS FRÉQUENTES" in prompt,
        "pas_solution_directe": "Ne révèle jamais la solution" in prompt or "ne donne jamais" in prompt.lower(),
    }
    return checks


def run_tests():
    tutor = get_tutor(DATA_DIR)
    results = []

    for i, tc in enumerate(TEST_CASES):
        print(f"\n{'='*60}")
        print(f"  {tc['name']}")
        print(f"{'='*60}")

        try:
            prompt = tutor.build_system_prompt(
                sujet_id=tc["sujet_id"],
                question_id=tc["question_id"],
                student_input=tc["student_input"],
                pre_analyse=tc["pre_analyse"],
                niveau_sm2=tc["niveau_sm2"],
                score_actuel=tc["score_actuel"],
                mode_force=tc["mode_force"],
                calendar_context=tc["calendar_context"],
            )
        except Exception as e:
            print(f"  ERREUR : {e}")
            continue

        prompt_chars = len(prompt)
        prompt_tokens = count_tokens_approx(prompt)
        leaks = check_solution_leak(prompt)
        quality = check_pedagogical_quality(prompt)

        print(f"  Taille prompt  : {prompt_chars} chars (~{prompt_tokens} tokens)")
        print(f"  Solutions leak : {'AUCUN' if not leaks else 'LEAK: ' + str(leaks)}")
        print(f"  Qualité pédago :")
        for k, v in quality.items():
            print(f"    {k}: {'V' if v else 'X'}")

        assert not leaks, f"SOLUTION LEAK dans {tc['name']}: {leaks}"

        results.append({
            "name": tc["name"],
            "prompt_chars": prompt_chars,
            "prompt_tokens": prompt_tokens,
            "quality_checks": quality,
        })

    print(f"\n{'='*60}")
    print("  RESUME DES TESTS")
    print(f"{'='*60}")
    total_chars = sum(r["prompt_chars"] for r in results)
    total_tokens = sum(r["prompt_tokens"] for r in results)
    avg_chars = total_chars // len(results)
    avg_tokens = total_tokens // len(results)

    print(f"  Taille moyenne  : {avg_chars} chars (~{avg_tokens} tokens)")
    print(f"  Taille totale   : {total_chars} chars (~{total_tokens} tokens)")

    all_quality = {}
    for r in results:
        for k, v in r["quality_checks"].items():
            if k not in all_quality:
                all_quality[k] = []
            all_quality[k].append(v)

    print(f"\n  Score qualité par critere :")
    perfect = 0
    for k, vals in all_quality.items():
        score = sum(vals) / len(vals) * 10
        mark = "V" if score == 10 else f"! {score:.0f}/10"
        print(f"    {k}: {mark}")
        if score == 10:
            perfect += 1

    total_checks = len(all_quality)
    global_score = perfect / total_checks * 10 if total_checks else 0
    print(f"\n  Score global : {global_score:.1f}/10 ({perfect}/{total_checks} criteres parfaits)")

    report = {
        "timestamp": time.strftime("%Y-%m-%d %H:%M:%S"),
        "engine_version": "2.0-optimized",
        "cases": results,
        "summary": {
            "avg_prompt_chars": avg_chars,
            "avg_prompt_tokens": avg_tokens,
            "total_cases": len(results),
            "global_quality_score": global_score,
        },
    }

    report_path = os.path.join(os.path.dirname(__file__), "test-results-optimized.json")
    with open(report_path, "w", encoding="utf-8") as f:
        json.dump(report, f, ensure_ascii=False, indent=2)
    print(f"\n  Rapport sauvegarde : {report_path}")

    return global_score >= 8.0


if __name__ == "__main__":
    success = run_tests()
    print(f"\n{'SUCCES' if success else 'ECHEC'} - Tests termines.")
    sys.exit(0 if success else 1)
