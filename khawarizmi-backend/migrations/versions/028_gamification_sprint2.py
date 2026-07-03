"""028 — Gamification Sprint 2: gems, duels, leaderboard

Revision ID: 028
Revises: 027
Create Date: 2026-07-04
"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects.postgresql import UUID

revision = "028"
down_revision = "027"
branch_labels = None
depends_on = None


def upgrade() -> None:
    # ── Gems ──
    op.create_table(
        "user_gems",
        sa.Column("id", UUID(as_uuid=True), primary_key=True, server_default=sa.text("gen_random_uuid()")),
        sa.Column("user_id", UUID(as_uuid=True), sa.ForeignKey("users.id", ondelete="CASCADE"), unique=True, nullable=False),
        sa.Column("balance", sa.Integer, server_default="0"),
        sa.Column("total_earned", sa.Integer, server_default="0"),
        sa.Column("total_spent", sa.Integer, server_default="0"),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), onupdate=sa.func.now()),
    )
    op.create_table(
        "gem_transactions",
        sa.Column("id", UUID(as_uuid=True), primary_key=True, server_default=sa.text("gen_random_uuid()")),
        sa.Column("user_id", UUID(as_uuid=True), sa.ForeignKey("users.id", ondelete="CASCADE"), nullable=False),
        sa.Column("amount", sa.Integer, nullable=False),
        sa.Column("reason", sa.String(100), nullable=False),
        sa.Column("reference_id", sa.String(50), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
    )
    op.create_index("idx_gem_tx_user", "gem_transactions", ["user_id", sa.text("created_at DESC")])

    # ── Duels ──
    op.create_table(
        "duels",
        sa.Column("id", UUID(as_uuid=True), primary_key=True, server_default=sa.text("gen_random_uuid()")),
        sa.Column("verb_slug", sa.String(50), nullable=False, index=True),
        sa.Column("host_user_id", UUID(as_uuid=True), sa.ForeignKey("users.id", ondelete="CASCADE"), nullable=False),
        sa.Column("guest_user_id", UUID(as_uuid=True), sa.ForeignKey("users.id", ondelete="CASCADE"), nullable=True),
        sa.Column("host_score", sa.Integer, nullable=True),
        sa.Column("guest_score", sa.Integer, nullable=True),
        sa.Column("host_completed_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("guest_completed_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("status", sa.String(20), server_default="pending"),
        sa.Column("winner_user_id", UUID(as_uuid=True), sa.ForeignKey("users.id", ondelete="SET NULL"), nullable=True),
        sa.Column("share_token", sa.String(50), unique=True, nullable=False),
        sa.Column("expires_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
    )
    op.create_index("idx_duels_share", "duels", ["share_token"])
    op.create_index("idx_duels_status", "duels", ["status"])

    # ── User Stats (leaderboard) ──
    op.create_table(
        "user_stats",
        sa.Column("id", UUID(as_uuid=True), primary_key=True, server_default=sa.text("gen_random_uuid()")),
        sa.Column("user_id", UUID(as_uuid=True), sa.ForeignKey("users.id", ondelete="CASCADE"), unique=True, nullable=False),
        sa.Column("wilaya_code", sa.String(10), nullable=True),
        sa.Column("school_name", sa.String(200), nullable=True),
        sa.Column("total_evaluations", sa.Integer, server_default="0"),
        sa.Column("total_correct", sa.Integer, server_default="0"),
        sa.Column("precision_score", sa.Float, server_default="0.0"),
        sa.Column("weighted_score", sa.Float, server_default="0.0"),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), onupdate=sa.func.now()),
    )
    op.create_index("idx_user_stats_score", "user_stats", [sa.text("weighted_score DESC")])
    op.create_index("idx_user_stats_wilaya", "user_stats", ["wilaya_code", sa.text("weighted_score DESC")])


def downgrade() -> None:
    op.drop_table("user_stats")
    op.drop_table("duels")
    op.drop_table("gem_transactions")
    op.drop_table("user_gems")
