import uuid
from datetime import date
from decimal import Decimal
from boto3.dynamodb.types import TypeDeserializer

_deserializer = TypeDeserializer()


def generate_id(prefix: str) -> str:
    return f"{prefix}-{uuid.uuid4().hex[:8]}"


def today() -> str:
    return date.today().isoformat()


def build_user_pk(user_id: str) -> str:
    return f"USER#{user_id}"


def build_order_sk(fecha: str, order_id: str) -> str:
    return f"ORDER#{fecha}#{order_id}"


def build_status_sk(estado: str, fecha: str, order_id: str) -> str:
    return f"STATUS#{estado}#{fecha}#{order_id}"


def build_order_pk(order_id: str) -> str:
    return f"ORDER#{order_id}"


def build_item_sk(product_id: str) -> str:
    return f"ITEM#{product_id}"


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
