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

    # Чат клиента
    path('chat/<int:order_pk>/', views.delivery_chat, name='delivery_chat'),
    path('chat/<int:order_pk>/api/', views.chat_messages_api, name='chat_messages_api'),
    path('chat/<int:order_pk>/location/', views.courier_location_api, name='courier_location_api'),
    path('chat/<int:order_pk>/update-location/', views.update_courier_location, name='update_courier_location'),

    # Панель курьера — по токену
    path('courier/<str:token>/', views.courier_panel, name='courier_panel'),
    path('courier/<str:token>/status/', views.courier_update_status, name='courier_update_status'),
    path('courier/<str:token>/send/', views.courier_chat_send, name='courier_chat_send'),
    path('courier/<str:token>/api/', views.courier_api_messages, name='courier_api_messages'),
    path('courier/<str:token>/location/', views.update_courier_location_by_token, name='update_location_by_token'),
]