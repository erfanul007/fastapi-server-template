import logging
from typing import Dict, List

from fastapi import WebSocket

logger = logging.getLogger(__name__)


class ConnectionManager:
    def __init__(self) -> None:
        self.active: List[WebSocket] = []
        self.group_connections: Dict[str, List[WebSocket]] = {}

    async def connect_to_group(self, ws: WebSocket, group_id: str) -> None:
        await ws.accept()
        if group_id not in self.group_connections:
            self.group_connections[group_id] = []
        self.group_connections[group_id].append(ws)
        logger.info(
            f"Connected to group {group_id}. Number of connections to this group: {len(self.group_connections[group_id])}"
        )

    async def disconnect_from_group(self, ws: WebSocket, group_id: str) -> None:
        if ws in self.group_connections.get(group_id, []):
            self.group_connections[group_id].remove(ws)
        await ws.close()

    async def send_message_to_group(self, group_id: str, message: str) -> None:
        if group_id in self.group_connections:
            for conn in self.group_connections[group_id]:
                await conn.send_text(message)


manager = ConnectionManager()
