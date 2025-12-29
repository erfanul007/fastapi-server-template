import logging

from .connection_manager import manager
from .schemas import WebSocketMessage

logger = logging.getLogger(__name__)


async def notify_group_on_update(notification: WebSocketMessage):
    payload_json = notification.model_dump_json()

    await manager.broadcast_to_topic(notification.topic, payload_json)
    logger.info("Notification sent to all clients in group [%s]", notification.topic)
