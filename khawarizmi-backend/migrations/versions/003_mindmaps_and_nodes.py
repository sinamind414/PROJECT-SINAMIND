"""Create mindmaps and mindmap_nodes tables

Revision ID: 003
Revises: 002
Create Date: 2026-06-15
"""
from alembic import op
import sqlalchemy as sa

revision = "003"
down_revision = "002"
branch_labels = None
depends_on = None


def upgrade() -> None:
    # 1. create mindmaps table
    op.create_table(
        "mindmaps",
        sa.Column("id", sa.String(50), primary_key=True),
        sa.Column("user_id", sa.Integer(), sa.ForeignKey("users.id", ondelete="CASCADE"), nullable=False),
        sa.Column("titre", sa.String(255), nullable=False),
        sa.Column("matiere", sa.String(50), nullable=False),
        sa.Column("filiere", sa.String(100), nullable=False),
        sa.Column("chapitre", sa.String(100), nullable=False),
        sa.Column("data", sa.Text(), nullable=False),
        sa.Column("created_at", sa.DateTime(), server_default=sa.func.now(), nullable=True)
    )
    op.create_index(
        "ix_mindmaps_user_chapter",
        "mindmaps",
        ["user_id", "chapitre"]
    )

    # 2. create mindmap_nodes table
    op.create_table(
        "mindmap_nodes",
        sa.Column("id", sa.String(50), primary_key=True),
        sa.Column("mindmap_id", sa.String(50), sa.ForeignKey("mindmaps.id", ondelete="CASCADE"), nullable=False),
        sa.Column("user_id", sa.Integer(), sa.ForeignKey("users.id", ondelete="CASCADE"), nullable=False),
        sa.Column("label", sa.String(255), nullable=False),
        sa.Column("type", sa.String(50), nullable=False),
        sa.Column("importance", sa.String(20), server_default="moyenne", nullable=False),
        sa.Column("bac_frequent", sa.Boolean(), server_default=sa.text("false"), nullable=False),
        sa.Column("fsrs_card_id", sa.String(50), nullable=True),
        sa.Column("maitrise_eleve", sa.Integer(), server_default=sa.text("0"), nullable=False),
        sa.Column("created_at", sa.DateTime(), server_default=sa.func.now(), nullable=True),
        sa.Column("updated_at", sa.DateTime(), server_default=sa.func.now(), nullable=True)
    )
    op.create_index(
        "ix_mindmap_nodes_lookup",
        "mindmap_nodes",
        ["mindmap_id", "user_id", "maitrise_eleve"]
    )


def downgrade() -> None:
    op.drop_table("mindmap_nodes")
    op.drop_table("mindmaps")
