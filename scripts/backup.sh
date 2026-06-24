#!/usr/bin/env bash
# backup.sh — Khawarizmi Pro
# Usage: bash scripts/backup.sh [--s3] [--local]
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_DIR="$(dirname "$SCRIPT_DIR")"

BACKUP_DIR="${BACKUP_DIR:-$PROJECT_DIR/backups}"
RETENTION_DAYS="${RETENTION_DAYS:-7}"
DB_URL="${DATABASE_URL:-postgresql://khawarizmi_user:khawarizmi_dev_pass_2024@localhost:5432/khawarizmi}"
TIMESTAMP="$(date +%Y%m%d_%H%M%S)"
FILENAME="khawarizmi_backup_${TIMESTAMP}.sql.gz"
LOG_FILE="$BACKUP_DIR/backup.log"

mkdir -p "$BACKUP_DIR"

log() { echo "[$(date '+%Y-%m-%d %H:%M:%S')] $*" | tee -a "$LOG_FILE"; }

log "Début du backup : $FILENAME"

# Backup PostgreSQL via pg_dump
PGPASSWORD="${DB_URL#*://*:}" && PGPASSWORD="${PGPASSWORD%@*}"
PGUSER="${DB_URL#*://}" && PGUSER="${PGUSER%%:*}"
PGHOST="${DB_URL#*@}" && PGHOST="${PGHOST%%:*}"
PGPORT="${PGHOST##*:}" && PGPORT="${PGPORT%%/*}"
PGDATABASE="${DB_URL##*/}" && PGDATABASE="${PGDATABASE%%\?*}"

pg_dump \
  --host="$PGHOST" \
  --port="$PGPORT" \
  --username="$PGUSER" \
  --dbname="$PGDATABASE" \
  --no-owner \
  --no-acl \
  --format=custom \
  --file="${BACKUP_DIR}/${FILENAME%.gz}" \
  2>>"$LOG_FILE"

gzip "${BACKUP_DIR}/${FILENAME%.gz}"
log "Backup terminé : $(du -h "${BACKUP_DIR}/${FILENAME}" | cut -f1)"

# Nettoyage des backups vieux de plus de RETENTION_DAYS jours
find "$BACKUP_DIR" -name "khawarizmi_backup_*.sql.gz" -mtime "+${RETENTION_DAYS}" -delete 2>/dev/null
log "Backups > ${RETENTION_DAYS} jours supprimés"

# Copy to S3-compatible storage if --s3 flag
if [ "${1:-}" = "--s3" ] && [ -n "${S3_BUCKET:-}" ]; then
  if command -v aws &>/dev/null; then
    aws s3 cp "${BACKUP_DIR}/${FILENAME}" "${S3_BUCKET}/khawarizmi/${FILENAME}" --only-show-errors 2>>"$LOG_FILE"
    log "Copie S3 : ${S3_BUCKET}/khawarizmi/${FILENAME}"
  else
    log "WARNING: aws CLI non installé, backup S3 ignoré"
  fi
fi

# Rotation : garder 1 backup par jour pour les 30 derniers jours
# (les backups plus vieux que RETENTION_DAYS sont déjà supprimés)
log "Backup terminé avec succès"
