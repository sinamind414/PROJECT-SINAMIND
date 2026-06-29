"""Widen micro_concept_id columns to VARCHAR(200)

Revision ID: 024
Revises: 023
Create Date: 2026-06-29

RÈGLE : les question_ids composés (sujet_id:ex_id:q_id) atteignent 96 caractères
alors que micro_concept_id était VARCHAR(50) → overflow PostgreSQL → 500 sur
/api/drill/result. On élargit à 200 sur mastery_micro_concepts et lexique_termes.
"""
from alembic import op

revision = '024'
down_revision = '023'
branch_labels = None
depends_on = None


def upgrade():
    op.execute(
        "ALTER TABLE mastery_micro_concepts "
        "ALTER COLUMN micro_concept_id TYPE VARCHAR(200)"
    )
    op.execute(
        "ALTER TABLE lexique_termes "
        "ALTER COLUMN micro_concept_id TYPE VARCHAR(200)"
    )


def downgrade():
    op.execute(
        "ALTER TABLE lexique_termes "
        "ALTER COLUMN micro_concept_id TYPE VARCHAR(50)"
    )
    op.execute(
        "ALTER TABLE mastery_micro_concepts "
        "ALTER COLUMN micro_concept_id TYPE VARCHAR(50)"
    )
