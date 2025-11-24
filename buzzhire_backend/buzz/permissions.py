from rest_framework import permissions

class IsAdmin(permissions.BasePermission):
    """
    Allows access only to users with role 'ADMIN'.
    """

    def has_permission(self, request, view):
        return bool(request.user and request.user.is_authenticated and request.user.role == 'ADMIN')


class IsSelfOrAdmin(permissions.BasePermission):
    """
    Object-level permission to only allow owners of an object to edit it.
    Admins can access any.
    Assumes view.get_object() returns a User or EmployeeProfile with .user.
    """

    def has_object_permission(self, request, view, obj):
        # If admin, allow
        if request.user and request.user.is_authenticated and request.user.role == 'ADMIN':
            return True

        # For User objects
        if hasattr(obj, 'id'):
            return obj.id == request.user.id

        # For Profile objects
        if hasattr(obj, 'user'):
            return obj.user.id == request.user.id

        return False
