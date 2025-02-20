"""
Файл маршрутизации (urls) внутри приложения `api`.
Здесь мы регистрируем ViewSet'ы (классы для обработки запросов),
которые будут отвечать на запросы к моделям Category, Genre, Title и т.д.
"""

# Функции для описания маршрутов
from django.urls import path, include
# Роутер DRF для автоматического создания маршрутов
from rest_framework.routers import DefaultRouter
from .views import CategoryViewSet, GenreViewSet, TitleViewSet

# Создаём роутер - объект, который автоматически сгенерирует
# стандартные маршруты CRUD (Create, Read, Update, Delete)
# на основе наших ViewSet-классов.
router = DefaultRouter()

# Регистрируем ViewSet для категорий под адресом "categories".
# Для CategoryViewSet будут созданы пути:
# GET /categories/, POST /categories/, GET /categories/{id}/,
# PATCH /categories/{id}/, DELETE /categories/{id}/
router.register('categories', CategoryViewSet)

# Регистрируем ViewSet для жанров под адресом "genres".
router.register('genres', GenreViewSet)

# Регистрируем ViewSet для произведений под адресом "titles".
router.register('titles', TitleViewSet)

# Подключаем все маршруты роутера под префиксом /v1/.
# То есть, всё, что начинается на "/v1/..." в адресе,
# будет обрабатываться соответствующими ViewSet'ами.
urlpatterns = [
    path('v1/', include(router.urls)),
]
