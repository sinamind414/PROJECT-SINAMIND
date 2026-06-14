from sqlalchemy import Column, BigInteger, SmallInteger, String, Float, Text, DateTime, UniqueConstraint, func, text
from sqlalchemy.dialects.postgresql import UUID
from database import Base


class ReferenceEmbedding(Base):
    __tablename__ = "reference_embeddings"

    id = Column(BigInteger, primary_key=True, autoincrement=True)
    question_id = Column(String(255), nullable=False)
    variant_index = Column(SmallInteger, server_default="0", nullable=False)
    reference_text = Column(Text, nullable=False)
    embedding = Column(Text, nullable=False)
    source = Column(String(20), nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=True)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=True)

    __table_args__ = (
        UniqueConstraint("question_id", "variant_index"),
    )


class CommonMistake(Base):
    __tablename__ = "common_mistakes"

    id = Column(UUID, server_default=text("gen_random_uuid()"), primary_key=True)
    chapitre_id = Column(String(32), nullable=False)
    error_type = Column(String(20), nullable=False)
    error_pattern = Column(Text, nullable=False)
    frequency = Column(Float, server_default="0.5", nullable=True)
    feedback_ar = Column(Text, nullable=False)
    feedback_fr = Column(Text, nullable=True)
    feynman_prompt = Column(Text, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=True)
