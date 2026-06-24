#!/usr/bin/env bash
# install-backup-cron.sh — Khawarizmi Pro
# Installe la tâche CRON pour backup quotidien à 03h00
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
BACKUP_SCRIPT="$SCRIPT_DIR/backup.sh"
CRON_FILE="/etc/cron.d/khawarizmi-backup"

if [ ! -f "$BACKUP_SCRIPT" ]; then
  echo "ERREUR: backup.sh introuvable dans $SCRIPT_DIR"
  exit 1
fi

chmod +x "$BACKUP_SCRIPT"

echo "=== Installation du CRON de backup Khawarizmi ==="

# Installation en mode root (via sudo) ou user
if [ "$(id -u)" -eq 0 ]; then
  cat > "$CRON_FILE" <<CRON
# Khawarizmi Pro — Backup quotidien
# Installé le $(date '+%Y-%m-%d %H:%M')
SHELL=/bin/bash
PATH=/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin

# Backup quotidien à 03h00
0 3 * * * root bash $BACKUP_SCRIPT --local >> /var/log/khawarizmi_backup.log 2>&1

# Backup S3 le dimanche à 04h00 (si S3_BUCKET configuré)
0 4 * * 0 root bash $BACKUP_SCRIPT --s3 >> /var/log/khawarizmi_backup_s3.log 2>&1
CRON
  chmod 644 "$CRON_FILE"
  echo "CRON installé: $CRON_FILE"
  echo "  - Quotidien à 03h00 (backup local)"
  echo "  - Dimanche à 04h00 (backup S3)"
else
  echo "Mode user — installation dans crontab utilisateur"
  (crontab -l 2>/dev/null || true; echo "0 3 * * * bash $BACKUP_SCRIPT --local >> /tmp/khawarizmi_backup.log 2>&1") | crontab -
  echo "Crontab utilisateur mise à jour"
fi

echo ""
echo "Pour tester: bash $BACKUP_SCRIPT"
echo "Logs: /var/log/khawarizmi_backup.log (root) ou /tmp/khawarizmi_backup.log (user)"
