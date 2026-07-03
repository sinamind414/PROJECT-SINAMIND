"""027 — Gamification Sprint 1: streaks, badges, boss

Revision ID: 027
Revises: 026
Create Date: 2026-07-04
"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects.postgresql import UUID, JSONB

revision = "027"
down_revision = "026"
branch_labels = None
depends_on = None


def upgrade() -> None:
    # ── Streaks ──
    op.create_table(
        "action_verb_streaks",
        sa.Column("id", UUID(as_uuid=True), primary_key=True, server_default=sa.text("gen_random_uuid()")),
        sa.Column("user_id", UUID(as_uuid=True), sa.ForeignKey("users.id", ondelete="CASCADE"), unique=True, nullable=False),
        sa.Column("current_streak", sa.Integer, server_default="0"),
        sa.Column("longest_streak", sa.Integer, server_default="0"),
        sa.Column("last_active_date", sa.Date, nullable=True),
        sa.Column("freezes_remaining", sa.Integer, server_default="1"),
        sa.Column("freezes_used_this_week", sa.Integer, server_default="0"),
        sa.Column("week_start_date", sa.Date, nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), onupdate=sa.func.now()),
    )
    op.create_index("idx_streaks_user", "action_verb_streaks", ["user_id"])

    # ── Badges ──
    op.create_table(
        "user_badges",
        sa.Column("id", UUID(as_uuid=True), primary_key=True, server_default=sa.text("gen_random_uuid()")),
        sa.Column("user_id", UUID(as_uuid=True), sa.ForeignKey("users.id", ondelete="CASCADE"), nullable=False),
        sa.Column("badge_code", sa.String(50), nullable=False),
        sa.Column("unlocked_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.UniqueConstraint("user_id", "badge_code", name="uq_user_badge"),
    )
    op.create_index("idx_badges_user", "user_badges", ["user_id"])

    # ── Boss questions + attempts ──
    op.create_table(
        "boss_questions",
        sa.Column("id", UUID(as_uuid=True), primary_key=True, server_default=sa.text("gen_random_uuid()")),
        sa.Column("verb_slug", sa.String(50), nullable=False, index=True),
        sa.Column("difficulty", sa.Integer, nullable=False),
        sa.Column("question_ar", sa.Text, nullable=False),
        sa.Column("context_ar", sa.Text, nullable=True),
        sa.Column("correct_answer", sa.Text, nullable=False),
        sa.Column("scoring_rubric", JSONB, nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
    )
    op.create_table(
        "boss_attempts",
        sa.Column("id", UUID(as_uuid=True), primary_key=True, server_default=sa.text("gen_random_uuid()")),
        sa.Column("user_id", UUID(as_uuid=True), sa.ForeignKey("users.id", ondelete="CASCADE"), nullable=False),
        sa.Column("question_id", UUID(as_uuid=True), sa.ForeignKey("boss_questions.id", ondelete="CASCADE"), nullable=False),
        sa.Column("user_answer", sa.Text, nullable=False),
        sa.Column("score_percentage", sa.Integer, nullable=False),
        sa.Column("attempted_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
    )
    op.create_index("idx_boss_attempts_user", "boss_attempts", ["user_id"])


def downgrade() -> None:
    op.drop_table("boss_attempts")
    op.drop_table("boss_questions")
    op.drop_table("user_badges")
    op.drop_table("action_verb_streaks")
