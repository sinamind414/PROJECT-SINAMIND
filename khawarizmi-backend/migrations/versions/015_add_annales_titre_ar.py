"""Ajout colonne titre_ar à la table annales."""

from alembic import op
import sqlalchemy as sa

revision = "015"
down_revision = "014"
branch_labels = None
depends_on = None


def upgrade():
    op.add_column("annales", sa.Column("titre_ar", sa.String(500), nullable=True))


def downgrade():
    op.drop_column("annales", "titre_ar")
