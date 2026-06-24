#!/usr/bin/env bash
# install-hooks.sh — Installation des hooks pre-commit pour Khawarizmi Pro
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_DIR="$(dirname "$SCRIPT_DIR")"

echo "=== Khawarizmi Pro — Installation Pre-commit ==="
echo ""

cd "$PROJECT_DIR"

# Vérifier pre-commit
if ! command -v pre-commit &>/dev/null; then
    echo "[1/3] Installation de pre-commit..."
    pip install pre-commit
else
    echo "[1/3] pre-commit déjà installé ✓"
fi

# Vérifier ruff
if ! command -v ruff &>/dev/null; then
    echo "[2/3] Installation de ruff..."
    pip install ruff
else
    echo "[2/3] ruff déjà installé ✓"
fi

# Installer les hooks
echo "[3/3] Installation des hooks..."
pre-commit install --hook-type pre-commit --hook-type pre-push

echo ""
echo "=== Installation terminée ==="
echo ""
echo "Prochaines étapes :"
echo "  1. pre-commit run --all-files   # Premier formatage"
echo "  2. git add -A                     # Re-stage"
echo "  3. pre-commit run --all-files   # Vérification finale"
echo "  4. git commit -m 'fix: format initial'"
echo ""
