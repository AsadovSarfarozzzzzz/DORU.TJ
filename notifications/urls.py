from django.urls import path
from . import views

urlpatterns = [
    path('', views.notification_list, name='notifications'),
    path('read/<int:pk>/', views.mark_read, name='notification_read'),
    path('read-all/', views.mark_all_read, name='notifications_read_all'),
    path('count/', views.notification_count, name='notification_count'),
]
