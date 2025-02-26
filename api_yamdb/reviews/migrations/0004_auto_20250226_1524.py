# Generated by Django 3.2 on 2025-02-26 15:24

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('reviews', '0003_title_rating'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='customuser',
            options={'verbose_name': 'пользователь', 'verbose_name_plural': 'Пользователи'},
        ),
        migrations.AlterField(
            model_name='customuser',
            name='role',
            field=models.CharField(choices=[('admin', 'Admin'), ('moderator', 'Moderator'), ('user', 'User')], default='user', max_length=10, verbose_name='Статус'),
        ),
    ]
