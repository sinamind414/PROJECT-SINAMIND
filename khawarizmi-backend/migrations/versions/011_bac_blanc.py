"""Add bac blanc immersif tables

Revision ID: 011
Revises: 010
"""

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects.postgresql import JSONB, UUID

revision = '011'
down_revision = '010'
branch_labels = None
depends_on = None


def upgrade():
    op.create_table(
        'bac_sessions',
        sa.Column('id', UUID(as_uuid=True), primary_key=True, server_default=sa.text("gen_random_uuid()")),
        sa.Column('user_id', sa.Integer, nullable=False, index=True),
        sa.Column('annale_slug', sa.String(200), nullable=False),
        sa.Column('subject_choice', sa.Integer),
        sa.Column('started_at', sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.Column('submitted_at', sa.DateTime(timezone=True)),
        sa.Column('time_used_sec', sa.Integer, server_default='0'),
        sa.Column('score_global', sa.Integer, server_default='0'),
        sa.Column('status', sa.String(20), server_default='in_progress'),
        sa.Column('scores_by_exercise', JSONB, server_default='{}'),
        sa.Column('scores_by_verb', JSONB, server_default='{}'),
        sa.Column('debrief', JSONB, server_default='{}'),
    )

    op.create_table(
        'bac_answers',
        sa.Column('id', UUID(as_uuid=True), primary_key=True, server_default=sa.text("gen_random_uuid()")),
        sa.Column('session_id', UUID(as_uuid=True), sa.ForeignKey('bac_sessions.id', ondelete='CASCADE'), nullable=False, index=True),
        sa.Column('exercise_id', sa.String(50), nullable=False),
        sa.Column('question_id', sa.String(50), nullable=False),
        sa.Column('verb_slug', sa.String(50)),
        sa.Column('answer_text', sa.Text, server_default=''),
        sa.Column('skipped', sa.Boolean, server_default='false'),
        sa.Column('score', sa.Integer, server_default='0'),
        sa.Column('feedback', sa.Text),
        sa.Column('saved_at', sa.DateTime(timezone=True), server_default=sa.func.now()),
    )

    op.create_table(
        'bac_subjects',
        sa.Column('id', UUID(as_uuid=True), primary_key=True, server_default=sa.text("gen_random_uuid()")),
        sa.Column('annale_slug', sa.String(200), nullable=False, index=True),
        sa.Column('subject_number', sa.Integer, nullable=False),
        sa.Column('title_ar', sa.String(300), nullable=False),
        sa.Column('themes_ar', JSONB, server_default='[]'),
        sa.Column('estimated_minutes', sa.Integer, server_default='120'),
        sa.Column('exercises', JSONB, server_default='[]'),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.UniqueConstraint('annale_slug', 'subject_number', name='uq_bac_subjects_annale_num'),
    )


def downgrade():
    op.drop_table('bac_subjects')
    op.drop_table('bac_answers')
    op.drop_table('bac_sessions')
