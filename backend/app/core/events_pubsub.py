import json
import logging
import redis
from backend.app.core.config import settings

logger = logging.getLogger("EventsPubSub")

try:
    redis_client = redis.from_url(settings.REDIS_URL, decode_responses=True)
except Exception as e:
    logger.error(f"Failed to connect to Redis for pub/sub: {e}")
    redis_client = None

def publish_event(event_type: str, data: dict):
    if not redis_client:
        return
    try:
        payload = json.dumps({
            "type": event_type,
            "data": data
        }, default=str)
        redis_client.publish("ibvap_events", payload)
    except Exception as e:
        logger.error(f"Failed to publish event to Redis: {e}")
