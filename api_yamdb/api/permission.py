from rest_framework import permissions
from rest_framework.permissions import BasePermission


class IsAuthorOrModeratorOrAdmin(BasePermission):

    def has_object_permission(self, request, view, obj):
        return (
            request.method in permissions.SAFE_METHODS
            or obj.author == request.user
            or request.user.is_admin
            or request.user.is_moderator
        )


class IsActionAllowed(permissions.BasePermission):
    """Разрешения для действий в зависимости от типа запроса."""

    def has_permission(self, request, view):
        if view.action in ['list', 'retrieve']:
            return True

        if view.action == 'partial_update':
            return request.user and (
                request.user == view.get_object().author
                or request.user.is_staff
                or getattr(request.user, 'is_moderator', False)
            )
        return request.user and request.user.is_authenticated
