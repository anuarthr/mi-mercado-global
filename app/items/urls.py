from django.urls import path
from items.views import ItemListCreateView

urlpatterns = [
    path('pedidos/<str:pedido_id>/items/', ItemListCreateView.as_view(), name='item-list-create'),
]
