import os
import boto3
import redis
from dotenv import load_dotenv

load_dotenv()

dynamodb = boto3.client(
    'dynamodb',
    endpoint_url=os.getenv('DYNAMODB_ENDPOINT_URL', 'http://localhost:8000'),
    aws_access_key_id=os.getenv('AWS_ACCESS_KEY_ID', 'fakeMyKeyId'),
    aws_secret_access_key=os.getenv('AWS_SECRET_ACCESS_KEY', 'fakeSecretAccessKey'),
    region_name=os.getenv('AWS_DEFAULT_REGION', 'us-east-1'),
)

redis_client = redis.from_url(os.getenv('REDIS_URL', 'redis://localhost:6379/0'))

TABLE_NAME = os.getenv('DYNAMODB_TABLE_NAME', 'mi_mercado')
