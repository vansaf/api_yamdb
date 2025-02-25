"""
Файл маршрутизации (urls) внутри приложения `api`.
Здесь мы регистрируем ViewSet'ы (классы для обработки запросов),
которые будут отвечать на запросы к моделям Category, Genre, Title и т.д.
"""

# Функции для описания маршрутов
from django.urls import include, path
from rest_framework import routers
from rest_framework.routers import DefaultRouter

from .views import (
    CategoryViewSet,
    GenreViewSet,
    TitleViewSet,
    SignUpView,
    TokenView,
    ReviewsViewSet,
    CommentsViewSet
)

app_name = 'api'
router_v1 = DefaultRouter()


# Регистрируем ViewSet для категорий под адресом "categories".
# Для CategoryViewSet будут созданы пути:
# GET /categories/, POST /categories/, GET /categories/{id}/,
# PATCH /categories/{id}/, DELETE /categories/{id}/
router_v1.register('categories', CategoryViewSet, basename='categories')

# Регистрируем ViewSet для жанров под адресом "genres".
router_v1.register('genres', GenreViewSet, basename='genres')

# Регистрируем ViewSet для произведений под адресом "titles".
router_v1.register('titles', TitleViewSet, basename='titles')

# Регистрируем ViewSet для произведений под адресом "reviews".
router_v1.register('reviews', ReviewsViewSet, basename='reviews')

# Регистрируем ViewSet для произведений под адресом "comments".
router_v1.register('comments', CommentsViewSet)



# Подключаем все маршруты роутера под префиксом /v1/.
# То есть, всё, что начинается на "/v1/..." в адресе,
# будет обрабатываться соответствующими ViewSet'ами.
urlpatterns = [
    path('v1/', include(router_v1.urls)),
    path('v1/auth/signup/', SignUpView.as_view(), name='signup'),
    path('v1/auth/token/', TokenView.as_view(), name='token'),
]
