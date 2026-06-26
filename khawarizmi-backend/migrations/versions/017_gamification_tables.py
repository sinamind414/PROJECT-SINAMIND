"""Create gamification tables (streaks, points, avatars, badges, mystery boxes).

Revision ID: 017
Revises: 016
Create Date: 2026-06-26

Tables créées :
- user_streaks
- user_points
- user_avatars
- badges
- user_badges
- mystery_boxes
"""
import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects.postgresql import JSONB

revision = "017"
down_revision = "016"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "user_streaks",
        sa.Column("user_id", sa.Integer(), sa.ForeignKey("users.id", ondelete="CASCADE"), primary_key=True),
        sa.Column("current_streak", sa.Integer(), server_default="0", nullable=False),
        sa.Column("longest_streak", sa.Integer(), server_default="0", nullable=False),
        sa.Column("last_activity", sa.Date(), nullable=True),
    )
    op.create_table(
        "user_points",
        sa.Column("user_id", sa.Integer(), sa.ForeignKey("users.id", ondelete="CASCADE"), primary_key=True),
        sa.Column("total_points", sa.Integer(), server_default="0", nullable=False),
        sa.Column("weekly_points", sa.Integer(), server_default="0", nullable=False),
    )
    op.create_table(
        "user_avatars",
        sa.Column("user_id", sa.Integer(), sa.ForeignKey("users.id", ondelete="CASCADE"), primary_key=True),
        sa.Column("level", sa.Integer(), server_default="1", nullable=False),
        sa.Column("xp", sa.Integer(), server_default="0", nullable=False),
    )
    op.create_table(
        "badges",
        sa.Column("id", sa.String(), primary_key=True),
        sa.Column("name", sa.String(100), nullable=False),
        sa.Column("description", sa.Text(), nullable=True),
        sa.Column("rarity", sa.String(20), nullable=True),
        sa.Column("icon", sa.String(50), nullable=True),
    )
    op.create_table(
        "user_badges",
        sa.Column("user_id", sa.Integer(), sa.ForeignKey("users.id", ondelete="CASCADE"), primary_key=True),
        sa.Column("badge_id", sa.String(), sa.ForeignKey("badges.id", ondelete="CASCADE"), primary_key=True),
        sa.Column("unlocked_at", sa.Date(), nullable=True),
    )
    op.create_table(
        "mystery_boxes",
        sa.Column("id", sa.String(), primary_key=True),
        sa.Column("user_id", sa.Integer(), sa.ForeignKey("users.id", ondelete="CASCADE"), nullable=False),
        sa.Column("rarity", sa.String(20), nullable=True),
        sa.Column("opened", sa.Boolean(), server_default="false", nullable=False),
        sa.Column("content_type", sa.String(50), nullable=True),
        sa.Column("content_value", JSONB(), nullable=True),
        sa.Column("created_at", sa.Date(), nullable=True),
    )
    op.execute(
        "CREATE INDEX IF NOT EXISTS idx_mystery_boxes_user_opened "
        "ON mystery_boxes (user_id, opened)"
    )


def downgrade() -> None:
    op.execute("DROP INDEX IF EXISTS idx_mystery_boxes_user_opened")
    op.drop_table("mystery_boxes")
    op.drop_table("user_badges")
    op.drop_table("badges")
    op.drop_table("user_avatars")
    op.drop_table("user_points")
    op.drop_table("user_streaks")
