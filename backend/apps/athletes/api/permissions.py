from rest_framework.permissions import BasePermission

from apps.accounts.models import User


class IsNutritionist(BasePermission):
    def has_permission(self, request, view):
        return (
            request.user.is_authenticated
            and request.user.role == User.Role.NUTRITIONIST
        )


class CanAccessAthlete(BasePermission):
    def has_permission(self, request, view):
        return request.user.is_authenticated

    def has_object_permission(self, request, view, athlete):
        if request.user.role == User.Role.NUTRITIONIST:
            return athlete.nutritionist_id == request.user.id
        if request.user.role == User.Role.ATHLETE:
            return request.method == 'GET' and athlete.user_id == request.user.id
        return False
