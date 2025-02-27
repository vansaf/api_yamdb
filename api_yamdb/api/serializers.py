from django.core.exceptions import ValidationError
from django.shortcuts import get_object_or_404

from rest_framework import serializers

import re

from reviews.models import Category, Comment, Genre, Review, Title, User
from .constants import (BAD_USERNAME,
                        MAX_CODE_LENGHT,
                        USERNAME_SYMBOLS)
from reviews.constants import (MAX_USERNAME_FIELD_LENGHT,
                               MAX_EMAIL_FIELD_LENGHT)


class SignUpSerializer(serializers.ModelSerializer):
    """
    Сериализатор для регистрации пользователя в системе.
    Валидация полей email и username.
    """
    class Meta:
        model = User
        fields = ('email', 'username')

    def validate_username(self, value):
        bad_username = [name for name in BAD_USERNAME if name == value]
        if len(bad_username) != 0:
            raise serializers.ValidationError(f'Неподходящее имя {value}.'
                                              'Попробуйте выбрать другое.')
        if len(value) > MAX_USERNAME_FIELD_LENGHT:
            raise serializers.ValidationError(
                f'Имя {value} превышает допустимую'
                'длину в {MAX_USERNAME_FIELD_LENGHT} символов')
        if not re.match(USERNAME_SYMBOLS, value):
            raise serializers.ValidationError('Недопустимые символы в имени '
                                              f'{value}')
        if User.objects.filter(username=value).exists():
            raise serializers.ValidationError('Пользователь с таким именем'
                                              ' уже зарегистрирован в системе')
        return value

    def validate_email(self, value):
        if len(value) > MAX_EMAIL_FIELD_LENGHT:
            raise serializers.ValidationError(
                f'Почта {value} превышает допустимую'
                'длину в {MAX_EMAIL_FIELD_LENGHT} символов')
        if User.objects.filter(email=value).exists():
            raise serializers.ValidationError('Пользователь с такой почтой'
                                              ' уже зарегистрирован в системе')
        return value


class TokenSerializer(serializers.Serializer):
    """
    Сериализатор для выдачи токена зарегистрированному пользователю.
    Валидация полей confirmation_code и username.
    """
    confirmation_code = serializers.CharField(max_length=MAX_CODE_LENGHT)
    username = serializers.CharField()

    def validate_username(self, value):
        if User.objects.filter(username=value).exists():
            return value
        raise serializers.ValidationError(f'Пользователь {value} не найден',
                                          code='user not found')

    def validate_confirmation_code(self, value):
        session_confirmation_code = self.context[
            'request'].session.get('confirmation_code')
        if value != session_confirmation_code:
            raise serializers.ValidationError('Неправильный код')
        return value


class UserSerializer(serializers.ModelSerializer):
    """
    Сериализатор для эндпоинта users.
    Валидация полей role и username.
    """
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
        if not re.match(USERNAME_SYMBOLS, value):
            raise serializers.ValidationError()
        return value

    def validate_role(self, value):
        user = self.context['request'].user
        if user.role != value and not user.is_admin:
            raise serializers.ValidationError('Запрещено изменять права.')
        return value


class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = ['name', 'slug']


class GenreSerializer(serializers.ModelSerializer):
    """
    Сериализатор для модели Genre.
    Аналогично CategorySerializer.
    """
    class Meta:
        model = Genre
        exclude = ('id',)


class TitleReadSerializer(serializers.ModelSerializer):
    category = CategorySerializer(read_only=True)
    genre = GenreSerializer(
        read_only=True,
        many=True
    )
    rating = serializers.IntegerField(read_only=True)

    class Meta:
        fields = '__all__'
        model = Title


class TitleWriteSerializer(serializers.ModelSerializer):
    category = serializers.SlugRelatedField(
        queryset=Category.objects.all(),
        slug_field='slug'
    )
    genre = serializers.SlugRelatedField(
        queryset=Genre.objects.all(),
        slug_field='slug',
        many=True
    )

    class Meta:
        fields = '__all__'
        model = Title


class ReviewSerializer(serializers.ModelSerializer):
    title = serializers.SlugRelatedField(
        slug_field='name',
        read_only=True
    )
    author = serializers.SlugRelatedField(
        slug_field='username',
        read_only=True
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
        if (
            request.method == 'POST'
            and Review.objects.filter(title=title, author=author).exists()
        ):
            raise ValidationError('Может существовать только один отзыв!')
        return data

    class Meta:
        fields = '__all__'
        model = Review


class CommentSerializer(serializers.ModelSerializer):
    author = serializers.SlugRelatedField(
        slug_field='username',
        read_only=True
    )

    class Meta:
        model = Comment
        fields = ('id', 'text', 'author', 'pub_date')