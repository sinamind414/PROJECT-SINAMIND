#!/usr/bin/env python3
"""
scripts/audit_ocr_corruption.py — Détecteur de corruption OCR (arabe) sur les contenus.

Audit 2026-08-22 (réserves de l'audit pédagogique) : une partie des contenus
importés (banque « 605 Questions de Révision », PDFs méthodologie…) provient
de transcriptions OCR de documents scannés. L'arabe est le cas le plus fragile
(lettres qui changent de forme selon la position, diacritiques mal placés) :
les mots se désolidarisent en fragments de 1-3 lettres.

Détecteur : ratio de « mots suspects » = mots de 1-3 lettres arabes (hors
diacritiques) qui ne sont pas des mots fonctionnels/lexicaux courts légitimes
(في، من، دم، كبد…). Ratio élevé ⇒ texte désintégré par l'OCR.

Seuils : score >= 0.30 → CORROMPU · 0.12 <= score < 0.30 → SUSPECT · sinon OK
(évaluation seulement si le texte contient >= 4 mots arabes).

Usage :
    python scripts/audit_ocr_corruption.py                 # scan + rapport stdout
    python scripts/audit_ocr_corruption.py --json out.json # + liste des items à traiter

Sortie JSON : liste d'items {fichier, item, champ, verdict, score, extrait,
mots_suspets} → liste de travail pour purge / re-transcription (R-Audit 2026-08-22).

C'est aussi le GARDE-FOU à exécuter avant toute future import de documents
(0 item CORROMPU exigé avant ingestion).
"""

from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path

BASE = Path(__file__).resolve().parent.parent  # khawarizmi-backend/
DATA = BASE / "data"

AR_LETTERS = re.compile(r"[\u0621-\u064A\u0671-\u06D3]")  # lettres arabes (sans diacritiques)
AR_ANY = re.compile(r"[\u0600-\u06FF]")
# Classe B : formes de présentation arabes (PDF non normalisés)
AR_PRES = re.compile(r"[\uFB50-\uFDFF\uFE70-\uFEFF]")
# Étiquettes de réponses à options (أ) / ب / …) à ignorer avant scoring
OPTION_LABEL = re.compile(r"(?:^|\s)[أبجد]\s*[).،:]\s")
# Diacritiques + tatweel (retraités avant comparaison whitelist)
DIAC = re.compile(r"[\u064B-\u065F\u0670\u0640]")
# Mots mixtes arabe/latin (وO2, لATP, بARNr…) = notations scientifiques
# composées LÉGITIMES, pas une fragmentation OCR.
LATIN = re.compile(r"[A-Za-z]")
# Jetons-labels de sujets de Bac : lettres isolées AVEC parenthèses
# «(س)»، «(أ و ب)»، «(ح)», «(غ1)» — convention officielle de désignation
# des éléments. Une lettre isolée SANS parenthèses reste un signal de
# corruption.
LABEL = re.compile(r"^[\(\[«{]?\s*[\u0600-\u06FF]\d?\s*[\)\]»}]?$")
LABEL_PAREN = re.compile(r"[\(\[«\{\)\]»}]")
# Références de page « ص208 », « ص18 »
PAGE_REF = re.compile(r"^ص\d+$")
# Jetons contenant des chiffres (و70, ت2, ز3) = notations, pas de l'arabe
DIGITS = re.compile(r"\d")

