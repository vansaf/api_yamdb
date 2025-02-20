"""
Здесь описываются модели, которые будут храниться в базе данных.
Модели Category, Genre, Title - зона ответственности Второго разработчика.
"""

from django.db import models  # Библиотека для описания моделей в Django


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
        # Метод, который возвращает строковое представление объекта (удобно для админки)
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
        on_delete=models.SET_NULL,  # Если удалить категорию, поле category станет null
        null=True,
        related_name='titles'       # Позволяет обратный доступ: category.titles.all()
    )
    genre = models.ManyToManyField(
        Genre, 
        related_name='titles'       # Обратный доступ: genre.titles.all()
    )

    def __str__(self):
        return self.name
