from rest_framework import serializers

ESTADOS_VALIDOS = ['pendiente', 'procesando', 'enviado', 'entregado', 'cancelado']


class PedidoCreateSerializer(serializers.Serializer):
    userId = serializers.CharField(max_length=50)
    estado = serializers.ChoiceField(choices=ESTADOS_VALIDOS)
    total = serializers.DecimalField(max_digits=10, decimal_places=2, min_value=0)


class PedidoSerializer(serializers.Serializer):
    orderId = serializers.CharField()
    userId = serializers.CharField()
    fecha = serializers.CharField()
    estado = serializers.CharField()
    total = serializers.FloatField()
