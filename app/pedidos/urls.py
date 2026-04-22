from django.urls import path
from pedidos.views import PedidoCreateView, PedidoListView, PedidoDetailView, PedidoByIdView

urlpatterns = [
    path('pedidos/', PedidoCreateView.as_view(), name='pedido-create'),
    path('pedidos/<str:pedido_id>/', PedidoByIdView.as_view(), name='pedido-by-id'),
    path('usuarios/<str:user_id>/pedidos/', PedidoListView.as_view(), name='pedido-list'),
    path('usuarios/<str:user_id>/pedidos/<str:fecha>/<str:pedido_id>/', PedidoDetailView.as_view(), name='pedido-detail'),
]
