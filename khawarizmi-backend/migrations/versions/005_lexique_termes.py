"""Create lexique_termes table

Revision ID: 005
Revises: 004
Create Date: 2026-06-15
"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects.postgresql import ARRAY, JSONB

revision = "005"
down_revision = "004"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "lexique_termes",
        sa.Column("id", sa.String(50), primary_key=True),
        sa.Column("terme_fr", sa.String(255), nullable=False),
        sa.Column("terme_ar", sa.String(255), nullable=False),
        sa.Column("abreviation", sa.String(50), nullable=True),
        sa.Column("type", sa.String(50), nullable=False),
        sa.Column("definition_fr", sa.Text(), nullable=False),
        sa.Column("definition_ar", sa.Text(), nullable=False),
        sa.Column("synonymes_fr", ARRAY(sa.String()), nullable=True),
        sa.Column("synonymes_ar", ARRAY(sa.String()), nullable=True),
        sa.Column("importance", sa.String(20), server_default="moyenne", nullable=False),
        sa.Column("bac_frequent", sa.Boolean(), server_default=sa.text("false"), nullable=False),
        sa.Column("chapitre_principal", sa.String(100), nullable=False),
        sa.Column("micro_concept_id", sa.String(50), nullable=True),
        sa.Column("exemples_contexte", ARRAY(sa.String()), nullable=True),
        sa.Column("termes_lies", ARRAY(sa.String()), nullable=True),
        sa.Column("tags", ARRAY(sa.String()), nullable=True),
        sa.Column("categorie_id", sa.String(50), nullable=True),
        sa.Column("categorie_fr", sa.String(255), nullable=True),
        sa.Column("categorie_ar", sa.String(255), nullable=True),
        sa.Column("domaine_id", sa.String(50), nullable=True),
        sa.Column("domaine_fr", sa.String(255), nullable=True),
        sa.Column("domaine_ar", sa.String(255), nullable=True),
        sa.Column("donnees_brutes", JSONB(), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=True),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=True)
    )

    op.create_index("ix_lexique_terme_fr", "lexique_termes", ["terme_fr"])
    op.create_index("ix_lexique_type", "lexique_termes", ["type"])
    op.create_index("ix_lexique_chapitre", "lexique_termes", ["chapitre_principal"])
    op.create_index("ix_lexique_micro_concept", "lexique_termes", ["micro_concept_id"])
    op.create_index("ix_lexique_domaine", "lexique_termes", ["domaine_id"])
    op.create_index(
        "ix_lexique_search",
        "lexique_termes",
        ["importance", "chapitre_principal", "type"]
    )


def downgrade() -> None:
    op.drop_table("lexique_termes")
