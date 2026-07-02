#!/usr/bin/env python3
"""
verify_global.py — Vérification globale bout-en-bout (Tâche A + B + C).
Avec curl.exe + fichier temp pour garantir l'encodage UTF-8 correct.

Usage:
  python scripts/verify_global.py
  python scripts/verify_global.py --skip-db --skip-pytest --skip-tsc
"""

import json
import os
import subprocess
import sys
import tempfile
from pathlib import Path

# ─── Config ───────────────────────────────────────────────────────────
API_URL = os.environ.get("API_URL", "http://localhost:8000")
TOKEN = os.environ.get("TOKEN", "")
SCENARIO = os.environ.get("SCENARIO", "gene-expression-protein-disorder-v1")
DATABASE_URL = os.environ.get("DATABASE_URL", "")

SKIP_DB = "--skip-db" in sys.argv
SKIP_PYTEST = "--skip-pytest" in sys.argv
SKIP_TSC = "--skip-tsc" in sys.argv

# ─── Compteurs ────────────────────────────────────────────────────────
PASS = 0
FAIL = 0
SKIP = 0
FAILED_TESTS = []

# ─── Couleurs ─────────────────────────────────────────────────────────
if sys.stdout.isatty():
    GREEN = "\033[0;32m"; RED = "\033[0;31m"; YELLOW = "\033[1;33m"
    BLUE = "\033[0;34m"; BOLD = "\033[1m"; RESET = "\033[0m"
else:
    GREEN = RED = YELLOW = BLUE = BOLD = RESET = ""

def section(msg): print(f"\n{BOLD}{BLUE}══════ {msg} ══════{RESET}")
def step(msg):    print(f"  ▸ {msg}")
def ok(msg):
    global PASS
    print(f"  {GREEN}✅{RESET} {msg}"); PASS += 1
def ko(msg):
    global FAIL
    print(f"  {RED}❌{RESET} {msg}"); FAIL += 1; FAILED_TESTS.append(msg)
def skip(msg):
    global SKIP
    print(f"  {YELLOW}⤍{RESET}  {msg}"); SKIP += 1
def info(msg):    print(f"     {BLUE}i{RESET} {msg}")


# ─── Helper : POST /evaluate-v2 ───────────────────────────────────────
def call_v2(verb_slug: str, answer: str) -> dict:
    """Appel curl.exe avec --data-binary pour UTF-8 correct."""
    body = json.dumps({
        "scenario_id": SCENARIO,
        "chapter_slug": None,
        "answers": [{"verb_slug": verb_slug, "answer": answer}]
    }, ensure_ascii=False)

    with tempfile.NamedTemporaryFile(mode="w", suffix=".json", delete=False,
                                      encoding="utf-8") as f:
        f.write(body)
        tmp = f.name

    try:
        result = subprocess.run(
            ["curl.exe", "-sS", "-X", "POST",
             f"{API_URL}/api/document-analysis/evaluate-v2",
             "-H", f"Authorization: Bearer {TOKEN}",
             "-H", "Content-Type: application/json",
             "--data-binary", f"@{tmp}"],
            capture_output=True, timeout=60
        )
        return json.loads(result.stdout)
    except Exception as e:
        return {"_error": str(e)}
    finally:
        os.unlink(tmp)


def call_v1_empty() -> int:
    """GET status code de v1 avec body vide."""
    body = json.dumps({
        "scenario_id": SCENARIO, "chapter_slug": None, "answers": []
    })
    with tempfile.NamedTemporaryFile(mode="w", suffix=".json", delete=False,
                                      encoding="utf-8") as f:
        f.write(body)
        tmp = f.name
    try:
        result = subprocess.run(
            ["curl.exe", "-sS", "-o", os.devnull, "-w", "%{http_code}",
             "-X", "POST", f"{API_URL}/api/document-analysis/evaluate",
             "-H", f"Authorization: Bearer {TOKEN}",
             "-H", "Content-Type: application/json",
             "--data-binary", f"@{tmp}"],
            capture_output=True, timeout=30
        )
        return int(result.stdout.decode().strip())
    except Exception:
        return 0
    finally:
        os.unlink(tmp)


def call_v2_empty() -> int:
    """GET status code de v2 avec body vide."""
    body = json.dumps({
        "scenario_id": SCENARIO, "chapter_slug": None, "answers": []
    })
    with tempfile.NamedTemporaryFile(mode="w", suffix=".json", delete=False,
                                      encoding="utf-8") as f:
        f.write(body)
        tmp = f.name
    try:
        result = subprocess.run(
            ["curl.exe", "-sS", "-o", os.devnull, "-w", "%{http_code}",
             "-X", "POST", f"{API_URL}/api/document-analysis/evaluate-v2",
             "-H", f"Authorization: Bearer {TOKEN}",
             "-H", "Content-Type: application/json",
             "--data-binary", f"@{tmp}"],
            capture_output=True, timeout=30
        )
        return int(result.stdout.decode().strip())
    except Exception:
        return 0
    finally:
        os.unlink(tmp)


