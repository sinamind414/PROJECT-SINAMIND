"""
scripts/parse_massive_qcm.py — Parse le fichier de 500 QCM + 120 définitions.

Dédouillonne les répétitions et génère deux JSON :
  - data/qcm_items.json ( fusionne avec les 50 existants )
  - data/micro_concepts.json ( fusionne avec les 208 existants )

Pour le drill 100% QCM :
  - Les QCM سN deviennent des QCM
  - Les définitions ( تN type A, B, C ) deviennent TOUTES des QCM
    "trouve le terme" ( génération automatique de distracteurs ).
"""

import json
import re
import sys
import unicodedata
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from services.units import normalize_unit as _normalize_unit

SOURCE_PATH = Path(__file__).resolve().parent.parent / "data" / "courses" / "drills_svt_arabe_500_QCM_120_definitions_programme_joint.md"
QCM_OUT = Path(__file__).resolve().parent.parent / "data" / "qcm_items.json"
DEFS_OUT = Path(__file__).resolve().parent.parent / "data" / "micro_concepts.json"

LETTER_MAP = {"أ": 0, "ا": 0, "ب": 1, "ج": 2, "د": 3}
MAX_DEF_LEN = 400


def norm(t: str) -> str:
    nf = unicodedata.normalize("NFKD", t)
    t = "".join(c for c in nf if not unicodedata.combining(c))
    t = re.sub(r'[*#\-><=؟!.،؛:\[\]()"""«»\s]+', "", t)
    return t.lower().strip()


def parse_qcm_line(line: str):
    m = re.match(r"\*\*(س\d+)\.\s*(.+)", line.strip())
    if not m:
        return None
    num = m.group(1)
    q = m.group(2).rstrip("*").strip()
    q = re.sub(r"\[.*?\]$", "", q).strip()
    return num, q


def parse_def_line(line: str):
    m = re.match(r"\*\*(ت\d+)\.\s*(.+)", line.strip())
    if not m:
        return None
    num = m.group(1)
    q = m.group(2).rstrip("*").strip()
    return num, q


def find_answer(lines: list, start: int):
    correct_idx = -1
    explanation = ""
    for i in range(start, min(start + 10, len(lines))):
        s = lines[i].strip()
        m = re.search(r"✅.*?الإجابة:\s*([أابجد])", s)
        if m:
            correct_idx = LETTER_MAP.get(m.group(1), -1)
        m2 = re.search(r"💡.*?التفسير:\s*(.+)", s)
        if m2:
            explanation = m2.group(1).strip().rstrip("*")
        if "📍" in s:
            break
    return correct_idx, explanation


def parse_file():
    if not SOURCE_PATH.exists():
        raise FileNotFoundError(f"Fichier source introuvable : {SOURCE_PATH}")

    raw = SOURCE_PATH.read_text(encoding="utf-8")
    lines = raw.split("\n")

    qcm_items = []
    def_items = []
    seen_qcm = set()
    seen_defs = set()

    current_unit = ""
    i = 0
    while i < len(lines):
        line = lines[i].strip()

        if line.startswith("## U") and "—" in line:
            current_unit = line

        qcm_parsed = parse_qcm_line(line)
        if qcm_parsed:
            num, question = qcm_parsed
            options = []
            for j in range(i + 1, min(i + 8, len(lines))):
                opt_line = lines[j].strip()
                m_opt = re.match(r"^([أابجد])\)\s*(.+)", opt_line)
                if m_opt:
                    options.append(m_opt.group(2).strip())
                elif opt_line.startswith("✅") or not opt_line:
                    break

            correct_idx, explanation = find_answer(lines, i)

            if len(options) >= 2 and correct_idx in range(len(options)):
                sig = norm(question)
                if sig not in seen_qcm:
                    seen_qcm.add(sig)
                    qcm_items.append({
                        "question_ar": question,
                        "options": options[:4],
                        "correct_idx": correct_idx,
                        "explanation": explanation,
                        "unit": current_unit,
                        "source": "fichier_500_qcm",
                    })
            i += 1
            continue

        def_parsed = parse_def_line(line)
        if def_parsed:
            num, question = def_parsed
            def_type = "unknown"
            if "النوع أ" in question or "ما المصطلح" in question:
                def_type = "term"
            elif "النوع ب" in question:
                def_type = "qcm"
            elif "النوع ج" in question or "أكمل" in question:
                def_type = "fill"

            correct_idx, explanation = find_answer(lines, i)
            sig = norm(question)
            if sig in seen_defs:
                i += 1
                continue
            seen_defs.add(sig)

            if def_type == "qcm":
                options = []
                for j in range(i + 1, min(i + 8, len(lines))):
                    opt_line = lines[j].strip()
                    m_opt = re.match(r"^([أابجد])\)\s*(.+)", opt_line)
                    if m_opt:
                        options.append(m_opt.group(2).strip())
                    elif opt_line.startswith("✅") or not opt_line:
                        break
                if len(options) >= 2 and correct_idx in range(len(options)):
                    qcm_items.append({
                        "question_ar": question,
                        "options": options[:4],
                        "correct_idx": correct_idx,
                        "explanation": explanation,
                        "unit": current_unit,
                        "source": "fichier_500_qcm_def_type_b",
                    })
            else:
                answer_text = ""
                for j in range(i + 1, min(i + 6, len(lines))):
                    s = lines[j].strip()
                    m_ans = re.search(r"✅.*?الإجابة:\s*(.+)", s)
                    if m_ans:
                        answer_text = m_ans.group(1).strip().rstrip("*")
                        break
                if answer_text:
                    def_items.append({
                        "label_ar": answer_text,
                        "definition_ar": question[:MAX_DEF_LEN],
                        "unit": current_unit,
                        "source": "fichier_120_defs",
                    })
            i += 1
            continue

        i += 1

    return qcm_items, def_items


