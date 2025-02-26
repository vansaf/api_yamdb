from django.shortcuts import get_object_or_404

from django_filters.rest_framework import DjangoFilterBackend

from rest_framework import (
    filters,
    generics,
    permissions,
    serializers,
    status,
    views,
    viewsets,
)
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from rest_framework_simplejwt.tokens import AccessToken

from reviews.models import Category, Genre, Title, Review, Comment, User
from .pagination import CustomPagination
from .permissions import (IsAdminIsModeratorIsAuthorOrReadOnly,
                          IsAdminOrReadOnly,
                          IsAdmin)
from .serializers import (
    CategorySerializer,
    CommentSerializer,
    GenreSerializer,
    ReviewSerializer,
    SignUpSerializer,
    TokenSerializer,
    TitleSerializer,
    UserSerializer
)
from .utils import generate_confirmation_code, send_confirmation_code


class SignUpView(generics.CreateAPIView):
    serializer_class = SignUpSerializer
    permission_classes = (permissions.AllowAny,)

    def post(self, request):
        email = request.data.get('email')
        username = request.data.get('username')

        if User.objects.filter(username=username, email=email).exists():
            confirmation_code = generate_confirmation_code()
            request.session['confirmation_code'] = confirmation_code
            send_confirmation_code(email, confirmation_code)
            return Response({
                'email': email,
                'username': username
            }, status=status.HTTP_200_OK)
        serializer = SignUpSerializer(data=request.data)
        if serializer.is_valid():
            user = serializer.save()
            confirmation_code = generate_confirmation_code()
            request.session['confirmation_code'] = confirmation_code
            send_confirmation_code(user.email, confirmation_code)
            return Response({
                'email': email,
                'username': username
            }, status=status.HTTP_200_OK)
        else:
            return Response(serializer.errors,
                            status=status.HTTP_400_BAD_REQUEST)


class TokenView(views.APIView):
    serializer_class = TokenSerializer
    permission_classes = (permissions.AllowAny,)

    def post(self, request):
        serializer = TokenSerializer(data=request.data,
                                     context={'request': request})
        if serializer.is_valid():
            username = serializer.validated_data['username']
            user = User.objects.get(username=username)
            token = AccessToken.for_user(user)
            return Response({'token': str(token)}, status=status.HTTP_200_OK)
        errors = serializer.errors
        if 'username' in errors and errors['username'][0].code == 'user not found':
            return Response(errors, status=status.HTTP_404_NOT_FOUND)
        return Response(errors, status=status.HTTP_400_BAD_REQUEST)


class UserViewSet(viewsets.ModelViewSet):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = (IsAdmin,)
    lookup_field = 'username'
    http_method_names = ['get', 'post', 'patch', 'delete']
    filter_backends = (filters.SearchFilter,)
    search_fields = ('username',)

    @action(detail=False,
            methods=['get', 'patch'],
            permission_classes=(IsAuthenticated,))
    def me(self, request):
        if request.method == 'GET':
            serializer = self.get_serializer(instance=request.user)
            return Response(serializer.data)

        if request.method == 'PATCH':
            serializer = self.get_serializer(
                data=request.data,
                instance=request.user,
                partial=True)
            serializer.is_valid(raise_exception=True)
            serializer.save()
            return Response(serializer.data)


class CategoryViewSet(viewsets.ModelViewSet):
    """
    ViewSet для работы с категориями (Category).
    Наследуется от ModelViewSet,
    который предоставляет стандартные действия:
    list(), create(), retrieve(), update(), partial_update(), destroy().
    """
    queryset = Category.objects.all()  # Указываем, какие данные обрабатываем
    serializer_class = CategorySerializer  # Какой сериализатор использовать
    permission_classes = (IsAdminOrReadOnly,)
    filter_backends = (filters.SearchFilter,)
    search_fields = ('name',)
    lookup_field = 'slug'


