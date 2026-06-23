"""Create exercises and user_exercise_responses tables

Revision ID: 014
Revises: 013
"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects.postgresql import JSONB

revision = '014'
down_revision = '013'
branch_labels = None
depends_on = None


def upgrade():
    op.create_table(
        'exercises',
        sa.Column('id', sa.Integer, primary_key=True, autoincrement=True),
        sa.Column('question', sa.Text, nullable=False),
        sa.Column('question_ar', sa.Text, nullable=True),
        sa.Column('corrige', sa.Text, nullable=True),
        sa.Column('corrige_ar', sa.Text, nullable=True),
        sa.Column('points', sa.Integer, server_default='4', nullable=False),
        sa.Column('chapitre', sa.String(255), nullable=False),
        sa.Column('matiere', sa.String(100), nullable=False),
        sa.Column('difficulte', sa.String(20), server_default='moyen'),
        sa.Column('type', sa.String(50), server_default='qroc'),
        sa.Column('language', sa.String(10), server_default='fr'),
        sa.Column('metadata_json', JSONB, nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.func.now()),
    )
    op.create_index('ix_exercises_chapitre', 'exercises', ['chapitre'])
    op.create_index('ix_exercises_matiere', 'exercises', ['matiere'])

    op.create_table(
        'exercise_documents',
        sa.Column('id', sa.Integer, primary_key=True, autoincrement=True),
        sa.Column('exercise_id', sa.Integer, sa.ForeignKey('exercises.id'), nullable=False),
        sa.Column('contenu', sa.Text, nullable=False),
        sa.Column('type_document', sa.String(50), server_default='sujet'),
        sa.Column('langue', sa.String(10), server_default='fr'),
        sa.Column('fichier_url', sa.String(500), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now()),
    )
    op.create_index('ix_exercise_documents_exercise', 'exercise_documents', ['exercise_id'])

    op.create_table(
        'user_exercise_responses',
        sa.Column('id', sa.Integer, primary_key=True, autoincrement=True),
        sa.Column('exercise_id', sa.Integer, sa.ForeignKey('exercises.id'), nullable=False),
        sa.Column('user_id', sa.Integer, nullable=False),
        sa.Column('answer', sa.Text, nullable=False),
        sa.Column('language', sa.String(10), server_default='ar'),
        sa.Column('score', sa.Float, nullable=True),
        sa.Column('max_score', sa.Float, nullable=True),
        sa.Column('feedback', sa.Text, nullable=True),
        sa.Column('corrected_answer', sa.Text, nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now()),
    )
    op.create_index('ix_user_exercise_responses_user', 'user_exercise_responses', ['user_id'])
    op.create_index('ix_user_exercise_responses_exercise', 'user_exercise_responses', ['exercise_id'])


def downgrade():
    op.drop_table('user_exercise_responses')
    op.drop_table('exercise_documents')
    op.drop_table('exercises')
