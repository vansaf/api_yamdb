
"""
Главный файл маршрутизации (urls) проекта YaMDb.
Здесь указываются пути (path), по которым мы можем получить
доступ к функционалу всего приложения.
"""

# Функции для описания маршрутов
from django.contrib import admin
from django.urls import include, path

from django.views.generic import TemplateView

urlpatterns = [
    # URL админки Django: стандартный путь,
    # даёт доступ к встроенной админ-панели Django.
    path('admin/', admin.site.urls),
    # Подключаем все URL из приложения "api" под префиксом "api/".
    # То есть, всё, что начинается с "/api/" в браузере,
    # будет искать маршруты в файле api/urls.py
    # Подключаем страницу redoc,
    # это документация в формате Redoc,
    # которая обычно хранится в шаблоне redoc.html
    path('api/', include('api.urls')),
    path(
        'redoc/',
        TemplateView.as_view(template_name='redoc.html'),
        name='redoc'
    ),
]
