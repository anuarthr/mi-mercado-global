from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from items.serializers import ItemCreateSerializer
from items import services


class ItemListCreateView(APIView):
    def post(self, request, pedido_id):
        serializer = ItemCreateSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        result = services.agregar_item(pedido_id, serializer.validated_data)
        return Response(result, status=status.HTTP_201_CREATED)

    def get(self, request, pedido_id):
        items, cache_hit = services.listar_items(pedido_id)
        response = Response(items)
        response['X-Cache'] = 'HIT' if cache_hit else 'MISS'
        return response