# Mots courts LÉGITIMES (fonctionnels + lexicaux fréquents en arabe scientifique).
WHITELIST = {
    # conjonctions / particules
    "في", "من", "إلى", "الى", "على", "علي", "عن", "مع", "ب", "ل", "ك", "و", "أو", "او",
    "ثم", "ف", "قد", "لا", "لن", "لم", "ما", "أن", "ان", "إن", "ان", "هل", "أم", "اما",
    "إذ", "إذا", "إذا", "لكن", "غير", "كم", "أي", "اي", "كل", "بعض", "مثل", "كأن",
    "هنا", "هناك", "حيث", "عند", "حول", "نحو", "منذ", "حتى", "بعد", "قبل", "بين",
    "داخل", "خارج", "تحت", "فوق", "ضمن", "خلف", "أمام", "ما", "لا",
    # interrogatives courtes
    "أين", "اين", "متى", "كيف", "ماذا", "من", "لماذا", "لما",
    # pronoms / démonstratifs courts
    "هو", "هي", "هم", "هن", "أنا", "انا", "أنت", "انت", "هذا", "هذه", "ذلك", "تلك",
    "الذي", "التي", "الذين", "إلا", "إلا", "له", "لها", "لهم", "بها", "به", "بهما",
    "منه", "منها", "عنه", "عنها", "إليه", "إليها",
    # lexique scientifique court légitime
    "دم", "عظم", "ماء", "نور", "شمس", "قمر", "كبد", "رئة", "أرض", "هواء", "زمن",
    "مس", "فراغ", "ذرة", "خلية", "أنسجة", "نسيج", "عضو", "أعضاء",
    "نوع", "شكل", "لون", "حجم", "وزن", "رقم", "جزء", "عدد", "مادة", "عمر",
    "وصف", "اسم", "علم", "قيمة", "قوة", "حرارة", "ضوء", "صوت", "جذر", "فرع",
    # mots courts légitimes relevés dans les faux positifs du scan 2026-08-22
    # (formes de base, comparés sans diacritiques)
    "و", "ب", "طلب", "فأي", "عمل", "سطح", "نقص", "نفس", "لكل", "جمع", "فقط",
    "فيه", "حد", "وسط", "لأن", "يجب", "يصف", "ولا", "قوي", "تتم", "دون",
    "فرق", "غني", "صف", "حمض", "وضح", "علل", "رفض", "عرض", "منع", "رغم",
    "يحد", "ضخ", "عبر", "وقد", "غوص", "هدم", "سان", "صلب", "تدل", "ضغط",
    "ليس", "لبا", "دور", "صنف", "حسب", "لل", "فرد", "كيف", "تفسر", "مثال",
    "دليل", "عينة", "مستوى", "نتيجة", "شروط", "شرط", "عند", "ضمن",
    # verbes impératifs des consignes d'exercice Bac + mots courts courants
    "حدد", "حلل", "فسر", "يتم", "كان", "ذات", "عدة", "يدل", "مما", "وهي",
    "طول", "خيط", "حقن", "غلق", "ذو", "رسم", "وفق", "سبب", "قدم", "اقل",
    "يصل", "آن", "مقر", "سم", "نقل", "نسخ", "صخر", "تمر",
    # mots courts validés à la relecture des 40 SUSPECT du 2026-08-22
    "صفر", "كما", "بيض", "لغة", "فقر", "ضد", "ذي", "موت", "فأر", "أدى",
    "مرض", "سدى", "أثر", "قرب", "سحب", "تجر", "جسم", "قاع", "تصل", "يقع",
    "علق", "نمط", "طرق", "قيد", "أحد", "ستة", "برر", "أنه", "يلي", "حي",
    "لخص", "نص", "حضر", "غاز", "وضع", "فطر", "زرع", "مشع", "عزل", "أجل",
    "pH", "ATP", "ADN", "ARN", "DNA", "RNA",
    # fragments d'article
    "الـ", "ال",
}


def score_text(text: str) -> tuple[float, int, list[str]]:
    """Ratio de mots arabes courts suspects (0.0 = propre, 1.0 = tout corrompu).

    Classe A : fragmentation OCR (mots désolidarisés en fragments 1-3 lettres).
    Les étiquettes d'options (أ) ب) …) sont retirées avant scoring (faux positifs)."""
    if not text:
        return 0.0, 0, []
    text = OPTION_LABEL.sub(" ", text)
    words = text.split()
    arab = [w for w in words if AR_ANY.search(w)]
    if len(arab) < 4:
        return 0.0, len(arab), []
    suspicious = []
    for w in arab:
        # Notation composite arabe/latin (وO2، لATP، بARNr) : légitime.
        if LATIN.search(w):
            continue
        # Jeton-label avec parenthèses (س) / (أ / ب) : convention Bac.
        if LABEL.match(w.strip("،.؟!?;،-–—*#")) and LABEL_PAREN.search(w):
            continue
        # Référence de page (ص208) ou jeton avec chiffres (و70, ت2) : notation.
        if PAGE_REF.match(w.strip("،.؟!?;،-–—*#")) or DIGITS.search(w):
            continue
        letters = AR_LETTERS.findall(w)
        n = len(letters)
        if n == 0:
            continue
        clean = DIAC.sub("", w.strip("،.؟!?«»():;،-–—*#؛:"))
        if n <= 3 and clean not in WHITELIST:
            suspicious.append(w)
    return len(suspicious) / len(arab), len(arab), suspicious


