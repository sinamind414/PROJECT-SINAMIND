"""Générateur de squelettes de grilles pour les questions qui n'en ont aucune.

Contexte — l'audit des surfaces de correction (2026-08-30) a mesuré 13 grilles git pour
68 questions de scénarios : les 55 questions des rubriques (`*-v1`, atteignables depuis
`/document-analysis/chapters/...` et `/diagnostic/chapters/...`) n'en ont aucune et restent
sur le mur « pas de grille locale ». Les remplir est un TRAVAIL D'AUTEUR — le repo interdit
d'inventer des données d'examen. Ce script n'invente donc rien : il recopie dans un brouillon
**inerte** ce que le scénario et son document contiennent déjà.

Deux garde-fous mécaniques, pas des opinions :
  1. un keypoint n'est proposé que si le nombre est cité par L'EXEMPLE de la question ET
     présent DANS LE DOCUMENT visé (intersection). C'est ce contrôle qui a fait rejeter en
     mesure le câblage `enzyme-activity-v1` → `enzyme-temp-analyse` : l'exigence 37 °م
     n'appartient pas au document pH. Les nombres de la copie modèle qui viennent du cours
     sont laissés au choix de l'auteur.
  2. le brouillon n'est pas déclaré dans `data/rubrics/index.json` : `services/rubric_store.py`
     ne le voit pas, donc il ne peut pas corriger des copies par accident. Les clés `_draft_*`
     sont en sus refusées par les schémas pydantic — impossible de charger le fichier sans
     avoir lu la notice.

`--check` mesure lui-même ce que le squelette peut accomplir sans humain : sur les 55 questions
des rubriques, 55 se chargent (schémas valides) mais **3 seulement s'auto-valident à 100 %** —
ailleurs l'exemple montré à l'élève cite des nombres qui ne sont pas lisibles dans le document
(savoir de cours), donc le keypoint reste à écrire. Le squelette est un gain de saisie, pas une
grille publiable : c'est le résultat attendu et c'est la raison pour laquelle rien n'est indexé.

Usage :
    python scripts/gen_rubric_skeletons.py                     # liste, n'écrit rien
    python scripts/gen_rubric_skeletons.py --check             # + auto-note chaque squelette
    python scripts/gen_rubric_skeletons.py --scenario enzyme-activity-v1 --out data/rubrics/drafts
"""

from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path

BACKEND = Path(__file__).resolve().parent.parent
DOCS_TS = BACKEND.parent / "khawarizmi-frontend" / "src" / "lib" / "methodology-documents.ts"
INDEX = BACKEND / "data" / "rubrics" / "index.json"

VERB_SLUGS = {
    "analyse",
    "interpret",
    "deduce",
    "justify",
    "hypothesis",
    "scientific-text",
    "compare",
    "relationship",
    "define",
    "describe",
    "cite",
    "schematiser",
}
# un chiffre isolé est inutilisable comme exigence : « 1 » se lit dans « 10 », « 5,1 », « 2023 »
_AMBIGUOUS = re.compile(r"^\d$")
_NUM = re.compile(r"\d+(?:[.,/]\d+)?")
_AR_WORD = re.compile(r"[\u0600-\u06ff][\u0600-\u06ff\s]{2,}")


def _blocks(src: str, decl: str) -> list[tuple[str, str]]:
    out = []
    for m in re.finditer(decl, src):
        i = src.index("{", m.start())
        depth, j = 0, i
        while True:
            if src[j] == "{":
                depth += 1
            elif src[j] == "}":
                depth -= 1
                if depth == 0:
                    break
            j += 1
        out.append((m.group(1), src[i : j + 1]))
    return out


def _obj_items(body: str, key: str) -> list[str]:
    start = body.find(key)
    if start < 0:
        return []
    i = body.index("[", start)
    out, depth, k = [], 0, i
    while k < len(body):
        c = body[k]
        if c == "[":
            depth += 1
        elif c == "]":
            depth -= 1
            if depth == 0:
                break
        elif c == "{" and depth == 1:
            d, s = 0, k
            while True:
                if body[s] == "{":
                    d += 1
                elif body[s] == "}":
                    d -= 1
                    if d == 0:
                        break
                s += 1
            out.append(body[k : s + 1])
            k = s
        k += 1
    return out


