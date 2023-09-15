from django.contrib import admin
from .models import *

class SportGroupAdmin(admin.ModelAdmin):
    list_display = ('name', 'user_view')
    list_filter = ('trener',)
    search_fields = ('name',)
    def user_view(self, obj):
        if obj.trener:
            return f"{obj.trener.first_name} {obj.trener.last_name}"
        else:
            return "Тренер не указан"

    user_view.short_description = "Тренер"

class TreningAdmin(admin.ModelAdmin):
    list_display = ('day', 'start', 'end', 'trening_type_view', 'clients_view', 'user_view', 'is_helper_view')
    search_fields = ('day',)
    list_filter = ('trening_type',)
    
    def user_view(self, obj):
        return f"{obj.trener.first_name} {obj.trener.last_name}"
    
    def trening_type_view(self, obj):
        if obj.trening_type == "group":
            return 'Групповое занятие'
        else:
            return 'Индивидуальное занятие'
    
    def clients_view(self, obj):
        if obj.trening_type == "group":
            return f"Группа: {obj.group.name}"
        else:
            client = obj.clients.first()
            return f"{client.name} {client.surname}"
    
    def is_helper_view(self, obj):
        if obj.helper:
            return True
        else:
            return False
    
    trening_type_view.short_description = "Тип"
    clients_view.short_description = "Участники"
    user_view.short_description = "Тренер"
    is_helper_view.short_description = "Есть ли помощник"
    is_helper_view.boolean = True


class ClientAdmin(admin.ModelAdmin):
    list_display = ('fio_view', 'phone', 'email')
    search_fields = ('name', 'surname', 'email', 'phone')
    def fio_view(self, obj):
        return f"{obj.name} {obj.surname}"
    
    fio_view.short_description = "Имя Фамилия"
  
class ParamAdmin(admin.ModelAdmin):
    list_display = ('title_view', 'value')
    
    def title_view(self, obj):
        if obj.title:
            return obj.title
        else:
            return obj.key


class PeymentAdmin(admin.ModelAdmin):
    list_display = ('fio_view', 'date', 'value', 'pay_type_view', 'way_view')
    
    def fio_view(self, obj):
        return f"{obj.client.name} {obj.client.surname}"
    
    def pay_type_view(self, obj):
        if obj.pay_type == "one":
            return "Индивидуальное занятие"
        elif obj.pay_type == "one_month":
            return "Абонемент на индивидуальное занятие"
        elif obj.pay_type == "group":
            return "Групповое занятие"
        elif obj.pay_type == "group_month":
            return "Абонемент на групповые занятия"
        
    def way_view(self, obj):
        if obj.way == "card":
            return "Безналичная оплата"
        else:
            return "Наличная оплата"
    
    fio_view.short_description = "Ученик"
    pay_type_view.short_description = "Тип оплаты"
    way_view.short_description = "Способ оплаты"


class SpendingAdmin(admin.ModelAdmin):
    list_display = ('date', 'key', 'value')
    list_display_links = ('date', 'key')
    search_fields = ('key', 'value')


class SalaryAdmin(admin.ModelAdmin):
    list_display = ('user_view', 'date', 'give')
    
    def user_view(self, obj):
        return f"{obj.user.first_name} {obj.user.last_name}"

    user_view.short_description = "Сотрудник"


class IncomeAdmin(admin.ModelAdmin):
    list_display = ('date', 'key', 'value')
    list_display_links = ('date', 'key')
    search_fields = ('key', 'value')

    
class ZalAdmin(admin.ModelAdmin):
    list_display = ('title',)


admin.site.site_title = 'Админ-панель'
admin.site.site_header = 'Админ-панель'

admin.site.register(SportGroup, SportGroupAdmin)
# admin.site.register(GroupTime)
admin.site.register(Trening, TreningAdmin)
admin.site.register(Client, ClientAdmin)
admin.site.register(Param, ParamAdmin)
admin.site.register(Peyment, PeymentAdmin)
admin.site.register(Spending, SpendingAdmin)
admin.site.register(Salary, SalaryAdmin)
admin.site.register(Income, IncomeAdmin)
admin.site.register(SingleTren)
admin.site.register(Subscription)
admin.site.register(Massage)
admin.site.register(MassageTypes)
admin.site.register(Zal, ZalAdmin)
