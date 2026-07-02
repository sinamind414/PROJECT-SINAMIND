"""Create correction_audit table for audit-logging LLM evaluations.

Revision ID: 025
Revises: 024
Create Date: 2026-07-02

Tables créées :
- correction_audit (hashes uniquement, pas de contenu brut)
"""
import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects.postgresql import JSONB

revision = "025"
down_revision = "024"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "correction_audit",
        sa.Column("id", sa.Integer(), primary_key=True, autoincrement=True),
        sa.Column("user_id", sa.Integer(), sa.ForeignKey("users.id", ondelete="SET NULL"), nullable=True),
        sa.Column("session_id", sa.String(64), nullable=True),
        sa.Column("question_hash", sa.String(64), nullable=False, comment="SHA256 de la question"),
        sa.Column("student_answer_hash", sa.String(64), nullable=False, comment="SHA256 de la réponse élève"),
        sa.Column("prompt_hash", sa.String(64), nullable=False, comment="SHA256 du prompt LLM complet"),
        sa.Column("verb_slug", sa.String(50), nullable=False),
        sa.Column("sanity_code", sa.String(20), nullable=True),
        sa.Column("source", sa.String(20), nullable=False),
        sa.Column("provider", sa.String(30), nullable=True),
        sa.Column("model", sa.String(50), nullable=True),
        sa.Column("finish_reason", sa.String(30), nullable=True),
        sa.Column("score", sa.Float(), nullable=True),
        sa.Column("score_max", sa.Integer(), nullable=True),
        sa.Column("percentage", sa.Float(), nullable=True),
        sa.Column("confidence", sa.Float(), nullable=True),
        sa.Column("parse_status", sa.String(20), nullable=True),
        sa.Column("attempts", sa.Integer(), nullable=True),
        sa.Column("error_message_hash", sa.String(64), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
    )
    op.execute(
        "CREATE INDEX idx_correction_audit_user_created "
        "ON correction_audit (user_id, created_at)"
    )
    op.execute(
        "CREATE INDEX idx_correction_audit_prompt_hash "
        "ON correction_audit (prompt_hash)"
    )


def downgrade() -> None:
    op.drop_table("correction_audit")
