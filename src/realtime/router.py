from fastapi import APIRouter, WebSocket, WebSocketDisconnect

from src.auth import WSValidToken

from .connection_manager import manager

ws_router = APIRouter()


@ws_router.websocket("/chat-connect/{group_id}")
async def chat_ws(ws: WebSocket, group_id: str, _: WSValidToken):
    await manager.connect_to_group(ws, group_id)
    try:
        while True:
            await ws.receive_text()
    except WebSocketDisconnect:
        await manager.disconnect_from_group(ws, group_id)
