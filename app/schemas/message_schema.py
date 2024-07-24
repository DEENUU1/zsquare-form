from pydantic import BaseModel
from typing import Optional
from datetime import datetime


class MessageInputSchema(BaseModel):
    role: Optional[str] = None
    text: Optional[str] = None
    form_id: int


class MessageOutputSchema(BaseModel):
    id: int
    role: Optional[str] = None
    text: Optional[str] = None
    form_id: int
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True
