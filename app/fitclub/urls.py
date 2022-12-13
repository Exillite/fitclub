from django.urls import path
 
from .views import *
 
urlpatterns = [
    path('', index, name='index'),
    path('ini/', ini),
    path('login/', login_request, name='login'),
    path('register/', register_request, name='register'),
    path('users/', admin_users, name='users'),
    path('user/<int:id>', user_info, name='user'),
    path('user/<int:id>/<int:month>/<int:year>/', user_info_zp, name='userzp'),
    path('groups/', admin_groups, name='groups'),
    path('addgroup/', add_group, name='addgroup'),
    path('group/<int:id>', group_info, name="group"),
    path('clients/', admin_clients, name='clients'),
    path('client/<int:id>', client_info, name='client'),
    path('newtime/<int:group_id>', add_new_time, name='newtime'),
    path('edittime/<int:time_id>', edit_time, name='edittime'),
    path('newtrening/<int:group_id>', new_trening, name='newtrining'),
    path('trenings/', admin_trenings, name='trenings'),
    path('trening/<int:id>', info_trenings, name='trening'),
    path('weekplan/', week_plan, name='weekplan'),
    path('calendar/<str:date>/<str:view>', calendar, name='calendar'),
    path('newper/<int:id>', new_per, name='newper'),
    path('newpay/<str:type>/<int:client_id>', new_pay, name='newpay'),
    path('selary/', selary, name='selary'),
    path('newselary/<int:id>', new_selary, name='newselary'),
    path('selary/<int:month>/<int:year>/', prselary, name='prselary'),
    path('dohod/', dohod, name='dohod'),
    path('dohod/<str:type>/<str:date>/', prdohod, name='prdohod'),
    path('newspend/', new_spend, name='newspend'),
    path('editspend/<int:id>', edit_spend, name='editspend'),
]
