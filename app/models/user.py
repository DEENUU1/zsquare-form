from sqlalchemy import Column, Integer, String
from config.database import Base


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    full_name = Column(String, unique=True, index=True)
    email = Column(String, unique=True, index=True)
    is_active = Column(Integer, default=0)
    hashed_password = Column(String)
