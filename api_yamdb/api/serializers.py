import re

from rest_framework import serializers, status

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
        raise serializers.ValidationError('Пользователь не найден', code='Пользователь не найден')

    def validate_confirmation_code(self, value):
        session_confirmation_code = self.context['request'].session.get('confirmation_code')
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
            'role'
        )

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
        fields = '__all__'


class GenreSerializer(serializers.ModelSerializer):
    """
    Сериализатор для модели Genre.
    Аналогично CategorySerializer.
    """
    class Meta:
        model = Genre
        fields = '__all__'


class TitleSerializer(serializers.ModelSerializer):
    """
    Сериализатор для модели Title.
    Здесь можно настроить вложенные сериализаторы,
    если нужно показывать detail-информацию о категории и жанрах.
    """
    # Если хотим вложенные поля, делаем так (пример):
    # category = CategorySerializer(read_only=True)
    # genre = GenreSerializer(many=True, read_only=True)

    class Meta:
        model = Title
        fields = '__all__'


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