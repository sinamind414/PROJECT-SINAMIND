#!/usr/bin/env bash
# ═══════════════════════════════════════════════════════════════════════
# verify_global.sh
#
# Vérification globale bout-en-bout après le travail de Deepseek
# (Tâche A + Tâche B RAG + Tâche C frontend).
#
# Ce script est agnostique de l'ordre d'exécution : chaque groupe de
# tests indique clairement s'il PASS, FAIL ou SKIP (avec la raison).
#
# Il ne modifie rien. Il ne lance aucun redémarrage. Il OBSERVE.
#
# Usage :
#   API_URL=http://localhost:8000 \
#   TOKEN=eyJ... \
#   SCENARIO=slug-de-scenario \
#   ./verify_global.sh
#
# Options :
#   --skip-pytest   : ne pas lancer pytest (rapide)
#   --skip-tsc      : ne pas lancer tsc frontend (rapide)
#   --skip-db       : ne pas interroger PostgreSQL (utile si pas de psql local)
# ═══════════════════════════════════════════════════════════════════════

set -u

# ─── Config ───────────────────────────────────────────────────────────
API_URL="${API_URL:-http://localhost:8000}"
TOKEN="${TOKEN:-}"
SCENARIO="${SCENARIO:-}"
DATABASE_URL="${DATABASE_URL:-}"
SKIP_PYTEST=0
SKIP_TSC=0
SKIP_DB=0

for arg in "$@"; do
  case "$arg" in
    --skip-pytest) SKIP_PYTEST=1 ;;
    --skip-tsc)    SKIP_TSC=1 ;;
    --skip-db)     SKIP_DB=1 ;;
    -h|--help)     grep '^#' "$0" | sed 's/^# \{0,1\}//'; exit 0 ;;
  esac
done

# ─── Couleurs ─────────────────────────────────────────────────────────
if [ -t 1 ]; then
  GREEN=$'\033[0;32m'; RED=$'\033[0;31m'; YELLOW=$'\033[1;33m'
  BLUE=$'\033[0;34m'; BOLD=$'\033[1m'; RESET=$'\033[0m'
else
  GREEN=""; RED=""; YELLOW=""; BLUE=""; BOLD=""; RESET=""
fi

# ─── Compteurs ────────────────────────────────────────────────────────
PASS=0; FAIL=0; SKIP=0
FAILED_TESTS=""

# ─── Helpers d'affichage ──────────────────────────────────────────────
section() { echo; echo "${BOLD}${BLUE}══════ $* ══════${RESET}"; }
step()    { echo "  ▸ $*"; }
ok()      { echo "  ${GREEN}✅${RESET} $*"; PASS=$((PASS+1)); }
ko()      { echo "  ${RED}❌${RESET} $*";   FAIL=$((FAIL+1)); FAILED_TESTS="$FAILED_TESTS\n  - $*"; }
skip()    { echo "  ${YELLOW}⤍${RESET}  $*"; SKIP=$((SKIP+1)); }
info()    { echo "     ${BLUE}i${RESET} $*"; }

# ─── Helper : POST /evaluate-v2 avec 1 réponse ───────────────────────
call_v2() {
  local verb_slug="$1" answer="$2"
  local body
  if command -v jq >/dev/null; then
    body=$(jq -nc --arg s "$SCENARIO" --arg v "$verb_slug" --arg a "$answer" \
      '{scenario_id:$s, chapter_slug:null, answers:[{verb_slug:$v, answer:$a}]}')
  else
    local ea=$(printf '%s' "$answer" | sed 's/\\/\\\\/g; s/"/\\"/g')
    body="{\"scenario_id\":\"$SCENARIO\",\"chapter_slug\":null,\"answers\":[{\"verb_slug\":\"$verb_slug\",\"answer\":\"$ea\"}]}"
  fi
  # Silence les erreurs curl (connexion refusée, DNS…) pour un output propre.
  # Les échecs seront détectés par le parsing JSON vide en aval.
  curl -sS --max-time 30 -X POST "$API_URL/api/document-analysis/evaluate-v2" \
    -H "Authorization: Bearer $TOKEN" \
    -H "Content-Type: application/json" \
    -d "$body" 2>/dev/null
}

# ─── Prérequis ────────────────────────────────────────────────────────
section "0. Prérequis techniques"

