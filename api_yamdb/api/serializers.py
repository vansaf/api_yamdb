import re
from django.db.models import Avg

from rest_framework import serializers

from reviews.models import Category, Comment, Genre, Review, Title, User


class SignUpSerializer(serializers.ModelSerializer):

    class Meta:
        model = User
        fields = ('email', 'username')

    def validate_username(self, value):
        if value == 'me':
            raise serializers.ValidationError()
        if len(value) > 150:
            raise serializers.ValidationError()
        if not re.match(r'^[\w.@+-]+$', value):
            raise serializers.ValidationError()
        if User.objects.filter(username=value).exists():
            raise serializers.ValidationError()
        return value

    def validate_email(self, value):
        if len(value) > 254:
            raise serializers.ValidationError()
        if User.objects.filter(email=value).exists():
            raise serializers.ValidationError()
        return value


class TokenSerializer(serializers.Serializer):
    confirmation_code = serializers.CharField(max_length=6)
    username = serializers.CharField()

    def validate_username(self, value):
        if User.objects.filter(username=value).exists():
            return value
        raise serializers.ValidationError('Пользователь не найден',
                                          code='user not found')

    def validate_confirmation_code(self, value):
        session_confirmation_code = self.context[
            'request'].session.get('confirmation_code')
        if value != session_confirmation_code:
            raise serializers.ValidationError('Неправильный код')
        return value


class UserSerializer(serializers.ModelSerializer):

    class Meta:
        model = User
        fields = (
            'username',
            'email',
            'first_name',
            'last_name',
            'bio',
            'role')

    def validate_username(self, value):
        if not re.match(r'^[\w.@+-]+$', value):
            raise serializers.ValidationError()
        return value

    def validate_role(self, value):
        user = self.context['request'].user
        if user.role != value and not user.is_admin:
            raise serializers.ValidationError('Нельзя изменять роль.')
        return value


class CategorySerializer(serializers.ModelSerializer):
    """
    Сериализатор для модели Category.
    ModelSerializer автоматически генерирует поля
    на основе полей модели Category.
    """
    class Meta:
        # С какой моделью работаем:
        model = Category
        # Какие поля будем сериализовать:
        exclude = ('id',)


class GenreSerializer(serializers.ModelSerializer):
    """
    Сериализатор для модели Genre.
    Аналогично CategorySerializer.
    """
    class Meta:
        model = Genre
        exclude = ('id',)


class TitleSerializer(serializers.ModelSerializer):
    genre = serializers.SlugRelatedField(
        slug_field='slug',
        queryset=Genre.objects.all(),
        many=True
    )
    category = serializers.SlugRelatedField(
        slug_field='slug',
        queryset=Category.objects.all()
    )

    class Meta:
        model = Title
        fields = ('id', 'name', 'year', 'description', 'category', 'genre', 'rating')

    def get_rating(self, obj):
        """Вычисляет средний рейтинг для произведения."""
        return obj.reviews.aggregate(Avg('score'))['score__avg']


class ReviewSerializer(serializers.ModelSerializer):
    """Сериализатор модели отзывов (Reviews)."""
    author = serializers.SlugRelatedField(
        slug_field='username',
        read_only=True
    )

    class Meta:
        model = Review
        fields = '__all__'


class CommentSerializer(serializers.ModelSerializer):
    """Сериализатор модели комментариев (Comments)."""
    author = serializers.SlugRelatedField(
        slug_field='username',
        read_only=True
    )

    class Meta:
        model = Comment
        fields = '__all__'