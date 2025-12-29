import logging

from .connection_manager import manager
from .schemas import WebSocketNotification

logger = logging.getLogger(__name__)


async def notify_group_on_update(notification: WebSocketNotification):
    payload_json = notification.model_dump_json()

    await manager.send_message_to_group(notification.group_id, payload_json)
    logger.info("Notification sent to all clients in group [%s]", notification.group_id)
