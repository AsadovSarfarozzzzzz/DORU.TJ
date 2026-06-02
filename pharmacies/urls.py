from django.urls import path
from . import views

urlpatterns = [
    path('', views.PharmacyListView.as_view(), name='pharmacy_list'),
    path('<int:pk>/', views.PharmacyDetailView.as_view(), name='pharmacy_detail'),
    path('product/<int:pk>/', views.ProductPharmaciesView.as_view(), name='product_pharmacies'),
]