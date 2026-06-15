"""Create rag_chunks table

Revision ID: 004
Revises: 003
Create Date: 2026-06-15
"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects.postgresql import UUID

revision = "004"
down_revision = "003"
branch_labels = None
depends_on = None


def upgrade() -> None:
    # 1. create rag_chunks table
    op.create_table(
        "rag_chunks",
        sa.Column("id", UUID(as_uuid=True), primary_key=True),
        sa.Column("content", sa.Text(), nullable=False),
        sa.Column("embedding", sa.Text(), nullable=False),
        sa.Column("source", sa.String(255), nullable=False),
        sa.Column("matiere", sa.String(50), nullable=False),
        sa.Column("chapitre", sa.String(100), nullable=False),
        sa.Column("importance", sa.String(20), server_default="moyenne", nullable=False),
        sa.Column("chunk_index", sa.Integer(), nullable=False),
        sa.Column("created_at", sa.DateTime(), server_default=sa.func.now(), nullable=True)
    )

    # 2. alter embedding column to vector(384)
    op.execute(
        "ALTER TABLE rag_chunks "
        "ALTER COLUMN embedding TYPE vector(384) USING embedding::vector(384)"
    )

    # 3. create HNSW index for vector similarity search
    op.execute(
        "CREATE INDEX idx_rag_chunks_hnsw "
        "ON rag_chunks "
        "USING hnsw (embedding vector_cosine_ops) "
        "WITH (m=16, ef_construction=64)"
    )


def downgrade() -> None:
    op.drop_table("rag_chunks")
