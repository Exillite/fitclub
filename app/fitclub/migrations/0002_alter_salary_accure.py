# Generated by Django 4.1.2 on 2022-12-12 07:05

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('fitclub', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='salary',
            name='accure',
            field=models.IntegerField(blank=True),
        ),
    ]