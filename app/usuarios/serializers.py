from rest_framework import serializers


class UsuarioSerializer(serializers.Serializer):
    userId = serializers.CharField(max_length=50)
    nombre = serializers.CharField(max_length=100)
    email = serializers.EmailField()
    direccion = serializers.CharField(max_length=200)
