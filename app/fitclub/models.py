from django.db import models
from django.conf import settings


class SportGroup(models.Model):
    name = models.CharField(max_length=255)
    trener = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        null=True
    )


    def __str__(self):
        return self.name


class GroupTime(models.Model):
    start = models.TimeField()
    end = models.TimeField()
    day = models.IntegerField() # 1 - 7

    group = models.ForeignKey('SportGroup', on_delete=models.PROTECT, null=True)
    
    def __str__(self):
        return f"{self.group.name}: {self.start} - {self.end}"



class Client(models.Model):
    name = models.CharField(max_length=255)
    surname = models.CharField(max_length=255)
    phone = models.CharField(max_length=255, null=True, blank=True)
    email = models.CharField(max_length=255, null=True, blank=True)
    groups = models.ManyToManyField(SportGroup)


class Trening(models.Model):
    start = models.TimeField()
    end = models.TimeField()
    day = models.DateField()
    group = models.ForeignKey('SportGroup', on_delete=models.PROTECT, null=True)
    trening_type = models.CharField(max_length=50) # "personal" / "group"
    col = models.IntegerField() # количество участников
    is_was = models.BooleanField() # Была ло занятие
    progul = models.BooleanField() # Был ли прогул
    clients = models.ManyToManyField(Client, blank=True)
    trener = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name='royal_trainer'
    )
    helper = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name='helper_for_training'
    )
