import base64
import logging
import mimetypes
from pathlib import Path

from src.core.config import settings

logger = logging.getLogger(__name__)


def get_file_content(path: str) -> tuple[bytes, str]:
    p = Path(path)

    try:
        if not p.is_absolute():
            p = (Path(settings.base_image_path) / p).resolve()
        else:
            p = p.resolve()

        if not p.exists() or not p.is_file():
            raise FileNotFoundError(f"File not found: {p}")

        content_type = mimetypes.guess_type(p.name)[0] or "application/octet-stream"
        return p.read_bytes(), content_type
    except Exception as e:
        logger.error(f"Error reading file {p}: {e}")
        raise


def _get_image_base64_safe(path: str | None) -> str | None:
    if not path:
        return None
    try:
        content, _ = get_file_content(path)
        return encode_image_to_base64(content)
    except Exception:
        return None


def encode_image_to_base64(image_bytes: bytes) -> str:
    return base64.b64encode(image_bytes).decode("utf-8")
