from django.core.exceptions import ValidationError
from django.shortcuts import get_object_or_404
import re

from rest_framework import serializers

from reviews.models import Category, Comment, Genre, Review, Title, User
from .constants import (
    BAD_USERNAME, MAX_CODE_LENGHT, USERNAME_SYMBOLS
)
from reviews.constants import (
    MAX_USERNAME_FIELD_LENGHT, MAX_EMAIL_FIELD_LENGHT
)


class SignUpSerializer(serializers.ModelSerializer):
    """
    Сериализатор для регистрации пользователя в системе.
    Производит валидацию полей email и username.
    """

    class Meta:
        model = User
        fields = ('email', 'username')

    def validate_username(self, value):
        if value in BAD_USERNAME:
            raise serializers.ValidationError(
                f'Неподходящее имя {value}. Попробуйте выбрать другое.'
            )
        if len(value) > MAX_USERNAME_FIELD_LENGHT:
            raise serializers.ValidationError(
                f'Имя {value} превышает допустимую длину в '
                f'{MAX_USERNAME_FIELD_LENGHT} символов'
            )
        if not re.match(USERNAME_SYMBOLS, value):
            raise serializers.ValidationError(
                f'Недопустимые символы в имени {value}'
            )
        if User.objects.filter(username=value).exists():
            raise serializers.ValidationError(
                'Пользователь с таким именем уже зарегистрирован в системе'
            )
        return value

    def validate_email(self, value):
        if len(value) > MAX_EMAIL_FIELD_LENGHT:
            raise serializers.ValidationError(
                f'Почта {value} превышает допустимую длину в '
                f'{MAX_EMAIL_FIELD_LENGHT} символов'
            )
        if User.objects.filter(email=value).exists():
            raise serializers.ValidationError(
                'Пользователь с такой почтой уже зарегистрирован в системе'
            )
        return value


class TokenSerializer(serializers.Serializer):
    """
    Сериализатор для выдачи токена зарегистрированному пользователю.
    Производит валидацию полей confirmation_code и username.
    """
    confirmation_code = serializers.CharField(max_length=MAX_CODE_LENGHT)
    username = serializers.CharField()

    def validate_username(self, value):
        if User.objects.filter(username=value).exists():
            return value
        raise serializers.ValidationError(
            f'Пользователь {value} не найден', code='user not found'
        )

    def validate_confirmation_code(self, value):
        session_code = self.context['request'].session.get(
            'confirmation_code'
        )
        if value != session_code:
            raise serializers.ValidationError('Неправильный код')
        return value


class UserSerializer(serializers.ModelSerializer):
    """
    Сериализатор для эндпоинта users.
    Производит валидацию полей role и username.
    """

    class Meta:
        model = User
        fields = (
            'username', 'email', 'first_name',
            'last_name', 'bio', 'role'
        )

    def validate_username(self, value):
        if not re.match(USERNAME_SYMBOLS, value):
            raise serializers.ValidationError()
        return value

    def validate_role(self, value):
        user = self.context['request'].user
        if user.role != value and not user.is_admin:
            raise serializers.ValidationError('Запрещено изменять права.')
        return value


class CategorySerializer(serializers.ModelSerializer):
    """
    Сериализатор для модели Category.
    """

    class Meta:
        model = Category
        fields = ['name', 'slug']


class GenreSerializer(serializers.ModelSerializer):
    """
    Сериализатор для модели Genre.
    Аналогичен CategorySerializer.
    """

    class Meta:
        model = Genre
        exclude = ('id',)


class TitleReadSerializer(serializers.ModelSerializer):
    """
    Сериализатор для чтения произведений (Title).
    Включает вложенные данные для категории и жанров, а также рейтинг.
    """
    category = CategorySerializer(read_only=True)
    genre = GenreSerializer(read_only=True, many=True)
    rating = serializers.IntegerField(read_only=True)

    class Meta:
        model = Title
        fields = '__all__'


class TitleWriteSerializer(serializers.ModelSerializer):
    """
    Сериализатор для создания и обновления произведений (Title).
    Использует slug-поля для категории и жанров.
    """
    category = serializers.SlugRelatedField(
        queryset=Category.objects.all(), slug_field='slug'
    )
    genre = serializers.SlugRelatedField(
        queryset=Genre.objects.all(), slug_field='slug', many=True
    )

    class Meta:
        model = Title
        fields = '__all__'


class ReviewSerializer(serializers.ModelSerializer):
    """
    Сериализатор для модели Review.
    Производит валидацию оценки и проверяет наличие
    существующего отзыва от того же пользователя для произведения.
    """
    title = serializers.SlugRelatedField(
        slug_field='name', read_only=True
    )
    author = serializers.SlugRelatedField(
        slug_field='username', read_only=True
    )

    def validate_score(self, value):
        if 0 > value > 10:
            raise serializers.ValidationError('Оценка по 10-бальной шкале!')
        return value

    def validate(self, data):
        request = self.context['request']
        author = request.user
        title_id = self.context.get('view').kwargs.get('title_id')
        title = get_object_or_404(Title, pk=title_id)
        if request.method == 'POST' and Review.objects.filter(
            title=title, author=author
        ).exists():
            raise ValidationError('Может существовать только один отзыв!')
        return data

    class Meta:
        model = Review
        fields = '__all__'


class CommentSerializer(serializers.ModelSerializer):
    """
    Сериализатор для модели Comment.
    Представляет автора комментария в виде username.
    """
    author = serializers.SlugRelatedField(
        slug_field='username', read_only=True
    )

    class Meta:
        model = Comment
        fields = ('id', 'text', 'author', 'pub_date')
