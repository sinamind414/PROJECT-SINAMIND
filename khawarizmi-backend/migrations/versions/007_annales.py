"""Add annales table

Revision ID: 007
Revises: 006
"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects.postgresql import ARRAY

revision = '007'
down_revision = '006'
branch_labels = None
depends_on = None


def upgrade():
    op.create_table(
        'annales',
        sa.Column('id', sa.Integer, primary_key=True, autoincrement=True),
        sa.Column('titre', sa.String(300), nullable=False, index=True),
        sa.Column('slug', sa.String(300), unique=True, nullable=False, index=True),
        sa.Column('matiere', sa.String(100), nullable=False, index=True),
        sa.Column('niveau', sa.String(50), nullable=False),
        sa.Column('filiere', sa.String(20), nullable=False),
        sa.Column('annee', sa.Integer, nullable=False, index=True),
        sa.Column('type', sa.String(20), nullable=False, server_default='examen'),
        sa.Column('fichier_sujet', sa.String(500), nullable=False),
        sa.Column('fichier_correction', sa.String(500)),
        sa.Column('tags', ARRAY(sa.String), server_default='{}'),
        sa.Column('difficulte', sa.Integer, server_default='3'),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.func.now(), onupdate=sa.func.now()),
    )


def downgrade():
    op.drop_table('annales')