def generate_qcm_from_defs(def_items: list, existing_labels: list) -> list:
    """Convertit les définitions en QCM 'trouve le terme'."""
    import random

    all_terms = []
    for d in def_items:
        t = d["label_ar"].strip()
        if 1 < len(t) <= 40:
            all_terms.append(t)
    random.shuffle(all_terms)

    qcm_from_defs = []
    for d in def_items:
        correct_term = d["label_ar"]
        definition = d["definition_ar"]

        definition = re.sub(r"\(النوع [أج]\s*—.*?\)\s*", "", definition).strip()
        definition = definition.replace("التعريف:", "").replace("التعريف :", "").strip()
        definition = definition.strip("*").strip("«»").strip()

        distractors = [l for l in all_terms if l != correct_term][:3]
        if len(distractors) < 3:
            continue

        options = [correct_term] + distractors
        random.shuffle(options)
        correct_idx = options.index(correct_term)

        qcm_from_defs.append({
            "question_ar": f"ما هو المصطلح العلمي المقابل للتعريف الآتي: «{definition}»؟",
            "options": options,
            "correct_idx": correct_idx,
            "explanation": f"التعريف يطابق مصطلح: {correct_term}.",
            "unit": d.get("unit", ""),
            "source": "qcm_genere_from_definition",
        })

    return qcm_from_defs


def merge_and_save(new_qcm: list, new_defs: list):
    existing_qcm = []
    if QCM_OUT.exists():
        existing_qcm = json.loads(QCM_OUT.read_text(encoding="utf-8"))
    existing_defs = []
    if DEFS_OUT.exists():
        existing_defs = json.loads(DEFS_OUT.read_text(encoding="utf-8"))

    ex_def_sigs = set(norm(d.get("label_ar", "") + d.get("definition_ar", "")) for d in existing_defs)
    merged_defs = list(existing_defs)
    for d in new_defs:
        sig = norm(d.get("label_ar", "") + d.get("definition_ar", ""))
        if sig not in ex_def_sigs:
            ex_def_sigs.add(sig)
            d["id"] = f"mcd_big_{len(merged_defs) + 1:03d}"
            d["domain"] = ""
            merged_defs.append(d)

    all_existing_labels = [d.get("label_ar", "") for d in merged_defs if d.get("label_ar")]
    qcm_from_defs = generate_qcm_from_defs(new_defs, all_existing_labels)

    all_new_qcm = new_qcm + qcm_from_defs
    ex_qcm_sigs = set(norm(q["question_ar"]) for q in existing_qcm)

    merged_qcm = list(existing_qcm)
    added_qcm = 0
    for q in all_new_qcm:
        sig = norm(q["question_ar"])
        if sig not in ex_qcm_sigs:
            ex_qcm_sigs.add(sig)
            q["id"] = f"qcm_big_{len(merged_qcm) + 1:03d}"
            merged_qcm.append(q)
            added_qcm += 1

    # Normaliser unit_id sur TOUS les QCM (finaux) en une passe
    for q in merged_qcm:
        norm_u = _normalize_unit(q.get("unit", ""))
        q["unit_id"] = norm_u["unit_id"]
        q["unit_ar"] = norm_u["unit_ar"]
        q["domain_ar"] = norm_u["domain_ar"]

    QCM_OUT.write_text(json.dumps(merged_qcm, ensure_ascii=False, indent=2), encoding="utf-8")
    DEFS_OUT.write_text(json.dumps(merged_defs, ensure_ascii=False, indent=2), encoding="utf-8")

    return len(existing_qcm), added_qcm, len(merged_qcm), len(existing_defs), len(merged_defs)


def main():
    new_qcm, new_defs = parse_file()
    print(f"Parsé : {len(new_qcm)} QCM originaux, {len(new_defs)} defs à convertir")
    ex_q, add_q, tot_q, ex_d, tot_d = merge_and_save(new_qcm, new_defs)
    print(f"\n=== QCM ( 100% clic, zéro écriture ) ===")
    print(f"  Existant : {ex_q}")
    print(f"  Ajouté : {add_q}")
    print(f"  Total : {tot_q}")
    print(f"\n=== Définitions ( source ) ===")
    print(f"  Existant : {ex_d}")
    print(f"  Total : {tot_d}")
    print(f"\n=== GRAND TOTAL drill : {tot_q} QCM ===")


if __name__ == "__main__":
    main()