def _str(obj: str, field: str) -> str | None:
    m = re.search(rf'{field}:\s*\n?\s*"((?:[^"\\]|\\.)*)"', obj)
    return m.group(1) if m else None


def scenarios() -> list[tuple[str, str]]:
    src = DOCS_TS.read_text(encoding="utf-8")
    return [
        (_str(body, "id") or name, body)
        for name, body in _blocks(src, r"(?:export )?const (\w+): MethodologyScenario = \{")
    ]


def questions_of(body: str) -> list[dict]:
    return [
        {
            "id": _str(q, "id") or f"q{i}",
            "verb": _str(q, "verbSlug") or "analyse",
            "gradeQuestionId": _str(q, "gradeQuestionId"),
            "docRef": _str(q, "docRef") or "",
            "prompt": _str(q, "prompt") or "",
            "modelAnswer": _str(q, "modelAnswer") or "",
            "placeholder": _str(q, "placeholder") or "",
        }
        for i, q in enumerate(_obj_items(body, "questions:"))
    ]


def referenced_doc(body: str, question: dict) -> str | None:
    """Le document visé — l'UI lie par libellé arabe « الوثيقة N », jamais par id."""
    docs = _obj_items(body, "documents:")
    if not docs:
        return None
    m = re.search(r"\d+", question.get("docRef") or "")
    idx = 0
    if m and (question.get("docRef") or "").strip().startswith("الوثيقة"):
        k = int(m.group()) - 1
        if 0 <= k < len(docs):
            idx = k
    return docs[idx]


def series_of(doc: str) -> list[tuple[float, float]]:
    """(x, y) des points d'une courbe, tels que la donnée les contient."""
    pts = []
    for m in re.finditer(r'\{\s*label:\s*"?([\d.,]+)"?[^}]*?value:\s*([\d.]+)', doc):
        try:
            pts.append((float(m.group(1).replace(",", ".")), float(m.group(2).replace(",", "."))))
        except ValueError:
            continue
    return pts


def doc_numbers(doc: str) -> set[str]:
    out: set[str] = set()
    for label in re.findall(r'label:\s*"?([^",\n]+)"?', doc):
        out |= {t for t in _NUM.findall(label) if not _AMBIGUOUS.match(t)}
    for val in re.findall(r"value:\s*([\d.]+)", doc):
        if not _AMBIGUOUS.match(val):
            out.add(val)
    for arr in re.findall(r"numbers:\s*\[([^\]]*)\]", doc):
        out |= {t for t in _NUM.findall(arr) if not _AMBIGUOUS.match(t)}
    return out


def _f(tok: str) -> float:
    return float(tok.replace(",", ".").replace("/", "."))


