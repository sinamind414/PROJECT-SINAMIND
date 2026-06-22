"""Add active lessons tables

Revision ID: 010
Revises: 009
"""

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects.postgresql import JSONB, UUID

revision = '010'
down_revision = '009'
branch_labels = None
depends_on = None


def upgrade():
    op.create_table(
        'lesson_blocks',
        sa.Column('id', UUID(as_uuid=True), primary_key=True, server_default=sa.text("gen_random_uuid()")),
        sa.Column('chapter_slug', sa.String(200), nullable=False, index=True),
        sa.Column('block_type', sa.String(20), nullable=False),
        sa.Column('sort_order', sa.Integer, nullable=False, server_default='0'),
        sa.Column('title_ar', sa.String(300), nullable=False),
        sa.Column('body_ar', sa.Text, nullable=False),
        sa.Column('visual_hint', sa.String(200)),
        sa.Column('quick_check', JSONB, server_default='{}'),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now()),
    )

    op.create_table(
        'lesson_progress',
        sa.Column('id', UUID(as_uuid=True), primary_key=True, server_default=sa.text("gen_random_uuid()")),
        sa.Column('user_id', sa.Integer, nullable=False, index=True),
        sa.Column('chapter_slug', sa.String(200), nullable=False),
        sa.Column('blocks_completed', sa.Integer, server_default='0'),
        sa.Column('blocks_total', sa.Integer, server_default='0'),
        sa.Column('score_percentage', sa.Integer, server_default='0'),
        sa.Column('completed', sa.Boolean, server_default='false'),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.func.now(), onupdate=sa.func.now()),
        sa.UniqueConstraint('user_id', 'chapter_slug', name='uq_lesson_progress_user_chapter'),
    )


def downgrade():
    op.drop_table('lesson_progress')
    op.drop_table('lesson_blocks')
