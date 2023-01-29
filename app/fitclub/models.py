from django.db import models
from django.conf import settings


class SportGroup(models.Model):
    name = models.CharField(max_length=255, verbose_name="Название")
    trener = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        null=True,
        verbose_name="Тренер"
    )
    
    class Meta:
        verbose_name = 'Группа'
        verbose_name_plural = 'Группы'


    def __str__(self):
        return self.name


class GroupTime(models.Model):
    start = models.TimeField(verbose_name="Начало")
    end = models.TimeField(verbose_name="Конец")
    day = models.IntegerField(verbose_name="День недели") # 1 - 7

    group = models.ForeignKey('SportGroup', on_delete=models.PROTECT, null=True, verbose_name="Группа")
        
    class Meta:
        verbose_name = 'Время занятий'
        verbose_name_plural = 'Время занятий'

    def __str__(self):
        return f"{self.group.name}: {self.start} - {self.end}"



class Client(models.Model):
    name = models.CharField(max_length=255, verbose_name="Имя")
    surname = models.CharField(max_length=255, verbose_name="Фамилия")
    phone = models.CharField(max_length=255, null=True, blank=True, verbose_name="Телефон")
    email = models.CharField(max_length=255, null=True, blank=True, verbose_name="e-mail")
    tg = models.CharField(max_length=255, null=True, blank=True, verbose_name="Telegram")
    groups = models.ManyToManyField(SportGroup, verbose_name="Группы")
    
    class Meta:
        verbose_name = 'Ученик'
        verbose_name_plural = 'Ученики'
    
    def __str__(self):
        return f"{self.name} {self.surname}"


class Trening(models.Model):
    start = models.TimeField(verbose_name="Начало")
    end = models.TimeField(verbose_name="Конец")
    day = models.DateField(verbose_name="Дата")
    group = models.ForeignKey('SportGroup', on_delete=models.PROTECT, null=True, blank=True, verbose_name="Группа")
    trening_type = models.CharField(max_length=50, verbose_name="Тип занятия") # "personal" / "group" / "massage_{type id}"
    col = models.IntegerField(verbose_name="Кол. участников") # количество участников
    is_was = models.BooleanField(verbose_name="Было ли занятие") # Была ло занятие
    progul = models.BooleanField(verbose_name="Прогул") # Был ли прогул
    clients = models.ManyToManyField(Client, blank=True, verbose_name="Участники")
    trener = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name='royal_trainer',
        verbose_name="Тренер"
    )
    helper = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name='helper_for_training',
        verbose_name="Помощник"
    )

    students_data = models.JSONField(null=True, blank=True, verbose_name="Данные посещаемости") # data[key] = value | key - client id; value - status | example: {"1": 0, "2": 2}
    # payed_students = models.ManyToManyField(Client, blank=True, related_name='payed_students', verbose_name="Заплатившие участники")

    class Meta:
        verbose_name = 'Занитие'
        verbose_name_plural = 'Занятия'
    
    def __str__(self):
        return f"Зантие {self.day}: {self.start.hour}:{self.start.minute}"


class Param(models.Model):
    key = models.CharField(max_length=150, verbose_name="Ключ")
    value = models.FloatField(null=True, blank=True, verbose_name="Значение")
    title = models.CharField(max_length=255, blank=True, verbose_name="Описание")


    """
    
        prise_one
        price_group
        price_one_month
        price_group_month

        sum_from_group
        sum_from_one
        sum_from_asist
        sum_from_late
        sum_from_single   -- когда из группы пришёл один

        site_pay_percent - процент с сайта

    """
    
    class Meta:
        verbose_name = 'Параметр'
        verbose_name_plural = 'Параметры'

    def __str__(self):
        if self.title != "":
            return f"{self.title}"
        return f"{self.key}"

class Peyment(models.Model):
    client = models.ForeignKey('Client', on_delete=models.PROTECT, verbose_name="Ученик")
    group = models.ForeignKey('SportGroup', on_delete=models.PROTECT, null=True, blank=True, verbose_name="Группа")
    way = models.CharField(max_length=150, verbose_name="Способ оплаты") # "cash" / "card" / "site"
    pay_type = models.CharField(max_length=150, verbose_name="Тип оплаты")
    date = models.DateField(null=True, blank=True, verbose_name="Дата") 
    value = models.FloatField(verbose_name="Сумма")

    class Meta:
        verbose_name = 'Платёж'
        verbose_name_plural = 'Платежи'
    
    def __str__(self):
        return f"{self.client}- {self.value}₽"

