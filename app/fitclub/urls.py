from django.urls import path
 
from .views import *
 
urlpatterns = [
    path('', index, name='index'),
    path('ini/', ini),
    path('login/', login_request, name='login'),
    path('register/', register_request, name='register'),
    path('users/', admin_users, name='users'),
    path('user/<int:id>', user_info, name='user'),
    path('groups/', admin_groups, name='groups'),
]
