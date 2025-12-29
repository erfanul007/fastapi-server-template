import json
import logging
from typing import Any, Dict, List

from fastapi import WebSocket

logger = logging.getLogger(__name__)


class ConnectionManager:
    def __init__(self) -> None:
        self.topic_connections: Dict[str, List[WebSocket]] = {}

    async def connect(self, ws: WebSocket, topic: str) -> None:
        await ws.accept()
        if topic not in self.topic_connections:
            self.topic_connections[topic] = []
        self.topic_connections[topic].append(ws)
        logger.info(
            f"WebSocket connected to topic '{topic}'. Total connections for topic: {len(self.topic_connections[topic])}"
        )

    async def disconnect(self, ws: WebSocket, topic: str) -> None:
        if topic in self.topic_connections and ws in self.topic_connections[topic]:
            self.topic_connections[topic].remove(ws)
            logger.info(
                f"WebSocket disconnected from topic '{topic}'. Remaining connections for topic: {len(self.topic_connections[topic])}"
            )
        await ws.close()

    async def broadcast_to_topic(self, topic: str, message: Any) -> None:
        if topic in self.topic_connections:
            if isinstance(message, dict):
                message_str = json.dumps(message)
            else:
                message_str = str(message)

            for connection in self.topic_connections[topic]:
                await connection.send_text(message_str)
            logger.info(f"Broadcasted message to topic '{topic}'.")


manager = ConnectionManager()
