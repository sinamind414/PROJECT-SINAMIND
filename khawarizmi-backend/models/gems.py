"""
Modèle UserGems — solde de gemmes de l'utilisateur.
"""

import uuid
from sqlalchemy import Column, DateTime, Integer, ForeignKey, func, text
from sqlalchemy.dialects.postgresql import UUID

from database import Base


class UserGems(Base):
    __tablename__ = "user_gems"

    id = Column(UUID(as_uuid=True), primary_key=True, server_default=text("gen_random_uuid()"))
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), unique=True, nullable=False)
    balance = Column(Integer, server_default="0", nullable=False)
    total_earned = Column(Integer, server_default="0", nullable=False)
    total_spent = Column(Integer, server_default="0", nullable=False)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())


class GemTransaction(Base):
    __tablename__ = "gem_transactions"

    id = Column(UUID(as_uuid=True), primary_key=True, server_default=text("gen_random_uuid()"))
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    amount = Column(Integer, nullable=False)
    reason = Column(String(100), nullable=False)
    reference_id = Column(String(50), nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
