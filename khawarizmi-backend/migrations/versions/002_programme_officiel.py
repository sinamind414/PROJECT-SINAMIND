"""Programme officiel — Tables domains, units, chapters

Revision ID: 002
Revises: 001
Create Date: 2026-06-15

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects.postgresql import UUID
import uuid


revision = "002"
down_revision = "001"
branch_labels = None
depends_on = None


def upgrade() -> None:

    op.create_table(
        "domains",
        sa.Column("id", UUID(as_uuid=True),
                  primary_key=True, default=uuid.uuid4),
        sa.Column("matiere", sa.String(50), nullable=False),
        sa.Column("filiere", sa.String(100), nullable=False),
        sa.Column("numero", sa.Integer, nullable=False),
        sa.Column("titre_fr", sa.String(500), nullable=False),
        sa.Column("titre_ar", sa.String(500)),
        sa.Column("created_at", sa.DateTime,
                  default=sa.func.now())
    )
    op.create_index(
        "ix_domains_matiere_filiere",
        "domains",
        ["matiere", "filiere"]
    )

    op.create_table(
        "units",
        sa.Column("id", UUID(as_uuid=True),
                  primary_key=True, default=uuid.uuid4),
        sa.Column("domain_id", UUID(as_uuid=True),
                  sa.ForeignKey("domains.id"),
                  nullable=False),
        sa.Column("numero", sa.Integer, nullable=False),
        sa.Column("titre_fr", sa.String(500), nullable=False),
        sa.Column("titre_ar", sa.String(500)),
        sa.Column("page", sa.Integer),
        sa.Column("created_at", sa.DateTime,
                  default=sa.func.now())
    )

    op.create_table(
        "chapters",
        sa.Column("id", UUID(as_uuid=True),
                  primary_key=True, default=uuid.uuid4),
        sa.Column("unit_id", UUID(as_uuid=True),
                  sa.ForeignKey("units.id"),
                  nullable=False),
        sa.Column("numero", sa.Integer, nullable=False),
        sa.Column("titre_fr", sa.String(500), nullable=False),
        sa.Column("titre_ar", sa.String(500)),
        sa.Column("page", sa.Integer),
        sa.Column("type", sa.String(50)),
        sa.Column("importance", sa.String(20),
                  default="moyenne"),
        sa.Column("bac_frequent", sa.Boolean,
                  default=False),
        sa.Column("created_at", sa.DateTime,
                  default=sa.func.now())
    )
    op.create_index(
        "ix_chapters_importance",
        "chapters",
        ["importance"]
    )


def downgrade() -> None:
    op.drop_table("chapters")
    op.drop_table("units")
    op.drop_table("domains")
