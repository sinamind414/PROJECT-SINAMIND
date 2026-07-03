"""
Modèle VerbCity — association verbe → ville d'Algérie.
"""

import uuid
from sqlalchemy import Column, DateTime, Float, ForeignKey, Integer, String, func, text
from sqlalchemy.dialects.postgresql import UUID

from database import Base


class VerbCity(Base):
    __tablename__ = "verb_cities"

    id = Column(UUID(as_uuid=True), primary_key=True, server_default=text("gen_random_uuid()"))
    verb_slug = Column(String(50), ForeignKey("action_verbs.slug", ondelete="CASCADE"), unique=True, nullable=False)
    city_name_ar = Column(String(100), nullable=False)
    city_name_fr = Column(String(100), nullable=False)
    wilaya_code = Column(String(10), nullable=False)
    latitude = Column(Float, nullable=False)
    longitude = Column(Float, nullable=False)
    difficulty = Column(String(20), nullable=False)
    position_index = Column(Integer, nullable=False)


class CityProgress(Base):
    __tablename__ = "city_progress"

    id = Column(UUID(as_uuid=True), primary_key=True, server_default=text("gen_random_uuid()"))
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    city_id = Column(UUID(as_uuid=True), ForeignKey("verb_cities.id", ondelete="CASCADE"), nullable=False)
    level = Column(Integer, server_default="0")
    unlocked_at = Column(DateTime(timezone=True), server_default=func.now())

    __table_args__ = (
        # UniqueConstraint('user_id', 'city_id', name='uq_user_city'),
    )
