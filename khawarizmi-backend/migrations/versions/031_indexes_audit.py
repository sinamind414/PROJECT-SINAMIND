"""031 : index prioritaires (audit P0-7)

- UNIQUE da_fsrs(user_id, verb_slug, chapter_slug)
- da_answers(session_id, question_id)
- da_questions(scenario_id, verb_slug)
- da_scenarios(slug)
- lesson_blocks(chapter_slug, sort_order)
- rag_chunks(chapitre) + (source, chapitre)
- correction_audit(created_at) pour purge
"""
from alembic import op

# revision identifiers, used by Alembic.
revision = "031"
down_revision = "030"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.execute(
        "CREATE UNIQUE INDEX IF NOT EXISTS ux_da_fsrs_user_verb_chapter "
        "ON da_fsrs(user_id, verb_slug, chapter_slug)"
    )
    op.execute(
        "CREATE INDEX IF NOT EXISTS ix_da_answers_session_question "
        "ON da_answers(session_id, question_id)"
    )
    op.execute(
        "CREATE INDEX IF NOT EXISTS ix_da_questions_scenario_verb "
        "ON da_questions(scenario_id, verb_slug)"
    )
    op.execute(
        "CREATE INDEX IF NOT EXISTS ix_da_scenarios_slug ON da_scenarios(slug)"
    )
    op.execute(
        "CREATE INDEX IF NOT EXISTS ix_lesson_blocks_chapter_order "
        "ON lesson_blocks(chapter_slug, sort_order)"
    )
    op.execute(
        "CREATE INDEX IF NOT EXISTS ix_rag_chunks_chapitre ON rag_chunks(chapitre)"
    )
    op.execute(
        "CREATE INDEX IF NOT EXISTS ix_rag_chunks_source_chapitre "
        "ON rag_chunks(source, chapitre)"
    )
    op.execute(
        "CREATE INDEX IF NOT EXISTS ix_correction_audit_created "
        "ON correction_audit(created_at)"
    )


def downgrade() -> None:
    for idx in (
        "ux_da_fsrs_user_verb_chapter",
        "ix_da_answers_session_question",
        "ix_da_questions_scenario_verb",
        "ix_da_scenarios_slug",
        "ix_lesson_blocks_chapter_order",
        "ix_rag_chunks_chapitre",
        "ix_rag_chunks_source_chapitre",
        "ix_correction_audit_created",
    ):
        op.execute(f"DROP INDEX IF EXISTS {idx}")
