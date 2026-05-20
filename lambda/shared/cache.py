import json
from shared.db import redis_client

DEFAULT_TTL = 300


def cache_get(key: str):
    data = redis_client.get(key)
    return json.loads(data) if data else None


def cache_set(key: str, value, ttl: int = DEFAULT_TTL):
    redis_client.setex(key, ttl, json.dumps(value))


def cache_delete(key: str):
    redis_client.delete(key)
