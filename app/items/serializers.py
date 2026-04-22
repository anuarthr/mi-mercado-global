from rest_framework import serializers


class ItemCreateSerializer(serializers.Serializer):
    productId = serializers.CharField(max_length=50)
    nombre_producto = serializers.CharField(max_length=200)
    cantidad = serializers.IntegerField(min_value=1)
    precio = serializers.DecimalField(max_digits=10, decimal_places=2, min_value=0)


class ItemSerializer(serializers.Serializer):
    orderId = serializers.CharField()
    productId = serializers.CharField()
    nombre_producto = serializers.CharField()
    cantidad = serializers.IntegerField()
    precio = serializers.FloatField()