def build_draft(sid: str, body: str, question: dict) -> tuple[str, dict, dict] | None:
    """(question_id, rubric, document) — ou None si rien n'est démontrable."""
    if question["gradeQuestionId"]:
        return None
    doc = referenced_doc(body, question)
    if doc is None:
        return None
    model = (question.get("modelAnswer") or "").strip()
    if not model:
        return None  # aucun exemple dans l'UI : rien à recopier
    verb = question["verb"] if question["verb"] in VERB_SLUGS else "analyse"
    doc_nums = doc_numbers(doc)
    # INTERSECTION : un keypoint proposé doit être lu dans le document, pas seulement écrit
    anchored = [t for t in dict.fromkeys(_NUM.findall(model)) if t in doc_nums]
    qid = f"{sid}-{question['id']}"
    kind = "curve" if re.search(r"type:\s*\"(line-chart|bar-chart|curve)\"", doc) else "table"
    keypoints, trend = [], "unknown"
    pts = series_of(doc)
    if pts:
        ys = [y for _, y in pts]
        i_max, i_min = ys.index(max(ys)), ys.index(min(ys))
        x_max, y_max = pts[i_max]
        keypoints.append(
            {
                "id": "max",
                "value": y_max,
                "unit": _str(doc, "unit") or None,
                "tolerance": 0.0,
                "aliases": [],
                "label_ar": f"{_str(doc, 'yLabel') or 'y'} = {y_max:g} عند {_str(doc, 'xLabel') or 'x'} = {x_max:g}",
            }
        )
        if len(ys) > 2 and 0 < i_max < len(ys) - 1:
            trend = "bell"
        elif ys == sorted(ys):
            trend = "increase"
        elif ys == sorted(ys, reverse=True):
            trend = "decrease"
    for tok in anchored:
        keypoints.append(
            {"id": f"n{tok.replace('.', '_')}", "value": _f(tok), "unit": None, "tolerance": 0.0, "aliases": [], "label_ar": ""}
        )
    seen_kp, uniq_kp = set(), []
    for kp in keypoints:
        key = kp["value"]
        if key in seen_kp:
            continue
        seen_kp.add(key)
        uniq_kp.append(kp)

    objects = ["الوثيقة"] + (["المنحنى"] if kind == "curve" else ["الجدول"])
    connectors = [
        s.strip()
        for s in re.split(r"[.…]", question.get("placeholder") or "")
        if s.strip() and not re.search(r"\d", s) and 2 <= len(s.strip()) <= 24 and not s.strip().startswith("منحنى")
    ]
    conclusions = [c for c in connectors if re.search(r"نستنتج|يدل|نستخلص", c)]
    relations = [c for c in connectors if c not in conclusions]

    criteria = [
        {"id": "object", "label_ar": "تقديم الوثيقة", "points": 0.75, "check": "cites_object", "required": True},
        {
            "id": "keypoint",
            "label_ar": "ذكر قيم الوثيقة" + (" (" + "، ".join(anchored) + ")" if anchored else ""),
            "points": 1.0,
            "check": "cites_keypoint",
            "required": True,
        },
    ]
    if relations:
        criteria.append(
            {"id": "relation", "label_ar": "صياغة العلاقة المطلوبة", "points": 0.75, "check": "any_of", "variants": relations, "required": True}
        )
    if conclusions:
        criteria.append(
            {"id": "conclusion", "label_ar": "اختتام بالاستنتاج", "points": 1.0, "check": "any_of", "variants": conclusions, "required": True}
        )
    theme = [w.strip() for w in _AR_WORD.findall(_str(doc, "title") or "")][:6]
    rubric = {
        "rubric_id": qid,
        "version": "1.0.0",
        "verb_slug": verb,
        "chapter_slug": sid.replace("-v1", ""),
        "language": "ar",
        "total_points": round(sum(c["points"] for c in criteria), 2),
        "document_id": f"{sid}-d{question['id']}",
        "theme_variants": theme,
        "theme_min_hits": 1,
        "method_graph": {"steps": [c["id"] for c in criteria], "require_order": False},
        "criteria": criteria,
        "model_answer": model,
        "source": "teacher_authored",
        "grader_min_version": "1.0.0",
    }
    document = {
        "doc_id": f"{sid}-d{question['id']}",
        "version": "1.0.0",
        "kind": kind,
        "keypoints": uniq_kp,
        "trend": trend,
        "trend_variants": [],
        "objects": objects,
    }
    return qid, rubric, document


def _load_pair(rubric: dict, document: dict):
    sys.path.insert(0, str(BACKEND))
    from schemas.document_model import DocumentModel
    from schemas.rubric import Rubric

    return Rubric.model_validate(rubric), DocumentModel.model_validate(document)


def check_drafts(drafts: list[tuple[str, dict, dict]]) -> int:
    """Charge chaque squelette et le note contre SA copie modèle : la charpente est-elle valide ?"""
    sys.path.insert(0, str(BACKEND))
    from services.local_grader import grade

    bad = 0
    for qid, rubric, document in drafts:
        try:
            r, d = _load_pair(rubric, document)
        except Exception as exc:
            print(f"  ✗ {qid}: schéma refusé — {str(exc).splitlines()[0][:110]}")
            bad += 1
            continue
        res = grade(student_answer=r.model_answer, rubric=r, document=d)
        flag = "✓" if res.overall_training_percent == 100 else "!"
        if res.overall_training_percent != 100:
            bad += 1
        print(
            f"  {flag} {qid}: auto-note {res.overall_training_percent} % "
            f"(manque {[c.id for c in res.criteria if c.status != 'full'] or 'rien'})"
        )
    return bad


