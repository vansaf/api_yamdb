from django.db import models
from django.contrib.auth import get_user_model
from django.core.validators import MinValueValidator, MaxValueValidator
from django.contrib.auth.models import AbstractUser

from .constants import (
    MAX_USERNAME_FIELD_LENGHT,
    MAX_FIRST_NAME_FIELD_LENGHT,
    MAX_LAST_NAME_FIELD_LENGHT,
    MAX_EMAIL_FIELD_LENGHT,
    MAX_ROLE_FIELD_LENGHT,
    MAX_NAME_LENGTH,
    MIN_REVIEW_SCORE,
    MAX_REVIEW_SCORE,
    MAX_FIELD_LENGHT_STR
)


class CustomUser(AbstractUser):
    """Кастомная модель пользователя."""

    class RoleChoices(models.TextChoices):
        """Класс выбора роли для пользователя."""
        ADMIN = 'admin', 'Admin'
        MODERATOR = 'moderator', 'Moderator'
        USER = 'user', 'User'

    username = models.CharField(
        'Логин',
        max_length=MAX_USERNAME_FIELD_LENGHT,
        unique=True
    )
    email = models.EmailField(
        'Электронная почта',
        max_length=MAX_EMAIL_FIELD_LENGHT,
        unique=True
    )
    first_name = models.TextField(
        'Имя',
        max_length=MAX_FIRST_NAME_FIELD_LENGHT,
        blank=True
    )
    last_name = models.TextField(
        'Фамилия',
        max_length=MAX_LAST_NAME_FIELD_LENGHT,
        blank=True
    )
    bio = models.TextField('Биография', blank=True)
    role = models.CharField(
        'Статус',
        max_length=MAX_ROLE_FIELD_LENGHT,
        choices=RoleChoices.choices,
        default=RoleChoices.USER
    )

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
    """Модель для категорий (например, 'Фильмы', 'Книги', 'Музыка')."""

    name = models.CharField(
        'Название категории',
        max_length=MAX_NAME_LENGTH
    )
    slug = models.SlugField('Идентификатор', unique=True)

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = 'Категория'
        verbose_name_plural = 'Категории'


class Genre(models.Model):
    """Модель для жанров (например, 'Рок', 'Артхаус', 'Сказка')."""

    name = models.CharField(
        'Название жанра',
        max_length=MAX_NAME_LENGTH
    )
    slug = models.SlugField('Идентификатор', unique=True)

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = 'Жанр'
        verbose_name_plural = 'Жанры'


class Title(models.Model):
    """Модель для произведений."""

    name = models.CharField(
        'Название',
        max_length=MAX_NAME_LENGTH
    )
    year = models.PositiveIntegerField('Год выпуска')
    description = models.TextField('Описание', blank=True, null=True)
    category = models.ForeignKey(
        Category,
        on_delete=models.SET_NULL,
        null=True,
        related_name='titles',
        verbose_name='Категория'
    )
    genre = models.ManyToManyField(
        Genre,
        through='GenreTitle',
        verbose_name='Жанры'
    )

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = 'Произведение'
        verbose_name_plural = 'Произведения'


class GenreTitle(models.Model):
    """Связующая модель для произведений и жанров."""

    title = models.ForeignKey(
        Title,
        on_delete=models.CASCADE,
        verbose_name='Произведение'
    )
    genre = models.ForeignKey(
        Genre,
        on_delete=models.CASCADE,
        verbose_name='Жанр'
    )

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=['title', 'genre'],
                name='unique_title_genre'
            )
        ]
        verbose_name = 'Жанр произведения'
        verbose_name_plural = 'Жанры произведений'

    def __str__(self):
        return f"{self.title} — {self.genre}"


class Review(models.Model):
    """Модель отзывов на произведения."""

    title = models.ForeignKey(
        Title,
        on_delete=models.CASCADE,
        related_name='reviews',
        verbose_name='Произведение'
    )
    text = models.TextField('Текст отзыва')
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='reviews',
        verbose_name='Автор'
    )
    score = models.PositiveSmallIntegerField(
        'Оценка',
        validators=[MinValueValidator(MIN_REVIEW_SCORE),
                    MaxValueValidator(MAX_REVIEW_SCORE)]
    )
    pub_date = models.DateTimeField('Дата публикации', auto_now_add=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=['title', 'author'],
                name='unique_review'
            )
        ]
        verbose_name = 'Отзыв'
        verbose_name_plural = 'Отзывы'

    def __str__(self):
        return self.text[:MAX_FIELD_LENGHT_STR]


class Comment(models.Model):
    """Модель комментариев к отзывам."""

    review = models.ForeignKey(
        Review,
        on_delete=models.CASCADE,
        related_name='comments',
        verbose_name='Отзыв'
    )
    text = models.TextField('Текст комментария')
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='comments',
        verbose_name='Автор'
    )
    pub_date = models.DateTimeField('Дата публикации', auto_now_add=True)

    class Meta:
        verbose_name = 'Комментарий'
        verbose_name_plural = 'Комментарии'

    def __str__(self):
        return self.text[:MAX_FIELD_LENGHT_STR]
