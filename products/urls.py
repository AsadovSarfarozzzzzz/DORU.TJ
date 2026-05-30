from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('catalog/', views.catalog, name='catalog'),
    path('product/<int:pk>/', views.product_detail, name='product_detail'),
    path('product_list/', views.product_list, name='product_list'),
    path('product_delete/', views.product_delete, name='product_delete'),
    path('product_update/', views.update_product, name='product_update'),
    path('product_add', views.product_add, name='product_add'),
]