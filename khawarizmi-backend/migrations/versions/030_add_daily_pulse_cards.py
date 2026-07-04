"""add daily_pulse_cards table

Revision ID: 030
Revises: 029
Create Date: 2026-07-04

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects.postgresql import JSONB


# revision identifiers, used by Alembic.
revision = "030"
down_revision = "029"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "daily_pulse_cards",
        sa.Column("id", sa.String(), primary_key=True),
        sa.Column("user_id", sa.Integer(), sa.ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True),
        sa.Column("card_date", sa.Date(), nullable=False, index=True),
        sa.Column("position", sa.Integer(), nullable=False),
        sa.Column("card_type", sa.String(), nullable=False),
        sa.Column("verb_slug", sa.String(), nullable=True, index=True),
        sa.Column("payload_json", JSONB, nullable=False),
        sa.Column("completed_at", sa.DateTime(), nullable=True),
    )
    op.create_index(
        "ix_daily_pulse_cards_user_date",
        "daily_pulse_cards",
        ["user_id", "card_date"],
    )


def downgrade() -> None:
    op.drop_index("ix_daily_pulse_cards_user_date", table_name="daily_pulse_cards")
    op.drop_table("daily_pulse_cards")