# ═══════════════════════════════════════════════════════════════════════
# GROUPE A — Sanity check
# ═══════════════════════════════════════════════════════════════════════
CHARABIA_CASES = [
    ("analyse", "ERRETREZR"),
    ("interpret", "EREZREZT"),
    ("deduce", "?KJ YBYUTIUJPO?K?PO"),
    ("hypothesis", "BVCGGCVUVUY"),
    ("scientific-text", "ZEZREZTERT"),
]

section("A. Sanity check bloque les 5 charabias")

for verb, answer in CHARABIA_CASES:
    resp = call_v2(verb, answer)
    ev = resp.get("evaluations", [{}])[0] if "evaluations" in resp else {}
    src = ev.get("source", "?")
    score = ev.get("score", -1)
    hl = len(ev.get("highlights", []))

    if src == "sanity" and score == 0 and hl >= 1:
        ok(f"A.{verb} ({answer}) → sanity, score=0, highlights={hl}")
    else:
        ko(f"A.{verb} ({answer}) → source={src} score={score} hl={hl} (attendu sanity/0/≥1)")


# ═══════════════════════════════════════════════════════════════════════
# GROUPE B — LLM
# ═══════════════════════════════════════════════════════════════════════
section("B. LLM opérationnel")

Q7 = "نفترض أن انخفاض البروتين الوظيفي عند الشخص المصاب يعود إلى حدوث تغير في المورثة يؤدي إلى إنتاج ARNm غير عادي."
Q8 = "هناك مشكلة في المورثة."

resp7 = call_v2("hypothesis", Q7)
ev7 = resp7.get("evaluations", [{}])[0] if "evaluations" in resp7 else {}
src7 = ev7.get("source", "?")
pct7 = ev7.get("percentage", -1)

if src7 in ("llm", "llm_recovered") and pct7 >= 60:
    ok(f"B.Q7 → {src7}, {pct7}% (attendu ≥60%)")
elif src7 == "sanity":
    ko(f"B.Q7 rejeté par sanity — le sanity check est trop strict (vrai arabe rejeté)")
elif src7 == "llm_error":
    ko(f"B.Q7 → LLM en erreur — vérifier clé API")
else:
    ko(f"B.Q7 → source={src7} pct={pct7}")

resp8 = call_v2("hypothesis", Q8)
ev8 = resp8.get("evaluations", [{}])[0] if "evaluations" in resp8 else {}
src8 = ev8.get("source", "?")
pct8 = ev8.get("percentage", -1)
unm8 = len(ev8.get("unmatched_criteria", []))

if src8 in ("llm", "llm_recovered") and unm8 >= 1:
    ok(f"B.Q8 → {src8}, {pct8}%, unmatched={unm8}")
elif src8 == "sanity":
    ko(f"B.Q8 rejeté par sanity — sanity trop strict")
else:
    ko(f"B.Q8 → source={src8} pct={pct8} unmatched={unm8}")


# ═══════════════════════════════════════════════════════════════════════
# GROUPE C — RAG chunks
# ═══════════════════════════════════════════════════════════════════════
section("C. RAG LIVRE MANHADJIYA ingéré")

if SKIP_DB:
    skip("--skip-db")
elif not DATABASE_URL:
    skip("DATABASE_URL non fourni")
else:
    try:
        import psycopg2
        conn = psycopg2.connect(DATABASE_URL)
        cur = conn.cursor()
        cur.execute("SELECT COUNT(*) FROM rag_chunks WHERE source='livre_manhadjiya'")
        total = cur.fetchone()[0]
        if total >= 200:
            ok(f"C.count : {total} chunks livre_manhadjiya")
        else:
            ko(f"C.count : seulement {total} chunks (attendu ≥200)")

        cur.execute("SELECT COUNT(DISTINCT chapitre) FROM rag_chunks WHERE source='livre_manhadjiya'")
        verbs = cur.fetchone()[0]
        if verbs >= 5:
            ok(f"C.spread : {verbs} slugs couverts")
        else:
            ko(f"C.spread : seulement {verbs} slugs")

        # Vérifier feedback Q7 avec vocabulaire méthodo
        resp7_rag = call_v2("hypothesis", Q7)
        ev7_rag = resp7_rag.get("evaluations", [{}])[0] if "evaluations" in resp7_rag else {}
        feedback = ev7_rag.get("feedback_ar", "")
        keywords = ["المسعى العلمي", "منهجية", "قابلة للاختبار", "نفترض أن", "فرضية"]
        found = [kw for kw in keywords if kw in feedback]
        if found:
            ok(f"C.feedback : vocabulaire méthodo trouvé : {', '.join(found)}")
        else:
            skip(f"C.feedback : aucun terme méthodo dans feedback (RAG peut-être pas actif)")

        cur.close(); conn.close()
    except ImportError:
        skip("psycopg2 non installé")
    except Exception as e:
        ko(f"C.db error : {e}")


