"""Initial schema — 10 tables + 1 materialized view

Revision ID: 001
Revises:
Create Date: 2026-06-14
"""
from typing import Sequence, Union
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

revision: str = "001"
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # pgvector extension
    op.execute("CREATE EXTENSION IF NOT EXISTS vector")

    # 1. users
    op.create_table(
        "users",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("email", sa.String(255), nullable=False),
        sa.Column("password_hash", sa.String(255), nullable=False),
        sa.Column("prenom", sa.String(100), nullable=True),
        sa.Column("wilaya", sa.String(50), nullable=True),
        sa.Column("filiere", sa.String(50), server_default="sciences", nullable=True),
        sa.Column("plan", sa.String(20), server_default="free", nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True),
                   server_default=sa.func.now(), nullable=True),
        sa.Column("last_active", sa.DateTime(timezone=True),
                   server_default=sa.func.now(), nullable=True),
        sa.Column("fsrs_config", postgresql.JSONB,
                   server_default=sa.text("'{}'::jsonb"), nullable=True),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("email"),
    )

    # 2. micro_concepts
    op.create_table(
        "micro_concepts",
        sa.Column("id", sa.String(50), nullable=False),
        sa.Column("chapitre_id", sa.String(50), nullable=False),
        sa.Column("matiere", sa.String(50), nullable=False),
        sa.Column("nom", sa.String(255), nullable=False),
        sa.Column("description", sa.Text(), nullable=True),
        sa.Column("code", sa.String(64), nullable=True),
        sa.Column("chapter", sa.String(32), nullable=True),
        sa.Column("label_fr", sa.Text(), nullable=True),
        sa.Column("label_ar", sa.Text(), nullable=True),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("code"),
    )
    op.create_index("idx_mc_chapitre", "micro_concepts", ["chapitre_id"])

    # 3. waitlist
    op.create_table(
        "waitlist",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("name", sa.String(50), nullable=False),
        sa.Column("email", sa.String(255), nullable=False),
        sa.Column("wilaya", sa.String(50), nullable=True),
        sa.Column("lang", sa.String(5), server_default="fr", nullable=True),
        sa.Column("source", sa.Text(), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True),
                   server_default=sa.func.now(), nullable=True),
        sa.Column("updated_at", sa.DateTime(timezone=True),
                   server_default=sa.func.now(), nullable=True),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("email"),
    )

    # 4. payments
    op.create_table(
        "payments",
        sa.Column("id", sa.BigInteger(), autoincrement=True, nullable=False),
        sa.Column("checkout_id", sa.String(100), nullable=False),
        sa.Column("user_id", sa.Integer(), nullable=True),
        sa.Column("amount", sa.Float(), nullable=False),
        sa.Column("status", sa.String(20), server_default="pending", nullable=True),
        sa.Column("raw_webhook", postgresql.JSONB,
                   server_default=sa.text("'{}'::jsonb"), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True),
                   server_default=sa.func.now(), nullable=True),
        sa.Column("paid_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("updated_at", sa.DateTime(timezone=True),
                   server_default=sa.func.now(), nullable=True),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("checkout_id"),
        sa.ForeignKeyConstraint(["user_id"], ["users.id"], ondelete="CASCADE"),
    )
    op.create_index("idx_payments_checkout", "payments", ["checkout_id"])

    # 5. reference_embeddings
    op.create_table(
        "reference_embeddings",
        sa.Column("id", sa.BigInteger(), autoincrement=True, nullable=False),
        sa.Column("question_id", sa.String(255), nullable=False),
        sa.Column("variant_index", sa.SmallInteger(),
                   server_default=sa.text("0"), nullable=False),
        sa.Column("reference_text", sa.Text(), nullable=False),
        sa.Column("embedding", sa.Text(), nullable=False),
        sa.Column("source", sa.String(20), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True),
                   server_default=sa.func.now(), nullable=True),
        sa.Column("updated_at", sa.DateTime(timezone=True),
                   server_default=sa.func.now(), nullable=True),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("question_id", "variant_index"),
    )
    op.execute(
        "ALTER TABLE reference_embeddings "
        "ALTER COLUMN embedding TYPE vector(384) USING embedding::vector(384)"
    )
    op.execute(
        "CREATE INDEX idx_ref_embeddings_hnsw "
        "ON reference_embeddings "
        "USING hnsw (embedding vector_cosine_ops) "
        "WITH (m=16, ef_construction=64)"
    )
    op.create_index("idx_ref_embeddings_question_id",
                     "reference_embeddings", ["question_id"])

    # 6. common_mistakes
    op.create_table(
        "common_mistakes",
        sa.Column("id", postgresql.UUID(),
                   server_default=sa.text("gen_random_uuid()"), nullable=False),
        sa.Column("chapitre_id", sa.String(32), nullable=False),
        sa.Column("error_type", sa.String(20), nullable=False),
        sa.Column("error_pattern", sa.Text(), nullable=False),
        sa.Column("frequency", sa.Float(), server_default=sa.text("0.5"), nullable=True),
        sa.Column("feedback_ar", sa.Text(), nullable=False),
        sa.Column("feedback_fr", sa.Text(), nullable=True),
        sa.Column("feynman_prompt", sa.Text(), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True),
                   server_default=sa.func.now(), nullable=True),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("idx_mistakes_chapitre", "common_mistakes", ["chapitre_id"])
    op.create_index("idx_mistakes_frequency", "common_mistakes", ["frequency"])

    # 7. concept_prerequisites
    op.create_table(
        "concept_prerequisites",
        sa.Column("concept_id", sa.String(100), nullable=False),
        sa.Column("prerequisite_id", sa.String(100), nullable=False),
        sa.Column("strength", sa.Float(), server_default=sa.text("1.0"), nullable=True),
        sa.Column("penalty_factor", sa.Float(),
                   server_default=sa.text("0.15"), nullable=True),
        sa.PrimaryKeyConstraint("concept_id", "prerequisite_id"),
    )

    # 8. question_concept_mapping (legacy)
    op.create_table(
        "question_concept_mapping",
        sa.Column("question_id", sa.String(100), nullable=False),
        sa.Column("concept_id", sa.String(100), nullable=False),
        sa.Column("weight", sa.Float(), nullable=False),
        sa.PrimaryKeyConstraint("question_id", "concept_id"),
    )

    # 9. question_concept_map (new, normalised)
    op.create_table(
        "question_concept_map",
        sa.Column("question_id", sa.String(100), nullable=False),
        sa.Column("micro_concept", sa.String(64), nullable=True),
        sa.Column("weight", sa.Float(), server_default=sa.text("1.0"), nullable=False),
        sa.PrimaryKeyConstraint("question_id", "micro_concept"),
        sa.ForeignKeyConstraint(
            ["micro_concept"],
            ["micro_concepts.code"],
            ondelete="CASCADE",
        ),
    )
    op.create_check_constraint(
        "weight_range",
        "question_concept_map",
        sa.text("weight > 0 AND weight <= 1"),
    )

    # 10. mastery_micro_concepts
    op.create_table(
        "mastery_micro_concepts",
        sa.Column("id", sa.BigInteger(), autoincrement=True, nullable=False),
        sa.Column("user_id", sa.Integer(), nullable=False),
        sa.Column("micro_concept_id", sa.String(50), nullable=False),
        sa.Column("concept_id", sa.String(100), nullable=True),
        sa.Column("chapter", sa.String(50), nullable=True),
        sa.Column("prochaine_revision", sa.DateTime(timezone=True),
                   server_default=sa.func.now(), nullable=True),
        sa.Column("interval_jours", sa.Integer(),
                   server_default=sa.text("1"), nullable=True),
        sa.Column("difficulty", sa.Float(),
                   server_default=sa.text("0.0"), nullable=True),
        sa.Column("stability", sa.Float(),
                   server_default=sa.text("0.0"), nullable=True),
        sa.Column("fsrs_state", postgresql.JSONB,
                   server_default=sa.text("'{}'::jsonb"), nullable=True),
        sa.Column("reps", sa.Integer(), server_default=sa.text("0"), nullable=True),
        sa.Column("lapses", sa.Integer(), server_default=sa.text("0"), nullable=True),
        sa.Column("state", sa.SmallInteger(), server_default=sa.text("0"), nullable=True),
        sa.Column("due_date", sa.DateTime(timezone=True),
                   server_default=sa.func.now(), nullable=True),
        sa.Column("last_review", sa.DateTime(timezone=True), nullable=True),
        sa.Column("total_reviews", sa.Integer(),
                   server_default=sa.text("0"), nullable=True),
        sa.Column("avg_score", sa.Float(),
                   server_default=sa.text("0.0"), nullable=True),
        sa.Column("streak", sa.Integer(),
                   server_default=sa.text("0"), nullable=True),
        sa.Column("pending_real_evaluation", sa.Boolean(),
                   server_default=sa.text("false"), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True),
                   server_default=sa.func.now(), nullable=True),
        sa.Column("updated_at", sa.DateTime(timezone=True),
                   server_default=sa.func.now(), nullable=True),
        sa.PrimaryKeyConstraint("id"),
        sa.ForeignKeyConstraint(["user_id"], ["users.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["micro_concept_id"], ["micro_concepts.id"]),
        sa.UniqueConstraint("user_id", "micro_concept_id"),
        sa.UniqueConstraint("user_id", "concept_id"),
    )
    op.create_index("idx_mastery_user_revision", "mastery_micro_concepts",
                     ["user_id", sa.text("prochaine_revision ASC")])
    op.create_index("idx_mastery_user_chapitre", "mastery_micro_concepts",
                     ["user_id", "micro_concept_id"])
    op.create_index("idx_mastery_fsrs_state", "mastery_micro_concepts",
                     [sa.text("fsrs_state")], postgresql_using="gin")
    op.create_index("idx_due_user", "mastery_micro_concepts",
                     ["user_id", "due_date"])

    # Materialised view
    op.execute("""
        CREATE MATERIALIZED VIEW IF NOT EXISTS mastery_by_chapter AS
        SELECT
            user_id,
            chapter,
            COUNT(*) AS total_concepts,
            COUNT(*) FILTER (WHERE stability > 10.0 AND streak >= 3) AS mastered,
            COUNT(*) FILTER (WHERE state = 0) AS not_started,
            AVG(stability) AS avg_stability,
            MIN(due_date) AS next_review_due
        FROM mastery_micro_concepts
        WHERE chapter IS NOT NULL
        GROUP BY user_id, chapter
    """)
    op.create_index("idx_mastery_by_chapter_user_chap",
                     "mastery_by_chapter",
                     ["user_id", "chapter"],
                     unique=True)


def downgrade() -> None:
    op.execute("DROP MATERIALIZED VIEW IF EXISTS mastery_by_chapter")
    op.drop_table("mastery_micro_concepts")
    op.drop_table("question_concept_map")
    op.drop_table("question_concept_mapping")
    op.drop_table("concept_prerequisites")
    op.drop_table("common_mistakes")
    op.drop_table("reference_embeddings")
    op.drop_table("payments")
    op.drop_table("waitlist")
    op.drop_table("micro_concepts")
    op.drop_table("users")
    op.execute("DROP EXTENSION IF EXISTS vector")