def pres_forms_count(text: str) -> int:
    """Classe B : nombre de caractères « formes de présentation » arabes
    (extraction PDF non normalisée — réparable par normalisation unicode)."""
    return len(AR_PRES.findall(text or ""))


def verdict_of(score: float, pres: int = 0) -> str:
    # Classe B d'abord : ≥ 5 formes de présentation = extraction PDF non
    # normalisée (réparable par normalisation unicode) — indépendamment du
    # ratio de fragmentation (le ratio peut rester bas : les « mots » en
    # formes de présentation ne sont pas comptés comme lettres standard).
    if pres >= 5:
        return "NON_NORMALISE"
    if score >= 0.30:
        return "CORROMPU"
    if score >= 0.12:
        return "SUSPECT"
    return "OK"


# ─── Extraction par fichier : yield (item_id, champ, texte) ──────────────


def iter_annales():
    for s in json.load(open(DATA / "annales_sciences_3as.json")):
        for e in s.get("exercices", []):
            for q in e.get("questions", []):
                qid = f"{s['sujet_id']}::{q.get('question_id','?')}"
                yield qid, "texte", q.get("texte", "")
                yield qid, "reponse_attendue", q.get("reponse_attendue", "")


def iter_qcm():
    for it in json.load(open(DATA / "qcm_items.json")):
        iid = str(it.get("id"))
        yield iid, "question_ar", it.get("question_ar", "")
        yield iid, "options", " ".join(str(o) for o in it.get("options", []))
        yield iid, "explanation", it.get("explanation", "")


def iter_tagged():
    for p in sorted(DATA.glob("processed_khelifa_questions_batch*.json")):
        for it in json.load(open(p)):
            yield f"{p.stem}::{it.get('id')}", "texte_corrige", it.get("texte_corrige", "")
    for it in json.load(open(DATA / "questions_taggees.json")):
        yield f"questions_taggees::{it.get('id')}", "texte_corrige", it.get("texte_corrige", "")


def iter_exercices():
    for name in ("sciences_bac_exercices.json", "sciences_resumes.json"):
        p = DATA / name
        if not p.exists():
            continue
        for it in json.load(open(p)):
            iid = f"{name}::{it.get('id')}"
            yield iid, "enonce", it.get("enonce", "")
            yield iid, "reponse_attendue", it.get("reponse_attendue", "")


def _walk_strings(o, path=""):
    if isinstance(o, str):
        if len(o) >= 30 and AR_ANY.search(o):
            yield path or "(racine)", o
    elif isinstance(o, dict):
        for k, v in o.items():
            yield from _walk_strings(v, f"{path}/{k}" if path else str(k))
    elif isinstance(o, list):
        for i, v in enumerate(o):
            yield from _walk_strings(v, f"{path}[{i}]")


def iter_recursive(label: str, p: Path):
    try:
        d = json.load(open(p))
    except Exception as e:
        print(f"  ⚠️  {label} : non lisible ({e})", file=sys.stderr)
        return
    for path, text in _walk_strings(d):
        yield f"{label}::{path[:80]}", "text", text


def iter_drills_md():
    p = DATA / "courses" / "drills_svt_arabe_500_QCM_120_definitions_programme_joint.md"
    txt = p.read_text(encoding="utf-8")
    for m in re.finditer(r"\*\*س(\d+)\.\s(.+?)\*\*", txt):
        num, q = m.group(1), m.group(2)
        end = m.end()
        nxt = txt.find("**س", end)
        block = txt[end:nxt if nxt != -1 else end + 600]
        yield f"drills620::س{num}", "question", q
        yield f"drills620::س{num}", "bloc(complet)", block[:800]


