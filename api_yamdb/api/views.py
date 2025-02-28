from django.shortcuts import get_object_or_404
from django.db.models import Avg
from django_filters.rest_framework import DjangoFilterBackend

from rest_framework import (
    filters,
    generics,
    permissions,
    status,
    views,
    viewsets
)
from rest_framework.decorators import action
from rest_framework.permissions import (
    IsAuthenticated, IsAuthenticatedOrReadOnly
)
from rest_framework.response import Response
from rest_framework_simplejwt.tokens import AccessToken

from reviews.models import (
    Category,
    Comment,
    Genre,
    Review,
    Title,
    User)
from .permissions import (
    IsAdminIsModeratorIsAuthorOrReadOnly,
    IsAdminOrReadOnly,
    IsAdmin
)
from .filters import TitleFilter
from .serializers import (
    CategorySerializer,
    CommentSerializer,
    GenreSerializer,
    ReviewSerializer,
    SignUpSerializer,
    TokenSerializer,
    TitleReadSerializer,
    TitleWriteSerializer,
    UserSerializer
)
from .utils import generate_confirmation_code, send_confirmation_code


class SignUpView(generics.CreateAPIView):
    """
    CreateAPIView для регистрации пользователей в системе.
    """

    serializer_class = SignUpSerializer
    permission_classes = (permissions.AllowAny,)

    def post(self, request):
        email = request.data.get('email')
        username = request.data.get('username')
        serializer = SignUpSerializer(data=request.data)

        if (User.objects.filter(username=username, email=email).exists()
                or serializer.is_valid()):
            confirmation_code = generate_confirmation_code()
            request.session['confirmation_code'] = confirmation_code
            send_confirmation_code(email, confirmation_code)
            if serializer.is_valid():
                serializer.save()
            return Response({'email': email, 'username': username},
                            status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class TokenView(views.APIView):
    """
    APIView для создания токена зарегистрированному пользователю.
    """

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
        if ('username' in errors
                and errors['username'][0].code == 'user not found'):
            return Response(errors, status=status.HTTP_404_NOT_FOUND)
        return Response(errors, status=status.HTTP_400_BAD_REQUEST)


class UserViewSet(viewsets.ModelViewSet):
    """
    ViewSet для работы с моделью User.
    """

    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = (IsAdmin,)
    lookup_field = 'username'
    http_method_names = ['get', 'post', 'patch', 'delete']
    filter_backends = (filters.SearchFilter,)
    search_fields = ('username',)

    @action(detail=False, methods=['get', 'patch'],
            permission_classes=(IsAuthenticated,))
    def me(self, request):
        if request.method == 'GET':
            serializer = self.get_serializer(instance=request.user)
            return Response(serializer.data)

        serializer = self.get_serializer(
            data=request.data, instance=request.user, partial=True
        )
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data)


class BaseCategoryGenreViewSet(viewsets.ModelViewSet):
    """
    Базовый ViewSet для управления категориями и жанрами.
    """
    permission_classes = (IsAdminOrReadOnly,)
    filter_backends = (filters.SearchFilter,)
    search_fields = ('name',)
    lookup_field = 'slug'
    http_method_names = ['get', 'post', 'delete']

    def retrieve(self, request, *args, **kwargs):
        return Response(status=status.HTTP_405_METHOD_NOT_ALLOWED)


class CategoryViewSet(BaseCategoryGenreViewSet):
    """
    ViewSet для управления категориями произведений.
    """
    queryset = Category.objects.all()
    serializer_class = CategorySerializer


class GenreViewSet(BaseCategoryGenreViewSet):
    """
    ViewSet для управления жанрами произведений.
    """
    queryset = Genre.objects.all()
    serializer_class = GenreSerializer


class TitleViewSet(viewsets.ModelViewSet):
    """
    ViewSet для работы с произведениями (Title).
    """

    queryset = Title.objects.annotate(rating=Avg('reviews__score')).all()
    permission_classes = (IsAdminOrReadOnly,)
    filter_backends = (DjangoFilterBackend,)
    filterset_class = TitleFilter
    http_method_names = ['get', 'post', 'patch', 'delete']

    def get_serializer_class(self):
        if self.action in ('list', 'retrieve'):
            return TitleReadSerializer
        return TitleWriteSerializer


class ReviewsViewSet(viewsets.ModelViewSet):
    """
    ViewSet для управления отзывами.
    """

    queryset = Review.objects.all()
    serializer_class = ReviewSerializer
    permission_classes = (
        IsAuthenticatedOrReadOnly, IsAdminIsModeratorIsAuthorOrReadOnly
    )
    http_method_names = ['get', 'post', 'patch', 'delete']

    def perform_create(self, serializer):
        serializer.save(
            author=self.request.user, title_id=self.kwargs.get('title_id')
        )

    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        self.perform_destroy(instance)
        return Response(status=status.HTTP_204_NO_CONTENT)


class CommentsViewSet(viewsets.ModelViewSet):
    """
    ViewSet для управления комментариями к отзывам.
    """

    queryset = Comment.objects.all()
    serializer_class = CommentSerializer
    permission_classes = (
        IsAuthenticatedOrReadOnly, IsAdminIsModeratorIsAuthorOrReadOnly
    )
    http_method_names = ['get', 'post', 'patch', 'delete']

    def perform_create(self, serializer):
        review = get_object_or_404(Review, id=self.kwargs.get('review_id'))
        serializer.save(author=self.request.user, review=review)
