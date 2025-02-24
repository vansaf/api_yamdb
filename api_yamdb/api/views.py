"""
Здесь описываются классы ViewSet,
которые определяют логику обработки запросов
к моделям Category, Genre и Title.
"""

from rest_framework import (generics,
                            viewsets,
                            serializers,
                            filters,
                            permissions,
                            status)
from rest_framework.response import Response

from reviews.models import Category, Genre, Title, Review, Comment, User

from .serializers import SignUpSerializer, CategorySerializer, GenreSerializer, TitleSerializer, ReviewSerializer, CommentSerializer
from .permissions import CustomReviewAndCommentPermission
from .pagination import CustomPagination
from .utils import generate_confirmation_code, send_confirmation_code
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


class SignUpView(generics.CreateAPIView):
    queryset = User.objects.all()
    serializer_class = SignUpSerializer
    permission_classes = (permissions.AllowAny, )

    def post(self, request):
        serializer = SignUpSerializer(data=request.data)
        # user = serializer.save()
        serializer.is_valid()
        serializer.save()
        data = serializer.data
        confirmation_code = generate_confirmation_code()
        self.request.session['confirmation_code'] = confirmation_code
        send_confirmation_code(data['email'], confirmation_code)
        return Response(
            {
                'email': data['email'],
                'username': data['username']
            },
            status=status.HTTP_200_OK
        )

   # def perform_create(self, serializer):
   #     user = serializer.save()
   #     confirmation_code = generate_confirmation_code()
   #     self.request.session['confirmation_code'] = confirmation_code
   #     send_confirmation_code(user.email, confirmation_code)
   #     return Response(status=status.HTTP_201_CREATED)
