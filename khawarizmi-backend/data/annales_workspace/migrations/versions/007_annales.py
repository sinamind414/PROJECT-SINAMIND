"""007_annales — Création des tables matieres + annales

Revision ID: 007
Revises: None (première migration)
Create Date: 2026-06-18
"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

revision: str = "007"
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ── Matières ────────────────────────────────────────────────────
    op.create_table(
        "matieres",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("nom", sa.String(150), nullable=False),
        sa.Column("slug", sa.String(150), nullable=False),
        sa.Column("description", sa.Text(), nullable=True),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.func.now(),
            nullable=True,
        ),
        sa.Column(
            "updated_at",
            sa.DateTime(timezone=True),
            server_default=sa.func.now(),
            nullable=True,
        ),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("nom"),
        sa.UniqueConstraint("slug"),
    )
    op.create_index("ix_matieres_nom", "matieres", ["nom"])
    op.create_index("ix_matieres_slug", "matieres", ["slug"])

    # ── Annales ─────────────────────────────────────────────────────
    op.create_table(
        "annales",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("titre", sa.String(300), nullable=False),
        sa.Column("slug", sa.String(300), nullable=False),
        sa.Column(
            "matiere_id",
            sa.Integer(),
            sa.ForeignKey("matieres.id", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column(
            "niveau",
            sa.Enum(
                "1ère année",
                "2ème année",
                "3ème année",
                "4ème année",
                "5ème année",
                name="niveau",
            ),
            nullable=False,
        ),
        sa.Column(
            "filiere",
            sa.Enum(
                "S", "ES", "L", "STMG", "STI2D", "STL", "ST2S", "Pro", "Autre",
                name="filiere",
            ),
            nullable=False,
        ),
        sa.Column("annee", sa.Integer(), nullable=False),
        sa.Column(
            "type",
            sa.Enum("examen", "concours", name="typeannale"),
            nullable=False,
            server_default="examen",
        ),
        sa.Column("fichier_sujet", sa.String(500), nullable=False),
        sa.Column("fichier_correction", sa.String(500), nullable=True),
        sa.Column("tags", postgresql.ARRAY(sa.String()), nullable=True),
        sa.Column(
            "difficulté",
            sa.Enum("1", "2", "3", "4", "5", name="difficulte"),
            nullable=False,
            server_default="3",
        ),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.func.now(),
            nullable=True,
        ),
        sa.Column(
            "updated_at",
            sa.DateTime(timezone=True),
            server_default=sa.func.now(),
            nullable=True,
        ),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("slug"),
    )
    op.create_index("ix_annales_titre", "annales", ["titre"])
    op.create_index("ix_annales_slug", "annales", ["slug"])
    op.create_index("ix_annales_matiere_id", "annales", ["matiere_id"])
    op.create_index("ix_annales_annee", "annales", ["annee"])


def downgrade() -> None:
    op.drop_index("ix_annales_annee", table_name="annales")
    op.drop_index("ix_annales_matiere_id", table_name="annales")
    op.drop_index("ix_annales_slug", table_name="annales")
    op.drop_index("ix_annales_titre", table_name="annales")
    op.drop_table("annales")

    op.drop_index("ix_matieres_slug", table_name="matieres")
    op.drop_index("ix_matieres_nom", table_name="matieres")
    op.drop_table("matieres")

    # Nettoyer les types enum PostgreSQL
    op.execute("DROP TYPE IF EXISTS difficulte")
    op.execute("DROP TYPE IF EXISTS typeannale")
    op.execute("DROP TYPE IF EXISTS filiere")
    op.execute("DROP TYPE IF EXISTS niveau")