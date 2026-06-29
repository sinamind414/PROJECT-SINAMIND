"""
scripts/extract_qcm_from_programme.py — Extrait les QCM du programme officiel.

Lit programme_national_svt_claude_opus.md, détecte les blocs QCM (🔵 ... (QCM)),
extrait chaque question + ses 4 options + l'option marquée ✅ ( bonne réponse ),
et associe chaque QCM à son unité/domaine ( le dernier header #/# ci-dessus ).

Sortie : data/qcm_items.json — liste de :
  {
    "id": "qcm_<n>",                        # ID global séquentiel ( zéro collision )
    "question_ar": "...",
    "options": ["...", "...", "...", "..."],
    "correct_idx": 0|1|2|3,
    "explanation": "...",
    "unit": "الوحدة 1: تركيب البروتين",
    "domain": "المجال الأول: ...",
    "unit_slug": "u_1",
    "source": "programme_officiel_svt"
  }
"""

import json
import re
import unicodedata
from pathlib import Path

PROGRAMME_PATH = Path(__file__).resolve().parent.parent / "data" / "courses" / "programme_national_svt_claude_opus.md"
OUTPUT_PATH = Path(__file__).resolve().parent.parent / "data" / "qcm_items.json"

RE_DOMAIN = re.compile(r"^# 📗 (المجال[^:]*):?\s*(.*)$")
RE_UNIT = re.compile(r"^# (?:🧬|🌿|⚡|🌍|🌋) (الوحدة[^:]*):\s*(.*?)\s*(?:\([^)]*\))?\s*$")
RE_QCM_HEADER = re.compile(r"^### .*?(?:اختيار من متعدد|QCM)", re.IGNORECASE)
RE_QUESTION = re.compile(r"^\*\*السؤال (\d+):\*\*\s*(.*)$")
RE_OPTION = re.compile(r"^-\s*([أابجد])\)\s*(.*)$")


def slugify(value: str) -> str:
    nf = unicodedata.normalize("NFKD", value)
    s = "".join(c for c in nf if not unicodedata.combining(c))
    s = re.sub(r"[^a-zA-Z0-9]+", "_", s).strip("_").lower()
    return s or "unit"


def extract_qcm():
    if not PROGRAMME_PATH.exists():
        raise FileNotFoundError(f"Programme introuvable : {PROGRAMME_PATH}")

    raw = PROGRAMME_PATH.read_text(encoding="utf-8")
    lines = raw.split("\n")

    items = []
    current_domain = ""
    current_unit = ""
    current_unit_slug = "unit"
    global_qcm_counter = 0

    i = 0
    n = len(lines)
    while i < n:
        line = lines[i].rstrip("\r").rstrip()
        stripped = line.strip()

        m_dom = RE_DOMAIN.match(stripped)
        if m_dom:
            current_domain = stripped.lstrip("# ").strip()
            i += 1
            continue
        m_unit = RE_UNIT.match(stripped)
        if m_unit:
            current_unit = stripped.lstrip("# ").strip()
            slug_src = re.sub(r"^[^\u0600-\u06ff]+", "", current_unit)
            slug_src = re.sub(r"\([^)]*\)", "", slug_src).strip()
            current_unit_slug = "u_" + slugify(slug_src)
            i += 1
            continue

        if RE_QCM_HEADER.match(stripped):
            i += 1
            q_num = 0
            while i < n:
                bl = lines[i].rstrip("\r").rstrip()
                bs = bl.strip()

                if bs.startswith("### ") or bs.startswith("# ") or bs == "---":
                    break

                m_q = RE_QUESTION.match(bs)
                if m_q:
                    q_num += 1
                    question_text = m_q.group(2).strip()
                    options = []
                    correct_idx = -1
                    explanation = ""
                    i += 1

                    while i < n:
                        ol = lines[i].rstrip("\r").rstrip()
                        os_ = ol.strip()
                        m_opt = RE_OPTION.match(os_)
                        if m_opt:
                            opt_text = m_opt.group(2).strip()
                            if "✅" in opt_text:
                                correct_idx = len(options)
                                opt_text = opt_text.replace("✅", "").strip()
                            elif "✓" in opt_text:
                                correct_idx = len(options)
                                opt_text = opt_text.replace("✓", "").strip()
                            options.append(opt_text)
                            i += 1
                            continue
                        if os_.startswith(">") and options:
                            exp = os_.lstrip("> ").strip()
                            exp = exp.strip("*").strip("()")
                            explanation = exp
                            i += 1
                            continue
                        break

                    if len(options) == 4 and correct_idx in (0, 1, 2, 3):
                        global_qcm_counter += 1
                        items.append({
                            "id": f"qcm_{global_qcm_counter:02d}",
                            "question_ar": question_text,
                            "options": options,
                            "correct_idx": correct_idx,
                            "explanation": explanation,
                            "unit": current_unit,
                            "domain": current_domain,
                            "unit_slug": current_unit_slug,
                            "source": "programme_officiel_svt",
                        })
                    continue

                i += 1
            continue

        i += 1

    return items


def main():
    items = extract_qcm()
    OUTPUT_PATH.parent.mkdir(parents=True, exist_ok=True)
    OUTPUT_PATH.write_text(
        json.dumps(items, ensure_ascii=False, indent=2), encoding="utf-8"
    )
    print(f"[OK] {len(items)} QCM extraits -> {OUTPUT_PATH}")


if __name__ == "__main__":
    main()
