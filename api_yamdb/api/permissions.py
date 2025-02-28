from rest_framework.permissions import BasePermission, SAFE_METHODS


class IsAdminIsModeratorIsAuthorOrReadOnly(BasePermission):
    """Класс проверки выполняется ли одно из четырех условий:
    - администратор
    - модератор
    - автор объекта
    - действия с объектом запрошены только на чтение
    """

    def has_object_permission(self, request, view, obj):
        return (request.method in SAFE_METHODS
                or request.user.is_admin
                or request.user.is_moderator
                or obj.author == request.user
                )


class IsAdminOrReadOnly(BasePermission):
    """Класс проверки является ли пользователь администраторм.
    Безопасные методы доступны всем пользователям.
    Права на изменение только у адмнистратора.
    """

    def has_permission(self, request, view):
        return (request.user.is_admin if request.user.is_authenticated
                else request.method in SAFE_METHODS)


class IsAdmin(BasePermission):
    """Класс проверки является ли пользователь администратором.
    Всем остальным пользователям доступ запрещен.
    """

    def has_permission(self, request, view):
        if request.user.is_authenticated:
            return request.user.is_admin or request.user.is_superuser
