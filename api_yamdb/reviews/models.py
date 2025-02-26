
from django.db import models
from django.db.models import Avg
from django.contrib.auth import get_user_model
from django.contrib.auth.models import AbstractUser


class CustomUser(AbstractUser):

    class RoleChoices(models.TextChoices):

        ADMIN = 'admin', 'Admin'
        MODERATOR = 'moderator', 'Moderator'
        USER = 'user', 'User'

    username = models.CharField('Логин', max_length=150,
                                unique=True, blank=False)
    email = models.EmailField('Электронная почта',
                              max_length=254, unique=True, blank=False)
    first_name = models.TextField('Имя', max_length=150, blank=True)
    last_name = models.TextField('Фамилия', max_length=150, blank=True)
    bio = models.TextField('Биография', blank=True)
    role = models.CharField('Статус',
                            max_length=100,
                            choices=RoleChoices.choices,
                            default=RoleChoices.USER)

    @property
    def is_admin(self):
        """Возвращает True, если роль пользователя — Admin."""
        return self.role == self.RoleChoices.ADMIN

    @property
    def is_moderator(self):
        """Возвращает True, если роль пользователя — Moderator."""
        return self.role == self.RoleChoices.MODERATOR

    def __str__(self):
        return self.username


User = get_user_model()

"""
Здесь описываются модели, которые будут храниться в базе данных.
Модели Category, Genre, Title - зона ответственности Второго разработчика.
"""


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
    """
    Модель для произведений (фильмы, книги, музыка).

    Поля:
    name - название произведения
    year - год выпуска
    description - описание (необязательно)
    category - связь с моделью Category (ForeignKey)
    genre - связь с моделью Genre (ManyToManyField,
            т.к. произведение может иметь несколько жанров)
    """
    name = models.CharField(max_length=256)
    year = models.PositiveIntegerField()
    description = models.TextField(blank=True, null=True)
    category = models.ForeignKey(
        Category,
        # Если удалить категорию, поле category станет null
        on_delete=models.SET_NULL,
        null=True,
        # Позволяет обратный доступ: category.titles.all()
        related_name='titles'
    )
    genre = models.ManyToManyField(
        Genre,
        # Обратный доступ: genre.titles.all()
        related_name='titles'
    )

    def __str__(self):
        return self.name


class GenreTitle(models.Model):
    """
    Промежуточная модель для связи Title и Genre.
    Каждая пара (title, genre) должна быть уникальной.
    """
    title = models.ForeignKey(
        Title,
        on_delete=models.CASCADE,
        related_name='genre_titles'
    )
    genre = models.ForeignKey(
        Genre,
        on_delete=models.CASCADE,
        related_name='genre_titles'
    )

    class Meta:
        unique_together = ('title', 'genre')
        verbose_name = 'Жанр Названия'
        verbose_name_plural = 'Жанры Названий'

    def __str__(self):
        return f"{self.title} — {self.genre}"


class Review(models.Model):
    """Модель для работы с отзывами."""
    title = models.ForeignKey(
        Title, on_delete=models.CASCADE,
        related_name='reviews'
    )
    text = models.TextField()
    author = models.ForeignKey(
        User,
        related_name='reviews',
        on_delete=models.CASCADE
    )
    score = models.PositiveSmallIntegerField(
        verbose_name='Оценка', choices=[(r, r) for r in range(1, 11)],
    )
    pub_date = models.DateTimeField(
        verbose_name='Дата оценки', auto_now_add=True, db_index=True
    )

    def __str__(self):
        return self.text
    """Функция save меняет средний рейтинг произведения в реальном времени."""
    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        self.score_avg = Review.objects.filter(title_id=self.title).aggregate(
            Avg('score')
        )
        self.title.rating = self.score_avg['score__avg']
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
