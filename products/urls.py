from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('catalog/', views.catalog, name='catalog'),
    path('product/<int:pk>/', views.product_detail, name='product_detail'),
    path('admin-panel/products/', views.product_list, name='product_list'),
    path('admin-panel/products/add/', views.product_add, name='product_add'),
    path('admin-panel/products/edit/<int:pk>/', views.product_edit, name='product_edit'),
    path('admin-panel/products/delete/<int:pk>/', views.product_delete, name='product_delete'),
]