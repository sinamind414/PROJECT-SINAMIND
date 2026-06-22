"""Add document analysis tables

Revision ID: 009
Revises: 008
"""

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects.postgresql import JSONB, UUID

revision = '009'
down_revision = '008'
branch_labels = None
depends_on = None


def upgrade():
    # ── Scénarios : 55 (un par chapitre du programme SVT) ──
    op.create_table(
        'da_scenarios',
        sa.Column('id', UUID(as_uuid=True), primary_key=True, server_default=sa.text("gen_random_uuid()")),
        sa.Column('slug', sa.String(120), unique=True, nullable=False, index=True),
        sa.Column('chapter_slug', sa.String(200), nullable=True, index=True),
        sa.Column('unit_key', sa.String(50), nullable=False),
        sa.Column('title_ar', sa.String(200), nullable=False),
        sa.Column('subtitle_ar', sa.String(300), nullable=False),
        sa.Column('context_ar', sa.Text, nullable=False),
        sa.Column('mindmap_node_id', sa.String(100), nullable=True),
        sa.Column('dominant_skills', JSONB, server_default='[]'),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now()),
    )

    # ── Documents : graphiques, tableaux, schémas, images ──
    op.create_table(
        'da_documents',
        sa.Column('id', UUID(as_uuid=True), primary_key=True, server_default=sa.text("gen_random_uuid()")),
        sa.Column('scenario_id', UUID(as_uuid=True), sa.ForeignKey('da_scenarios.id', ondelete='CASCADE'), nullable=False, index=True),
        sa.Column('doc_type', sa.String(30), nullable=False),
        sa.Column('title_ar', sa.String(200), nullable=False),
        sa.Column('caption_ar', sa.Text),
        sa.Column('data', JSONB, server_default='{}'),
        sa.Column('sort_order', sa.Integer, server_default='0'),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now()),
    )

    # ── Questions : L1/L2/L3 par verbe d'action ──
    op.create_table(
        'da_questions',
        sa.Column('id', UUID(as_uuid=True), primary_key=True, server_default=sa.text("gen_random_uuid()")),
        sa.Column('scenario_id', UUID(as_uuid=True), sa.ForeignKey('da_scenarios.id', ondelete='CASCADE'), nullable=False, index=True),
        sa.Column('verb_slug', sa.String(50), nullable=False, index=True),
        sa.Column('level', sa.String(5), nullable=False, server_default='L2'),
        sa.Column('n', sa.Integer, nullable=False),
        sa.Column('title_ar', sa.String(200), nullable=False),
        sa.Column('skill_ar', sa.String(200), nullable=False),
        sa.Column('doc_ref', sa.String(50), nullable=False),
        sa.Column('prompt_ar', sa.Text, nullable=False),
        sa.Column('placeholder_ar', sa.Text),
        sa.Column('model_answer_ar', sa.Text, nullable=False),
        sa.Column('learning_focus_ar', sa.Text),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now()),
    )

    # ── Sessions : une session = un élève fait un scénario ──
    op.create_table(
        'da_sessions',
        sa.Column('id', UUID(as_uuid=True), primary_key=True, server_default=sa.text("gen_random_uuid()")),
        sa.Column('user_id', UUID(as_uuid=True), nullable=False, index=True),
        sa.Column('scenario_id', UUID(as_uuid=True), sa.ForeignKey('da_scenarios.id', ondelete='CASCADE'), nullable=False, index=True),
        sa.Column('chapter_slug', sa.String(200), nullable=True),
        sa.Column('score_global', sa.Integer, server_default='0'),
        sa.Column('nb_questions', sa.Integer, server_default='0'),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now()),
    )

    # ── Réponses : évaluation par question ──
    op.create_table(
        'da_answers',
        sa.Column('id', UUID(as_uuid=True), primary_key=True, server_default=sa.text("gen_random_uuid()")),
        sa.Column('session_id', UUID(as_uuid=True), sa.ForeignKey('da_sessions.id', ondelete='CASCADE'), nullable=False, index=True),
        sa.Column('question_id', UUID(as_uuid=True), sa.ForeignKey('da_questions.id', ondelete='CASCADE'), nullable=False),
        sa.Column('verb_slug', sa.String(50), nullable=False),
        sa.Column('chapter_slug', sa.String(200), nullable=True),
        sa.Column('answer_text', sa.Text, nullable=False),
        sa.Column('score', sa.Integer, server_default='0'),
        sa.Column('score_max', sa.Integer, server_default='1'),
        sa.Column('percentage', sa.Integer, server_default='0'),
        sa.Column('feedback_ar', sa.Text),
        sa.Column('success', JSONB, server_default='[]'),
        sa.Column('errors', JSONB, server_default='[]'),
        sa.Column('missing_markers', JSONB, server_default='[]'),
        sa.Column('forbidden_found', JSONB, server_default='[]'),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now()),
    )

    # ── FSRS : état par user × verbe × chapitre ──
    op.create_table(
        'da_fsrs',
        sa.Column('id', UUID(as_uuid=True), primary_key=True, server_default=sa.text("gen_random_uuid()")),
        sa.Column('user_id', UUID(as_uuid=True), nullable=False, index=True),
        sa.Column('verb_slug', sa.String(50), nullable=False),
        sa.Column('chapter_slug', sa.String(200), nullable=False),
        sa.Column('stability', sa.Float, server_default='0.0'),
        sa.Column('difficulty', sa.Float, server_default='0.0'),
        sa.Column('fsrs_state', JSONB, server_default='{}'),
        sa.Column('prochaine_revision', sa.DateTime(timezone=True)),
        sa.Column('interval_jours', sa.Float, server_default='0.0'),
        sa.Column('last_score', sa.Integer, server_default='0'),
        sa.Column('attempts', sa.Integer, server_default='0'),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.func.now(), onupdate=sa.func.now()),
        sa.UniqueConstraint('user_id', 'verb_slug', 'chapter_slug', name='uq_da_fsrs_user_verb_chapter'),
    )


def downgrade():
    op.drop_table('da_fsrs')
    op.drop_table('da_answers')
    op.drop_table('da_sessions')
    op.drop_table('da_questions')
    op.drop_table('da_documents')
    op.drop_table('da_scenarios')
