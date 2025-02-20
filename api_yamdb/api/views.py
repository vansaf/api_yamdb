"""
Здесь описываются классы ViewSet,
которые определяют логику обработки запросов
к моделям Category, Genre и Title.
"""

# DRF-класс для создания набора представлений
from rest_framework import viewsets
# Импортируем наши модели
from reviews.models import Category, Genre, Title
# Импорт сериализаторов
from .serializers import CategorySerializer, GenreSerializer, TitleSerializer


class CategoryViewSet(viewsets.ModelViewSet):
    """
    ViewSet для работы с категориями (Category).
    Наследуется от ModelViewSet,
    который предоставляет стандартные действия:
    list(), create(), retrieve(), update(), partial_update(), destroy().
    """
    queryset = Category.objects.all()  # Указываем, какие данные обрабатываем
    serializer_class = CategorySerializer  # Какой сериализатор использовать


class GenreViewSet(viewsets.ModelViewSet):
    """
    ViewSet для работы с жанрами (Genre).
    Аналогично CategoryViewSet.
    """
    queryset = Genre.objects.all()
    serializer_class = GenreSerializer


class TitleViewSet(viewsets.ModelViewSet):
    """
    ViewSet для работы с произведениями (Title).
    """
    queryset = Title.objects.all()
    serializer_class = TitleSerializer
