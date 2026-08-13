import hashlib
import secrets
from datetime import timedelta

from django.conf import settings
from django.contrib.auth.password_validation import validate_password
from django.core.exceptions import ValidationError as DjangoValidationError
from django.db import transaction
from django.utils import timezone
from rest_framework.exceptions import PermissionDenied, ValidationError

from apps.accounts.models import User

from .models import Athlete, AthleteInvitation


def hash_invitation_token(token):
    return hashlib.sha256(token.encode('utf-8')).hexdigest()


def get_invitation_state(invitation):
    if invitation.used_at:
        return 'used'
    if invitation.revoked_at:
        return 'revoked'
    if invitation.expires_at <= timezone.now():
        return 'expired'
    if not invitation.athlete.is_active:
        return 'revoked'
    return 'valid'


def get_invitation_by_token(token, *, for_update=False):
    queryset = AthleteInvitation.objects.select_related('athlete__user')
    if for_update:
        queryset = queryset.select_for_update()
    return queryset.filter(token_hash=hash_invitation_token(token)).first()


@transaction.atomic
def create_invitation(*, athlete, nutritionist):
    athlete = Athlete.objects.select_for_update().select_related(
        'user', 'nutritionist'
    ).get(pk=athlete.pk)
    if nutritionist.role != User.Role.NUTRITIONIST:
        raise PermissionDenied('Only nutritionists can invite athletes.')
    if athlete.nutritionist_id != nutritionist.id:
        raise PermissionDenied('You cannot invite this athlete.')
    if not athlete.is_active:
        raise ValidationError({'athlete': ['Inactive athletes cannot be invited.']})
    if athlete.user.role != User.Role.ATHLETE:
        raise ValidationError({'athlete': ['The associated user is not an athlete.']})
    if athlete.user.has_usable_password():
        raise ValidationError(
            {'athlete': ['This athlete has already completed onboarding.']}
        )

    now = timezone.now()
    AthleteInvitation.objects.select_for_update().filter(
        athlete=athlete,
        used_at__isnull=True,
        revoked_at__isnull=True,
    ).update(revoked_at=now)

    raw_token = secrets.token_urlsafe(32)
    invitation = AthleteInvitation.objects.create(
        athlete=athlete,
        token_hash=hash_invitation_token(raw_token),
        expires_at=now + timedelta(hours=settings.ATHLETE_INVITATION_EXPIRY_HOURS),
    )
    return invitation, raw_token


@transaction.atomic
def activate_invitation(*, token, password, password_confirm):
    if password != password_confirm:
        raise ValidationError({'password_confirm': ['Passwords do not match.']})

    invitation = get_invitation_by_token(token, for_update=True)
    if invitation is None:
        raise ValidationError({'token': ['Invitation is invalid.']})

    state = get_invitation_state(invitation)
    if state != 'valid':
        raise ValidationError({'token': [f'Invitation is {state}.']})

    user = invitation.athlete.user
    try:
        validate_password(password, user=user)
    except DjangoValidationError as exc:
        raise ValidationError({'password': list(exc.messages)}) from exc

    user.set_password(password)
    user.full_clean()
    user.save(update_fields=['password', 'updated_at'])
    invitation.used_at = timezone.now()
    invitation.save(update_fields=['used_at'])
    return invitation
