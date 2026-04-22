from config import dynamodb, TABLE_NAME


def put_item(order_id: str, product_id: str, nombre_producto: str, cantidad: int, precio: str) -> None:
    dynamodb.put_item(
        TableName=TABLE_NAME,
        Item={
            'pk': {'S': f'ORDER#{order_id}'},
            'sk': {'S': f'ITEM#{product_id}'},
            'nombre_producto': {'S': nombre_producto},
            'cantidad': {'N': str(cantidad)},
            'precio': {'N': precio},
        },
    )


def query_items(order_id: str) -> list:
    response = dynamodb.query(
        TableName=TABLE_NAME,
        KeyConditionExpression='pk = :pk AND begins_with(sk, :prefix)',
        ExpressionAttributeValues={
            ':pk': {'S': f'ORDER#{order_id}'},
            ':prefix': {'S': 'ITEM#'},
        },
    )
    return response.get('Items', [])
