from django.urls import path
from usuarios.views import UsuarioListCreateView, UsuarioDetailView

urlpatterns = [
    path('usuarios/', UsuarioListCreateView.as_view(), name='usuario-list-create'),
    path('usuarios/<str:user_id>/', UsuarioDetailView.as_view(), name='usuario-detail'),
]
