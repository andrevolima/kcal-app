from django.contrib.auth.models import AbstractUser
from django.db import models
from django.db.models.functions import Lower

from .managers import UserManager


class User(AbstractUser):
    class Role(models.TextChoices):
        NUTRITIONIST = 'nutritionist', 'Nutritionist'
        ATHLETE = 'athlete', 'Athlete'

    username = None
    email = models.EmailField(unique=True)
    role = models.CharField(max_length=20, choices=Role.choices)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['role']

    objects = UserManager()

    class Meta:
        constraints = [
            models.UniqueConstraint(
                Lower('email'),
                name='accounts_user_email_ci_unique',
            ),
            models.CheckConstraint(
                condition=models.Q(role__in=('nutritionist', 'athlete')),
                name='accounts_user_valid_role',
            ),
        ]

    def clean(self):
        super().clean()
        self.email = self.__class__.objects.normalize_email(self.email)

    def __str__(self):
        return self.email