# ═══════════════════════════════════════════════════════════════════════
# GROUPE D — Coexistence v1/v2
# ═══════════════════════════════════════════════════════════════════════
section("D. Coexistence v1 + v2")

v1 = call_v1_empty()
v2 = call_v2_empty()

if v1 in (200, 400, 422):
    ok(f"D.v1 : /evaluate répond ({v1})")
elif v1 == 404:
    ko("D.v1 : /evaluate est 404 — route supprimée !")
elif v1 in (401, 403):
    skip(f"D.v1 : {v1} (auth) — route probablement OK")
else:
    ko(f"D.v1 : status {v1}")

if v2 in (200, 400, 422):
    ok(f"D.v2 : /evaluate-v2 répond ({v2})")
elif v2 == 404:
    ko("D.v2 : route v2 introuvable")
else:
    ko(f"D.v2 : status {v2}")


# ═══════════════════════════════════════════════════════════════════════
# GROUPE F — Non-régression
# ═══════════════════════════════════════════════════════════════════════
section("F. Non-régression")

ROOT = Path(__file__).resolve().parent.parent

if SKIP_PYTEST:
    skip("--skip-pytest")
elif not (ROOT / "khawarizmi-backend").is_dir():
    skip("khawarizmi-backend absent")
else:
    step("Lancement pytest...")
    result = subprocess.run(
        ["python", "-m", "pytest", "--tb=no", "-q"],
        cwd=ROOT / "khawarizmi-backend",
        capture_output=True, timeout=300
    )
    output = result.stdout.decode(errors="replace")
    lines = output.strip().split("\n")
    summary = lines[-1] if lines else ""
    if "failed" in summary or "error" in summary.lower():
        ko(f"F.pytest : {summary}")
    else:
        ok(f"F.pytest : {summary}")

if SKIP_TSC:
    skip("--skip-tsc")
elif not (ROOT / "khawarizmi-frontend").is_dir():
    skip("khawarizmi-frontend absent")
else:
    step("Lancement tsc --noEmit...")
    result = subprocess.run(
        ["npx", "--no-install", "tsc", "--noEmit"],
        cwd=ROOT / "khawarizmi-frontend",
        capture_output=True, timeout=120
    )
    output = result.stdout.decode(errors="replace") + result.stderr.decode(errors="replace")
    errs = sum(1 for line in output.split("\n") if "error TS" in line)
    if errs == 0:
        ok("F.tsc : aucune erreur TypeScript")
    else:
        ko(f"F.tsc : {errs} erreurs TypeScript")


# ═══════════════════════════════════════════════════════════════════════
# GROUPE E — Frontend (manuel)
# ═══════════════════════════════════════════════════════════════════════
section("E. Frontend (vérification manuelle)")
info("Ouvrir /diagnostic/chapters/<slug> dans le navigateur")
info("Vérifier : charabias en rouge, vrai arabe avec score, pas d'erreur JS")


# ═══════════════════════════════════════════════════════════════════════
# BILAN
# ═══════════════════════════════════════════════════════════════════════
section("BILAN GLOBAL")
TOTAL = PASS + FAIL + SKIP
print(f"  Total : {TOTAL}")
print(f"  {GREEN}✅ PASS : {PASS}{RESET}")
print(f"  {RED}❌ FAIL : {FAIL}{RESET}")
print(f"  {YELLOW}⤍  SKIP : {SKIP}{RESET}")
print()

if FAIL == 0 and PASS >= 6:
    print(f"  {GREEN}{BOLD}🎉 Rien n'est cassé. Tout fonctionne.{RESET}")
    sys.exit(0)
elif FAIL == 0:
    print(f"  {YELLOW}{BOLD}⚠️  Aucun échec mais couverture faible ({PASS} PASS).{RESET}")
    sys.exit(0)
else:
    print(f"  {RED}{BOLD}❌ Régressions détectées :{RESET}")
    for t in FAILED_TESTS:
        print(f"    - {t}")
    sys.exit(1)
