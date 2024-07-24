from pydantic import BaseModel
from datetime import datetime


class ReportInputSchema(BaseModel):
    report_content: str
    form_data_id: int


class ReportOutputSchema(BaseModel):
    id: int
    report_content: bytes
    form_data_id: int
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True