from sqlalchemy import ForeignKey, Column, Integer, String, DateTime, func, Text
from sqlalchemy.orm import relationship
from config.database import Base


class FormData(Base):
    __tablename__ = "form"

    id = Column(Integer, primary_key=True, autoincrement=True)
    bike_brand = Column(String, nullable=True)
    bike_model = Column(String, nullable=True)
    bike_size = Column(String, nullable=True)
    bike_year = Column(String, nullable=True)
    drive_group = Column(String, nullable=True)
    year_distance = Column(String, nullable=True)
    weekly_frequency = Column(String, nullable=True)
    avg_kilometer = Column(String, nullable=True)
    ride_style = Column(String, nullable=True)
    event = Column(String, nullable=True)
    other_activity = Column(String, nullable=True)
    visit_goal = Column(String, nullable=True)
    visit_problems = Column(Text, nullable=True)
    injuries = Column(Text, nullable=True)
    client_id = Column(Integer, ForeignKey("client.id"), nullable=False)
    report = relationship("Report", back_populates="form_data", uselist=False)
    message = relationship("Message", backref="form", cascade="all, delete-orphan")
    created_at = Column(DateTime, default=func.now())
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())
