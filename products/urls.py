from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('catalog/', views.catalog, name='catalog'),
    path('product/<int:pk>/', views.product_detail, name='product_detail'),
    path('admin-panel/products/', views.ProductView.as_view(), name='product_list'),
    path('admin-panel/products/add/', views.ProductAdd.as_view(), name='product_add'),
    path('admin-panel/products/edit/<int:pk>/', views.ProductUpdateView.as_view(), name='product_edit'),
    path('admin-panel/products/delete/<int:pk>/', views.ProductDeleteView.as_view(), name='product_delete'),
    path('product/<int:pk>/review/', views.add_review, name='add_review'),
    path('favorites/', views.favorites_list, name='favorites'),
    path('favorite/toggle/<int:pk>/', views.toggle_favorite, name='toggle_favorite'),
    path('admin-panel/analytics/', views.analytics, name='analytics'),
]