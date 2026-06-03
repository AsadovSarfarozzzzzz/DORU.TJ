from django.urls import path
from . import views

urlpatterns = [
    path('', views.PharmacyListView.as_view(), name='pharmacy_list'),
    path('<int:pk>/', views.PharmacyDetailView.as_view(), name='pharmacy_detail'),
    path('product/<int:pk>/', views.ProductPharmaciesView.as_view(), name='product_pharmacies'),
    path('<int:pk>/chat/', views.pharmacy_chat, name='pharmacy_chat'),
    path('<int:pk>/chat/api/', views.pharmacy_chat_api, name='pharmacy_chat_api'),
    path('manager/<int:pk>/', views.manager_panel, name='manager_panel'),
    path('manager/chat/<int:chat_pk>/', views.manager_chat, name='manager_chat'),
]