def main() -> None:
    ap = argparse.ArgumentParser(description="Génère des squelettes de grilles (brouillons inertes).")
    ap.add_argument("--out", default="", help="répertoire de sortie (défaut : liste seulement)")
    ap.add_argument("--scenario", default="", help="limiter à un id de scénario")
    ap.add_argument("--check", action="store_true", help="valider + auto-noter chaque squelette")
    ap.add_argument("--force", action="store_true", help="écraser les brouillons existants")
    args = ap.parse_args()

    indexed = set(json.loads(INDEX.read_text(encoding="utf-8")).keys())
    drafts: list[tuple[str, dict, dict]] = []
    no_example = wired = 0
    for sid, body in scenarios():
        if args.scenario and sid != args.scenario:
            continue
        for q in questions_of(body):
            wired += 1 if q["gradeQuestionId"] else 0
            if q["gradeQuestionId"]:
                continue
            built = build_draft(sid, body, q)
            if built is None:
                no_example += 1
                continue
            drafts.append(built)
        if args.scenario:
            break

    print(
        f"{len(drafts)} squelettes ancrables · {wired} questions déjà branchées · "
        f"{no_example} questions sans exemple dans l'UI · index.json : {len(indexed)} grilles"
    )
    for qid, rubric, _doc in sorted(drafts):
        warn = " ⚠ id déjà indexé" if qid in indexed else ""
        print(
            f"  {qid:<40} verbe={rubric['verb_slug']:<14} points={rubric['total_points']:<5}"
            f" keypoint→{len(rubric['criteria'][1].get('variants', [])) or 'doc'}{warn}"
        )
    if args.check:
        print("\n--check (schéma + auto-note de la copie modèle) :")
        bad = check_drafts(sorted(drafts))
        print(f"{len(drafts) - bad}/{len(drafts)} squelettes se chargent et s'auto-valident à 100 %")
    if not args.out:
        print("\n(aucune écriture — relancer avec --out data/rubrics/drafts)")
        return
    out = Path(args.out)
    if not out.is_absolute():
        out = BACKEND / out
    (out / "questions").mkdir(parents=True, exist_ok=True)
    (out / "documents").mkdir(parents=True, exist_ok=True)
    written = 0
    index_snippet = []
    for qid, rubric, document in drafts:
        rf = out / "questions" / f"{qid}.draft.json"
        df = out / "documents" / f"{qid}.draft.json"
        note = {
            "_draft_notice": [
                "brouillon généré par scripts/gen_rubric_skeletons.py — NON VALIDÉ PAR UN HUMAIN",
                "keypoints = intersection (nombres de l'exemple UI) ∩ (valeurs du document) ; élargir si le barème doit être plus exigeant",
                "trend_variants / counter_examples laissés vides : les remplir (validate_rubrics.py les exige avant indexation)",
                "pour publier : retirer ces clés _draft_*, renommer en .v1.json, ajouter l'entrée dans data/rubrics/index.json, "
                "puis brancher gradeQuestionId dans methodology-documents.ts — le gate tests/test_grade_s40.py vérifie le 100 %",
            ]
        }
        if rf.exists() and not args.force:
            continue
        rf.write_text(json.dumps({**rubric, **note}, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
        df.write_text(json.dumps({**document, **note}, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
        written += 1
        index_snippet.append(
            f'  "{qid}": {{\n    "rubric": "rubrics/drafts/questions/{qid}.draft.json",\n'
            f'    "document": "rubrics/drafts/documents/{qid}.draft.json"\n  }}'
        )
    print(f"\nécrit : {written} paires de brouillons dans {out} — hors index.json, donc inertes")
    if index_snippet:
        print("extrait d'entrée index.json APRÈS validation humaine (ne pas coller tel quel) :")
        print("{\n" + ",\n".join(index_snippet[:2]) + "\n}")


if __name__ == "__main__":
    main()
