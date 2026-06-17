"""Add videos table

Revision ID: 006
Revises: 005
"""
from alembic import op
import sqlalchemy as sa

revision = '006'
down_revision = '005'
branch_labels = None
depends_on = None


def upgrade():
    op.create_table(
        'videos',
        sa.Column('id', sa.Integer, primary_key=True),
        sa.Column('youtube_id', sa.String(50), nullable=False),
        sa.Column('titre', sa.String(255), nullable=False),
        sa.Column('chaine', sa.String(100), nullable=False),
        sa.Column('duree', sa.String(20)),
        sa.Column('chapitre', sa.String(255), nullable=False, index=True),
        sa.Column('description', sa.Text),
        sa.Column('created_at', sa.DateTime, server_default=sa.func.now())
    )


def downgrade():
    op.drop_table('videos')