"""

    one
    one_month
    group
    group_month

    massage_{type id}

"""


class Spending(models.Model):
    key = models.CharField(max_length=255, verbose_name="Описание")
    value = models.FloatField(verbose_name="Сумма")
    spend_type = models.CharField(max_length=150, verbose_name="Тип")
    date = models.DateField(null=True, blank=True, verbose_name="Дата")
    
    class Meta:
        verbose_name = 'Расход'
        verbose_name_plural = 'Расходы'
    
    def __str__(self):
        return f"{self.key}- {self.value}₽"

class Salary(models.Model):
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name='who_trainer',
        verbose_name="Сотрудник"
    )
    date = models.DateField(verbose_name="Дата")
    accure = models.FloatField(blank=True)
    give = models.FloatField(verbose_name="Выплачено")
    
    class Meta:
        verbose_name = 'Выплата'
        verbose_name_plural = 'Зарплаты'
    
    def __str__(self):
        return f"{self.user.first_name[0]}. {self.user.last_name} - {self.give}₽"


class Income(models.Model):
    key = models.CharField(max_length=255, verbose_name="Описание")
    value = models.FloatField(verbose_name="Сумма")
    date = models.DateField(null=True, blank=True, verbose_name="Дата")
    
    class Meta:
        verbose_name = 'Доход'
        verbose_name_plural = 'Доходы'
    
    def __str__(self):
        return f"{self.key}- {self.value}₽"
    
class SingleTren(models.Model):
    trening = models.ForeignKey('Trening', on_delete=models.PROTECT, null=True, verbose_name="Занятие")
    client = models.ForeignKey('Client', on_delete=models.PROTECT, null=True, verbose_name="Ученик")
    pay = models.ForeignKey('Peyment', on_delete=models.PROTECT, null=True, verbose_name="Платёж")


class MassageTypes(models.Model):
    title = models.CharField(max_length=255, verbose_name="Название")
    prise = models.FloatField(verbose_name="Стоимость")
    trener_sum = models.FloatField(verbose_name="Зарплата тренера")

    class Meta:
        verbose_name = 'Тип занятия по массажу'
        verbose_name_plural = 'Типы занятий по массажу'
    
    def __str__(self):
        return f"{self.title}"

class Massage(models.Model):
    trening = models.ForeignKey('Trening', on_delete=models.PROTECT, null=True, verbose_name="Занятие")
    client = models.ForeignKey('Client', on_delete=models.PROTECT, null=True, verbose_name="Клиент")
    pay = models.ForeignKey('Peyment', on_delete=models.PROTECT, null=True, verbose_name="Платёж")
    
    class Meta:
        verbose_name = 'Массаж'
        verbose_name_plural = 'Занятия по массажу'


class Subscription(models.Model):
    start_date = models.DateField(verbose_name="Дата начала")
    end_date = models.DateField(verbose_name="Дата окончания")
    num_sessions = models.IntegerField(verbose_name="Количество занятий")
    client = models.ForeignKey(Client, on_delete=models.PROTECT, verbose_name="Клиент")
    sport_group = models.ForeignKey(SportGroup, on_delete=models.PROTECT, verbose_name="Группа", null=True)
    pay = models.ForeignKey('Peyment', on_delete=models.PROTECT, null=True, verbose_name="Платёж")
    trenings = models.ManyToManyField(Trening, blank=True, verbose_name="Занятия")
    tren_type = models.CharField(max_length=255, verbose_name="Тип", blank=True) # single or group
    
    class Meta:
        verbose_name = 'Абонемент'
        verbose_name_plural = 'Абонементы'
    
    def __str__(self):
        return f"Абонемент клиента {self.client.name}"


# Зарплата для администратора
class AdminSalary(models.Model):
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.PROTECT,
        null=True,
        blank=True,
        related_name='who_admin',
        verbose_name="Сотрудник"
    )
    type = models.CharField(max_length=255, verbose_name="Тип") # percent or sum
    value = models.FloatField(verbose_name="Сумма / Процент")

    class Meta:
        verbose_name = 'Зарплата администратора'
        verbose_name_plural = 'Зарплаты администраторов'