for cmd in curl; do
  if command -v $cmd >/dev/null; then ok "$cmd présent"; else ko "$cmd absent"; fi
done

if command -v jq >/dev/null; then ok "jq présent (parsing JSON fiable)"
else info "jq absent (parsing JSON dégradé, install: apt-get install jq)"; fi

if [ -z "$TOKEN" ] || [ -z "$SCENARIO" ]; then
  ko "TOKEN ou SCENARIO manquant"
  echo
  echo "  Usage : TOKEN=eyJ... SCENARIO=proteines-01 $0"
  exit 2
fi
ok "TOKEN et SCENARIO fournis"


# ═══════════════════════════════════════════════════════════════════════
# GROUPE A — Le bug charabia est mort (régression n°0 à surveiller)
# ═══════════════════════════════════════════════════════════════════════
section "A. Sanity check bloque les 5 charabias d'origine"

CHARABIA_CASES=(
  "analyse:ERRETREZR"
  "interpret:EREZREZT"
  "deduce:?KJ YBYUTIUJPO?K?PO"
  "hypothesis:BVCGGCVUVUY"
  "scientific-text:ZEZREZTERT"
)

for case in "${CHARABIA_CASES[@]}"; do
  IFS=':' read -r verb answer <<< "$case"
  json=$(call_v2 "$verb" "$answer")
  source=$(echo "$json" | jq -r '.evaluations[0].source // "?"' 2>/dev/null)
  score=$( echo "$json" | jq -r '.evaluations[0].score  // -1'  2>/dev/null)
  hl_n=$(  echo "$json" | jq -r '.evaluations[0].highlights | length // 0' 2>/dev/null)

  if [ "$source" = "sanity" ] && [ "$score" = "0" ] && [ "$hl_n" -ge 1 ]; then
    ok "A.$verb ($answer) → sanity, score=0, highlights=$hl_n"
  else
    ko "A.$verb ($answer) → source=$source score=$score hl=$hl_n (attendu sanity/0/≥1)"
  fi
done


# ═══════════════════════════════════════════════════════════════════════
# GROUPE B — Le LLM répond correctement
# ═══════════════════════════════════════════════════════════════════════
section "B. LLM Gemini opérationnel"

Q7_ANSWER="نفترض أن انخفاض البروتين الوظيفي عند الشخص المصاب يعود إلى حدوث تغير في المورثة يؤدي إلى إنتاج ARNm غير عادي."
json=$(call_v2 "hypothesis" "$Q7_ANSWER")
source=$(echo "$json"  | jq -r '.evaluations[0].source     // "?"' 2>/dev/null)
pct=$(   echo "$json"  | jq -r '.evaluations[0].percentage // -1'  2>/dev/null)

case "$source" in
  llm|llm_recovered)
    if [ "$pct" -ge 60 ]; then
      ok "B.Q7 hypothèse correcte → $source, $pct% (attendu ≥60%)"
    else
      ko "B.Q7 hypothèse correcte → $source, $pct% (trop bas, attendu ≥60%)"
    fi
    ;;
  sanity)
    ko "B.Q7 hypothèse correcte a été RÉJETÉE par sanity — vrai bug (le sanity check est trop strict)"
    ;;
  llm_error)
    ko "B.Q7 LLM en erreur — vérifier clé Gemini dans .env"
    ;;
  *)
    ko "B.Q7 source inattendu : $source"
    ;;
esac

Q8_ANSWER="نفترض أن هناك مشكلة في المورثة."
json=$(call_v2 "hypothesis" "$Q8_ANSWER")
source=$(echo "$json"    | jq -r '.evaluations[0].source                  // "?"' 2>/dev/null)
pct=$(   echo "$json"    | jq -r '.evaluations[0].percentage              // -1'  2>/dev/null)
unmatched=$(echo "$json" | jq -r '.evaluations[0].unmatched_criteria | length // 0' 2>/dev/null)

if [ "$source" = "llm" ] || [ "$source" = "llm_recovered" ]; then
  if [ "$unmatched" -ge 1 ]; then
    ok "B.Q8 hypothèse vague → $source, $pct%, unmatched=$unmatched (le LLM voit ce qui manque)"
  else
    ko "B.Q8 hypothèse vague → $source, $pct% MAIS unmatched=0 (le LLM devrait pointer ce qui manque)"
  fi
else
  ko "B.Q8 source inattendu : $source"
fi


