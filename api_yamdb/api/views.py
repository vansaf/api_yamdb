from reviews.models import Review, Comment
from .serializers import ReviewSerializer, CommentSerializer
from .permissions import CustomReviewAndCommentPermission
from .pagination import CustomPagination
from rest_framework import serializers
from rest_framework import viewsets, filters
from django_filters.rest_framework import DjangoFilterBackend


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
