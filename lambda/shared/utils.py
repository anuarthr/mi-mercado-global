import uuid
import json
from decimal import Decimal
from datetime import date
from boto3.dynamodb.types import TypeDeserializer

_deserializer = TypeDeserializer()


def generate_id(prefix: str) -> str:
    return f'{prefix}-{uuid.uuid4().hex[:8]}'


def today() -> str:
    return date.today().isoformat()


def deserialize_item(raw: dict) -> dict:
    return {k: _deserializer.deserialize(v) for k, v in raw.items()}


def sanitize(obj):
    if isinstance(obj, list):
        return [sanitize(i) for i in obj]
    if isinstance(obj, dict):
        return {k: sanitize(v) for k, v in obj.items()}
    if isinstance(obj, Decimal):
        return float(obj)
    return obj


CORS_HEADERS = {
    'Access-Control-Allow-Origin': '*',
    'Access-Control-Allow-Methods': 'GET,POST,PUT,DELETE,OPTIONS',
    'Access-Control-Allow-Headers': 'Content-Type,Authorization,X-Cache',
    'Access-Control-Expose-Headers': 'X-Cache',
}


def ok(body, status=200, headers=None):
    h = {'Content-Type': 'application/json', 'X-Cache': 'MISS', **CORS_HEADERS}
    if headers:
        h.update(headers)
    return {'statusCode': status, 'headers': h, 'body': json.dumps(body)}


def err(message, status=400):
    return {
        'statusCode': status,
        'headers': {'Content-Type': 'application/json', **CORS_HEADERS},
        'body': json.dumps({'error': message}),
    }


def cors_preflight():
    """Respuesta para requests OPTIONS (preflight CORS)."""
    return {'statusCode': 200, 'headers': CORS_HEADERS, 'body': ''}
