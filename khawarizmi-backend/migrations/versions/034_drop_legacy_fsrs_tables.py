"""034 : suppression des tables FSRS héritées (da_fsrs, action_verb_progress).

Contexte (S3 finale) : depuis la fusion 033, mastery_micro_concepts est la
table mémoire UNIQUE — toutes les écritures passent par services/fsrs_unified.py
(mastery-first) et toutes les lectures aussi (les lectures analytics restantes
ont été migrées : city_service.get_national_stats lit désormais mastery avec
source='verb_action'). Les tables da_fsrs et action_verb_progress ne sont plus
que des cibles de fallback pour les environnements pré-033.

Cette migration :
  1. Re-backfille vers mastery TOUT ce qui manquerait encore depuis les tables
     héritées (idempotent — WHERE NOT EXISTS ; exécuté seulement si la table
     contient des lignes).
  2. DROP TABLE da_fsrs + action_verb_progress.

Sécurité :
  - Tables vides ou absentes → drop sans risque (rien à perdre).
  - Tables non vides mais backfill en échec (ex. Postgres : user_id UUID
    non convertible en INTEGER — les écritures legacy ont historiquement
    échoué sur ce cast) → la migration ABORTE avec un message explicite :
    jamais de perte de données silencieuse.

downgrade : recrée les deux tables (schémas 008/009 + index 031) puis
re-backfille DEPUIS mastery (inverse). NOTE : user_id est recréé en INTEGER
(aligné sur users.id — les schémas d'origine déclaraient UUID, ce qui
empêchait toute écriture legacy avec les ids entiers de l'app) et
action_verb_progress reçoit avg_pct/total_users (lus par le fallback
fsrs_unified).

⚠️ Postgres-only (les migrations Alembic du projet le sont — CREATE EXTENSION
vector en 001). En preview SQLite, l'auto-DDL de database.py conserve les
tables héritées (simulation d'un environnement pré-033 : les fallbacks y
restent testables).
"""

import logging
import uuid

import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision = "034"
down_revision = "033"
branch_labels = None
depends_on = None

logger = logging.getLogger("khawarizmi.migrations")


# ── Backfills upgrade (héritées → mastery) ───────────────────────────

def _count(conn, table: str) -> int:
    try:
        return int(conn.execute(sa.text(f"SELECT COUNT(*) FROM {table}")).scalar() or 0)
    except Exception:
        # Table absente (environnement où elle n'a jamais été créée) → 0
        return 0


def _backfill_da_fsrs(conn) -> None:
    """da_fsrs (verbe/chapitre) → mastery source='verb_chapter'."""
    if _count(conn, "da_fsrs") == 0:
        logger.info("034: da_fsrs vide ou absente — rien à backfiller")
        return
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
        logger.info("034: backfill da_fsrs → mastery OK")
    except Exception as e:
        raise RuntimeError(
            "034: backfill da_fsrs → mastery IMPOSSIBLE — la table contient "
            f"des lignes non fusionnées. ABORT (ne pas dropper). Cause : {e}"
        ) from e


