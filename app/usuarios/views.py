from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from usuarios.serializers import UsuarioSerializer
from usuarios import services


class UsuarioListCreateView(APIView):
    def post(self, request):
        serializer = UsuarioSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        result = services.crear_perfil(serializer.validated_data)
        return Response(result, status=status.HTTP_201_CREATED)


class UsuarioDetailView(APIView):
    def get(self, request, user_id):
        perfil, cache_hit = services.obtener_perfil(user_id)
        if not perfil:
            return Response(
                {'error': 'Usuario no encontrado'},
                status=status.HTTP_404_NOT_FOUND,
            )
        response = Response(perfil)
        response['X-Cache'] = 'HIT' if cache_hit else 'MISS'
        return response
