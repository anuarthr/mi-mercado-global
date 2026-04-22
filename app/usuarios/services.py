from usuarios import repository
from core.cache import cache_get, cache_set, cache_delete
from core.utils import deserialize_item, sanitize

CACHE_TTL = 300  # 5 minutos


def _cache_key(user_id: str) -> str:
    return f'perfil:{user_id}'


def crear_perfil(data: dict) -> dict:
    repository.put_perfil(
        user_id=data['userId'],
        nombre=data['nombre'],
        email=data['email'],
        direccion=data['direccion'],
    )
    cache_delete(_cache_key(data['userId']))
    return data


def obtener_perfil(user_id: str) -> tuple[dict | None, bool]:
    """Retorna (perfil, cache_hit). cache_hit=True si vino de Redis."""
    cached = cache_get(_cache_key(user_id))
    if cached is not None:
        return cached, True

    raw = repository.get_perfil(user_id)
    if not raw:
        return None, False

    item = sanitize(deserialize_item(raw))
    item['userId'] = user_id

    cache_set(_cache_key(user_id), item, CACHE_TTL)
    return item, False
