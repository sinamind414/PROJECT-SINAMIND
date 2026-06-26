from sqlalchemy import Column, ForeignKey, Integer

from database import Base


class ComboState(Base):
    __tablename__ = "combo_states"

    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), primary_key=True)
    current_combo = Column(Integer, default=0, nullable=False)
    max_combo = Column(Integer, default=0, nullable=False)
