"""Create social / live classroom tables (friend_activities, challenges).

Revision ID: 018
Revises: 017
Create Date: 2026-06-26

Tables créées :
- friend_activities
- challenges
"""
import sqlalchemy as sa
from alembic import op

revision = "018"
down_revision = "017"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "friend_activities",
        sa.Column("id", sa.Integer(), primary_key=True, autoincrement=True),
        sa.Column("user_id", sa.Integer(), sa.ForeignKey("users.id", ondelete="CASCADE"), nullable=True),
        sa.Column("actor_name", sa.String(100), nullable=False),
        sa.Column("action", sa.String(255), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=True),
    )
    op.create_table(
        "challenges",
        sa.Column("id", sa.String(), primary_key=True),
        sa.Column("challenger_id", sa.Integer(), sa.ForeignKey("users.id", ondelete="CASCADE"), nullable=False),
        sa.Column("friend_id", sa.String(100), nullable=False),
        sa.Column("status", sa.String(20), server_default="pending", nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=True),
    )
    op.execute(
        "CREATE INDEX IF NOT EXISTS idx_friend_activities_user_created "
        "ON friend_activities (user_id, created_at)"
    )
    op.execute(
        "CREATE INDEX IF NOT EXISTS idx_challenges_challenger_status "
        "ON challenges (challenger_id, status)"
    )


def downgrade() -> None:
    op.execute("DROP INDEX IF EXISTS idx_challenges_challenger_status")
    op.execute("DROP INDEX IF EXISTS idx_friend_activities_user_created")
    op.drop_table("challenges")
    op.drop_table("friend_activities")
