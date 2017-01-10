from rest_framework import permissions

class IsCustomUserOwner(permissions.BasePermission):
    def has_object_permission(self, request, view, customuser):
        if request.user:
            return customuser == request.user
        return False
