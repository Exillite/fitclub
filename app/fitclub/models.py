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
    trening_type = models.CharField(max_length=50, verbose_name="Тип занятия") # "personal" / "group"
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
    
    class Meta:
        verbose_name = 'Занитие'
        verbose_name_plural = 'Занятия'
    
    def __str__(self):
        return f"Зантие {self.day}: {self.start.hour}:{self.start.minute}"


class Param(models.Model):
    key = models.CharField(max_length=150, verbose_name="Ключ")
    value = models.IntegerField(null=True, blank=True, verbose_name="Значение")
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
    way = models.CharField(max_length=150, verbose_name="Способ оплаты") # "cash" / "card"
    pay_type = models.CharField(max_length=150, verbose_name="Тип оплаты")
    date = models.DateField(null=True, blank=True, verbose_name="Дата") 
    value = models.IntegerField(verbose_name="Сумма")

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

"""


class Spending(models.Model):
    key = models.CharField(max_length=255, verbose_name="Описание")
    value = models.IntegerField(verbose_name="Сумма")
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
    accure = models.IntegerField(blank=True)
    give = models.IntegerField(verbose_name="Выплачено")
    
    class Meta:
        verbose_name = 'Выплата'
        verbose_name_plural = 'Зарплаты'
    
    def __str__(self):
        return f"{self.user.first_name[0]}. {self.user.last_name} - {self.give}₽"


class Income(models.Model):
    key = models.CharField(max_length=255, verbose_name="Описание")
    value = models.IntegerField(verbose_name="Сумма")
    date = models.DateField(null=True, blank=True, verbose_name="Дата")
    
    class Meta:
        verbose_name = 'Доход'
        verbose_name_plural = 'Доходы'
    
    def __str__(self):
        return f"{self.key}- {self.value}₽"
