from sqlalchemy import Column, Integer, BigInteger, SmallInteger, String, Float, Boolean, DateTime, ForeignKey, UniqueConstraint, func, text
from sqlalchemy.dialects.postgresql import JSONB
from database import Base


class MasteryMicroConcept(Base):
    __tablename__ = "mastery_micro_concepts"

    id = Column(BigInteger, primary_key=True, autoincrement=True)
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
    total_reviews = Column(Integer, server_default="0", nullable=True)
    avg_score = Column(Float, server_default="0.0", nullable=True)
    streak = Column(Integer, server_default="0", nullable=True)
    pending_real_evaluation = Column(Boolean, server_default="false", nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=True)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=True)

    __table_args__ = (
        UniqueConstraint("user_id", "micro_concept_id"),
        UniqueConstraint("user_id", "concept_id"),
    )
