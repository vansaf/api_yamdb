"""
Файл маршрутизации (urls) внутри приложения `api`.
Здесь мы регистрируем ViewSet'ы (классы для обработки запросов),
которые будут отвечать на запросы к моделям Category, Genre, Title и т.д.
"""

# Функции для описания маршрутов
from django.urls import path, include
# Роутер DRF для автоматического создания маршрутов
from rest_framework import routers
from rest_framework.routers import DefaultRouter
from .views import (
    CategoryViewSet,
    GenreViewSet,
    TitleViewSet,
    SignUpView,
    ReviewsViewSet,
    CommentsViewSet
)

# Создаём роутер - объект, который автоматически сгенерирует
# стандартные маршруты CRUD (Create, Read, Update, Delete)
# на основе наших ViewSet-классов.

# Исправить route - привести к 1 константе
router = DefaultRouter()
app_name = 'api'
router_v1 = routers.DefaultRouter()


# Регистрируем ViewSet для категорий под адресом "categories".
# Для CategoryViewSet будут созданы пути:
# GET /categories/, POST /categories/, GET /categories/{id}/,
# PATCH /categories/{id}/, DELETE /categories/{id}/
router.register('categories', CategoryViewSet)

# Регистрируем ViewSet для жанров под адресом "genres".
router.register('genres', GenreViewSet)

# Регистрируем ViewSet для произведений под адресом "titles".
router.register('titles', TitleViewSet)

# Регистрируем ViewSet для произведений под адресом "reviews".
router.register('reviews', ReviewsViewSet)

# Регистрируем ViewSet для произведений под адресом "comments".
router.register('reviews', CommentsViewSet)
# Подключаем все маршруты роутера под префиксом /v1/.
# То есть, всё, что начинается на "/v1/..." в адресе,
# будет обрабатываться соответствующими ViewSet'ами.
urlpatterns = [
    path('v1/', include(router.urls)),
    path('v1/auth/signup/', SignUpView.as_view(), name='signup'),
    #path('v1/auth/token/', GetTokenView.as_view(), name='token'),
]

urlpatterns += router_v1.urls

# Пора ли раскомментировать?
# router_v1.register('v1/posts', PostViewSet, basename='posts')
# router_v1.register('v1/groups', GroupViewSet, basename='groups')
# router_v1.register('v1/follow', FollowView, basename='follow')
# router_v1.register(r'v1/posts/(?P<post_id>\d+)/comments',
#                    CommentViewSet, basename='comments')
