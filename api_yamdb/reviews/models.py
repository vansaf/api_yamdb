from django.db import models
from django.contrib.auth.models import AbstractUser


class CustomUser(AbstractUser):
    username = models.CharField('Логин', max_length=150,
                                unique=True, null=False)
    email = models.EmailField('Электронная почта',
                              max_length=254, unique=True, null=False)
    first_name = models.TextField('Имя', max_length=150, blank=True)
    last_name = models.TextField('Фамилия', max_length=150, blank=True)
    bio = models.TextField('Биография', blank=True)
    role = models.CharField('Статус', default='user')

    def __str__(self):
        return self.username
