"""033 : fusion FSRS — mastery_micro_concepts devient la table mémoire unique (S3c).

Contexte (audit S3) : 3 tables d'état FSRS cohabitent :
  - mastery_micro_concepts (par micro-concept)
  - da_fsrs (par verbe/chapitre — analyse de documents)
  - action_verb_progress (par verbe d'action)

L'API unifiée (services/fsrs_unified.py) expose déjà une vue consolidée et
toutes les écritures passent par elle. Cette migration ajoute à
mastery_micro_concepts les colonnes nécessaires pour absorber les 2 autres
tables SANS perte, puis backfille depuis les sources. Les tables da_fsrs et
action_verb_progress sont CONSERVÉES (lectures analytics existantes) mais ne
sont plus la source d'écriture.

Colonnes ajoutées (pour la fusion) :
  - source TEXT DEFAULT 'concept'    — 'concept' | 'verb_chapter' | 'verb_action'
  - item_key TEXT                    — identifiant métier (verb::chapter, verb)
  - avg_pct REAL                     — action_verb_progress.avg_pct
  - total_users INTEGER              — action_verb_progress.total_users

Le backfill :
  - da_fsrs → source='verb_chapter', item_key = verb_slug || '::' || chapter_slug
  - action_verb_progress → source='verb_action', item_key = verb_slug

⚠️ Postgres-only (les migrations Alembic du projet le sont — CREATE EXTENSION
vector en 001). En preview SQLite, l'auto-DDL de database.py doit être mis à
jour en parallèle (voir database.py).
"""

import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision = "033"
down_revision = "032"
branch_labels = None
depends_on = None


def upgrade() -> None:
    conn = op.get_bind()

    # ── 1. Colonnes de fusion ───────────────────────────────────────
    op.add_column("mastery_micro_concepts", sa.Column("source", sa.String(20),
                                                      server_default="concept",
                                                      nullable=False))
    op.add_column("mastery_micro_concepts", sa.Column("item_key", sa.String(120),
                                                      nullable=True))
    op.add_column("mastery_micro_concepts", sa.Column("avg_pct", sa.Float(),
                                                      nullable=True))
    op.add_column("mastery_micro_concepts", sa.Column("total_users", sa.Integer(),
                                                      nullable=True))

    # ── 2. Backfill depuis da_fsrs (verbe/chapitre) ─────────────────
    try:
        conn.execute(sa.text("""
            INSERT INTO mastery_micro_concepts
                (user_id, micro_concept_id, concept_id, chapter,
                 stability, difficulty, fsrs_state, prochaine_revision,
                 interval_jours, last_score, attempts, last_review,
                 source, item_key, updated_at)
            SELECT
                CAST(user_id AS INTEGER), 'vc_' || verb_slug || '_' || chapter_slug,
                'vc_' || verb_slug || '_' || chapter_slug, chapter_slug,
                stability, difficulty, fsrs_state, prochaine_revision,
                interval_jours, last_score, attempts, last_review,
                'verb_chapter', verb_slug || '::' || chapter_slug, CURRENT_TIMESTAMP
            FROM da_fsrs
            WHERE NOT EXISTS (
                SELECT 1 FROM mastery_micro_concepts mmc
                WHERE mmc.user_id = CAST(da_fsrs.user_id AS INTEGER)
                  AND mmc.concept_id = 'vc_' || da_fsrs.verb_slug || '_' || da_fsrs.chapter_slug
            )
        """))
        logger.info("033: backfill da_fsrs OK")
    except Exception as e:
        logger.warning(f"033: backfill da_fsrs ignoré ({e}) — table absente ?")

    # ── 3. Backfill depuis action_verb_progress (verbe d'action) ────
    try:
        conn.execute(sa.text("""
            INSERT INTO mastery_micro_concepts
                (user_id, micro_concept_id, concept_id, chapter,
                 stability, difficulty, fsrs_state, prochaine_revision,
                 interval_jours, last_score, attempts, last_review,
                 avg_pct, total_users, source, item_key, updated_at)
            SELECT
                CAST(user_id AS INTEGER), 'va_' || verb_slug, 'va_' || verb_slug,
                NULL, stability, difficulty, fsrs_state, prochaine_revision,
                interval_jours, last_score, attempts, NULL,
                avg_pct, total_users, 'verb_action', verb_slug, CURRENT_TIMESTAMP
            FROM action_verb_progress
            WHERE NOT EXISTS (
                SELECT 1 FROM mastery_micro_concepts mmc
                WHERE mmc.user_id = CAST(action_verb_progress.user_id AS INTEGER)
                  AND mmc.concept_id = 'va_' || action_verb_progress.verb_slug
            )
        """))
        logger.info("033: backfill action_verb_progress OK")
    except Exception as e:
        logger.warning(f"033: backfill action_verb_progress ignoré ({e}) — table absente ?")

    # ── 4. Index de lecture par source (requêtes analytics) ─────────
    op.execute(
        "CREATE INDEX IF NOT EXISTS ix_mastery_source_item "
        "ON mastery_micro_concepts(user_id, source, item_key)"
    )


def downgrade() -> None:
    op.execute("DROP INDEX IF EXISTS ix_mastery_source_item")
    op.drop_column("mastery_micro_concepts", "total_users")
    op.drop_column("mastery_micro_concepts", "avg_pct")
    op.drop_column("mastery_micro_concepts", "item_key")
    op.drop_column("mastery_micro_concepts", "source")


import logging

logger = logging.getLogger("khawarizmi.migrations")
