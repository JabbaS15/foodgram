from rest_framework.permissions import SAFE_METHODS, BasePermission


class ReadOnly(BasePermission):
    """Только чтение"""
    def has_permission(self, request, view):
        return request.method in SAFE_METHODS


class UserOnly(BasePermission):
    """Доступ только для пользователя."""
    def has_permission(self, request, view):
        return request.user.is_user


class AdminOnly(BasePermission):
    """Доступ только для Админа."""
    def has_permission(self, request, view):
        return (request.user.is_authenticated
                and request.user.is_superuser)


class AuthorOrReadOnly(BasePermission):
    """Доступ для автора или только чтение"""
    def has_permission(self, request, view):
        return request.method in SAFE_METHODS or request.user.is_authenticated

    def has_object_permission(self, request, view, obj):
        return request.method in SAFE_METHODS or obj.author == request.user
