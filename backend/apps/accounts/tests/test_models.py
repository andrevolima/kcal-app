from django.contrib.auth import authenticate, get_user_model
from django.contrib import admin
from django.core.exceptions import ValidationError
from django.db import IntegrityError, transaction
from django.test import TestCase


class UserModelTests(TestCase):
    def setUp(self):
        self.user_model = get_user_model()

    def test_create_user_with_email_and_hashed_password(self):
        user = self.user_model.objects.create_user(
            email='USER@Example.COM',
            password='a-strong-test-password',
            role=self.user_model.Role.NUTRITIONIST,
        )

        self.assertEqual(user.email, 'user@example.com')
        self.assertTrue(user.check_password('a-strong-test-password'))
        self.assertNotEqual(user.password, 'a-strong-test-password')

    def test_email_is_unique_case_insensitively(self):
        self.user_model.objects.create_user(
            email='user@example.com',
            password='a-strong-test-password',
            role=self.user_model.Role.ATHLETE,
        )

        with self.assertRaises(ValidationError):
            self.user_model.objects.create_user(
                email='USER@example.com',
                password='another-strong-password',
                role=self.user_model.Role.ATHLETE,
            )

    def test_database_rejects_duplicate_normalized_email(self):
        self.user_model.objects.create_user(
            email='user@example.com',
            password='a-strong-test-password',
            role=self.user_model.Role.ATHLETE,
        )

        with self.assertRaises(IntegrityError), transaction.atomic():
            self.user_model.objects.create(
                email='USER@example.com',
                password='not-used',
                role=self.user_model.Role.ATHLETE,
            )

    def test_supported_roles(self):
        nutritionist = self.user_model.objects.create_user(
            email='nutritionist@example.com',
            password='a-strong-test-password',
            role=self.user_model.Role.NUTRITIONIST,
        )
        athlete = self.user_model.objects.create_user(
            email='athlete@example.com',
            password='a-strong-test-password',
            role=self.user_model.Role.ATHLETE,
        )

        self.assertEqual(nutritionist.role, 'nutritionist')
        self.assertEqual(athlete.role, 'athlete')

    def test_invalid_role_is_rejected(self):
        with self.assertRaises(ValidationError):
            self.user_model.objects.create_user(
                email='user@example.com',
                password='a-strong-test-password',
                role='invalid',
            )

    def test_database_rejects_invalid_role(self):
        with self.assertRaises(IntegrityError), transaction.atomic():
            self.user_model.objects.create(
                email='user@example.com',
                password='not-used',
                role='invalid',
            )

    def test_create_superuser(self):
        user = self.user_model.objects.create_superuser(
            email='admin@example.com',
            password='a-strong-test-password',
            role=self.user_model.Role.NUTRITIONIST,
        )

        self.assertTrue(user.is_staff)
        self.assertTrue(user.is_superuser)
        self.assertTrue(user.is_active)

    def test_authentication_uses_email(self):
        user = self.user_model.objects.create_user(
            email='user@example.com',
            password='a-strong-test-password',
            role=self.user_model.Role.ATHLETE,
        )

        authenticated = authenticate(
            email='USER@example.com', password='a-strong-test-password'
        )

        self.assertEqual(authenticated, user)

    def test_inactive_user_cannot_authenticate(self):
        self.user_model.objects.create_user(
            email='inactive@example.com',
            password='a-strong-test-password',
            role=self.user_model.Role.ATHLETE,
            is_active=False,
        )

        authenticated = authenticate(
            email='inactive@example.com', password='a-strong-test-password'
        )

        self.assertIsNone(authenticated)

    def test_custom_user_is_registered_in_admin(self):
        self.assertIn(self.user_model, admin.site._registry)
