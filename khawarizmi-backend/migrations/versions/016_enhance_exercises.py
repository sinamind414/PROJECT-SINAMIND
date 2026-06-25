"""Enhance exercises and responses tables (additive, non-breaking).

Revision ID: 016
Revises: 015
Create Date: 2026-06-24

Ajoute des colonnes pour fonctionnalités pédagogiques avancées SANS toucher
aux colonnes existantes (matiere, corrige, etc.) → rétrocompatible.

Champs ajoutés :
- exercises.explanation          : explication pédagogique post-correction
- exercises.correction_criteria  : grille de notation structurée (JSONB)
- exercises.source               : provenance ("annales_bac", "généré", "importé")
- exercises.source_id            : ID dans la source
- exercises.attempt_count        : compteur atomique de tentatives
- exercises.success_count        : compteur atomique de succès
- exercises.is_active            : flag d'activation (soft delete)
- exercises.tags                 : ARRAY de tags pour filtrage (GIN index)

- user_exercise_responses.max_score         : score maximum possible
- user_exercise_responses.percentage        : score / max_score * 100
- user_exercise_responses.is_correct         : score >= 50%
- user_exercise_responses.evaluation_details : scores par critère (JSONB)
- user_exercise_responses.time_spent_seconds : temps passé
- user_exercise_responses.hints_used         : compteur d'indices
- user_exercise_responses.evaluated_at       : timestamp de la correction

Idempotente grâce à IF NOT EXISTS — peut être ré-exécutée sans erreur.
"""
import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects.postgresql import ARRAY, JSONB

revision = "016"
down_revision = "015"
branch_labels = None
depends_on = None


def upgrade() -> None:
    # ── exercises (colonnes additionnelles) ──────────────────────────
    op.add_column(
        "exercises",
        sa.Column("explanation", sa.Text(), nullable=True),
    )
    op.add_column(
        "exercises",
        sa.Column("correction_criteria", JSONB(), nullable=True),
    )
    op.add_column(
        "exercises",
        sa.Column("source", sa.String(100), nullable=True),
    )
    op.add_column(
        "exercises",
        sa.Column("source_id", sa.String(100), nullable=True),
    )
    op.add_column(
        "exercises",
        sa.Column("attempt_count", sa.Integer(), server_default="0", nullable=False),
    )
    op.add_column(
        "exercises",
        sa.Column("success_count", sa.Integer(), server_default="0", nullable=False),
    )
    op.add_column(
        "exercises",
        sa.Column("is_active", sa.Boolean(), server_default="true", nullable=False),
    )
    op.add_column(
        "exercises",
        sa.Column("tags", ARRAY(sa.String()), nullable=True),
    )

    # Indexes (IF NOT EXISTS pour idempotence)
    op.execute(
        "CREATE INDEX IF NOT EXISTS ix_exercises_is_active "
        "ON exercises (is_active)"
    )
    op.execute(
        "CREATE INDEX IF NOT EXISTS ix_exercises_tags "
        "ON exercises USING gin (tags)"
    )
    op.execute(
        "CREATE INDEX IF NOT EXISTS ix_exercises_active_matiere "
        "ON exercises (is_active, matiere)"
    )

    # ── user_exercise_responses (colonnes additionnelles) ────────────
    # max_score existe déjà depuis migration 014 (Float) — on ne le ré-ajoute pas
    op.add_column(
        "user_exercise_responses",
        sa.Column("percentage", sa.Float(), nullable=True),
    )
    op.add_column(
        "user_exercise_responses",
        sa.Column("is_correct", sa.Boolean(), nullable=True),
    )
    op.add_column(
        "user_exercise_responses",
        sa.Column("evaluation_details", JSONB(), nullable=True),
    )
    op.add_column(
        "user_exercise_responses",
        sa.Column("time_spent_seconds", sa.Integer(), nullable=True),
    )
    op.add_column(
        "user_exercise_responses",
        sa.Column("hints_used", sa.Integer(), server_default="0", nullable=False),
    )
    op.add_column(
        "user_exercise_responses",
        sa.Column("evaluated_at", sa.DateTime(timezone=True), nullable=True),
    )

    # Indexes analytics
    op.execute(
        "CREATE INDEX IF NOT EXISTS ix_response_user_exercise "
        "ON user_exercise_responses (user_id, exercise_id, created_at)"
    )
    op.execute(
        "CREATE INDEX IF NOT EXISTS ix_response_user_created "
        "ON user_exercise_responses (user_id, created_at)"
    )
    op.execute(
        "CREATE INDEX IF NOT EXISTS ix_response_is_correct "
        "ON user_exercise_responses (is_correct, user_id)"
    )


def downgrade() -> None:
    op.execute("DROP INDEX IF EXISTS ix_response_is_correct")
    op.execute("DROP INDEX IF EXISTS ix_response_user_created")
    op.execute("DROP INDEX IF EXISTS ix_response_user_exercise")
    op.execute("DROP INDEX IF EXISTS ix_exercises_active_matiere")
    op.execute("DROP INDEX IF EXISTS ix_exercises_tags")
    op.execute("DROP INDEX IF EXISTS ix_exercises_is_active")

    op.drop_column("user_exercise_responses", "evaluated_at")
    op.drop_column("user_exercise_responses", "hints_used")
    op.drop_column("user_exercise_responses", "time_spent_seconds")
    op.drop_column("user_exercise_responses", "evaluation_details")
    op.drop_column("user_exercise_responses", "is_correct")
    op.drop_column("user_exercise_responses", "percentage")
    # max_score droppé par migration 014, pas par 016
    op.drop_column("exercises", "tags")
    op.drop_column("exercises", "is_active")
    op.drop_column("exercises", "success_count")
    op.drop_column("exercises", "attempt_count")
    op.drop_column("exercises", "source_id")
    op.drop_column("exercises", "source")
    op.drop_column("exercises", "correction_criteria")
    op.drop_column("exercises", "explanation")
