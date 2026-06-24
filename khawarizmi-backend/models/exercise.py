# models/exercise.py — Khawarizmi Pro
# Aligné sur migration 014 (création) + 016 (enhance)

from sqlalchemy import (
    Column, Integer, String, Text, Float, DateTime, ForeignKey, Boolean, Index,
)
from sqlalchemy.dialects.postgresql import JSONB, ARRAY
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from database import Base


class Exercise(Base):
    __tablename__ = "exercises"

    # ── Identité (014) ─────────────────────────────────────────────────
    id = Column(Integer, primary_key=True, autoincrement=True)
    question = Column(Text, nullable=False)
    question_ar = Column(Text, nullable=True)
    corrige = Column(Text, nullable=True)
    corrige_ar = Column(Text, nullable=True)

    # ── Métadonnées (014) ──────────────────────────────────────────────
    points = Column(Integer, server_default="4", nullable=False)
    chapitre = Column(String(255), nullable=False, index=True)
    matiere = Column(String(100), nullable=False, index=True)
    difficulte = Column(String(20), server_default="moyen", index=True)
    type = Column(String(50), server_default="qroc", index=True)
    language = Column(String(10), server_default="fr", index=True)
    metadata_json = Column(JSONB, nullable=True)

    # ── Pédagogie avancée (016) ────────────────────────────────────────
    explanation = Column(Text, nullable=True)
    correction_criteria = Column(JSONB, nullable=True)
    tags = Column(ARRAY(String), nullable=True)

    # ── Provenance (016) ───────────────────────────────────────────────
    source = Column(String(100), nullable=True)
    source_id = Column(String(100), nullable=True)

    # ── Stats (016) ────────────────────────────────────────────────────
    attempt_count = Column(Integer, server_default="0", nullable=False)
    success_count = Column(Integer, server_default="0", nullable=False)

    # ── Flags (016) ────────────────────────────────────────────────────
    is_active = Column(Boolean, server_default="true", nullable=False, index=True)

    # ── Timestamps (014) ───────────────────────────────────────────────
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=True)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=True)

    # ── Relations ──────────────────────────────────────────────────────
    documents = relationship(
        "ExerciseDocument", back_populates="exercise", cascade="all, delete-orphan"
    )
    responses = relationship(
        "UserExerciseResponse", back_populates="exercise", cascade="all, delete-orphan"
    )

    def get_question(self, lang: str = "fr") -> str:
        if lang == "ar" and self.question_ar:
            return self.question_ar
        return self.question

    def get_corrige(self, lang: str = "fr") -> str:
        if lang == "ar" and self.corrige_ar:
            return self.corrige_ar
        return self.corrige or ""

    @property
    def corrected_answer(self) -> str:
        return self.corrige or ""

    @property
    def success_rate(self) -> float:
        if not self.attempt_count:
            return 0.0
        return self.success_count / self.attempt_count


class ExerciseDocument(Base):
    __tablename__ = "exercise_documents"

    id = Column(Integer, primary_key=True, autoincrement=True)
    exercise_id = Column(
        Integer, ForeignKey("exercises.id", ondelete="CASCADE"), nullable=False, index=True
    )
    contenu = Column(Text, nullable=False)
    type_document = Column(String(50), server_default="sujet")
    langue = Column(String(10), server_default="fr")
    fichier_url = Column(String(500), nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=True)

    exercise = relationship("Exercise", back_populates="documents")


class UserExerciseResponse(Base):
    __tablename__ = "user_exercise_responses"

    id = Column(Integer, primary_key=True, autoincrement=True)
    exercise_id = Column(
        Integer, ForeignKey("exercises.id", ondelete="CASCADE"), nullable=False, index=True
    )
    user_id = Column(Integer, nullable=False, index=True)

    # ── Réponse élève (014) ────────────────────────────────────────────
    answer = Column(Text, nullable=False)
    language = Column(String(10), server_default="ar")
    score = Column(Float, nullable=True)
    feedback = Column(Text, nullable=True)
    corrected_answer = Column(Text, nullable=True)

    # ── Évaluation avancée (016) ──────────────────────────────────────
    max_score = Column(Float, nullable=True)
    percentage = Column(Float, nullable=True)
    is_correct = Column(Boolean, nullable=True)
    evaluation_details = Column(JSONB, nullable=True)

    # ── Contexte d'apprentissage (016) ─────────────────────────────────
    time_spent_seconds = Column(Integer, nullable=True)
    hints_used = Column(Integer, server_default="0", nullable=False)

    # ── Timestamps (014 + 016) ─────────────────────────────────────────
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=True)
    evaluated_at = Column(DateTime(timezone=True), nullable=True)

    exercise = relationship("Exercise", back_populates="responses")

    __table_args__ = (
        Index("ix_response_user_exercise", "user_id", "exercise_id", "created_at"),
        Index("ix_response_user_created", "user_id", "created_at"),
        Index("ix_response_is_correct", "is_correct", "user_id"),
    )
