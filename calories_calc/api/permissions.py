from rest_framework import permissions


class AdminOrReadOnly(permissions.BasePermission):

    def has_permission(self, request, view):
        return (
            request.method in permissions.SAFE_METHODS or
            request.user.is_staff
        )


class AccessForUser(permissions.BasePermission):

    def has_object_permission(self, request, view, obj):
        return obj.user == request.user
