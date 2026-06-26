"""Add social graph tables: friends, friend_requests, challenge_results, activity_type.

Revision ID: 019
Revises: 018
Create Date: 2026-06-26

Tables créées :
- friend_requests
- friends
- challenge_results

Ajout colonne activity_type à friend_activities.
"""
import sqlalchemy as sa
from alembic import op

revision = "019"
down_revision = "018"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column(
        "friend_activities",
        sa.Column("activity_type", sa.String(50), nullable=True),
    )
    op.create_table(
        "friend_requests",
        sa.Column("id", sa.String(), primary_key=True),
        sa.Column("requester_id", sa.Integer(), sa.ForeignKey("users.id", ondelete="CASCADE"), nullable=False),
        sa.Column("friend_ref", sa.String(100), nullable=False),
        sa.Column("status", sa.String(20), server_default="pending", nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("responded_at", sa.DateTime(timezone=True), nullable=True),
    )
    op.create_table(
        "friends",
        sa.Column("user_id", sa.Integer(), sa.ForeignKey("users.id", ondelete="CASCADE"), nullable=False),
        sa.Column("friend_ref", sa.String(100), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=True),
        sa.PrimaryKeyConstraint("user_id", "friend_ref"),
    )
    op.create_table(
        "challenge_results",
        sa.Column("id", sa.Integer(), primary_key=True, autoincrement=True),
        sa.Column("challenge_id", sa.String(), sa.ForeignKey("challenges.id", ondelete="CASCADE"), nullable=False),
        sa.Column("user_id", sa.Integer(), sa.ForeignKey("users.id", ondelete="CASCADE"), nullable=False),
        sa.Column("score", sa.Integer(), nullable=False),
        sa.Column("correct_answers", sa.Integer(), nullable=False),
        sa.Column("total_questions", sa.Integer(), nullable=False),
        sa.Column("duration_seconds", sa.Integer(), nullable=False),
        sa.Column("points_awarded", sa.Integer(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=True),
        sa.UniqueConstraint("challenge_id", "user_id"),
    )

    op.execute(
        "CREATE INDEX IF NOT EXISTS idx_friend_activities_type_created "
        "ON friend_activities (activity_type, created_at)"
    )
    op.execute(
        "CREATE INDEX IF NOT EXISTS idx_friend_requests_requester_status "
        "ON friend_requests (requester_id, status)"
    )
    op.execute(
        "CREATE INDEX IF NOT EXISTS idx_friend_requests_friend_ref_status "
        "ON friend_requests (friend_ref, status)"
    )
    op.execute(
        "CREATE INDEX IF NOT EXISTS idx_friends_user "
        "ON friends (user_id)"
    )
    op.execute(
        "CREATE INDEX IF NOT EXISTS idx_challenge_results_challenge "
        "ON challenge_results (challenge_id)"
    )
    op.execute(
        "CREATE INDEX IF NOT EXISTS idx_challenge_results_user_created "
        "ON challenge_results (user_id, created_at)"
    )


def downgrade() -> None:
    op.execute("DROP INDEX IF EXISTS idx_challenge_results_user_created")
    op.execute("DROP INDEX IF EXISTS idx_challenge_results_challenge")
    op.execute("DROP INDEX IF EXISTS idx_friends_user")
    op.execute("DROP INDEX IF EXISTS idx_friend_requests_friend_ref_status")
    op.execute("DROP INDEX IF EXISTS idx_friend_requests_requester_status")
    op.execute("DROP INDEX IF EXISTS idx_friend_activities_type_created")
    op.drop_table("challenge_results")
    op.drop_table("friends")
    op.drop_table("friend_requests")
    op.drop_column("friend_activities", "activity_type")
