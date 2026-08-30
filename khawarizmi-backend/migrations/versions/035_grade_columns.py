"""035 : colonnes grade() sur da_answers (méthode / science, pas la copie).

Revision ID: 035
Revises: 034
"""

from alembic import op

revision = "035"
down_revision = "034"
branch_labels = None
depends_on = None


def upgrade() -> None:
    for stmt in (
        "ALTER TABLE da_answers ADD COLUMN IF NOT EXISTS rubric_version VARCHAR(32)",
        "ALTER TABLE da_answers ADD COLUMN IF NOT EXISTS grader_version VARCHAR(32)",
        "ALTER TABLE da_answers ADD COLUMN IF NOT EXISTS grading_engine VARCHAR(32)",
        "ALTER TABLE da_answers ADD COLUMN IF NOT EXISTS science_status VARCHAR(32)",
        "ALTER TABLE da_answers ADD COLUMN IF NOT EXISTS stuffing_suspected BOOLEAN",
        "ALTER TABLE da_answers ADD COLUMN IF NOT EXISTS method_percent INTEGER",
        "ALTER TABLE da_answers ADD COLUMN IF NOT EXISTS order_ok BOOLEAN",
        "ALTER TABLE da_answers ADD COLUMN IF NOT EXISTS diagnosis_code VARCHAR(80)",
    ):
        op.execute(stmt)


def downgrade() -> None:
    for col in (
        "rubric_version",
        "grader_version",
        "grading_engine",
        "science_status",
        "stuffing_suspected",
        "method_percent",
        "order_ok",
        "diagnosis_code",
    ):
        op.execute(f"ALTER TABLE da_answers DROP COLUMN IF EXISTS {col}")
