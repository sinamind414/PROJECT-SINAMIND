"""Add mindmap_tasks table for async generation

Revision ID: 012
Revises: 011

But : Suivre l'état de génération asynchrone des Mind Maps.
- status: pending -> running -> completed | failed
- progress: étape courante (rag, llm, save, flashcards)
- mindmap_id: rempli quand la génération réussit
"""

from alembic import op
import sqlalchemy as sa

revision = '012'
down_revision = '011'
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "mindmap_tasks",
        sa.Column("id", sa.String(50), primary_key=True),
        sa.Column("user_id", sa.Integer(), sa.ForeignKey("users.id", ondelete="CASCADE"), nullable=False),
        sa.Column("chapitre", sa.String(100), nullable=False),
        sa.Column("matiere", sa.String(50), nullable=False),
        sa.Column("filiere", sa.String(100), nullable=False),
        sa.Column("status", sa.String(20), server_default="pending", nullable=False),
        sa.Column("progress", sa.String(50), nullable=True),
        sa.Column("error", sa.Text(), nullable=True),
        sa.Column("mindmap_id", sa.String(50), nullable=True),
        sa.Column("created_at", sa.DateTime(), server_default=sa.func.now(), nullable=True),
        sa.Column("updated_at", sa.DateTime(), server_default=sa.func.now(), nullable=True)
    )
    op.create_index(
        "ix_mindmap_tasks_user",
        "mindmap_tasks",
        ["user_id", "status"]
    )


def downgrade() -> None:
    op.drop_table("mindmap_tasks")
