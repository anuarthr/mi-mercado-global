from config import dynamodb, TABLE_NAME


def put_pedido(user_id: str, order_id: str, fecha: str, estado: str, total: str) -> None:
    # AP2 / AP3 / AP6 — ítem principal del pedido
    dynamodb.put_item(
        TableName=TABLE_NAME,
        Item={
            'pk': {'S': f'USER#{user_id}'},
            'sk': {'S': f'ORDER#{fecha}#{order_id}'},
            'estado': {'S': estado},
            'total': {'N': total},
        },
    )
    # AP5 — ítem duplicado indexado por estado
    dynamodb.put_item(
        TableName=TABLE_NAME,
        Item={
            'pk': {'S': f'USER#{user_id}'},
            'sk': {'S': f'STATUS#{estado}#{fecha}#{order_id}'},
            'total': {'N': total},
        },
    )
    # Lookup por orderId — permite GET /pedidos/{orderId}/ sin GSI
    dynamodb.put_item(
        TableName=TABLE_NAME,
        Item={
            'pk': {'S': f'ORDER#{order_id}'},
            'sk': {'S': 'META'},
            'userId': {'S': user_id},
            'fecha': {'S': fecha},
            'estado': {'S': estado},
            'total': {'N': total},
        },
    )


def get_pedido_by_id(order_id: str) -> dict | None:
    response = dynamodb.get_item(
        TableName=TABLE_NAME,
        Key={
            'pk': {'S': f'ORDER#{order_id}'},
            'sk': {'S': 'META'},
        },
    )
    return response.get('Item')


def get_pedido(user_id: str, fecha: str, order_id: str) -> dict | None:
    response = dynamodb.get_item(
        TableName=TABLE_NAME,
        Key={
            'pk': {'S': f'USER#{user_id}'},
            'sk': {'S': f'ORDER#{fecha}#{order_id}'},
        },
    )
    return response.get('Item')


def query_pedidos(user_id: str) -> list:
    response = dynamodb.query(
        TableName=TABLE_NAME,
        KeyConditionExpression='pk = :pk AND begins_with(sk, :prefix)',
        ExpressionAttributeValues={
            ':pk': {'S': f'USER#{user_id}'},
            ':prefix': {'S': 'ORDER#'},
        },
    )
    return response.get('Items', [])


def query_pedidos_por_estado(user_id: str, estado: str) -> list:
    response = dynamodb.query(
        TableName=TABLE_NAME,
        KeyConditionExpression='pk = :pk AND begins_with(sk, :prefix)',
        ExpressionAttributeValues={
            ':pk': {'S': f'USER#{user_id}'},
            ':prefix': {'S': f'STATUS#{estado}#'},
        },
    )
    return response.get('Items', [])


def query_pedidos_por_rango(user_id: str, desde: str, hasta: str) -> list:
    response = dynamodb.query(
        TableName=TABLE_NAME,
        KeyConditionExpression='pk = :pk AND sk BETWEEN :desde AND :hasta',
        ExpressionAttributeValues={
            ':pk': {'S': f'USER#{user_id}'},
            ':desde': {'S': f'ORDER#{desde}'},
            ':hasta': {'S': f'ORDER#{hasta}~'},  # ~ (ASCII 126) mayor que cualquier char del orderId
        },
    )
    return response.get('Items', [])
