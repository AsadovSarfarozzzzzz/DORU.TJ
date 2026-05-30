from django.urls import path
from . import views

urlpatterns = [
    path('register/', views.register, name='register'),
    path('confirm-email/', views.confirm_email, name='confirm'),
    path('login/', views.login_user, name='login_user'),
    path('logout/', views.logout_user, name='logout'),
    path('profile/', views.profile_view, name='profile'),
    path('forgot/', views.forgot_password, name='forgot_password'),
    path('reset/', views.reset_password, name='reset_password'),
]