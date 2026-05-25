from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from pedidos.serializers import PedidoCreateSerializer
from pedidos import services


class PedidoByIdView(APIView):
    def get(self, request, pedido_id):
        pedido, cache_hit = services.obtener_pedido_por_id(pedido_id)
        if not pedido:
            return Response(
                {'error': 'Pedido no encontrado'},
                status=status.HTTP_404_NOT_FOUND,
            )

        response = Response(pedido)
        response['X-Cache'] = 'HIT' if cache_hit else 'MISS'
        return response


class PedidoCreateView(APIView):
    def post(self, request):
        serializer = PedidoCreateSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        result = services.crear_pedido(serializer.validated_data)
        return Response(result, status=status.HTTP_201_CREATED)


class PedidoListView(APIView):
    def get(self, request, user_id):
        estado = request.query_params.get('estado')
        desde = request.query_params.get('desde')
        hasta = request.query_params.get('hasta')

        cache_hit = False

        if estado:
            pedidos = services.listar_pedidos_por_estado(user_id, estado)
        elif desde and hasta:
            pedidos = services.listar_pedidos_por_rango(user_id, desde, hasta)
        else:
            pedidos, cache_hit = services.listar_pedidos(user_id)

        response = Response(pedidos)

        if not estado and not (desde and hasta):
            response['X-Cache'] = 'HIT' if cache_hit else 'MISS'

        return response


class PedidoDetailView(APIView):
    def get(self, request, user_id, fecha, pedido_id):
        pedido = services.obtener_pedido(user_id, fecha, pedido_id)
        if not pedido:
            return Response(
                {'error': 'Pedido no encontrado'},
                status=status.HTTP_404_NOT_FOUND,
            )
        return Response(pedido)