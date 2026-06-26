"""Create chatbot memory, weak concepts, socratic streaks, daily missions.

Revision ID: 022
Revises: 021
Create Date: 2026-06-26

Tables créées :
- chatbot_memory (conversation memory)
- chatbot_weak_concepts (weak concepts tracking)
- chatbot_socratic_streaks (streak tracking)
- chatbot_daily_missions (daily missions)
"""
import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects.postgresql import JSONB

revision = "022"
down_revision = "021"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "chatbot_memory",
        sa.Column("id", sa.Integer(), primary_key=True, autoincrement=True),
        sa.Column("user_id", sa.Integer(), sa.ForeignKey("users.id", ondelete="CASCADE"), nullable=False, unique=True),
        sa.Column("last_topic", sa.String(200), nullable=True),
        sa.Column("last_chapter", sa.String(100), nullable=True),
        sa.Column("preferred_mode", sa.String(20), server_default="quick"),
        sa.Column("total_messages", sa.Integer(), server_default="0"),
        sa.Column("last_interaction_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), onupdate=sa.func.now()),
    )
    op.create_table(
        "chatbot_weak_concepts",
        sa.Column("id", sa.Integer(), primary_key=True, autoincrement=True),
        sa.Column("user_id", sa.Integer(), sa.ForeignKey("users.id", ondelete="CASCADE"), nullable=False),
        sa.Column("concept", sa.String(200), nullable=False),
        sa.Column("chapter", sa.String(100), nullable=True),
        sa.Column("weakness_score", sa.Float(), server_default="1.0"),
        sa.Column("occurrences", sa.Integer(), server_default="1"),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), onupdate=sa.func.now()),
    )
    op.create_table(
        "chatbot_socratic_streaks",
        sa.Column("id", sa.Integer(), primary_key=True, autoincrement=True),
        sa.Column("user_id", sa.Integer(), sa.ForeignKey("users.id", ondelete="CASCADE"), nullable=False, unique=True),
        sa.Column("current_streak", sa.Integer(), server_default="0"),
        sa.Column("longest_streak", sa.Integer(), server_default="0"),
        sa.Column("last_interaction_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), onupdate=sa.func.now()),
    )
    op.create_table(
        "chatbot_daily_missions",
        sa.Column("id", sa.Integer(), primary_key=True, autoincrement=True),
        sa.Column("user_id", sa.Integer(), sa.ForeignKey("users.id", ondelete="CASCADE"), nullable=False),
        sa.Column("mission_type", sa.String(60), nullable=False),
        sa.Column("mission_data", JSONB(), nullable=True),
        sa.Column("completed", sa.Boolean(), server_default="false"),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.Column("completed_at", sa.DateTime(timezone=True), nullable=True),
    )
    op.execute(
        "CREATE INDEX IF NOT EXISTS idx_chatbot_weak_concepts_user "
        "ON chatbot_weak_concepts (user_id, weakness_score DESC)"
    )
    op.execute(
        "CREATE INDEX IF NOT EXISTS idx_chatbot_daily_missions_user_date "
        "ON chatbot_daily_missions (user_id, created_at)"
    )


def downgrade() -> None:
    op.execute("DROP INDEX IF EXISTS idx_chatbot_daily_missions_user_date")
    op.execute("DROP INDEX IF EXISTS idx_chatbot_weak_concepts_user")
    op.drop_table("chatbot_daily_missions")
    op.drop_table("chatbot_socratic_streaks")
    op.drop_table("chatbot_weak_concepts")
    op.drop_table("chatbot_memory")
