from rest_framework.permissions import BasePermission, SAFE_METHODS


class CustomReviewAndCommentPermission(BasePermission):

    def has_permission(self, request, view):
        if view.action in ['list', 'retrieve']:
            return True
        if view.action == 'create':
            return request.user and request.user.is_authenticated
        return True

    def has_object_permission(self, request, view, obj):
        if view.action in ['retrieve']:
            return True
        if view.action in ['partial_update', 'destroy']:
            return request.user == obj.author or request.user.is_staff
        return False


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
    """Класс проверки выполняется ли одно из двух условий:
    - является ли пользователь администратором
    - действия с объектом запрошены только на чтение для
    авторизованного пользователя
    """
    def has_object_permission(self, request, view):
        return (request.method in SAFE_METHODS
                and request.user.is_authenticated
                or request.user.is_admin)


class IsAdmin(BasePermission):
    """Класс проверки является ли пользователь администратором."""
    def has_object_permission(self, request, view):
        return request.user.is_admin
