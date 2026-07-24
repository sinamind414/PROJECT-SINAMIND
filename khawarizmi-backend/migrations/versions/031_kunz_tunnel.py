"""add tunnel_events and recall_items tables

Revision ID: 031
Revises: 030
Create Date: 2026-07-22

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.dialects.postgresql import UUID


revision = "031"
down_revision = "030"
branch_labels = None
depends_on = None


def upgrade() -> None:
    # tunnel_events — append-only event log with idempotency
    op.create_table(
        "tunnel_events",
        sa.Column("id", sa.String(), primary_key=True),
        sa.Column("user_id", sa.Integer(), sa.ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True),
        sa.Column("lesson_id", sa.String(200), nullable=False, index=True),
        sa.Column("session_id", sa.String(100), nullable=False),
        sa.Column("event_type", sa.String(50), nullable=False),
        sa.Column("payload", JSONB, server_default=sa.text("'{}'::jsonb"), nullable=True),
        sa.Column("client_event_id", sa.String(100), nullable=True),
        sa.Column("client_ts", sa.DateTime(timezone=True), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=True),
    )
    op.create_index(
        "ix_tunnel_events_user_client",
        "tunnel_events",
        ["user_id", "client_event_id"],
        unique=True,
        postgresql_where=sa.text("client_event_id IS NOT NULL"),
    )
    op.create_index(
        "ix_tunnel_events_user_lesson_type",
        "tunnel_events",
        ["user_id", "lesson_id", "event_type"],
    )

    # recall_items — lesson-aware spaced repetition items
    op.create_table(
        "recall_items",
        sa.Column("id", sa.String(), primary_key=True),
        sa.Column("user_id", sa.Integer(), sa.ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True),
        sa.Column("lesson_id", sa.String(200), nullable=False, index=True),
        sa.Column("concept_id", sa.String(200), nullable=True),
        sa.Column("stage", sa.SmallInteger(), server_default=sa.text("0"), nullable=False),
        sa.Column("next_review_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("last_result", sa.String(10), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=True),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=True),
    )
    op.create_index(
        "ix_recall_items_due",
        "recall_items",
        ["user_id", sa.text("next_review_at ASC")],
        postgresql_where=sa.text("last_result IS NULL OR last_result != 'completed'"),
    )
    op.create_index(
        "ix_recall_items_user_lesson",
        "recall_items",
        ["user_id", "lesson_id"],
    )


def downgrade() -> None:
    op.drop_table("recall_items")
    op.drop_table("tunnel_events")
