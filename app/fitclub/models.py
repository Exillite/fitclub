from itertools import count
from multiprocessing import Event
from tracemalloc import start
from django.db import models
from django.conf import settings


class SportGroup(models.Model):
    name = models.CharField(max_length=255)
    trener = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
    )
    trener = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
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

class Trening(models.Model):
    start = models.TimeField()
    end = models.TimeField()
    day = models.DateField()
    group = models.ForeignKey('SportGroup', on_delete=models.PROTECT, null=True)
    trening_type = models.CharField(max_length=50) # "personal" / "group"
    col = models.IntegerField()
    is_was = models.BooleanField() # Была ло занятие
    progul = models.BooleanField() # Был ли прогул
    