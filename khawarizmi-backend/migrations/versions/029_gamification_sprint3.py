"""029 — Gamification Sprint 3: cities + onboarding + polish

Revision ID: 029
Revises: 028
Create Date: 2026-07-04
"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects.postgresql import UUID

revision = "029"
down_revision = "028"
branch_labels = None
depends_on = None


def upgrade() -> None:
    # ── Verb Cities (Carte) ──
    op.create_table(
        "verb_cities",
        sa.Column("id", UUID(as_uuid=True), primary_key=True, server_default=sa.text("gen_random_uuid()")),
        sa.Column("verb_slug", sa.String(50), nullable=False, unique=True),
        sa.Column("city_name_ar", sa.String(100), nullable=False),
        sa.Column("city_name_fr", sa.String(100), nullable=False),
        sa.Column("wilaya_code", sa.String(10), nullable=False, index=True),
        sa.Column("latitude", sa.Float, nullable=False),
        sa.Column("longitude", sa.Float, nullable=False),
        sa.Column("difficulty", sa.String(20), nullable=False),
        sa.Column("position_index", sa.Integer, nullable=False),
    )
    op.create_table(
        "city_progress",
        sa.Column("id", UUID(as_uuid=True), primary_key=True, server_default=sa.text("gen_random_uuid()")),
        sa.Column("user_id", UUID(as_uuid=True), sa.ForeignKey("users.id", ondelete="CASCADE"), nullable=False),
        sa.Column("city_id", UUID(as_uuid=True), sa.ForeignKey("verb_cities.id", ondelete="CASCADE"), nullable=False),
        sa.Column("level", sa.Integer, server_default="0"),
        sa.Column("unlocked_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.UniqueConstraint("user_id", "city_id", name="uq_user_city"),
    )
    op.create_index("idx_city_progress_user", "city_progress", ["user_id"])

    # ── Onboarding ──
    op.create_table(
        "user_onboarding",
        sa.Column("id", UUID(as_uuid=True), primary_key=True, server_default=sa.text("gen_random_uuid()")),
        sa.Column("user_id", UUID(as_uuid=True), sa.ForeignKey("users.id", ondelete="CASCADE"), unique=True, nullable=False),
        sa.Column("step_1_done", sa.Boolean, server_default="false"),
        sa.Column("step_2_done", sa.Boolean, server_default="false"),
        sa.Column("step_3_done", sa.Boolean, server_default="false"),
        sa.Column("completed_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("welcome_gems_awarded", sa.Boolean, server_default="false"),
    )


def downgrade() -> None:
    op.drop_table("user_onboarding")
    op.drop_table("city_progress")
    op.drop_table("verb_cities")
