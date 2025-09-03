from __future__ import annotations
from pydantic import BaseModel, Field
from typing import Literal, Optional
from datetime import datetime

Channel = Literal["whatsapp", "web"]

class MessageIn(BaseModel):
    channel: Channel = "web"
    convo_id: Optional[str] = None
    from_user: str = Field(..., description="לקוח/מספר שולח, לדוגמה: 972501234567")
    to_business: Optional[str] = None
    text: str
    ts: datetime = Field(default_factory=datetime.utcnow)
    metadata: dict = Field(default_factory=dict)

class MessageOut(BaseModel):
    channel: Channel = "web"
    to_user: str
    text: str
    handoff: bool = False
    handoff_reason: Optional[str] = None
    tone: Optional[str] = None