def _backfill_avp(conn) -> None:
    """action_verb_progress (verbe) → mastery source='verb_action'.

    Deux variantes : avec avg_pct/total_users (SQLite auto-DDL, Postgres
    enrichi) puis sans (schéma Postgres 008 d'origine, colonnes absentes).
    """
    if _count(conn, "action_verb_progress") == 0:
        logger.info("034: action_verb_progress vide ou absente — rien à backfiller")
        return

    base = """
        INSERT INTO mastery_micro_concepts
            (user_id, micro_concept_id, concept_id, chapter,
             stability, difficulty, fsrs_state, prochaine_revision,
             interval_jours, last_score, attempts, last_review,
             {extra_cols}source, item_key, updated_at)
        SELECT
            CAST(user_id AS INTEGER), 'va_' || verb_slug, 'va_' || verb_slug,
            NULL, stability, difficulty, fsrs_state, prochaine_revision,
            interval_jours, last_score, attempts, NULL,
            {extra_vals}'verb_action', verb_slug, CURRENT_TIMESTAMP
        FROM action_verb_progress
        WHERE NOT EXISTS (
            SELECT 1 FROM mastery_micro_concepts mmc
            WHERE mmc.user_id = CAST(action_verb_progress.user_id AS INTEGER)
              AND mmc.concept_id = 'va_' || action_verb_progress.verb_slug
        )
    """
    try:
        conn.execute(sa.text(base.format(
            extra_cols="avg_pct, total_users, ",
            extra_vals="avg_pct, total_users, ",
        )))
        logger.info("034: backfill action_verb_progress → mastery OK (avec avg_pct/total_users)")
    except Exception as e1:
        # Colonnes absentes (Postgres 008) → re-tentative sans elles
        try:
            conn.execute(sa.text(base.format(extra_cols="", extra_vals="")))
            logger.info("034: backfill action_verb_progress → mastery OK (sans avg_pct/total_users)")
        except Exception as e2:
            raise RuntimeError(
                "034: backfill action_verb_progress → mastery IMPOSSIBLE — la table "
                "contient des lignes non fusionnées. ABORT (ne pas dropper). "
                f"Cause : {e2}"
            ) from e2


def upgrade() -> None:
    conn = op.get_bind()

    # 1. Re-backfill de rattrapage (idempotent, sécurisé)
    _backfill_da_fsrs(conn)
    _backfill_avp(conn)

    # 2. Suppression des tables héritées
    op.execute("DROP TABLE IF EXISTS da_fsrs")
    op.execute("DROP TABLE IF EXISTS action_verb_progress")
    logger.info("034: tables héritées da_fsrs / action_verb_progress supprimées")


# ── Downgrade (restauration) ─────────────────────────────────────────

def _restore_legacy(conn) -> None:
    """Re-backfill les tables héritées DEPUIS mastery (inverse du upgrade).

    Boucle Python : portable SQLite/Postgres, ids générés côté client
    (gen_random_uuid() est Postgres-only).
    """
    # da_fsrs : mastery source='verb_chapter' → da_fsrs
    rows = conn.execute(sa.text("""
        SELECT user_id, item_key, chapter, stability, difficulty, fsrs_state,
               prochaine_revision, interval_jours, last_score, attempts,
               last_review
        FROM mastery_micro_concepts
        WHERE source = 'verb_chapter'
    """)).fetchall()
    for r in rows:
        item_key = r[1] or ""
        verb, _, chapter = item_key.partition("::")
        conn.execute(sa.text("""
            INSERT INTO da_fsrs
                (id, user_id, verb_slug, chapter_slug, stability, difficulty,
                 fsrs_state, prochaine_revision, interval_jours, last_score,
                 attempts, last_review, created_at, updated_at)
            VALUES
                (:id, :uid, :verb, :chapter, :stability, :difficulty, :fsrs,
                 :due, :interval, :score, :attempts, :last_review,
                 CURRENT_TIMESTAMP, CURRENT_TIMESTAMP)
        """), {
            "id": str(uuid.uuid4()), "uid": r[0], "verb": verb or r[2] or "",
            "chapter": chapter or r[2] or "",
            "stability": float(r[3] or 0.0), "difficulty": float(r[4] or 0.0),
            "fsrs": r[5] or "{}", "due": r[6],
            "interval": float(r[7] or 0.0), "score": r[8],
            "attempts": int(r[9] or 0), "last_review": r[10],
        })
    logger.info("034 (downgrade): da_fsrs restaurée (%d lignes)", len(rows))

    # action_verb_progress : mastery source='verb_action' → avp
    rows = conn.execute(sa.text("""
        SELECT user_id, item_key, stability, difficulty, fsrs_state,
               prochaine_revision, interval_jours, last_score, attempts,
               avg_pct, total_users
        FROM mastery_micro_concepts
        WHERE source = 'verb_action'
    """)).fetchall()
    for r in rows:
        conn.execute(sa.text("""
            INSERT INTO action_verb_progress
                (id, user_id, verb_slug, stability, difficulty, fsrs_state,
                 prochaine_revision, interval_jours, last_score, attempts,
                 avg_pct, total_users, updated_at, created_at)
            VALUES
                (:id, :uid, :verb, :stability, :difficulty, :fsrs, :due,
                 :interval, :score, :attempts, :avg_pct, :total_users,
                 CURRENT_TIMESTAMP, CURRENT_TIMESTAMP)
        """), {
            "id": str(uuid.uuid4()), "uid": r[0], "verb": r[1] or "",
            "stability": float(r[2] or 0.0), "difficulty": float(r[3] or 0.0),
            "fsrs": r[4] or "{}", "due": r[5],
            "interval": float(r[6] or 0.0), "score": r[7],
            "attempts": int(r[8] or 0),
            "avg_pct": r[9], "total_users": r[10],
        })
    logger.info("034 (downgrade): action_verb_progress restaurée (%d lignes)", len(rows))


