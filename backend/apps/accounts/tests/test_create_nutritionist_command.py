from io import StringIO
from unittest.mock import patch

from django.contrib.auth import get_user_model
from django.core.management import call_command
from django.core.management.base import CommandError
from django.test import TestCase
from rest_framework import status
from rest_framework.test import APIClient

from apps.accounts.services import create_token_pair


class CreateNutritionistCommandTests(TestCase):
    password = 'Safe-command-password-2026!'

    def run_command(self, *, email='NUTRITIONIST@Example.COM', passwords=None):
        stdout = StringIO()
        password_values = passwords or [self.password, self.password]
        with patch(
            'apps.accounts.management.commands.create_nutritionist.getpass.getpass',
            side_effect=password_values,
        ) as password_prompt:
            call_command(
                'create_nutritionist',
                email=email,
                first_name='Nome',
                last_name='Sobrenome',
                stdout=stdout,
            )
        return stdout.getvalue(), password_prompt

    def test_creates_regular_nutritionist_with_normalized_email_and_hashed_password(self):
        output, password_prompt = self.run_command()

        user = get_user_model().objects.get(email='nutritionist@example.com')
        self.assertEqual(user.role, user.Role.NUTRITIONIST)
        self.assertTrue(user.is_active)
        self.assertFalse(user.is_staff)
        self.assertFalse(user.is_superuser)
        self.assertTrue(user.check_password(self.password))
        self.assertNotEqual(user.password, self.password)
        self.assertEqual(password_prompt.call_count, 2)
        self.assertNotIn(self.password, output)

    def test_duplicate_email_is_rejected_before_password_prompt(self):
        user_model = get_user_model()
        user_model.objects.create_user(
            email='nutritionist@example.com',
            password=self.password,
            role=user_model.Role.NUTRITIONIST,
        )

        with patch(
            'apps.accounts.management.commands.create_nutritionist.getpass.getpass'
        ) as password_prompt:
            with self.assertRaisesMessage(
                CommandError, 'A user with this email already exists.'
            ):
                call_command(
                    'create_nutritionist',
                    email='NUTRITIONIST@example.com',
                )

        password_prompt.assert_not_called()

    def test_invalid_password_is_rejected(self):
        with self.assertRaisesMessage(CommandError, 'Password validation failed'):
            self.run_command(passwords=['123', '123'])

        self.assertFalse(get_user_model().objects.exists())

    def test_password_confirmation_must_match(self):
        with self.assertRaisesMessage(CommandError, 'Passwords do not match.'):
            self.run_command(passwords=[self.password, 'different-password'])

        self.assertFalse(get_user_model().objects.exists())

    def test_created_nutritionist_authenticates_with_existing_jwt_and_me_endpoint(self):
        self.run_command()
        user, access, _refresh = create_token_pair(
            email='nutritionist@example.com',
            password=self.password,
        )
        client = APIClient()
        client.credentials(HTTP_AUTHORIZATION=f'Bearer {access}')

        response = client.get('/api/v1/auth/me/')

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['id'], user.id)
        self.assertEqual(response.data['email'], 'nutritionist@example.com')
        self.assertEqual(response.data['role'], user.Role.NUTRITIONIST)