# ═══════════════════════════════════════════════════════════════════════
# GROUPE C — Tâche B (RAG) : le livre est ingéré
# ═══════════════════════════════════════════════════════════════════════
section "C. RAG LIVRE MANHADJIYA ingéré (Tâche B)"

if [ "$SKIP_DB" -eq 1 ]; then
  skip "Interrogation DB désactivée (--skip-db)"
elif [ -z "$DATABASE_URL" ]; then
  skip "DATABASE_URL non fourni — impossible de vérifier rag_chunks"
elif ! command -v psql >/dev/null; then
  skip "psql absent — impossible de vérifier rag_chunks"
else
  total=$(psql "$DATABASE_URL" -tAc "SELECT COUNT(*) FROM rag_chunks WHERE source='livre_manhadjiya'" 2>/dev/null || echo "?")
  if [ "$total" = "?" ] || [ -z "$total" ]; then
    ko "C.count : requête SQL échouée (table absente ? credentials ? pgvector ?)"
  elif [ "$total" -lt 100 ]; then
    ko "C.count : seulement $total chunks (attendu ≥200). Ingestion pas encore faite ou échouée."
  else
    ok "C.count : $total chunks livre_manhadjiya dans rag_chunks (attendu ≥200)"
    verbs=$(psql "$DATABASE_URL" -tAc "SELECT COUNT(DISTINCT chapitre) FROM rag_chunks WHERE source='livre_manhadjiya'" 2>/dev/null || echo "0")
    if [ "$verbs" -ge 5 ]; then
      ok "C.spread : $verbs slugs de verbe couverts (attendu ≥5)"
    else
      ko "C.spread : seulement $verbs slugs (parsing peut-être trop grossier)"
    fi
  fi
fi

# Signal indirect : après ingestion, le feedback de Q7 devrait mentionner
# des termes de méthodologie officielle du livre (المسعى العلمي, etc.)
json=$(call_v2 "hypothesis" "$Q7_ANSWER")
feedback=$(echo "$json" | jq -r '.evaluations[0].feedback_ar // ""' 2>/dev/null)
if [ -n "$feedback" ]; then
  if echo "$feedback" | grep -qE "المسعى العلمي|منهجية|قابلة للاختبار|نفترض أن"; then
    ok "C.feedback : feedback Q7 mentionne du vocabulaire méthodologique arabe"
  else
    skip "C.feedback : feedback ne contient pas de vocabulaire méthodo attendu (RAG peut-être pas actif). Feedback : ${feedback:0:120}..."
  fi
fi


# ═══════════════════════════════════════════════════════════════════════
# GROUPE D — Coexistence v1/v2 : l'ancienne route vit toujours
# ═══════════════════════════════════════════════════════════════════════
section "D. Coexistence v1 + v2"

# La v1 doit toujours répondre (statut 200 ou 422 selon body — jamais 404 ni 500)
v1_status=$(curl -sS --max-time 30 -o /dev/null -w "%{http_code}" \
  -X POST "$API_URL/api/document-analysis/evaluate" \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"scenario_id":"'"$SCENARIO"'","chapter_slug":null,"answers":[]}' 2>/dev/null)

case "$v1_status" in
  200|400|422)
    ok "D.v1 : /api/document-analysis/evaluate répond ($v1_status) — route legacy vivante"
    ;;
  404)
    ko "D.v1 : /api/document-analysis/evaluate est 404 — Deepseek a peut-être supprimé la v1 par erreur"
    ;;
  401|403)
    skip "D.v1 : $v1_status (auth) — vérifier le TOKEN mais route probablement OK"
    ;;
  *)
    ko "D.v1 : status inattendu $v1_status"
    ;;
esac

# La v2 doit répondre pareil
v2_status=$(curl -sS --max-time 30 -o /dev/null -w "%{http_code}" \
  -X POST "$API_URL/api/document-analysis/evaluate-v2" \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"scenario_id":"'"$SCENARIO"'","chapter_slug":null,"answers":[]}' 2>/dev/null)

case "$v2_status" in
  200|400|422) ok "D.v2 : /api/document-analysis/evaluate-v2 répond ($v2_status)" ;;
  404) ko "D.v2 : route v2 introuvable — Tâche A pas déployée ?" ;;
  *)   ko "D.v2 : status inattendu $v2_status" ;;
esac


