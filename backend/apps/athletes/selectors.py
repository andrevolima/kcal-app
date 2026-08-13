from .models import Athlete


def get_accessible_athletes(*, user):
    queryset = Athlete.objects.select_related('user', 'nutritionist')
    if user.role == user.Role.NUTRITIONIST:
        return queryset.filter(nutritionist=user)
    if user.role == user.Role.ATHLETE:
        return queryset.filter(user=user)
    return queryset.none()


def get_nutritionist_athletes(*, nutritionist):
    return get_accessible_athletes(user=nutritionist).filter(
        nutritionist=nutritionist
    )
