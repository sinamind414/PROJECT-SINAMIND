"""Create chatbot explain-back attempts, boss fights, mystery boxes.

Revision ID: 023
Revises: 022
Create Date: 2026-06-26

Tables créées :
- chatbot_explain_back_attempts (explain-back tracking)
- chatbot_boss_fights (boss fight bacs)
- chatbot_mystery_boxes (chatbot mystery boxes)
"""
import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects.postgresql import JSONB

revision = "023"
down_revision = "022"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "chatbot_explain_back_attempts",
        sa.Column("id", sa.Integer(), primary_key=True, autoincrement=True),
        sa.Column("user_id", sa.Integer(), sa.ForeignKey("users.id", ondelete="CASCADE"), nullable=False),
        sa.Column("concept", sa.String(200), nullable=False),
        sa.Column("answer", sa.Text(), nullable=True),
        sa.Column("clarity_score", sa.Float(), nullable=True),
        sa.Column("scientific_terms_score", sa.Float(), nullable=True),
        sa.Column("structure_score", sa.Float(), nullable=True),
        sa.Column("total_score", sa.Float(), nullable=True),
        sa.Column("feedback", sa.Text(), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
    )
    op.create_index(
        "idx_explain_back_user_concept",
        "chatbot_explain_back_attempts",
        ["user_id", "concept"],
    )
    op.create_table(
        "chatbot_boss_fights",
        sa.Column("id", sa.Integer(), primary_key=True, autoincrement=True),
        sa.Column("user_id", sa.Integer(), sa.ForeignKey("users.id", ondelete="CASCADE"), nullable=False),
        sa.Column("boss_fight_id", sa.String(60), nullable=False, unique=True),
        sa.Column("chapter", sa.String(100), nullable=False),
        sa.Column("status", sa.String(20), server_default="started"),
        sa.Column("questions", JSONB(), nullable=True),
        sa.Column("answers", JSONB(), nullable=True),
        sa.Column("score", sa.Float(), nullable=True),
        sa.Column("passed", sa.Boolean(), nullable=True),
        sa.Column("details", JSONB(), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.Column("completed_at", sa.DateTime(timezone=True), nullable=True),
    )
    op.create_index(
        "idx_boss_fights_user",
        "chatbot_boss_fights",
        ["user_id", "status"],
    )
    op.create_table(
        "chatbot_mystery_boxes",
        sa.Column("id", sa.Integer(), primary_key=True, autoincrement=True),
        sa.Column("user_id", sa.Integer(), sa.ForeignKey("users.id", ondelete="CASCADE"), nullable=False),
        sa.Column("rarity", sa.String(20), nullable=False),
        sa.Column("reward_type", sa.String(30), nullable=True),
        sa.Column("reward_value", sa.Integer(), nullable=True),
        sa.Column("reward_data", JSONB(), nullable=True),
        sa.Column("opened", sa.Boolean(), server_default="true"),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
    )
    op.create_index(
        "idx_mystery_boxes_user",
        "chatbot_mystery_boxes",
        ["user_id", "created_at"],
    )


def downgrade() -> None:
    op.execute("DROP INDEX IF EXISTS idx_mystery_boxes_user")
    op.drop_table("chatbot_mystery_boxes")
    op.execute("DROP INDEX IF EXISTS idx_boss_fights_user")
    op.drop_table("chatbot_boss_fights")
    op.execute("DROP INDEX IF EXISTS idx_explain_back_user_concept")
    op.drop_table("chatbot_explain_back_attempts")
