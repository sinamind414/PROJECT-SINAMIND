"""Add action verbs tables

Revision ID: 008
Revises: 007
"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects.postgresql import JSONB, UUID

revision = '008'
down_revision = '007'
branch_labels = None
depends_on = None


def upgrade():
    op.create_table(
        'action_verbs',
        sa.Column('id', UUID(as_uuid=True), primary_key=True, server_default=sa.text("gen_random_uuid()")),
        sa.Column('slug', sa.String(50), unique=True, nullable=False, index=True),
        sa.Column('ar', sa.String(100), nullable=False),
        sa.Column('fr', sa.String(100), nullable=False),
        sa.Column('category', sa.String(50), nullable=False),
        sa.Column('priority', sa.String(20), nullable=False, server_default='medium'),
        sa.Column('definition_ar', sa.Text, nullable=False),
        sa.Column('objective_ar', sa.Text, nullable=False),
        sa.Column('formula_ar', sa.Text),
        sa.Column('steps', JSONB, server_default='[]'),
        sa.Column('required_markers', JSONB, server_default='[]'),
        sa.Column('forbidden_markers', JSONB, server_default='[]'),
        sa.Column('common_errors', JSONB, server_default='[]'),
        sa.Column('scoring_rules', JSONB, server_default='[]'),
        sa.Column('bad_example', JSONB),
        sa.Column('good_example', JSONB),
        sa.Column('feedback_template_ar', sa.Text),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now()),
    )

    op.create_table(
        'action_verb_exercises',
        sa.Column('id', UUID(as_uuid=True), primary_key=True, server_default=sa.text("gen_random_uuid()")),
        sa.Column('verb_slug', sa.String(50), sa.ForeignKey('action_verbs.slug', ondelete='CASCADE'), nullable=False, index=True),
        sa.Column('type', sa.String(30), nullable=False, server_default='application'),
        sa.Column('question_ar', sa.Text, nullable=False),
        sa.Column('context_ar', sa.Text),
        sa.Column('model_answer_ar', sa.Text),
        sa.Column('difficulty', sa.Integer, server_default='3'),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now()),
    )

    op.create_table(
        'action_verb_progress',
        sa.Column('id', UUID(as_uuid=True), primary_key=True, server_default=sa.text("gen_random_uuid()")),
        sa.Column('user_id', UUID(as_uuid=True), nullable=False, index=True),
        sa.Column('verb_slug', sa.String(50), sa.ForeignKey('action_verbs.slug', ondelete='CASCADE'), nullable=False),
        sa.Column('stability', sa.Float, server_default='0.0'),
        sa.Column('difficulty', sa.Float, server_default='0.0'),
        sa.Column('fsrs_state', JSONB, server_default='{}'),
        sa.Column('prochaine_revision', sa.DateTime(timezone=True)),
        sa.Column('interval_jours', sa.Float, server_default='0.0'),
        sa.Column('last_score', sa.Integer, server_default='0'),
        sa.Column('attempts', sa.Integer, server_default='0'),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.func.now(), onupdate=sa.func.now()),
        sa.UniqueConstraint('user_id', 'verb_slug', name='uq_verb_progress_user_verb'),
    )


def downgrade():
    op.drop_table('action_verb_progress')
    op.drop_table('action_verb_exercises')
    op.drop_table('action_verbs')
