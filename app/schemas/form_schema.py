from pydantic import BaseModel
from typing import Optional
from datetime import datetime


class FormOutputSchema(BaseModel):
    id: int
    bike: Optional[str] = None
    boots: Optional[str] = None
    insoles: Optional[str] = None
    pedals: Optional[str] = None
    other_bikes: Optional[str] = None
    tool_annotation: Optional[str] = None
    sport_history: Optional[str] = None
    sport_annotation: Optional[str] = None
    position_problem: Optional[str] = None
    adnotation_position_problem: Optional[str] = None
    years_cycling: Optional[int] = None
    annual_mileage: Optional[int] = None
    weekly_rides: Optional[int] = None
    session_duration: Optional[str] = None
    participated_in_races: Optional[bool] = None
    best_results: Optional[str] = None
    intensity_measurement: Optional[str] = None
    other_sports: Optional[str] = None
    bike_confidence: Optional[int] = None
    gear_changing: Optional[bool] = None
    autumn_winter_riding: Optional[bool] = None
    preferred_grip: Optional[str] = None
    cadence_comfort: Optional[str] = None
    group_riding_skills: Optional[str] = None
    cornering_style: Optional[str] = None
    brake_usage: Optional[str] = None
    tire_pressure_check: Optional[str] = None
    injuries: Optional[str] = None
    injuries_during_cycling: Optional[bool] = None
    client_id: int
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True