"""Uniformise user_id en integer dans les tables DA/action-verbs.

Revision ID: 017_fix_user_id_types
Revises: 016_enhance_exercises
Create Date: 2026-06-24

Contexte :
  Les tables da_fsrs, da_sessions et action_verb_progress avaient user_id en UUID
  alors que toutes les autres tables (8+) utilisent integer. JWT retourne un entier
  → erreur 500 sur tout endpoint requêtant ces tables.

  Les colonnes sont vides (pas de données seed avant cette migration), donc
  USING (0) est sûr.
"""

from alembic import op

revision = "017_fix_user_id_types"
down_revision = "016"
branch_labels = None
depends_on = None


def upgrade():
    op.execute("""
        ALTER TABLE da_fsrs
        ALTER COLUMN user_id TYPE integer
        USING (0)
    """)
    op.execute("""
        ALTER TABLE da_sessions
        ALTER COLUMN user_id TYPE integer
        USING (0)
    """)
    op.execute("""
        ALTER TABLE action_verb_progress
        ALTER COLUMN user_id TYPE integer
        USING (0)
    """)


def downgrade():
    # Pas de retour en arrière : une fois en integer on perd l'info UUID.
    # Si nécessaire, recréer les colonnes en UUID via add_column.
    pass
