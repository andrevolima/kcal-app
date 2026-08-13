from django.core.exceptions import ValidationError as DjangoValidationError
from django.db import IntegrityError, transaction
from rest_framework.exceptions import PermissionDenied, ValidationError

from apps.accounts.models import User

from .models import Athlete


def _require_nutritionist(user):
    if user.role != User.Role.NUTRITIONIST:
        raise PermissionDenied('Only nutritionists can manage athletes.')


@transaction.atomic
def create_athlete(*, nutritionist, email, first_name='', last_name=''):
    _require_nutritionist(nutritionist)
    try:
        user = User.objects.create_user(
            email=email,
            password=None,
            role=User.Role.ATHLETE,
            first_name=first_name,
            last_name=last_name,
        )
    except DjangoValidationError as exc:
        raise ValidationError(exc.message_dict) from exc
    except IntegrityError as exc:
        raise ValidationError({'email': ['A user with this email already exists.']}) from exc

    athlete = Athlete(user=user, nutritionist=nutritionist)
    athlete.full_clean()
    athlete.save()
    return athlete


@transaction.atomic
def update_athlete(*, athlete, nutritionist, first_name=None, last_name=None):
    _require_nutritionist(nutritionist)
    if athlete.nutritionist_id != nutritionist.id:
        raise PermissionDenied('You cannot update this athlete.')

    user = athlete.user
    fields = []
    if first_name is not None:
        user.first_name = first_name
        fields.append('first_name')
    if last_name is not None:
        user.last_name = last_name
        fields.append('last_name')
    if fields:
        user.full_clean(exclude=('password',))
        user.save(update_fields=[*fields, 'updated_at'])
    return athlete


@transaction.atomic
def deactivate_athlete(*, athlete, nutritionist):
    _require_nutritionist(nutritionist)
    if athlete.nutritionist_id != nutritionist.id:
        raise PermissionDenied('You cannot deactivate this athlete.')
    if athlete.is_active:
        athlete.is_active = False
        athlete.save(update_fields=['is_active', 'updated_at'])
    return athlete
