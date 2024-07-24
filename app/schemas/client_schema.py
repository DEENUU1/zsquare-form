from pydantic import BaseModel
from datetime import datetime


class ClientOutputSchema(BaseModel):
    id: int
    full_name: str
    birth_date: str
    location: str
    phone: str
    email: str
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True
