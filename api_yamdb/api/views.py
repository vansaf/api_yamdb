from compositions.models import Review, Comment
from .serializers import ReviewSerializer, CommentSerializer
from .permission import IsAuthorOrModeratorOrAdmin, IsActionAllowed
from .pagination import ReviewPagination
from rest_framework import serializers
from rest_framework import viewsets, permissions


class ReviewsViewSet(viewsets.ModelViewSet):
    queryset = Review.objects.all()
    serializer_class = ReviewSerializer
    permission_classes = [
        IsAuthorOrModeratorOrAdmin,
        IsActionAllowed
    ]
    pagination_class = ReviewPagination

    def perform_create(self, serializer):
        """Создание отзыва с ограничением: один пользователь — один отзыв на произведение."""
        work_id = self.kwargs.get('work_id')
        user = self.request.user

        if Review.objects.filter(author=user, work_id=work_id).exists():
            raise serializers.ValidationError(
                "Вы уже оставили отзыв на это произведение."
            )

        serializer.save(author=user, work_id=work_id)

    def get_queryset(self):
        """Фильтрует отзывы по ID произведения."""
        work_id = self.kwargs.get('work_id')
        return Review.objects.filter(work_id=work_id)


class CommentsViewSet(viewsets.ModelViewSet):
    queryset = Comment.objects.all()
    serializer_class = CommentSerializer
    permission_classes = [
        IsAuthorOrModeratorOrAdmin,
        IsActionAllowed
    ]
    pagination_class = ReviewPagination

    def get_queryset(self):
        """Фильтрует коментарии по ID произведения."""
        review_id = self.kwargs.get('review_id')
        return Comment.objects.filter(review__id=review_id)
