"""scripts/validate_golden_annotations.py — Validation des annotations golden.

À lancer AVANT de livrer des annotations humaines (approche A) : vérifie la
cohérence de tests/golden/golden_annotated.json pour que la mécanique de
mesure (metrics.py, test_golden_local.py) fonctionne sans surprise.

Vérifications :
- champs requis présents (12) ;
- human_score entier dans [0, bareme] ;
- human_dominant_error ∈ codes valides ;
- human_matched/unmatched partitionnent mots_cles_attendus (tolérance ال) ;
- copie vide → code empty + score 0 ;
- copie == reponse_attendue → score = bareme.

Usage : python scripts/validate_golden_annotations.py
Sortie : liste des problèmes (ou "OK — N items valides"). Exit 1 si erreurs.
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

GOLDEN_ANNOTATED = Path(__file__).parent.parent / "tests" / "golden" / "golden_annotated.json"

REQUIRED_FIELDS = [
    "question_id", "verb_slug", "chapitre", "question", "student_answer",
    "bareme", "reponse_attendue", "mots_cles_attendus", "human_score",
    "human_score_max", "human_dominant_error", "annotator", "annotation_date",
]

VALID_CODES = {
    "scientific_error", "methodology_error", "off_topic", "partial_correct",
    "all_correct", "insufficient", "gibberish", "too_short", "empty",
    "not_arabic", "repeated_chars", "server_error", "unknown",
}


def _strip_article(word: str) -> str:
    w = word.strip()
    if w.startswith("ال") and len(w) > 4:
        return w[2:]
    return w


def _strip_articles(text: str) -> str:
    """Normalise TOUS les mots (même logique que build_golden_annotated)."""
    return " ".join(_strip_article(w) for w in text.split())


def _kw_present(keyword: str, text: str) -> bool:
    return _strip_articles(keyword) in _strip_articles(text)


def validate_item(item: dict, index: int) -> list[str]:
    """Retourne la liste des problèmes d'un item (vide si OK)."""
    problems: list[str] = []
    prefix = f"[item {index} q={item.get('question_id', '?')}]"

    for field in REQUIRED_FIELDS:
        if field not in item:
            problems.append(f"{prefix} champ requis absent: {field}")

    bareme = item.get("bareme")
    score = item.get("human_score")
    code = item.get("human_dominant_error")

    if isinstance(bareme, int) and isinstance(score, int):
        if not (0 <= score <= bareme):
            problems.append(f"{prefix} human_score {score} hors [0, {bareme}]")
    else:
        problems.append(f"{prefix} bareme/human_score non entiers")

    if code not in VALID_CODES:
        problems.append(f"{prefix} code invalide: {code!r}")

    # Copie == réponse modèle → score = bareme (par définition)
    answer = item.get("student_answer") or ""
    if answer and answer == item.get("reponse_attendue"):
        if score != bareme:
            problems.append(
                f"{prefix} copie == modèle mais score={score} (attendu {bareme})"
            )
        return problems  # la partition littérale ne s'applique pas (concept
        # exprimé autrement dans le modèle — tous les critères sont satisfaits)

    # Copie vide → empty + 0, sans exigence de partition (redondante : tous
    # les critères sont non satisfaits par définition)
    if not answer.strip():
        if code != "empty":
            problems.append(f"{prefix} copie vide mais code={code!r} (attendu empty)")
        if score != 0:
            problems.append(f"{prefix} copie vide mais score={score} (attendu 0)")
        return problems

    # Partition des mots-clés (tolérance ال) — copies PARTIELLES uniquement
    keywords = item.get("mots_cles_attendus") or []
    matched = set(item.get("human_matched_criteria") or [])
    unmatched = set(item.get("human_unmatched_criteria") or [])

    for kw in keywords:
        present = _kw_present(kw, answer)
        in_matched = any(_strip_article(kw) == _strip_article(m) for m in matched)
        in_unmatched = any(_strip_article(kw) == _strip_article(u) for u in unmatched)
        if present and not in_matched:
            problems.append(f"{prefix} mot-clé présent '{kw}' absent de matched")
        if not present and in_matched:
            problems.append(f"{prefix} mot-clé absent '{kw}' présent dans matched")
        if present and in_unmatched:
            problems.append(f"{prefix} mot-clé présent '{kw}' dans unmatched")
        if not present and not in_unmatched:
            problems.append(f"{prefix} mot-clé absent '{kw}' ni dans unmatched")

    return problems


def main() -> int:
    if not GOLDEN_ANNOTATED.exists():
        print(f"❌ {GOLDEN_ANNOTATED} absent — lancez d'abord "
              "tests/golden/build_golden_annotated.py")
        return 1

    data = json.loads(GOLDEN_ANNOTATED.read_text(encoding="utf-8"))
    items = data.get("items", data if isinstance(data, list) else [])
    problems: list[str] = []
    for i, item in enumerate(items):
        problems.extend(validate_item(item, i))

    if problems:
        print(f"❌ {len(problems)} problème(s) sur {len(items)} items :")
        for p in problems[:20]:
            print(f"  - {p}")
        if len(problems) > 20:
            print(f"  … et {len(problems) - 20} autres")
        return 1

    print(f"✅ OK — {len(items)} items valides (annotator="
          f"{items[0].get('annotator') if items else '?'})")
    return 0


if __name__ == "__main__":
    sys.exit(main())
