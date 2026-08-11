from sqlalchemy import (
    Boolean,
    Column,
    DateTime,
    Float,
    ForeignKey,
    Integer,
    SmallInteger,
    String,
    UniqueConstraint,
    func,
    text,
)
from sqlalchemy.dialects.postgresql import JSONB

from database import Base


class MasteryMicroConcept(Base):
    __tablename__ = "mastery_micro_concepts"

    # INTEGER PRIMARY KEY est l'alias rowid requis pour l'autoincrement SQLite.
    # PostgreSQL conserve son BIGINT créé par les migrations Alembic.
    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    micro_concept_id = Column(String(50), ForeignKey("micro_concepts.id"), nullable=False)
    concept_id = Column(String(100), nullable=True)
    chapter = Column(String(50), nullable=True)
    prochaine_revision = Column(DateTime(timezone=True), server_default=func.now(), nullable=True)
    interval_jours = Column(Integer, server_default="1", nullable=True)
    difficulty = Column(Float, server_default="0.0", nullable=True)
    stability = Column(Float, server_default="0.0", nullable=True)
    fsrs_state = Column(JSONB, server_default=text("'{}'::jsonb"), nullable=True)
    reps = Column(Integer, server_default="0", nullable=True)
    lapses = Column(Integer, server_default="0", nullable=True)
    state = Column(SmallInteger, server_default="0", nullable=True)
    due_date = Column(DateTime(timezone=True), server_default=func.now(), nullable=True)
    last_review = Column(DateTime(timezone=True), nullable=True)
    last_score = Column(Integer, nullable=True)
    attempts = Column(Integer, server_default="0", nullable=True)
    total_reviews = Column(Integer, server_default="0", nullable=True)
    avg_score = Column(Float, server_default="0.0", nullable=True)
    streak = Column(Integer, server_default="0", nullable=True)
    pending_real_evaluation = Column(Boolean, server_default="false", nullable=True)
    # Colonnes de fusion FSRS ajoutées par la migration 033. Elles doivent
    # aussi exister dans le modèle pour create_all en preview SQLite.
    source = Column(String(20), server_default="concept", nullable=True)
    item_key = Column(String(120), nullable=True)
    avg_pct = Column(Float, nullable=True)
    total_users = Column(Integer, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=True)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=True)

    __table_args__ = (
        UniqueConstraint("user_id", "micro_concept_id"),
        UniqueConstraint("user_id", "concept_id"),
    )
