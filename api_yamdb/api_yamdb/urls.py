"""
Главный файл маршрутизации (urls) проекта YaMDb.
Здесь указываются пути (path), по которым мы можем получить
доступ к функционалу всего приложения.
"""
"""YaMDb URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/3.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
# Функции для описания маршрутов
from django.urls import path, include
from django.views.generic import TemplateView

urlpatterns = [
    # URL админки Django: стандартный путь,
    # даёт доступ к встроенной админ-панели Django.
    path('admin/', admin.site.urls),

    # Подключаем все URL из приложения "api" под префиксом "api/".
    # То есть, всё, что начинается с "/api/" в браузере,
    # будет искать маршруты в файле api/urls.py
    path('api/', include('api.urls')),

    # Подключаем страницу redoc,
    # это документация в формате Redoc,
    # которая обычно хранится в шаблоне redoc.html
    path(
        'redoc/',
        TemplateView.as_view(template_name='redoc.html'),
        name='redoc'
    ),
]
