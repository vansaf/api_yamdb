from django.db import models
from django.db.models import Avg
from django.contrib.auth import get_user_model
from django.contrib.auth.models import AbstractUser

from .constants import (MAX_USERNAME_FIELD_LENGHT,
                        MAX_FIRST_NAME_FIELD_LENGHT,
                        MAX_LAST_NAME_FIELD_LENGHT,
                        MAX_EMAIL_FIELD_LENGHT,
                        MAX_ROLE_FIELD_LENGHT)


class CustomUser(AbstractUser):
    """Кастомная модель пользователя."""

    class RoleChoices(models.TextChoices):
        """Класс выбора роли для пользователя."""

        ADMIN = 'admin', 'Admin'
        MODERATOR = 'moderator', 'Moderator'
        USER = 'user', 'User'

    username = models.CharField('Логин',
                                max_length=MAX_USERNAME_FIELD_LENGHT,
                                unique=True)
    email = models.EmailField('Электронная почта',
                              max_length=MAX_EMAIL_FIELD_LENGHT,
                              unique=True)
    first_name = models.TextField('Имя',
                                  max_length=MAX_FIRST_NAME_FIELD_LENGHT,
                                  blank=True)
    last_name = models.TextField('Фамилия',
                                 max_length=MAX_LAST_NAME_FIELD_LENGHT,
                                 blank=True)
    bio = models.TextField('Биография', blank=True)
    role = models.CharField('Статус',
                            max_length=MAX_ROLE_FIELD_LENGHT,
                            choices=RoleChoices.choices,
                            default=RoleChoices.USER)

    @property
    def is_admin(self):
        return self.role == self.RoleChoices.ADMIN

    @property
    def is_moderator(self):
        return self.role == self.RoleChoices.MODERATOR

    def __str__(self):
        return self.username

    class Meta:
        verbose_name = 'пользователь'
        verbose_name_plural = 'Пользователи'


User = get_user_model()


class Category(models.Model):
    """
    Модель для категорий (например, 'Фильмы', 'Книги', 'Музыка').

    Поля:
    name - название категории
    slug - уникальный идентификатор (URL-friendly),
           удобен для формирования адресов.
    """
    name = models.CharField(max_length=256)
    slug = models.SlugField(unique=True)

    def __str__(self):
        # Метод, который возвращает строковое представление объекта
        # (удобно для админки)
        return self.name


class Genre(models.Model):
    """
    Модель для жанров (например, 'Рок', 'Артхаус', 'Сказка').
    Поля:
    name - название жанра
    slug - уникальный идентификатор
    """
    name = models.CharField(max_length=256)
    slug = models.SlugField(unique=True)

    def __str__(self):
        return self.name


class Title(models.Model):
    name = models.CharField(max_length=256)
    year = models.PositiveIntegerField()
    description = models.TextField(blank=True, null=True)
    category = models.ForeignKey(
        Category, on_delete=models.SET_NULL, null=True, related_name='titles'
    )
    genre = models.ManyToManyField(Genre, through='GenreTitle')
    #rating = models.FloatField(null=True, blank=True)

    def __str__(self):
        return self.name


class GenreTitle(models.Model):
    title = models.ForeignKey(Title, on_delete=models.CASCADE)
    genre = models.ForeignKey(Genre, on_delete=models.CASCADE)

    class Meta:
        constraints = [
            models.UniqueConstraint(fields=['title', 'genre'], name='unique_title_genre')
        ]

    def __str__(self):
        return f"{self.title} — {self.genre}"


class Review(models.Model):
    """Модель для работы с отзывами."""
    title = models.ForeignKey(Title, on_delete=models.CASCADE,
                              related_name='reviews')
    text = models.TextField()
    author = models.ForeignKey(User, on_delete=models.CASCADE,
                               related_name='reviews')
    score = models.PositiveSmallIntegerField(
        verbose_name='Оценка', choices=[(r, r) for r in range(1, 11)],
    )
    pub_date = models.DateTimeField(verbose_name='Дата оценки',
                                    auto_now_add=True, db_index=True)

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        score_avg = Review.objects.filter(title=self.title).aggregate(Avg('score'))
        self.title.rating = score_avg['score__avg'] or 0
        self.title.save()


class Comment(models.Model):
    """Модель для работы с коментариями."""
    review = models.ForeignKey(
        Review,
        on_delete=models.CASCADE,
        related_name='comments'
    )
    text = models.TextField()
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='comments'
    )
    pub_date = models.DateTimeField(
        auto_now_add=True,
        db_index=True
    )

    def __str__(self):
        return self.text
