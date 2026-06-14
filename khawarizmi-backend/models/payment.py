from sqlalchemy import Column, Integer, BigInteger, String, Float, DateTime, ForeignKey, func, text
from sqlalchemy.dialects.postgresql import JSONB
from database import Base


class Payment(Base):
    __tablename__ = "payments"

    id = Column(BigInteger, primary_key=True, autoincrement=True)
    checkout_id = Column(String(100), nullable=False, unique=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=True)
    amount = Column(Float, nullable=False)
    status = Column(String(20), server_default="pending", nullable=True)
    raw_webhook = Column(JSONB, server_default=text("'{}'::jsonb"), nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=True)
    paid_at = Column(DateTime(timezone=True), nullable=True)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=True)
