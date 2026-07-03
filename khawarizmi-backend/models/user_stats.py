"""
Modèle UserStats — statistiques pour le classement.
"""

import uuid
from sqlalchemy import Column, DateTime, Float, ForeignKey, Integer, String, func, text
from sqlalchemy.dialects.postgresql import UUID

from database import Base


class UserStats(Base):
    __tablename__ = "user_stats"

    id = Column(UUID(as_uuid=True), primary_key=True, server_default=text("gen_random_uuid()"))
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), unique=True, nullable=False)
    wilaya_code = Column(String(10), nullable=True)
    school_name = Column(String(200), nullable=True)
    total_evaluations = Column(Integer, server_default="0")
    total_correct = Column(Integer, server_default="0")
    precision_score = Column(Float, server_default="0.0")
    weighted_score = Column(Float, server_default="0.0")
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
