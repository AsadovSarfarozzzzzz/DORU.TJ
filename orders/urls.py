from django.urls import path
from . import views

urlpatterns = [
    path('cart/', views.cart_view, name='cart'),
    path('cart/add/<int:pk>/', views.add_to_cart, name='add_to_cart'),
    path('cart/remove/<int:pk>/', views.remove_from_cart, name='remove_from_cart'),
    path('cart/update/<int:pk>/', views.update_cart, name='update_cart'),
    path('checkout/', views.checkout, name='checkout'),
    path('my-orders/', views.my_orders, name='my_orders'),
    path('order/<int:pk>/', views.order_detail, name='order_detail'),
    path('order/<int:pk>/cancel/', views.cancel_order, name='cancel_order'),
    path('order/<int:pk>/repeat/', views.repeat_order, name='repeat_order'),
]