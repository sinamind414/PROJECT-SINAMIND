from sqlalchemy import Column, Integer, String, DateTime, func, text
from sqlalchemy.dialects.postgresql import JSONB
from database import Base


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, autoincrement=True)
    email = Column(String(255), nullable=False, unique=True)
    password_hash = Column(String(255), nullable=False)
    prenom = Column(String(100), nullable=True)
    wilaya = Column(String(50), nullable=True)
    filiere = Column(String(50), server_default="sciences", nullable=True)
    plan = Column(String(20), server_default="free", nullable=True)
    fsrs_config = Column(JSONB, server_default=text("'{}'::jsonb"), nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=True)
    last_active = Column(DateTime(timezone=True), server_default=func.now(), nullable=True)


class Waitlist(Base):
    __tablename__ = "waitlist"

    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(50), nullable=False)
    email = Column(String(255), nullable=False, unique=True)
    wilaya = Column(String(50), nullable=True)
    lang = Column(String(5), server_default="fr", nullable=True)
    source = Column(String, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=True)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=True)