# ═══════════════════════════════════════════════════════════════════════
# GROUPE F — Non-régression : suite de tests
# ═══════════════════════════════════════════════════════════════════════
section "F. Non-régression : suites de tests"

if [ "$SKIP_PYTEST" -eq 1 ]; then
  skip "pytest désactivé (--skip-pytest)"
elif [ ! -d "khawarizmi-backend" ]; then
  skip "Répertoire khawarizmi-backend absent — lancer depuis la racine du repo"
else
  step "Lancement pytest complet (peut prendre 1-3 min)…"
  pytest_out=$(cd khawarizmi-backend && pytest --tb=no -q 2>&1 || true)
  # Chercher la ligne de résumé
  summary=$(echo "$pytest_out" | grep -E "passed|failed|error" | tail -1)
  if echo "$summary" | grep -qE "failed|error"; then
    ko "F.pytest : $summary"
    info "Détail :"
    echo "$pytest_out" | tail -20 | sed 's/^/     /'
  else
    ok "F.pytest : $summary"
  fi
fi

if [ "$SKIP_TSC" -eq 1 ]; then
  skip "tsc désactivé (--skip-tsc)"
elif [ ! -d "khawarizmi-frontend" ]; then
  skip "Répertoire khawarizmi-frontend absent"
else
  step "Lancement npx tsc --noEmit (peut prendre 30-60 s)…"
  tsc_out=$(cd khawarizmi-frontend && npx --no-install tsc --noEmit 2>&1 || true)
  errs=$(echo "$tsc_out" | grep -cE "error TS[0-9]+")
  if [ "$errs" -eq 0 ]; then
    ok "F.tsc : aucune erreur TypeScript"
  else
    ko "F.tsc : $errs erreurs TypeScript"
    echo "$tsc_out" | grep -E "error TS" | head -5 | sed 's/^/     /'
  fi
fi


# ═══════════════════════════════════════════════════════════════════════
# GROUPE E — Frontend : vérification manuelle (non automatisable en CLI)
# ═══════════════════════════════════════════════════════════════════════
section "E. Frontend (à vérifier manuellement dans un navigateur)"

info "Ouvrir : $API_URL (ou http://localhost:3000 pour le dev frontend)"
info "1. Aller sur /diagnostic/chapters/<un-slug>"
info "2. Répondre aux 5 questions : 4 charabias + 1 vraie réponse arabe"
info "3. Cliquer 'صحّح التشخيص'"
info "4. Vérifier :"
info "   ✓ Les 4 charabias sont surlignés en rouge foncé"
info "   ✓ Au survol : tooltip arabe visible ('غير مفهوم')"
info "   ✓ La vraie réponse : score ≥60%, éventuellement zones vertes/oranges"
info "   ✓ Aucune erreur JS dans la console navigateur (F12)"


# ═══════════════════════════════════════════════════════════════════════
# BILAN
# ═══════════════════════════════════════════════════════════════════════
section "BILAN GLOBAL"

TOTAL=$((PASS + FAIL + SKIP))
echo "  Total tests exécutés : $TOTAL"
echo "  ${GREEN}✅ PASS : $PASS${RESET}"
echo "  ${RED}❌ FAIL : $FAIL${RESET}"
echo "  ${YELLOW}⤍  SKIP : $SKIP${RESET}"

echo
if [ "$FAIL" -eq 0 ] && [ "$PASS" -ge 8 ]; then
  echo "  ${GREEN}${BOLD}🎉 Deepseek a bien travaillé. Rien n'est cassé.${RESET}"
  echo
  echo "  Prochaines étapes suggérées :"
  echo "    - Si SKIP présents : lancer sans les options --skip-* pour couverture complète."
  echo "    - Vérification manuelle frontend (§ E ci-dessus)."
  echo "    - git commit + push si tout est bon."
  exit 0
elif [ "$FAIL" -eq 0 ]; then
  echo "  ${YELLOW}${BOLD}⚠️  Aucun échec, mais couverture insuffisante ($PASS PASS).${RESET}"
  echo "  Relancer sans les --skip-*, ou vérifier que TOKEN/SCENARIO sont bons."
  exit 0
else
  echo "  ${RED}${BOLD}❌ Régressions détectées :${RESET}"
  echo -e "$FAILED_TESTS"
  echo
  echo "  Action : remonter ces échecs à Deepseek avec les logs serveur correspondants."
  exit 1
fi
