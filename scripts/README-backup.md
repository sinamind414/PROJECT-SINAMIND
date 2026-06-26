# Backup & Récupération — Khawarizmi Pro

## Scripts

| Script | Rôle |
|--------|------|
| `backup.sh` | Backup PostgreSQL → fichier compressé local (+ S3 optionnel) |
| `restore.sh` | Restauration complète depuis un backup |
| `install-backup-cron.sh` | Installation de la tâche CRON quotidienne |

## Utilisation

```bash
# Backup local simple
bash scripts/backup.sh

# Backup local + copie S3
export S3_BUCKET=s3://mon-bucket-backups
bash scripts/backup.sh --s3

# Installer le CRON (root requis)
sudo bash scripts/install-backup-cron.sh

# Restaurer un backup
bash scripts/restore.sh backups/khawarizmi_backup_20260624_030000.sql.gz
```

## Configuration

Variables d'environnement (ou `.env`) :

| Variable | Défaut | Description |
|----------|--------|-------------|
| `BACKUP_DIR` | `./backups` | Dossier de stockage |
| `RETENTION_DAYS` | `7` | Jours de rétention |
| `DATABASE_URL` | (obligatoire) | URL de connexion PostgreSQL |
| `S3_BUCKET` | — | Bucket S3 pour backup distant |

## Rétention

- **7 jours** : backups conservés par défaut
- **Rotation automatique** : les backups > 7 jours sont supprimés
- **Backup S3 hebdomadaire** : le dimanche à 04h00 (via CRON)
- **S3** : stockage illimité (coût ~$0.023/GB/mois)

## Restauration en production

```bash
# 1. Stopper le backend
docker stop khawarizmi_backend

# 2. Restaurer la base
export DATABASE_URL="postgresql://user:password@localhost:5432/khawarizmi"
bash scripts/restore.sh backup.sql.gz

# 3. Forcer la version Alembic (si nécessaire)
psql $DATABASE_URL -c "UPDATE alembic_version SET version_num = '016'"

# 4. Redémarrer
docker start khawarizmi_backend
```

## Disaster Recovery Plan

1. **Perdu la base ?** → `bash scripts/restore.sh dernier_backup.sql.gz`
2. **Perdu le serveur ?** → `docker compose up -d` → restaurer depuis S3
3. **Perdu S3 + local ?** → `bash scripts/seed.sh` (données minimales) + re-sync depuis les élèves
