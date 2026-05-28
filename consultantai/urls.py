from django.urls import path
from . import views

urlpatterns = [
    path('', views.consultant, name='consultantai'),
    path('clear/', views.clear_chat, name='clear_chat'),
]