import json
from shared.db import dynamodb, TABLE_NAME
from shared.utils import deserialize_item, sanitize, ok, err, cors_preflight
from shared.cache import cache_get, cache_set, cache_delete


def lambda_handler(event, context):
    method = event.get('httpMethod', '')
    params = event.get('pathParameters') or {}
    pedido_id = params.get('pedidoId')

    if method == 'OPTIONS':
        return cors_preflight()

    if not pedido_id:
        return err('pedidoId requerido', 400)

    if method == 'POST':
        return _agregar_item(pedido_id, event)
    if method == 'GET':
        return _listar_items(pedido_id)
    return err('Método no permitido', 405)


# POST /pedidos/{pedidoId}/items/
def _agregar_item(pedido_id, event):
    try:
        body = json.loads(event.get('body') or '{}')
    except json.JSONDecodeError:
        return err('Body JSON inválido')

    product_id       = body.get('productId')
    nombre_producto  = body.get('nombre_producto')
    cantidad         = body.get('cantidad')
    precio           = body.get('precio')

    if not all([product_id, nombre_producto, cantidad is not None, precio is not None]):
        return err('productId, nombre_producto, cantidad y precio son requeridos')

    dynamodb.put_item(
        TableName=TABLE_NAME,
        Item={
            'pk':              {'S': f'ORDER#{pedido_id}'},
            'sk':              {'S': f'ITEM#{product_id}'},
            'nombre_producto': {'S': nombre_producto},
            'cantidad':        {'N': str(cantidad)},
            'precio':          {'N': str(precio)},
        },
    )
    cache_delete(f'items:{pedido_id}')

    return ok({
        'orderId':         pedido_id,
        'productId':       product_id,
        'nombre_producto': nombre_producto,
        'cantidad':        cantidad,
        'precio':          float(precio),
    }, status=201)


# GET /pedidos/{pedidoId}/items/
def _listar_items(pedido_id):
    key = f'items:{pedido_id}'

    cached = cache_get(key)
    if cached is not None:
        return ok(cached, headers={'X-Cache': 'HIT'})

    response = dynamodb.query(
        TableName=TABLE_NAME,
        KeyConditionExpression='pk = :pk AND begins_with(sk, :prefix)',
        ExpressionAttributeValues={
            ':pk':     {'S': f'ORDER#{pedido_id}'},
            ':prefix': {'S': 'ITEM#'},
        },
    )
    result = []
    for raw in response.get('Items', []):
        item       = sanitize(deserialize_item(raw))
        product_id = item['sk'].split('#', 1)[1]
        result.append({
            'orderId':         pedido_id,
            'productId':       product_id,
            'nombre_producto': item.get('nombre_producto', ''),
            'cantidad':        item.get('cantidad', 0),
            'precio':          item.get('precio', 0),
        })

    cache_set(key, result)
    return ok(result, headers={'X-Cache': 'MISS'})