TARGETS = [
    ("annales_sciences_3as", iter_annales),
    ("qcm_items (670)", iter_qcm),
    ("questions taggées + khelifa", iter_tagged),
    ("exercices/resumes bac", iter_exercices),
    ("methodologie (16 doc)", lambda: iter_recursive("methodologie", DATA / "methodologie_sciences_3as.json")),
    ("lexique", lambda: iter_recursive("lexique", DATA / "lexique_svt_terminale_complet.json")),
    ("manhadjiya_seed", lambda: iter_recursive("manhadjiya", DATA / "manhadjiya_v1_seed.json")),
    ("annales_seed", lambda: iter_recursive("annales_seed", DATA / "annales_seed.json")),
    ("drills 620 (md)", iter_drills_md),
]


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[1])
    ap.add_argument("--json", metavar="FICHIER", help="écrit la liste des items flaggés (SUSPECT+CORROMPU)")
    ap.add_argument("--verbose", action="store_true")
    args = ap.parse_args()

    print("=" * 100)
    print("SCAN CORRUPTION OCR (arabe) — audit 2026-08-22")
    print("Seuils : score ≥ 0.30 CORROMPU · ≥ 0.12 SUSPECT · sinon OK (min. 4 mots arabes)")
    print("=" * 100)

    flagged = []
    grand = {"n": 0, "ok": 0, "suspect": 0, "corrompu": 0}
    for label, it in TARGETS:
        stats = {"n": 0, "ok": 0, "suspect": 0, "corrompu": 0, "non_normalise": 0}
        samples: list[str] = []
        for item, field, text in it():
            score, n_ar, susp = score_text(text)
            pres = pres_forms_count(text)
            # Évaluer s'il y a du texte arabe standard OU des formes de
            # présentation (qui ne comptent pas comme lettres standard).
            v = verdict_of(score, pres) if (n_ar >= 4 or pres >= 5) else "OK"
            stats["n"] += 1
            stats[v.lower()] = stats.get(v.lower(), 0) + 1
            grand["n"] += 1
            grand[v.lower()] = grand.get(v.lower(), 0) + 1
            if v in ("SUSPECT", "CORROMPU", "NON_NORMALISE"):
                entry = {
                    "fichier": label,
                    "item": item,
                    "champ": field,
                    "verdict": v,
                    "score": round(score, 3),
                    "formes_presentation": pres,
                    "mots_suspets": susp[:12],
                    "extrait": (text[:140] + "…") if len(text) > 140 else text,
                }
                flagged.append(entry)
                if len(samples) < 2:
                    samples.append(f"      [{v} {score:.0%}] {item} :: {text[:110]}")
        pct_c = 100 * (stats["corrompu"] + stats.get("non_normalise", 0)) / max(stats["n"], 1)
        line = (f"{label:<38} {stats['n']:>6} texte  ·  OK {stats['ok']:>5}  "
                f"SUSPECT {stats['suspect']:>4}  CORROMPU {stats['corrompu']:>3}  "
                f"NON-NORM {stats.get('non_normalise',0):>3}  (à traiter {pct_c:.1f}%)")
        print(line)
        for s in samples:
            print(s)

    print("-" * 100)
    print(f"{'TOTAL':<38} {grand['n']:>6} texte  ·  OK {grand['ok']:>5}  "
          f"SUSPECT {grand['suspect']:>4}  CORROMPU {grand['corrompu']:>3}  "
          f"NON-NORM {grand.get('non_normalise',0):>3}  "
          f"(à traiter {100*(grand['corrompu']+grand.get('non_normalise',0))/max(grand['n'],1):.1f}%)")

    if args.json:
        out = Path(args.json)
        out.parent.mkdir(parents=True, exist_ok=True)
        out.write_text(json.dumps(flagged, ensure_ascii=False, indent=1), encoding="utf-8")
        print(f"\nListe de travail écrite : {out} ({len(flagged)} items)")


if __name__ == "__main__":
    main()
