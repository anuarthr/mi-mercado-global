from pedidos import repository
from core.utils import generate_id, today, deserialize_item, sanitize
from core.cache import cache_get, cache_set, cache_delete
from core.pubsub import publish, CHANNEL_PEDIDO_CREADO


def crear_pedido(data: dict) -> dict:
    order_id = generate_id('ord')
    fecha = today()

    repository.put_pedido(
        user_id=data['userId'],
        order_id=order_id,
        fecha=fecha,
        estado=data['estado'],
        total=str(data['total']),
    )

    result = {
        'orderId': order_id,
        'userId': data['userId'],
        'fecha': fecha,
        'estado': data['estado'],
        'total': float(data['total']),
    }

    cache_delete(f"pedidos:{data['userId']}")

    publish(CHANNEL_PEDIDO_CREADO, result)
    return result


def _parse_pedido(raw: dict, user_id: str) -> dict:
    item = sanitize(deserialize_item(raw))
    sk = item['sk']

    if sk.startswith('ORDER#'):
        _, fecha, order_id = sk.split('#', 2)
        estado = item.get('estado', '')
    else:
        _, estado, fecha, order_id = sk.split('#', 3)

    return {
        'orderId': order_id,
        'userId': user_id,
        'fecha': fecha,
        'estado': estado,
        'total': item.get('total', 0),
    }


def listar_pedidos(user_id: str) -> tuple[list, bool]:
    """
    AP2: listar pedidos de un usuario.

    Implementa cache-aside con Redis:
    - Clave: pedidos:{userId}
    - Si existe en caché, retorna HIT.
    - Si no existe, consulta DynamoDB, guarda en caché y retorna MISS.
    """
    key = f'pedidos:{user_id}'

    cached = cache_get(key)
    if cached is not None:
        return cached, True

    items = repository.query_pedidos(user_id)
    pedidos = [_parse_pedido(item, user_id) for item in items]

    cache_set(key, pedidos)
    return pedidos, False


def obtener_pedido(user_id: str, fecha: str, order_id: str) -> dict | None:
    raw = repository.get_pedido(user_id, fecha, order_id)
    if not raw:
        return None
    return _parse_pedido(raw, user_id)


def obtener_pedido_por_id(order_id: str) -> tuple[dict | None, bool]:
    """Retorna (pedido, cache_hit). Usa cache-aside con clave pedido:{orderId}."""
    key = f'pedido:{order_id}'
    cached = cache_get(key)
    if cached is not None:
        return cached, True

    raw = repository.get_pedido_by_id(order_id)
    if not raw:
        return None, False

    item = sanitize(deserialize_item(raw))
    result = {
        'orderId': order_id,
        'userId': item.get('userId', ''),
        'fecha': item.get('fecha', ''),
        'estado': item.get('estado', ''),
        'total': item.get('total', 0),
    }

    cache_set(key, result)
    return result, False


def listar_pedidos_por_estado(user_id: str, estado: str) -> list:
    items = repository.query_pedidos_por_estado(user_id, estado)
    return [_parse_pedido(item, user_id) for item in items]


def listar_pedidos_por_rango(user_id: str, desde: str, hasta: str) -> list:
    items = repository.query_pedidos_por_rango(user_id, desde, hasta)
    return [_parse_pedido(item, user_id) for item in items]