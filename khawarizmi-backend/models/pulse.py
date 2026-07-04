import uuid
from datetime import date, datetime

from sqlalchemy import Column, Date, DateTime, ForeignKey, Integer, String
from sqlalchemy.dialects.postgresql import JSONB

from database import Base


class DailyPulseCard(Base):
    __tablename__ = "daily_pulse_cards"

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id = Column(
        Integer,
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    card_date = Column(Date, nullable=False, index=True)
    position = Column(Integer, nullable=False)
    card_type = Column(String, nullable=False)
    verb_slug = Column(String, nullable=True, index=True)
    payload_json = Column(JSONB, nullable=False)
    completed_at = Column(DateTime, nullable=True)
