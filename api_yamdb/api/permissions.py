from rest_framework.permissions import BasePermission


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
