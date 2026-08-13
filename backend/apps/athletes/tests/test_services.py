from django.core.exceptions import ValidationError as DjangoValidationError
from django.test import TestCase
from rest_framework.exceptions import PermissionDenied

from apps.accounts.models import User
from apps.athletes.models import Athlete
from apps.athletes.services import create_athlete, deactivate_athlete, update_athlete


class AthleteServiceTests(TestCase):
    def setUp(self):
        self.nutritionist = User.objects.create_user(
            email='nutritionist@example.com',
            password='test-password',
            role=User.Role.NUTRITIONIST,
        )

    def test_create_athlete_builds_identity_and_profile_atomically(self):
        athlete = create_athlete(
            nutritionist=self.nutritionist,
            email='ATHLETE@Example.COM',
            first_name='Ada',
            last_name='Runner',
        )

        self.assertEqual(athlete.nutritionist, self.nutritionist)
        self.assertEqual(athlete.user.email, 'athlete@example.com')
        self.assertEqual(athlete.user.role, User.Role.ATHLETE)
        self.assertFalse(athlete.user.has_usable_password())
        self.assertTrue(athlete.is_active)

    def test_non_nutritionist_cannot_create_athlete(self):
        athlete_user = User.objects.create_user(
            email='existing@example.com',
            password='test-password',
            role=User.Role.ATHLETE,
        )

        with self.assertRaises(PermissionDenied):
            create_athlete(
                nutritionist=athlete_user,
                email='new@example.com',
            )
        self.assertFalse(User.objects.filter(email='new@example.com').exists())

    def test_model_rejects_users_with_incorrect_roles(self):
        another_nutritionist = User.objects.create_user(
            email='another@example.com',
            password='test-password',
            role=User.Role.NUTRITIONIST,
        )
        athlete = Athlete(
            user=another_nutritionist,
            nutritionist=self.nutritionist,
        )

        with self.assertRaises(DjangoValidationError):
            athlete.full_clean()

    def test_update_changes_only_permitted_identity_fields(self):
        athlete = create_athlete(
            nutritionist=self.nutritionist,
            email='athlete@example.com',
        )

        update_athlete(
            athlete=athlete,
            nutritionist=self.nutritionist,
            first_name='Updated',
            last_name='Name',
        )

        athlete.user.refresh_from_db()
        self.assertEqual(athlete.user.first_name, 'Updated')
        self.assertEqual(athlete.user.last_name, 'Name')
        self.assertEqual(athlete.user.email, 'athlete@example.com')

    def test_deactivation_preserves_user_and_authentication_state(self):
        athlete = create_athlete(
            nutritionist=self.nutritionist,
            email='athlete@example.com',
        )

        deactivate_athlete(athlete=athlete, nutritionist=self.nutritionist)

        athlete.refresh_from_db()
        athlete.user.refresh_from_db()
        self.assertFalse(athlete.is_active)
        self.assertTrue(athlete.user.is_active)
        self.assertTrue(Athlete.objects.filter(pk=athlete.pk).exists())
        self.assertTrue(User.objects.filter(pk=athlete.user_id).exists())
