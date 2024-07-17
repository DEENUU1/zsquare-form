from sqlalchemy import ForeignKey, Column, Integer, String, DateTime, func, create_engine, Boolean
from sqlalchemy.orm import relationship
from config.database import Base


class FormData(Base):
    __tablename__ = "form"

    id = Column(Integer, primary_key=True, autoincrement=True)
    bike = Column(String, nullable=True)
    boots = Column(String, nullable=True)
    insoles = Column(String, nullable=True)
    pedals = Column(String, nullable=True)
    other_bikes = Column(String, nullable=True)
    tool_annotation = Column(String, nullable=True)
    sport_history = Column(String, nullable=True)
    sport_annotation = Column(String, nullable=True)
    position_problem = Column(String, nullable=True)
    adnotation_position_problem = Column(String, nullable=True)
    years_cycling = Column(Integer, nullable=True)
    annual_mileage = Column(Integer, nullable=True)
    weekly_rides = Column(Integer, nullable=True)
    session_duration = Column(String, nullable=True)
    participated_in_races = Column(Boolean, nullable=True)
    best_results = Column(String, nullable=True)
    intensity_measurement = Column(String, nullable=True)
    other_sports = Column(String, nullable=True)
    bike_confidence = Column(Integer, nullable=True)
    gear_changing = Column(Boolean, nullable=True)
    autumn_winter_riding = Column(Boolean, nullable=True)
    preferred_grip = Column(String, nullable=True)
    cadence_comfort = Column(String, nullable=True)
    group_riding_skills = Column(String, nullable=True)
    cornering_style = Column(String, nullable=True)
    brake_usage = Column(String, nullable=True)
    tire_pressure_check = Column(String, nullable=True)
    injuries = Column(String, nullable=True)
    injuries_during_cycling = Column(Boolean, nullable=True)
    client_id = Column(Integer, ForeignKey("client.id"), nullable=False)
    report = relationship("Report", back_populates="form_data", uselist=False)
    message = relationship("Message", backref="form", cascade="all, delete-orphan")
    created_at = Column(DateTime, default=func.now())
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())
