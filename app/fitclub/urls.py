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
    path('addgroup/', add_group, name='addgroup'),
    path('group/<int:id>', group_info, name="group"),
    path('clients/', admin_clients, name='clients'),
    path('client/<int:id>', client_info, name='client'),
    path('newtime/<int:group_id>', add_new_time, name='newtime'),
    path('edittime/<int:time_id>', edit_time, name='edittime'),
    path('newtrening/<int:group_id>', new_trening, name='newtrining')
]
