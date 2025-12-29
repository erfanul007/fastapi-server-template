from pydantic import BaseModel, Field


class WebSocketNotification(BaseModel):
    group_id: str
    message_type: str = Field(..., description="different purposes message type")
