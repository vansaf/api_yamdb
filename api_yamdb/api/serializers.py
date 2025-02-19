from django.contrib.auth import get_user_model
from rest_framework import serializers
from reviews.models import Review, Comment

User = get_user_model()


class ReviewSerializer(serializers.ModelSerializer):
    """Сериализатор модели отзывов"""
    author = serializers.SlugRelatedField(
        slug_fields='username',
        read_only=True
    )

    class Meta:
        model = Review
        fields = '__all__'


class CommentSerializer(serializers.ModelSerializer):
    """Сериализатор модели комментариев"""
    author = serializers.SlugRelatedField(
        slug_fields='username',
        read_only=True
    )

    class Meta:
        model = Comment
        fields = '__all__'
