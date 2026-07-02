#!/usr/bin/env bash
# Verification end-to-end de POST /api/document-analysis/evaluate-v2.
# Teste les 5 charabias d'origine, une reponse vide et 2 reponses plausibles.
#
# Usage:
#   API_URL=https://votre-api.com TOKEN=votre_jwt SCENARIO=slug ./scripts/verify_corrector_v2.sh
#   API_URL=https://votre-api.com TOKEN=votre_jwt SCENARIO=slug ./scripts/verify_corrector_v2.sh --dry-run

set -u

API_URL="${API_URL:-http://localhost:8000}"
TOKEN="${TOKEN:-}"
SCENARIO="${SCENARIO:-}"
DRY_RUN=0

for arg in "$@"; do
  case "$arg" in
    --dry-run) DRY_RUN=1 ;;
    -h|--help)
      grep '^#' "$0" | sed 's/^# \{0,1\}//'
      exit 0
      ;;
    *)
      echo "Unknown argument: $arg" >&2
      exit 2
      ;;
  esac
done

missing=""
[ -z "$TOKEN" ] && missing="$missing TOKEN"
[ -z "$SCENARIO" ] && missing="$missing SCENARIO"
if [ -n "$missing" ] && [ "$DRY_RUN" -eq 0 ]; then
  echo "ERROR: missing variables:$missing"
  echo "Example: TOKEN=eyJhbGc... SCENARIO=proteines-01 ./scripts/verify_corrector_v2.sh"
  echo "Dry-run: ./scripts/verify_corrector_v2.sh --dry-run"
  exit 2
fi

command -v curl >/dev/null || { echo "ERROR: curl is missing"; exit 3; }
if ! command -v jq >/dev/null; then
  echo "WARN: jq is missing; request bodies use a minimal JSON fallback"
fi

# Format: name|verb_slug|answer|expected_source_regex|expected_max_pct
CASES=(
  "Q1_charabia_analyse|analyse|ERRETREZR|sanity|0"
  "Q2_charabia_interpret|interpret|EREZREZT|sanity|0"
  "Q3_charabia_deduce|deduce|?KJ YBYUTIUJPO?K?PO|sanity|0"
  "Q4_charabia_hypothesis|hypothesis|BVCGGCVUVUY|sanity|0"
  "Q5_charabia_scientific-text|scientific-text|ZEZREZTERT|sanity|0"
  "Q6_reponse_vide|deduce||sanity|0"
  "Q7_hypothese_correcte|hypothesis|نفترض أن انخفاض البروتين الوظيفي عند الشخص المصاب يعود إلى حدوث تغير في المورثة يؤدي إلى إنتاج ARNm غير عادي.|llm|100"
  "Q8_hypothese_partielle|hypothesis|نفترض أن هناك مشكلة في المورثة.|llm|100"
)

pass=0
fail=0
suspect=0

check_result() {
  local name="$1" json="$2" expected_source="$3" expected_max_pct="$4"

  if [ -z "$json" ]; then
    echo "  FAIL $name: empty response"
    fail=$((fail + 1))
    return
  fi

  if ! command -v jq >/dev/null; then
    echo "  WARN $name: cannot parse response because jq is missing"
    echo "       Raw: $(printf '%s' "$json" | head -c 300)"
    suspect=$((suspect + 1))
    return
  fi

  local err
  err=$(printf '%s' "$json" | jq -r '.detail // empty' 2>/dev/null)
  if [ -n "$err" ]; then
    echo "  FAIL $name: API error - $err"
    fail=$((fail + 1))
    return
  fi

  local source pct hl_count
  source=$(printf '%s' "$json" | jq -r '.evaluations[0].source // "?"' 2>/dev/null)
  pct=$(printf '%s' "$json" | jq -r '.evaluations[0].percentage // -1' 2>/dev/null)
  hl_count=$(printf '%s' "$json" | jq -r '.evaluations[0].highlights | length // 0' 2>/dev/null)

  local ok_source=1
  printf '%s' "$source" | grep -qE "^$expected_source$" || ok_source=0

  local ok_score=1
  [ "$pct" = "-1" ] && ok_score=0
  [ "$expected_max_pct" = "0" ] && [ "$pct" != "0" ] && ok_score=0

  if [ "$ok_source" -eq 1 ] && [ "$ok_score" -eq 1 ]; then
    echo "  PASS $name: source=$source pct=$pct% highlights=$hl_count"
    pass=$((pass + 1))
  else
    echo "  SUSPECT $name: source=$source expected=$expected_source pct=$pct max_expected=$expected_max_pct"
    echo "          JSON: $(printf '%s' "$json" | jq -c '.evaluations[0] // .' 2>/dev/null | head -c 300)"
    suspect=$((suspect + 1))
  fi
}

json_escape_fallback() {
  printf '%s' "$1" | sed 's/\\/\\\\/g; s/"/\\"/g'
}

build_body() {
  local verb_slug="$1" answer="$2"

  if command -v jq >/dev/null; then
    jq -nc \
      --arg s "$SCENARIO" \
      --arg v "$verb_slug" \
      --arg a "$answer" \
      '{scenario_id: $s, chapter_slug: null, answers: [{verb_slug: $v, answer: $a}]}'
  else
    local esc_s esc_v esc_a
    esc_s=$(json_escape_fallback "$SCENARIO")
    esc_v=$(json_escape_fallback "$verb_slug")
    esc_a=$(json_escape_fallback "$answer")
    printf '{"scenario_id":"%s","chapter_slug":null,"answers":[{"verb_slug":"%s","answer":"%s"}]}' "$esc_s" "$esc_v" "$esc_a"
  fi
}

send_request() {
  local body="$1"

  curl -sS -X POST "$API_URL/api/document-analysis/evaluate-v2" \
    -H "Authorization: Bearer $TOKEN" \
    -H "Content-Type: application/json" \
    -d "$body"
}

echo "==================================================================="
echo "  Verification Correcteur V2"
echo "  API      : $API_URL/api/document-analysis/evaluate-v2"
echo "  Scenario : $SCENARIO"
[ "$DRY_RUN" -eq 1 ] && echo "  Mode     : dry-run"
echo "==================================================================="

for spec in "${CASES[@]}"; do
  IFS='|' read -r name verb answer expected_source expected_max <<< "$spec"
  body=$(build_body "$verb" "$answer")

  echo
  echo "> $name"
  echo "  verb=$verb answer=$(printf '%s' "$answer" | head -c 60)"

  if [ "$DRY_RUN" -eq 1 ]; then
    echo "  body=$body"
    continue
  fi

  json=$(send_request "$body")
  check_result "$name" "$json" "$expected_source" "$expected_max"
done

echo
echo "==================================================================="
if [ "$DRY_RUN" -eq 1 ]; then
  echo "  Dry-run complete: 8 cases listed."
  exit 0
fi

total=$((pass + suspect + fail))
echo "  Summary: $pass PASS, $suspect SUSPECT, $fail FAIL, total $total"
echo "==================================================================="
echo

if [ "$fail" -gt 0 ]; then
  echo "FAILURES detected: route v2 did not respond correctly."
  echo "Check app status, JWT token validity, and scenario_id."
  exit 1
fi

if [ "$suspect" -gt 0 ]; then
  echo "SUSPECT behavior detected."
  echo "If Q1-Q5 have pct>0, sanity check is not blocking gibberish."
  echo "If Q7-Q8 have source=sanity, the LLM path may be unavailable."
  exit 1
fi

echo "All cases are conforming. The gibberish bug is fixed on route v2."
exit 0
