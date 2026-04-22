from django.urls import path, include
from drf_spectacular.views import SpectacularAPIView, SpectacularSwaggerView
from core.views import HealthView, PlaygroundView

urlpatterns = [
    path('', PlaygroundView.as_view(), name='playground'),
    path('health/', HealthView.as_view(), name='health'),
    path('api/schema/', SpectacularAPIView.as_view(), name='schema'),
    path('api/docs/', SpectacularSwaggerView.as_view(url_name='schema'), name='swagger-ui'),
    path('', include('usuarios.urls')),
    path('', include('pedidos.urls')),
    path('', include('items.urls')),
]
