"""
Modèle Streak — série quotidienne d'entraînement aux verbes d'action.
"""


from sqlalchemy import Column, Date, DateTime, ForeignKey, Integer, func, text
from sqlalchemy.dialects.postgresql import UUID

from database import Base


class ActionVerbStreak(Base):
    __tablename__ = "action_verb_streaks"

    id = Column(UUID(as_uuid=True), primary_key=True, server_default=text("gen_random_uuid()"))
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), unique=True, nullable=False)
    current_streak = Column(Integer, server_default="0", nullable=False)
    longest_streak = Column(Integer, server_default="0", nullable=False)
    last_active_date = Column(Date, nullable=True)
    freezes_remaining = Column(Integer, server_default="1", nullable=False)
    freezes_used_this_week = Column(Integer, server_default="0", nullable=False)
    week_start_date = Column(Date, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
