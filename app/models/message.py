from sqlalchemy import ForeignKey, Column, Integer, String, DateTime, func
from config.database import Base
from enum import Enum
from sqlalchemy import Enum as SQLAlchemyEnum


class Role(Enum):
    assistant = "assistant"
    user = "user"
    system = "system"


class Message(Base):
    __tablename__ = "message"

    id = Column(Integer, primary_key=True, autoincrement=True)
    role = Column(SQLAlchemyEnum(Role), nullable=False)
    text = Column(String, nullable=False)
    form_id = Column(Integer, ForeignKey("form.id"), nullable=False)
    created_at = Column(DateTime, default=func.now())
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())
