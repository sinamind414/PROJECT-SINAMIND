#!/usr/bin/env bash
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
SRC="$ROOT/GENZ_SVT_INNOVATIONS_EXECUTE_ONLY/files"
copy_file() {
  local rel="$1"
  mkdir -p "$(dirname "$ROOT/$rel")"
  cp "$SRC/$rel" "$ROOT/$rel"
  echo "OK $rel"
}
copy_file "khawarizmi-frontend/src/lib/svt-quiz-bank.ts"
copy_file "khawarizmi-frontend/src/components/learning/InstantQuizButton.tsx"
copy_file "khawarizmi-frontend/src/components/learning/ProgressiveReveal.tsx"
copy_file "khawarizmi-frontend/src/components/learning/FlashChallenge.tsx"
copy_file "khawarizmi-frontend/src/components/learning/HintButton.tsx"
copy_file "khawarizmi-frontend/src/components/learning/SVTProgressMap.tsx"
copy_file "khawarizmi-frontend/src/components/learning/GenZLabWidget.tsx"
copy_file "khawarizmi-frontend/src/components/simulations/EnzymeActivitySimulator.tsx"
copy_file "khawarizmi-frontend/src/app/exercises/page.tsx"
copy_file "khawarizmi-frontend/src/app/dashboard/page.tsx"
echo "DONE: Gen Z SVT interactive learning features copied exactly."
