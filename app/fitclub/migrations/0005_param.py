# Generated by Django 4.1.2 on 2022-11-29 07:03

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('fitclub', '0004_alter_trening_group'),
    ]

    operations = [
        migrations.CreateModel(
            name='Param',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('key', models.CharField(max_length=150)),
                ('value', models.ImageField(blank=True, null=True, upload_to='')),
            ],
        ),
    ]
