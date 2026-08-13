from django.conf import settings
from django.core.exceptions import ValidationError
from django.db import models

from apps.accounts.models import User


class Athlete(models.Model):
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='athlete_profile',
    )
    nutritionist = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.PROTECT,
        related_name='athletes',
    )
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        constraints = [
            models.CheckConstraint(
                condition=~models.Q(user=models.F('nutritionist')),
                name='athlete_user_differs_from_nutritionist',
            ),
        ]
        ordering = ('user__first_name', 'user__last_name', 'id')

    def __str__(self):
        return self.user.email

    def clean(self):
        super().clean()
        errors = {}
        if self.user_id and self.user.role != User.Role.ATHLETE:
            errors['user'] = 'The athlete user must have the athlete role.'
        if self.nutritionist_id and self.nutritionist.role != User.Role.NUTRITIONIST:
            errors['nutritionist'] = 'The responsible user must have the nutritionist role.'
        if errors:
            raise ValidationError(errors)