def downgrade() -> None:
    conn = op.get_bind()

    # 1. Recréation (schémas 008/009 + index 031 ; user_id en INTEGER, voir docstring)
    op.create_table(
        "da_fsrs",
        sa.Column("id", sa.UUID(as_uuid=True), primary_key=True,
                  server_default=sa.text("gen_random_uuid()")),
        sa.Column("user_id", sa.Integer(), nullable=False, index=True),
        sa.Column("verb_slug", sa.String(50), nullable=False),
        sa.Column("chapter_slug", sa.String(200), nullable=False),
        sa.Column("stability", sa.Float, server_default="0.0"),
        sa.Column("difficulty", sa.Float, server_default="0.0"),
        sa.Column("fsrs_state", sa.JSON(), server_default="{}"),
        sa.Column("prochaine_revision", sa.DateTime(timezone=True)),
        sa.Column("interval_jours", sa.Float, server_default="0.0"),
        sa.Column("last_score", sa.Integer, server_default="0"),
        sa.Column("attempts", sa.Integer, server_default="0"),
        sa.Column("last_review", sa.DateTime(timezone=True)),
        sa.Column("created_at", sa.DateTime(timezone=True),
                  server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime(timezone=True),
                  server_default=sa.func.now(), onupdate=sa.func.now()),
        sa.UniqueConstraint("user_id", "verb_slug", "chapter_slug",
                            name="uq_da_fsrs_user_verb_chapter"),
    )
    op.create_table(
        "action_verb_progress",
        sa.Column("id", sa.UUID(as_uuid=True), primary_key=True,
                  server_default=sa.text("gen_random_uuid()")),
        sa.Column("user_id", sa.Integer(), nullable=False, index=True),
        sa.Column("verb_slug", sa.String(50), nullable=False),
        sa.Column("stability", sa.Float, server_default="0.0"),
        sa.Column("difficulty", sa.Float, server_default="0.0"),
        sa.Column("fsrs_state", sa.JSON(), server_default="{}"),
        sa.Column("prochaine_revision", sa.DateTime(timezone=True)),
        sa.Column("interval_jours", sa.Float, server_default="0.0"),
        sa.Column("last_score", sa.Integer, server_default="0"),
        sa.Column("attempts", sa.Integer, server_default="0"),
        sa.Column("avg_pct", sa.Float(), nullable=True),
        sa.Column("total_users", sa.Integer(), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True),
                  server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime(timezone=True),
                  server_default=sa.func.now(), onupdate=sa.func.now()),
        sa.UniqueConstraint("user_id", "verb_slug",
                            name="uq_verb_progress_user_verb"),
    )
    op.execute(
        "CREATE UNIQUE INDEX IF NOT EXISTS ux_da_fsrs_user_verb_chapter "
        "ON da_fsrs(user_id, verb_slug, chapter_slug)"
    )

    # 2. Re-backfill depuis mastery
    _restore_legacy(conn)
    logger.info("034 (downgrade): tables héritées restaurées")
