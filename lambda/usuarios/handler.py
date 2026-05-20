import json
from shared.db import dynamodb, TABLE_NAME
from shared.utils import deserialize_item, sanitize, ok, err, cors_preflight
from shared.cache import cache_get, cache_set, cache_delete

CACHE_TTL = 300


def lambda_handler(event, context):
    method = event.get('httpMethod', '')
    params = event.get('pathParameters') or {}
    user_id = params.get('userId')

    if method == 'OPTIONS':
        return cors_preflight()

    if method == 'POST':
        return _crear_usuario(event)
    if method == 'GET' and user_id:
        return _obtener_usuario(user_id)
    return err('Ruta no encontrada', 404)


# POST /usuarios/
def _crear_usuario(event):
    try:
        body = json.loads(event.get('body') or '{}')
    except json.JSONDecodeError:
        return err('Body JSON inválido')

    user_id  = body.get('userId')
    nombre   = body.get('nombre')
    email    = body.get('email')

    if not all([user_id, nombre, email]):
        return err('userId, nombre y email son requeridos')

    dynamodb.put_item(
        TableName=TABLE_NAME,
        Item={
            'pk':        {'S': f'USER#{user_id}'},
            'sk':        {'S': 'PROFILE'},
            'nombre':    {'S': nombre},
            'email':     {'S': email},
            'direccion': {'S': body.get('direccion', '')},
        },
    )
    cache_delete(f'perfil:{user_id}')
    return ok(body, status=201)


# GET /usuarios/{userId}/
def _obtener_usuario(user_id):
    key = f'perfil:{user_id}'

    cached = cache_get(key)
    if cached is not None:
        return ok(cached, headers={'X-Cache': 'HIT'})

    response = dynamodb.get_item(
        TableName=TABLE_NAME,
        Key={
            'pk': {'S': f'USER#{user_id}'},
            'sk': {'S': 'PROFILE'},
        },
    )
    raw = response.get('Item')
    if not raw:
        return err('Usuario no encontrado', 404)

    item = sanitize(deserialize_item(raw))
    item['userId'] = user_id
    cache_set(key, item, CACHE_TTL)
    return ok(item, headers={'X-Cache': 'MISS'})
