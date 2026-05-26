import json
from shared.db import dynamodb, TABLE_NAME
from shared.utils import deserialize_item, sanitize, generate_id, today, ok, err, cors_preflight
from shared.cache import cache_get, cache_set, cache_delete


def lambda_handler(event, context):
    method   = event.get('httpMethod', '')
    params   = event.get('pathParameters') or {}
    resource = event.get('resource', '')
    qs       = event.get('queryStringParameters') or {}

    if method == 'OPTIONS':
        return cors_preflight()

    user_id   = params.get('userId')
    pedido_id = params.get('pedidoId')

    # POST /pedidos/
    if method == 'POST' and not pedido_id:
        return _crear_pedido(event)

    # GET /pedidos/{pedidoId}/
    if method == 'GET' and pedido_id and 'items' not in resource:
        return _obtener_pedido(pedido_id)

    # GET /usuarios/{userId}/pedidos/
    if method == 'GET' and user_id:
        return _listar_pedidos(user_id, qs)

    return err('Ruta no encontrada', 404)


# POST /pedidos/
def _crear_pedido(event):
    try:
        body = json.loads(event.get('body') or '{}')
    except json.JSONDecodeError:
        return err('Body JSON inválido')

    user_id = body.get('userId')
    total   = body.get('total')
    estado  = body.get('estado', 'pendiente')

    if not all([user_id, total is not None]):
        return err('userId y total son requeridos')

    order_id = generate_id('ord')
    fecha    = today()
    total_s  = str(total)

    # Ítem principal ORDER#
    dynamodb.put_item(
        TableName=TABLE_NAME,
        Item={
            'pk':     {'S': f'USER#{user_id}'},
            'sk':     {'S': f'ORDER#{fecha}#{order_id}'},
            'estado': {'S': estado},
            'total':  {'N': total_s},
        },
    )
    # Ítem STATUS# para filtrar por estado
    dynamodb.put_item(
        TableName=TABLE_NAME,
        Item={
            'pk':    {'S': f'USER#{user_id}'},
            'sk':    {'S': f'STATUS#{estado}#{fecha}#{order_id}'},
            'total': {'N': total_s},
        },
    )
    # Ítem META para lookup directo por orderId
    dynamodb.put_item(
        TableName=TABLE_NAME,
        Item={
            'pk':     {'S': f'ORDER#{order_id}'},
            'sk':     {'S': 'META'},
            'userId': {'S': user_id},
            'fecha':  {'S': fecha},
            'estado': {'S': estado},
            'total':  {'N': total_s},
        },
    )

    cache_delete(f'pedidos:{user_id}')

    result = {
        'orderId': order_id,
        'userId':  user_id,
        'fecha':   fecha,
        'estado':  estado,
        'total':   float(total),
    }
    return ok(result, status=201)


# GET /pedidos/{pedidoId}/
def _obtener_pedido(pedido_id):
    key = f'pedido:{pedido_id}'

    cached = cache_get(key)
    if cached is not None:
        return ok(cached, headers={'X-Cache': 'HIT'})

    response = dynamodb.get_item(
        TableName=TABLE_NAME,
        Key={
            'pk': {'S': f'ORDER#{pedido_id}'},
            'sk': {'S': 'META'},
        },
    )
    raw = response.get('Item')
    if not raw:
        return err('Pedido no encontrado', 404)

    item = sanitize(deserialize_item(raw))
    result = {
        'orderId': pedido_id,
        'userId':  item.get('userId', ''),
        'fecha':   item.get('fecha', ''),
        'estado':  item.get('estado', ''),
        'total':   item.get('total', 0),
    }
    cache_set(key, result)
    return ok(result, headers={'X-Cache': 'MISS'})


# GET /usuarios/{userId}/pedidos/
def _listar_pedidos(user_id, qs):
    estado = qs.get('estado')
    desde  = qs.get('desde')
    hasta  = qs.get('hasta')

    # Solo cacheamos el listado sin filtros (caso más frecuente: "Mis Pedidos").
    # Las consultas con filtros van directo a DynamoDB.
    use_cache = not (estado or desde or hasta)
    cache_key = f'pedidos:{user_id}'

    if use_cache:
        cached = cache_get(cache_key)
        if cached is not None:
            return ok(cached, headers={'X-Cache': 'HIT'})

    if estado:
        response = dynamodb.query(
            TableName=TABLE_NAME,
            KeyConditionExpression='pk = :pk AND begins_with(sk, :prefix)',
            ExpressionAttributeValues={
                ':pk':     {'S': f'USER#{user_id}'},
                ':prefix': {'S': f'STATUS#{estado}#'},
            },
        )
    elif desde and hasta:
        response = dynamodb.query(
            TableName=TABLE_NAME,
            KeyConditionExpression='pk = :pk AND sk BETWEEN :desde AND :hasta',
            ExpressionAttributeValues={
                ':pk':    {'S': f'USER#{user_id}'},
                ':desde': {'S': f'ORDER#{desde}'},
                ':hasta': {'S': f'ORDER#{hasta}~'},
            },
        )
    else:
        response = dynamodb.query(
            TableName=TABLE_NAME,
            KeyConditionExpression='pk = :pk AND begins_with(sk, :prefix)',
            ExpressionAttributeValues={
                ':pk':     {'S': f'USER#{user_id}'},
                ':prefix': {'S': 'ORDER#'},
            },
        )

    items = response.get('Items', [])
    result = []
    for raw in items:
        item = sanitize(deserialize_item(raw))
        sk   = item['sk']
        if sk.startswith('ORDER#'):
            _, fecha, order_id = sk.split('#', 2)
            est = item.get('estado', '')
        else:
            _, est, fecha, order_id = sk.split('#', 3)
        result.append({
            'orderId': order_id,
            'userId':  user_id,
            'fecha':   fecha,
            'estado':  est,
            'total':   item.get('total', 0),
        })

    if use_cache:
        cache_set(cache_key, result)
        return ok(result, headers={'X-Cache': 'MISS'})
    return ok(result)
