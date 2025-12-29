from pydantic import BaseModel


class WebSocketMessage(BaseModel):
    topic: str
    type: str