class GenreViewSet(viewsets.ModelViewSet):
    """
    ViewSet для работы с жанрами (Genre).
    Аналогично CategoryViewSet.
    """
    queryset = Genre.objects.all()
    serializer_class = GenreSerializer
    permission_classes = (IsAdminOrReadOnly,)
    filter_backends = (filters.SearchFilter,)
    search_fields = ('name',)
    lookup_field = 'slug'


class TitleViewSet(viewsets.ModelViewSet):
    """
    ViewSet для работы с произведениями (Title).
    """
    queryset = Title.objects.all()
    serializer_class = TitleSerializer
    permission_classes = (IsAdminOrReadOnly,)


class ReviewsViewSet(viewsets.ModelViewSet):
    """
    ViewSet для работы с отзывами (Reviews).
    """
    queryset = Review.objects.all()
    serializer_class = ReviewSerializer
    permission_classes = (IsAdminIsModeratorIsAuthorOrReadOnly,)
    pagination_class = CustomPagination
    filter_backends = (DjangoFilterBackend, filters.SearchFilter)
    filterset_fields = ('pub_date', 'score')
    search_fields = ('author', )

    def get_queryset(self):
        """Фильтрует отзывы по ID произведения."""
        title_id = self.kwargs.get('title_id')
        get_object_or_404(Title, id=title_id)
        return Review.objects.filter(title_id=title_id)

    def perform_create(self, serializer):
        """Создание отзыва с ограничением: один пользователь — один отзыв"""
        title_id = self.kwargs.get('title_id')
        user = self.request.user

        get_object_or_404(Title, id=title_id)

        review, created = Review.objects.get_or_create(
            title_id=title_id,
            author=user,
            defaults=serializer.validated_data
        )

        if not created:
            raise serializers.ValidationError(
                'Вы уже оставили отзыв на это произведение.'
            )

        serializer.instance = review

    def partial_update(self, request, *args, **kwargs):
        """Частичное обновление отзыва (PATCH)."""
        title_id = self.kwargs.get('title_id')
        get_object_or_404(Title, id=title_id)

        return super().partial_update(request, *args, **kwargs)

    def destroy(self, request, *args, **kwargs):
        """Удаление отзыва по ID."""
        title_id = self.kwargs.get('title_id')
        get_object_or_404(Title, id=title_id)

        get_object_or_404(Review, id=kwargs.get('review_id'))
        return super().destroy(request, *args, **kwargs)


class CommentsViewSet(viewsets.ModelViewSet):
    """
    ViewSet для работы с коментариями (Comments).
    """
    queryset = Comment.objects.all()
    serializer_class = CommentSerializer
    permission_classes = (IsAdminIsModeratorIsAuthorOrReadOnly,)
    pagination_class = CustomPagination
    filter_backends = (DjangoFilterBackend, filters.SearchFilter)
    filterset_fields = ('pub_date')
    search_fields = ('author',)

    def get_queryset(self):
        """Фильтрует отзывы по ID произведения."""
        comment_id = self.kwargs.get('comment_id')
        get_object_or_404(Comment, id=comment_id)
        return Comment.objects.filter(comment_id=comment_id)

    def perform_create(self, serializer):
        """Создание отзыва с ограничением: один пользователь — один отзыв"""
        comment_id = self.kwargs.get('comment_id')
        user = self.request.user

        get_object_or_404(Comment, id=comment_id)

        comment, created = Comment.objects.get_or_create(
            comment_id=comment_id,
            author=user,
            defaults=serializer.validated_data
        )

        if not created:
            raise serializers.ValidationError(
                'Вы уже оставили отзыв на это произведение.'
            )

        serializer.instance = comment

    def partial_update(self, request, *args, **kwargs):
        """Частичное обновление отзыва (PATCH)."""
        comment_id = self.kwargs.get('comment_id')
        get_object_or_404(Comment, id=comment_id)

        return super().partial_update(request, *args, **kwargs)

    def destroy(self, request, *args, **kwargs):
        """Удаление отзыва по ID."""
        comment_id = self.kwargs.get('comment_id')
        get_object_or_404(Comment, id=comment_id)

        get_object_or_404(Comment, id=kwargs.get('comment_id'))
        return super().destroy(request, *args, **kwargs)
