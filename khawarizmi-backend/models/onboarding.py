"""
Modèle UserOnboarding — statut d'onboarding d'un utilisateur.
"""

import uuid
from sqlalchemy import Boolean, Column, DateTime, ForeignKey, func, text
from sqlalchemy.dialects.postgresql import UUID

from database import Base


class UserOnboarding(Base):
    __tablename__ = "user_onboarding"

    id = Column(UUID(as_uuid=True), primary_key=True, server_default=text("gen_random_uuid()"))
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), unique=True, nullable=False)
    step_1_done = Column(Boolean, server_default="false")
    step_2_done = Column(Boolean, server_default="false")
    step_3_done = Column(Boolean, server_default="false")
    completed_at = Column(DateTime(timezone=True), nullable=True)
    welcome_gems_awarded = Column(Boolean, server_default="false")
