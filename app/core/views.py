from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from config import dynamodb, redis_client, TABLE_NAME


class HealthView(APIView):
    def get(self, request):
        result = {}

        try:
            dynamodb.describe_table(TableName=TABLE_NAME)
            result['dynamodb'] = 'ok'
        except Exception as e:
            result['dynamodb'] = f'error: {e}'

        try:
            redis_client.ping()
            result['redis'] = 'ok'
        except Exception as e:
            result['redis'] = f'error: {e}'

        http_status = (
            status.HTTP_200_OK
            if all(v == 'ok' for v in result.values())
            else status.HTTP_503_SERVICE_UNAVAILABLE
        )

        return Response(result, status=http_status)
