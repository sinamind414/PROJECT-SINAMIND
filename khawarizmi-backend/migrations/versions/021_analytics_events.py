"""Create analytics_events table for event tracking & funnels.

Revision ID: 021
Revises: 020
Create Date: 2026-06-26

Tables créées :
- analytics_events
- indexes pour queries funnel et user timeline
"""
import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects.postgresql import JSONB

revision = "021"
down_revision = "020"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "analytics_events",
        sa.Column("id", sa.Integer(), primary_key=True, autoincrement=True),
        sa.Column("user_id", sa.Integer(), sa.ForeignKey("users.id", ondelete="CASCADE"), nullable=False),
        sa.Column("session_id", sa.String(64), nullable=False),
        sa.Column("event_type", sa.String(80), nullable=False),
        sa.Column("feature", sa.String(80), nullable=True),
        sa.Column("chapter", sa.String(100), nullable=True),
        sa.Column("metadata", JSONB(), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=True),
    )
    op.execute(
        "CREATE INDEX IF NOT EXISTS idx_analytics_events_user_created "
        "ON analytics_events (user_id, created_at)"
    )
    op.execute(
        "CREATE INDEX IF NOT EXISTS idx_analytics_events_event_type "
        "ON analytics_events (event_type)"
    )
    op.execute(
        "CREATE INDEX IF NOT EXISTS idx_analytics_events_session "
        "ON analytics_events (session_id)"
    )


def downgrade() -> None:
    op.execute("DROP INDEX IF EXISTS idx_analytics_events_session")
    op.execute("DROP INDEX IF EXISTS idx_analytics_events_event_type")
    op.execute("DROP INDEX IF EXISTS idx_analytics_events_user_created")
    op.drop_table("analytics_events")
