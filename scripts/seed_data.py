import os
import boto3
from dotenv import load_dotenv

load_dotenv()


def seed():
    client = boto3.client(
        'dynamodb',
        endpoint_url=os.getenv('DYNAMODB_ENDPOINT_URL', 'http://localhost:8000'),
        aws_access_key_id=os.getenv('AWS_ACCESS_KEY_ID', 'fakeMyKeyId'),
        aws_secret_access_key=os.getenv('AWS_SECRET_ACCESS_KEY', 'fakeSecretAccessKey'),
        region_name=os.getenv('AWS_DEFAULT_REGION', 'us-east-1'),
    )

    table_name = os.getenv('DYNAMODB_TABLE_NAME', 'mi_mercado')

    items = [
        # ── Perfil de usuario ────────────────────────────────────────────────
        {
            'pk': {'S': 'USER#usr-001'},
            'sk': {'S': 'PROFILE'},
            'nombre': {'S': 'Juan Narváez'},
            'email': {'S': 'juan@mail.com'},
            'direccion': {'S': 'Calle 123 #45-67, Bogotá'},
        },
        # ── Pedido (ORDER#) ──────────────────────────────────────────────────
        {
            'pk': {'S': 'USER#usr-001'},
            'sk': {'S': 'ORDER#2026-04-07#ord-7f3a1b'},
            'estado': {'S': 'pendiente'},
            'total': {'N': '149.99'},
        },
        # ── Pedido indexado por estado (STATUS#) ─────────────────────────────
        {
            'pk': {'S': 'USER#usr-001'},
            'sk': {'S': 'STATUS#pendiente#2026-04-07#ord-7f3a1b'},
            'total': {'N': '149.99'},
        },
        # ── Lookup del pedido por orderId ────────────────────────────────────
        {
            'pk': {'S': 'ORDER#ord-7f3a1b'},
            'sk': {'S': 'META'},
            'userId': {'S': 'usr-001'},
            'fecha': {'S': '2026-04-07'},
            'estado': {'S': 'pendiente'},
            'total': {'N': '149.99'},
        },
        # ── Ítems del pedido ─────────────────────────────────────────────────
        {
            'pk': {'S': 'ORDER#ord-7f3a1b'},
            'sk': {'S': 'ITEM#prod-001'},
            'nombre_producto': {'S': 'Audífonos Bluetooth'},
            'cantidad': {'N': '2'},
            'precio': {'N': '59.99'},
        },
        {
            'pk': {'S': 'ORDER#ord-7f3a1b'},
            'sk': {'S': 'ITEM#prod-002'},
            'nombre_producto': {'S': 'Cable USB-C'},
            'cantidad': {'N': '1'},
            'precio': {'N': '12.99'},
        },
    ]

    for item in items:
        client.put_item(TableName=table_name, Item=item)

    print(f'[OK] {len(items)} ítems insertados en "{table_name}".')


if __name__ == '__main__':
    seed()
