import os
import boto3
from dotenv import load_dotenv

load_dotenv()


def create_table():
    client = boto3.client(
        'dynamodb',
        endpoint_url=os.getenv('DYNAMODB_ENDPOINT_URL', 'http://localhost:8000'),
        aws_access_key_id=os.getenv('AWS_ACCESS_KEY_ID', 'fakeMyKeyId'),
        aws_secret_access_key=os.getenv('AWS_SECRET_ACCESS_KEY', 'fakeSecretAccessKey'),
        region_name=os.getenv('AWS_DEFAULT_REGION', 'us-east-1'),
    )

    table_name = os.getenv('DYNAMODB_TABLE_NAME', 'mi_mercado')

    try:
        client.create_table(
            TableName=table_name,
            KeySchema=[
                {'AttributeName': 'pk', 'KeyType': 'HASH'},
                {'AttributeName': 'sk', 'KeyType': 'RANGE'},
            ],
            AttributeDefinitions=[
                {'AttributeName': 'pk', 'AttributeType': 'S'},
                {'AttributeName': 'sk', 'AttributeType': 'S'},
            ],
            BillingMode='PAY_PER_REQUEST',
        )
        print(f'[OK] Tabla "{table_name}" creada exitosamente.')
    except client.exceptions.ResourceInUseException:
        print(f'[SKIP] La tabla "{table_name}" ya existe.')


if __name__ == '__main__':
    create_table()
