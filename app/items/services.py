from items import repository
from core.utils import deserialize_item, sanitize
from core.cache import cache_get, cache_set, cache_delete


def _cache_key(order_id: str) -> str:
    return f'items:{order_id}'


def agregar_item(order_id: str, data: dict) -> dict:
    repository.put_item(
        order_id=order_id,
        product_id=data['productId'],
        nombre_producto=data['nombre_producto'],
        cantidad=data['cantidad'],
        precio=str(data['precio']),
    )

    cache_delete(_cache_key(order_id))

    return {
        'orderId': order_id,
        'productId': data['productId'],
        'nombre_producto': data['nombre_producto'],
        'cantidad': data['cantidad'],
        'precio': float(data['precio']),
    }


def listar_items(order_id: str) -> tuple[list, bool]:
    """Retorna (items, cache_hit). cache_hit=True si vino de Redis."""
    cached = cache_get(_cache_key(order_id))
    if cached is not None:
        return cached, True

    raw_items = repository.query_items(order_id)
    result = []
    for raw in raw_items:
        item = sanitize(deserialize_item(raw))
        product_id = item['sk'].split('#', 1)[1]
        result.append({
            'orderId': order_id,
            'productId': product_id,
            'nombre_producto': item.get('nombre_producto', ''),
            'cantidad': item.get('cantidad', 0),
            'precio': item.get('precio', 0),
        })

    cache_set(_cache_key(order_id), result)
    return result, False
