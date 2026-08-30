#!/usr/bin/env python3
"""Valide les grilles L0 : G5 model ≥ 85 % + goldens négatifs + counter_examples.

Sortie ≠ 0 si une grille est sourde OU sur-note le faux. Bloque le merge.
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

BACKEND = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(BACKEND))

from services.lexicon import in_file  # noqa: E402
from services.local_grader import grade  # noqa: E402
from services.rubric_store import data_dir, list_question_ids, load  # noqa: E402

# Mêmes copies que tests/golden/test_rubric_l0.py — pas de سلم inventé.
GEOLOGY = (
    "تمثل الوثيقة منحنى تباعد الصفائح عند الأعراف المحيطية. "
    "كلما ابتعدت الصفيحة ازداد الخندق المحيطي. نستنتج غوص اللوح في الاندساس."
)
ATP36 = " وتنتج الخلية 36 ATP في التنفس الهوائي."
_ALLOWED_USE = {"model+atp36"}
_ALLOWED_AXIS = {"overall", "method"}


def _unknown_lex(r) -> list[str]:
    unknown: list[str] = []
    blobs: list[str] = list(r.theme_variants)
    for c in r.criteria:
        blobs.extend(c.variants)
    for v in blobs:
        if v.startswith("$lex:"):
            key = v[5:].strip()
            if not in_file(key):
                unknown.append(v)
    return unknown


def _check_counter_examples(qid: str, packed, r) -> list[str]:
    """S20 — ≥2 contre-exemples git, dont off_topic. Jamais exposés par GET."""
    fails: list[str] = []
    path = data_dir() / packed.rubric_path
    try:
        raw = json.loads(path.read_text(encoding="utf-8"))
    except Exception as e:
        return [f"{qid}: JSON illisible ({e})"]
    examples = raw.get("counter_examples")
    if not isinstance(examples, list) or len(examples) < 2:
        return [f"{qid}: counter_examples < 2 (gate négatif auteur)"]
    ids = [str(x.get("id") or "") for x in examples if isinstance(x, dict)]
    if "off_topic" not in ids:
        fails.append(f"{qid}: manque counter_example id=off_topic")
    for i, ex in enumerate(examples):
        if not isinstance(ex, dict):
            fails.append(f"{qid}: counter_examples[{i}] pas un objet")
            continue
        eid = str(ex.get("id") or f"#{i}")
        axis = str(ex.get("axis") or "overall")
        if axis not in _ALLOWED_AXIS:
            fails.append(f"{qid}:{eid}: axis={axis} interdit")
            continue
        try:
            cap = int(ex.get("max_percent"))
        except (TypeError, ValueError):
            fails.append(f"{qid}:{eid}: max_percent manquant")
            continue
        use = ex.get("use")
        text = ex.get("text_ar")
        if use:
            if use not in _ALLOWED_USE:
                fails.append(f"{qid}:{eid}: use={use} hors liste fermée")
                continue
            student = r.model_answer + ATP36 if use == "model+atp36" else ""
        elif isinstance(text, str) and text.strip():
            student = text
        else:
            fails.append(f"{qid}:{eid}: ni text_ar ni use")
            continue
        got = grade(student_answer=student, rubric=r, document=packed.document)
        score = (
            got.overall_training_percent if axis == "overall" else got.method_percent
        )
        if score > cap:
            fails.append(
                f"{qid}:{eid}: {axis}={score} > max_percent={cap} "
                f"science={got.science_status}"
            )
    return fails


def check_question(qid: str) -> list[str]:
    """Erreurs bloquantes pour une grille. Vide = OK."""
    fails: list[str] = []
    packed = load(qid)
    if packed is None:
        return [f"{qid}: ungraded"]
    r = packed.rubric
    unknown = _unknown_lex(r)
    if unknown:
        fails.append(f"{qid}: $lex: hors fichier {unknown}")
    if r.verb_slug == "analyse" and packed.document is None:
        fails.append(f"{qid}: analyse sans DocumentModel")
    if not r.model_answer.strip():
        fails.append(f"{qid}: model_answer vide")
        return fails

    model = grade(
        student_answer=r.model_answer,
        rubric=r,
        document=packed.document,
    )
    if model.method_percent < 85:
        fails.append(
            f"{qid}: G5 sourde method={model.method_percent}% "
            f"({model.method_points}/{model.method_points_max})"
        )
    if model.science_status != "ok":
        fails.append(f"{qid}: G5 model science={model.science_status}")

    empty = grade(student_answer="", rubric=r, document=packed.document)
    if empty.method_percent != 0 or empty.sanity_code != "empty":
        fails.append(
            f"{qid}: vide noté method={empty.method_percent} sanity={empty.sanity_code}"
        )

    off = grade(student_answer=GEOLOGY, rubric=r, document=packed.document)
    if off.science_status != "error" or off.overall_training_percent > 40:
        fails.append(
            f"{qid}: hors-sujet overall={off.overall_training_percent} "
            f"science={off.science_status}"
        )

    fake = grade(
        student_answer=r.model_answer + ATP36,
        rubric=r,
        document=packed.document,
    )
    if fake.science_status != "error" or fake.overall_training_percent > 40:
        fails.append(
            f"{qid}: 36 ATP overall={fake.overall_training_percent} "
            f"science={fake.science_status} method={fake.method_percent}"
        )

    fails.extend(_check_counter_examples(qid, packed, r))
    return fails


def main() -> int:
    ids = list_question_ids()
    if not ids:
        print("FAIL: aucune rubric dans index.json", file=sys.stderr)
        return 1
    errors = 0
    for qid in ids:
        fails = check_question(qid)
        if fails:
            for line in fails:
                print(f"FAIL {line}")
            errors += len(fails)
            continue
        packed = load(qid)
        assert packed is not None
        result = grade(
            student_answer=packed.rubric.model_answer,
            rubric=packed.rubric,
            document=packed.document,
        )
        print(
            f"OK {qid} method={result.method_percent}% "
            f"({result.method_points}/{result.method_points_max}) "
            f"label={result.method_label_ar} science={result.science_status} "
            f"diag={result.diagnosis.code if result.diagnosis else '-'}"
        )
    if errors:
        print(f"\n{errors} échec(s) G5/négatifs/counter_examples.", file=sys.stderr)
        return 1
    print(f"\n{len(ids)} grilles valides (G5 + hors-sujet + 36 ATP + vide + counter_examples).")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
