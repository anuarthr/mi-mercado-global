from config import dynamodb, TABLE_NAME


def put_perfil(user_id: str, nombre: str, email: str, direccion: str) -> None:
    dynamodb.put_item(
        TableName=TABLE_NAME,
        Item={
            'pk': {'S': f'USER#{user_id}'},
            'sk': {'S': 'PROFILE'},
            'nombre': {'S': nombre},
            'email': {'S': email},
            'direccion': {'S': direccion},
        },
    )


def get_perfil(user_id: str) -> dict | None:
    response = dynamodb.get_item(
        TableName=TABLE_NAME,
        Key={
            'pk': {'S': f'USER#{user_id}'},
            'sk': {'S': 'PROFILE'},
        },
    )
    return response.get('Item')
