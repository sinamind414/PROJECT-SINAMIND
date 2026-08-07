"""tests/golden/build_golden_annotated.py — Génère golden_annotated.json.

⚠️ Annotations SYNTHÉTIQUES déterministes (approche B du plan) : en l'absence
d'expert SVT disponible pour annoter 50 copies (approche A, 2-3 h), le score
humain est défini par CONSTRUCTION à partir des mots-clés attendus du golden
set ONEC :

  - copie parfaite  = reponse_attendue (tous les mots-clés) → barème, all_correct
  - copie partielle = texte tronqué à ~55 % (limite de mot) → score = barème ×
    (mots-clés présents dans la troncature / total), dominant partial_correct
    ou insufficient
  - copie vide (1 item sur 2) → 0, empty (teste les vrais rejets sanity)

Le format est IDENTIQUE à l'annotation humaine du plan (human_score,
human_dominant_error, annotator, annotation_date) : il suffira de remplacer
annotator: "synthetic_keyword_v1" par "expert_svt" et les scores humains par
les vraies annotations — la mécanique de mesure ne change pas.

Usage :
    python tests/golden/build_golden_annotated.py
"""

from __future__ import annotations

import json
from pathlib import Path

GOLDEN_ONEC = Path(__file__).parent.parent.parent / "data" / "golden_set_onec.json"
OUT = Path(__file__).parent / "golden_annotated.json"

ANNOTATOR = "synthetic_keyword_v1"
ANNOTATION_DATE = "2026-08-07"


def _truncate_to_word(text: str, ratio: float) -> str:
    """Tronque à `ratio` du texte, à la limite du dernier mot complet."""
    cut = int(len(text) * ratio)
    head = text[:cut]
    if " " in head:
        head = head.rpartition(" ")[0]
    return head


def _strip_article(word: str) -> str:
    """Retire l'article arabe défini 'ال' en tête de mot (len > 4).

    Le golden set ONEC liste des mots-clés canoniques ('حرارة مثلى') que la
    reponse_attendue écrit sous forme définie ('الحرارة المثلى') — le matching
    d'annotation doit tolérer cette flexion, sinon des copies parfaites sont
    annotées avec des scores faux (artefact mesuré : gs_016 noté 4/4 humain
    mais 2/4 par le moteur à cause du littéral 'حرارة مثلى' absent).
    """
    w = word.strip()
    if w.startswith("ال") and len(w) > 4:
        return w[2:]
    return w


def _strip_articles(text: str) -> str:
    """Normalise TOUS les mots du texte (l'article peut être n'importe où)."""
    return " ".join(_strip_article(w) for w in text.split())


def _kw_present(keyword: str, text: str) -> bool:
    """Mot-clé présent dans le texte (tolérance à l'article défini)."""
    return _strip_articles(keyword) in _strip_articles(text)


def _dominant_for(human_score: int, bareme: int) -> str:
    if human_score >= bareme:
        return "all_correct"
    if human_score > 0:
        return "partial_correct"
    return "insufficient"


def _kw_present_list(keywords: list[str], text: str) -> list[str]:
    """Mots-clés présents dans une copie (définition unique d'annotation)."""
    return [k for k in keywords if _kw_present(k, text)]


def build() -> list[dict]:
    data = json.loads(GOLDEN_ONEC.read_text(encoding="utf-8"))
    items: list[dict] = []

    for q in data["questions"]:
        # Copie parfaite (réponse modèle) — score = proportion réelle de
        # mots-clés présents (certains mots-clés du golden ne figurent pas
        # littéralement dans la réponse modèle : l'annotation doit le refléter)
        items.append(_annot_item(q, q.get("reponse_attendue", "")))

        # Copie partielle : troncature → seuls les mots-clés du début restent
        partial = _truncate_to_word(q.get("reponse_attendue", ""), 0.55)
        if partial and partial != q.get("reponse_attendue", ""):
            items.append(_annot_item(q, partial))

        # Copie vide (1 item sur 2) → vrai rejet sanity attendu
        if str(q["id"]).endswith(("1", "3", "5", "7", "9")):
            items.append(_annot_item(q, "", code_override="empty"))

    return items


def _annot_item(q: dict, copy: str, code_override: str | None = None) -> dict:
    """Définition unique : human_score = barème × proportion de mots-clés
    présents dans la copie (parfaite, partielle ou vide)."""
    bareme = int(q.get("bareme", 2))
    keywords = list(q.get("mots_cles_attendus", []) or [])
    present = _kw_present_list(keywords, copy)
    human = round(bareme * len(present) / max(1, len(keywords)))
    code = code_override or _dominant_for(human, bareme)
    return {
        "question_id": q["id"],
        "verb_slug": q.get("type", "restitution"),
        "chapitre": q.get("chapitre", ""),
        "question": q.get("question", ""),
        "student_answer": copy,
        "bareme": bareme,
        "reponse_attendue": q.get("reponse_attendue", ""),
        "mots_cles_attendus": keywords,
        "human_score": human,
        "human_score_max": bareme,
        "human_dominant_error": code,
        "human_matched_criteria": present,
        "human_unmatched_criteria": [k for k in keywords if k not in present],
        "annotator": ANNOTATOR,
        "annotation_date": ANNOTATION_DATE,
    }


if __name__ == "__main__":
    items = build()
    OUT.write_text(
        json.dumps({
            "metadata": {
                "source": "golden_set_onec.json (ONEC Bac SVT)",
                "annotation_type": "synthetic_keyword_based",
                "annotator": ANNOTATOR,
                "date": ANNOTATION_DATE,
                "note": "Approche B — remplacer par annotations expert_svt "
                        "(même format) quand disponible",
            },
            "items": items,
        }, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )
    print(f"✅ {len(items)} items annotés → {OUT}")
