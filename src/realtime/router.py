from fastapi import APIRouter, WebSocket, WebSocketDisconnect
from pydantic import ValidationError

from src.auth import WSValidToken

from .connection_manager import manager
from .schemas import WebSocketMessage

ws_router = APIRouter()


@ws_router.websocket("/{topic}")
async def websocket_endpoint(ws: WebSocket, topic: str, _: WSValidToken):
    await manager.connect(ws, topic)
    try:
        while True:
            data = await ws.receive_json()
            try:
                message = WebSocketMessage.model_validate(data)
                if message.topic != topic:
                    await ws.send_text(
                        f"Error: Message topic '{message.topic}' does not match connection topic '{topic}'."
                    )
                    continue

                # Broadcast the original, full message
                await manager.broadcast_to_topic(topic, data)
            except ValidationError as e:
                # Handle invalid message format
                await ws.send_text(f"Invalid message format: {e}")

    except WebSocketDisconnect:
        await manager.disconnect(ws, topic)
