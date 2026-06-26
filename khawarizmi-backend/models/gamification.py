import uuid

from sqlalchemy import Boolean, Column, Date, ForeignKey, Integer, String
from sqlalchemy.dialects.postgresql import JSONB

from database import Base


class UserStreak(Base):
    __tablename__ = "user_streaks"

    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), primary_key=True)
    current_streak = Column(Integer, default=0, nullable=False)
    longest_streak = Column(Integer, default=0, nullable=False)
    last_activity = Column(Date, nullable=True)


class UserPoints(Base):
    __tablename__ = "user_points"

    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), primary_key=True)
    total_points = Column(Integer, default=0, nullable=False)
    weekly_points = Column(Integer, default=0, nullable=False)


class UserAvatar(Base):
    __tablename__ = "user_avatars"

    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), primary_key=True)
    level = Column(Integer, default=1, nullable=False)
    xp = Column(Integer, default=0, nullable=False)


class Badge(Base):
    __tablename__ = "badges"

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    name = Column(String(100), nullable=False)
    description = Column(String, nullable=True)
    rarity = Column(String(20), nullable=True)
    icon = Column(String(50), nullable=True)


class UserBadge(Base):
    __tablename__ = "user_badges"

    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), primary_key=True)
    badge_id = Column(String, ForeignKey("badges.id", ondelete="CASCADE"), primary_key=True)
    unlocked_at = Column(Date, nullable=True)


class MysteryBox(Base):
    __tablename__ = "mystery_boxes"

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    rarity = Column(String(20), nullable=True)
    opened = Column(Boolean, default=False, nullable=False)
    content_type = Column(String(50), nullable=True)
    content_value = Column(JSONB, nullable=True)
    created_at = Column(Date, nullable=True)
