"""Add strict friend_user_id FK columns to social tables.

Revision ID: 020
Revises: 019
Create Date: 2026-06-26

Ajoute friend_user_id FK stricte → users.id sur :
- friend_requests
- friends
- challenges

friend_ref reste présent pour compatibilité legacy.
"""
import sqlalchemy as sa
from alembic import op

revision = "020"
down_revision = "019"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column(
        "friend_requests",
        sa.Column("friend_user_id", sa.Integer(), sa.ForeignKey("users.id", ondelete="CASCADE"), nullable=True),
    )
    op.add_column(
        "friends",
        sa.Column("friend_user_id", sa.Integer(), sa.ForeignKey("users.id", ondelete="CASCADE"), nullable=True),
    )
    op.add_column(
        "challenges",
        sa.Column("friend_user_id", sa.Integer(), sa.ForeignKey("users.id", ondelete="CASCADE"), nullable=True),
    )
    op.execute(
        "CREATE INDEX IF NOT EXISTS idx_friend_requests_friend_user_status "
        "ON friend_requests (friend_user_id, status)"
    )
    op.execute(
        "CREATE INDEX IF NOT EXISTS idx_friends_friend_user "
        "ON friends (friend_user_id)"
    )
    op.execute(
        "CREATE INDEX IF NOT EXISTS idx_challenges_friend_user_status "
        "ON challenges (friend_user_id, status)"
    )
    op.execute(
        "CREATE UNIQUE INDEX IF NOT EXISTS uq_friends_user_friend_user_id "
        "ON friends (user_id, friend_user_id) WHERE friend_user_id IS NOT NULL"
    )


def downgrade() -> None:
    op.execute("DROP INDEX IF EXISTS uq_friends_user_friend_user_id")
    op.execute("DROP INDEX IF EXISTS idx_challenges_friend_user_status")
    op.execute("DROP INDEX IF EXISTS idx_friends_friend_user")
    op.execute("DROP INDEX IF EXISTS idx_friend_requests_friend_user_status")
    op.drop_column("challenges", "friend_user_id")
    op.drop_column("friends", "friend_user_id")
    op.drop_column("friend_requests", "friend_user_id")
