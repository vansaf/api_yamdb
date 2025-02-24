"""
В этом файле описываются сериализаторы,
которые превращают объекты моделей в формат JSON (и обратно),
чтобы их можно было отправлять/получать по API.
"""

# DRF-библиотека для сериализации
from rest_framework import serializers
# Импорт моделей
from reviews.models import Category, Genre, Title, Review, Comment, User



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


class ReviewSerializer(serializers.ModelSerializer):
    """Сериализатор модели отзывов"""
    author = serializers.SlugRelatedField(
        slug_field='username',
        read_only=True
    )

    class Meta:
        model = Review
        fields = '__all__'


class CommentSerializer(serializers.ModelSerializer):
    """Сериализатор модели комментариев"""
    author = serializers.SlugRelatedField(
        slug_field='username',
        read_only=True
    )

    class Meta:
        model = Comment
        fields = '__all__'


class SignUpSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ('email', 'username')


#class GetTokenSerializer(serializers.ModelSerializer):
#    username = serializers.Charfield()
#    confirmation_code = serializers.Charfield()
