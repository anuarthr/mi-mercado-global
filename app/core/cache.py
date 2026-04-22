import json
from config import redis_client

DEFAULT_TTL = 300  # 5 minutos


def cache_get(key: str):
    data = redis_client.get(key)
    if data:
        return json.loads(data)
    return None


def cache_set(key: str, value: dict, ttl: int = DEFAULT_TTL):
    redis_client.setex(key, ttl, json.dumps(value))


def cache_delete(key: str):
    redis_client.delete(key)
