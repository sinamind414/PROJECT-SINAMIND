#!/usr/bin/env bash
# restore.sh — Khawarizmi Pro
# Usage: bash scripts/restore.sh <backup_file>
set -euo pipefail

if [ $# -lt 1 ]; then
  echo "Usage: bash scripts/restore.sh <backup_file.sql.gz>"
  echo "       bash scripts/restore.sh <backup_file.sql>"
  exit 1
fi

BACKUP_FILE="$1"
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_DIR="$(dirname "$SCRIPT_DIR")"
DB_URL="${DATABASE_URL:-postgresql://khawarizmi_user:khawarizmi_dev_pass_2024@localhost:5432/khawarizmi}"
LOG_FILE="/tmp/khawarizmi_restore_$(date +%Y%m%d_%H%M%S).log"

if [ ! -f "$BACKUP_FILE" ]; then
  echo "ERREUR: Fichier introuvable: $BACKUP_FILE"
  exit 1
fi

log() { echo "[$(date '+%Y-%m-%d %H:%M:%S')] $*" | tee -a "$LOG_FILE"; }

log "=== RESTAURATION KHAWARIZMI ==="
log "Source: $BACKUP_FILE"
log "Cible: $DB_URL"

# Extraire les credentials de DATABASE_URL
PGPASSWORD="${DB_URL#*://*:}" && PGPASSWORD="${PGPASSWORD%@*}"
PGUSER="${DB_URL#*://}" && PGUSER="${PGUSER%%:*}"
PGHOST="${DB_URL#*@}" && PGHOST="${PGHOST%%:*}"
PGPORT="${PGHOST##*:}" && PGPORT="${PGPORT%%/*}"
PGDATABASE="${DB_URL##*/}" && PGDATABASE="${PGDATABASE%%\?*}"

export PGPASSWORD

# Vérifier la connexion
pg_isready -h "$PGHOST" -p "$PGPORT" -U "$PGUSER" 2>/dev/null || {
  log "ERREUR: PostgreSQL inaccessible sur $PGHOST:$PGPORT"
  exit 1
}

# Demander confirmation
echo ""
echo "⚠️  ATTENTION: La base '$PGDATABASE' va être REMPLACÉE."
echo "   Toutes les données actuelles seront perdues."
read -rp "   Taper 'RESTORE' pour confirmer: " CONFIRM
if [ "$CONFIRM" != "RESTORE" ]; then
  log "Restauration annulée"
  exit 0
fi

# Restaurer
if [[ "$BACKUP_FILE" == *.gz ]]; then
  log "Décompression et restauration..."
  gunzip -c "$BACKUP_FILE" | pg_restore \
    --host="$PGHOST" \
    --port="$PGPORT" \
    --username="$PGUSER" \
    --dbname="$PGDATABASE" \
    --no-owner \
    --no-acl \
    --clean \
    --if-exists \
    --verbose 2>&1 | tee -a "$LOG_FILE"
else
  log "Restauration depuis fichier SQL..."
  psql -h "$PGHOST" -p "$PGPORT" -U "$PGUSER" -d "$PGDATABASE" -f "$BACKUP_FILE" 2>&1 | tee -a "$LOG_FILE"
fi

log "=== RESTAURATION TERMINÉE ==="
log "Log: $LOG_FILE"
