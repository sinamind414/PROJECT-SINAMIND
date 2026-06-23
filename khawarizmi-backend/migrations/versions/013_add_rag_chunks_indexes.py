"""Add indexes to rag_chunks table

Revision ID: 013
Revises: 012
"""
from alembic import op
import sqlalchemy as sa

revision = '013'
down_revision = '012'
branch_labels = None
depends_on = None


def upgrade():
    op.create_index(
        "idx_rag_chunks_chapitre",
        "rag_chunks",
        ["chapitre"]
    )
    op.execute(
        "CREATE INDEX idx_rag_chunks_chapitre_lower "
        "ON rag_chunks (LOWER(chapitre))"
    )
    op.create_index(
        "idx_rag_chunks_source",
        "rag_chunks",
        ["source"]
    )


def downgrade():
    op.drop_index("idx_rag_chunks_source")
    op.execute("DROP INDEX IF EXISTS idx_rag_chunks_chapitre_lower")
    op.drop_index("idx_rag_chunks_chapitre")
