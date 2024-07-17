from datetime import datetime

from pydantic import BaseModel


class ReportOutputSchema(BaseModel):
    id: int
    report_content: bytes
    form_data_id: int
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True
