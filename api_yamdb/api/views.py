"""
Здесь описываются классы ViewSet,
которые определяют логику обработки запросов
к моделям Category, Genre и Title.
"""

# DRF-класс для создания набора представлений
from rest_framework import viewsets, serializers, filters
# Импортируем наши модели
from reviews.models import Category, Genre, Title, Review, Comment
# Импорт сериализаторов
from .serializers import CategorySerializer, GenreSerializer, TitleSerializer, ReviewSerializer, CommentSerializer
from .permissions import CustomReviewAndCommentPermission
from .pagination import CustomPagination

from django_filters.rest_framework import DjangoFilterBackend

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


class ReviewsViewSet(viewsets.ModelViewSet):
    queryset = Review.objects.all()
    serializer_class = ReviewSerializer
    permission_classes = CustomReviewAndCommentPermission
    pagination_class = CustomPagination
    filter_backends = (DjangoFilterBackend, filters.SearchFilter)
    filterset_fields = ('pub_date', 'score')
    search_fields = ('author')

    def perform_create(self, serializer):
        """Создание отзыва с ограничением: один пользователь — один отзыв"""
        review_id = self.kwargs.get('review_id')
        user = self.request.user

        if Review.objects.filter(author=user, review_id=review_id).exists():
            raise serializers.ValidationError(
                "Вы уже оставили отзыв на это произведение."
            )

        serializer.save(author=user, review_id=review_id)

    def get_queryset(self):
        """Фильтрует отзывы по ID произведения."""
        title_id = self.kwargs.get('title_id')
        return Review.objects.filter(title_id=title_id)


class CommentsViewSet(viewsets.ModelViewSet):
    queryset = Comment.objects.all()
    serializer_class = CommentSerializer
    permission_classes = CustomReviewAndCommentPermission
    pagination_class = CustomPagination
    filter_backends = (DjangoFilterBackend, filters.SearchFilter)
    filterset_fields = ('pub_date')
    search_fields = ('author')

    def get_queryset(self):
        """Фильтрует коментарии по ID произведения."""
        review_id = self.kwargs.get('review_id')
        return Comment.objects.filter(review__id=review_id)
