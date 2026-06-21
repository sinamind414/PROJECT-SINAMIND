#!/usr/bin/env python3
"""
Validation des tags pour le pipeline Annales SVT.

Vérifie, pour chaque question de output/questions_taggees.json :
  - micro_concept_id   ∈ {42 concepts autorisés}
  - secondary_concepts ∈ {42 concepts autorisés} (0 à 2 max)
  - presence des champs obligatoires
  - coherence bac_frequent avec le concept principal

Usage :
    python3 annales_svt/scripts/validate_tags.py
"""
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
REF_PATH = ROOT / "referentiel" / "micro_concepts.json"
OUT_PATH = ROOT / "output" / "questions_taggees.json"

REQUIRED_FIELDS = [
    "id", "texte_corrige", "micro_concept_id", "secondary_concepts",
    "source", "type", "difficulte", "bac_frequent", "notes",
]
VALID_TYPES = {
    "analyse_document", "definition", "qcm", "vraix_faux",
    "completion", "schema_a_completer", "raisonnement", "comparaison",
    "application", "ouverture", "autre",
}
VALID_DIFF = {"facile", "moyenne", "difficile"}


def load_json(path: Path):
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


def main() -> int:
    ref = load_json(REF_PATH)
    valid_ids = {c["id"] for c in ref["concepts"]}
    id_to_bac = {c["id"]: c["bac"] for c in ref["concepts"]}

    if not OUT_PATH.exists():
        print(f"[ERR] Fichier de sortie introuvable : {OUT_PATH}")
        return 1

    questions = load_json(OUT_PATH)
    if not isinstance(questions, list):
        print("[ERR] Le fichier de sortie doit être une liste JSON.")
        return 1

    errors = []
    warnings = []
    stats = {}

    for i, q in enumerate(questions):
        ctx = f"question #{i} (id={q.get('id', '?')})"

        # Champs obligatoires
        for field in REQUIRED_FIELDS:
            if field not in q:
                errors.append(f"{ctx}: champ manquant '{field}'")

        # Concept principal
        mc = q.get("micro_concept_id")
        if mc not in valid_ids and not str(mc).startswith("mc_xxx"):
            errors.append(f"{ctx}: micro_concept_id invalide -> {mc}")
        else:
            stats[mc] = stats.get(mc, 0) + 1

        # Concepts secondaires (0 à 2)
        sec = q.get("secondary_concepts", [])
        if not isinstance(sec, list):
            errors.append(f"{ctx}: secondary_concepts doit être une liste")
        else:
            if len(sec) > 2:
                warnings.append(f"{ctx}: {len(sec)} concepts secondaires (>2 conseillé)")
            for s in sec:
                if s not in valid_ids and not str(s).startswith("mc_xxx"):
                    errors.append(f"{ctx}: concept secondaire invalide -> {s}")

        # Cohérence bac_frequent
        if mc in id_to_bac and q.get("bac_frequent") is not id_to_bac[mc]:
            # info seulement : bac_frequent reflète la fréquence réelle au bac,
            # pas forcément le drapeau du concept. On warning.
            warnings.append(
                f"{ctx}: bac_frequent={q.get('bac_frequent')} alors que le concept "
                f"{mc} a bac={id_to_bac[mc]} (à vérifier si volontaire)"
            )

        # Type / difficulté
        if q.get("type") and q["type"] not in VALID_TYPES:
            warnings.append(f"{ctx}: type non standard -> {q['type']}")
        if q.get("difficulte") and q["difficulte"] not in VALID_DIFF:
            warnings.append(f"{ctx}: difficulté non standard -> {q['difficulte']}")

        # a_verifier
        if q.get("a_verifier"):
            warnings.append(f"{ctx}: a_verifier=true (concept à confirmer)")

    # Rapport
    print("=" * 60)
    print("RAPPORT DE VALIDATION DES TAGS")
    print("=" * 60)
    print(f"Total questions : {len(questions)}")
    print(f"Concepts distincts utilisés : {len(stats)}")
    print(f"Erreurs : {len(errors)}  |  Avertissements : {len(warnings)}")
    print("-" * 60)
    if errors:
        print("\nERREURS :")
        for e in errors:
            print("  ✗", e)
    if warnings:
        print("\nAVERTISSEMENTS :")
        for w in warnings:
            print("  ⚠", w)
    print("-" * 60)
    print("\nDistribution des micro-concepts :")
    for cid, n in sorted(stats.items(), key=lambda x: -x[1]):
        label = next((c["fr"] for c in ref["concepts"] if c["id"] == cid), cid)
        print(f"  {n:>3}  {cid:<14} {label}")

    return 1 if errors else 0


if __name__ == "__main__":
    sys.exit(main())
