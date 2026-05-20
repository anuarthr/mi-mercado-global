import os
import boto3
import redis as redis_lib

dynamodb = boto3.client(
    'dynamodb',
    endpoint_url=os.environ.get('DYNAMODB_ENDPOINT_URL', 'http://localstack:4566'),
    aws_access_key_id=os.environ.get('AWS_ACCESS_KEY_ID', 'fakeMyKeyId'),
    aws_secret_access_key=os.environ.get('AWS_SECRET_ACCESS_KEY', 'fakeSecretAccessKey'),
    region_name=os.environ.get('AWS_DEFAULT_REGION', 'us-east-1'),
)

TABLE_NAME = os.environ.get('DYNAMODB_TABLE_NAME', 'mi_mercado')

redis_client = redis_lib.from_url(
    os.environ.get('REDIS_URL', 'redis://localhost:6379/0')
)
