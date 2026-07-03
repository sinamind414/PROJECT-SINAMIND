"""
Modèle Duel — defi 1v1 entre amis.
"""

import uuid
from sqlalchemy import Column, DateTime, ForeignKey, Integer, String, func, text
from sqlalchemy.dialects.postgresql import UUID

from database import Base


class Duel(Base):
    __tablename__ = "duels"

    id = Column(UUID(as_uuid=True), primary_key=True, server_default=text("gen_random_uuid()"))
    verb_slug = Column(String(50), nullable=False, index=True)
    host_user_id = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    guest_user_id = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=True)
    host_score = Column(Integer, nullable=True)
    guest_score = Column(Integer, nullable=True)
    host_completed_at = Column(DateTime(timezone=True), nullable=True)
    guest_completed_at = Column(DateTime(timezone=True), nullable=True)
    status = Column(String(20), server_default="pending")
    winner_user_id = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="SET NULL"), nullable=True)
    share_token = Column(String(50), unique=True, nullable=False, index=True)
    expires_at = Column(DateTime(timezone=True), nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
