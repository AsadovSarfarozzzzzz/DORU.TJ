from django.urls import path
from . import views

urlpatterns = [
    path('', views.consultant, name='consultant'),
    path('clear/', views.clear_chat, name='clear_chat'),
    path('symptom-search/', views.symptom_search, name='symptom_search'),
]