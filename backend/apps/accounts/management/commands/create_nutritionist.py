import getpass

from django.contrib.auth import get_user_model
from django.contrib.auth.password_validation import validate_password
from django.core.exceptions import ValidationError
from django.core.management.base import BaseCommand, CommandError
from django.db import IntegrityError


class Command(BaseCommand):
    help = 'Create a regular nutritionist application user.'

    def add_arguments(self, parser):
        parser.add_argument('--email', required=True)
        parser.add_argument('--first-name', default='')
        parser.add_argument('--last-name', default='')

    def handle(self, *args, **options):
        user_model = get_user_model()
        email = user_model.objects.normalize_email(options['email'])

        if user_model.objects.filter(email__iexact=email).exists():
            raise CommandError('A user with this email already exists.')

        password = getpass.getpass('Password: ')
        password_confirmation = getpass.getpass('Password (again): ')
        if password != password_confirmation:
            raise CommandError('Passwords do not match.')

        candidate = user_model(
            email=email,
            first_name=options['first_name'],
            last_name=options['last_name'],
            role=user_model.Role.NUTRITIONIST,
            is_active=True,
            is_staff=False,
            is_superuser=False,
        )
        try:
            validate_password(password, user=candidate)
        except ValidationError as exc:
            raise CommandError('Password validation failed: ' + ' '.join(exc.messages)) from exc

        try:
            user = user_model.objects.create_user(
                email=email,
                password=password,
                first_name=options['first_name'],
                last_name=options['last_name'],
                role=user_model.Role.NUTRITIONIST,
                is_active=True,
                is_staff=False,
                is_superuser=False,
            )
        except (IntegrityError, ValidationError) as exc:
            raise CommandError('Unable to create nutritionist with this email.') from exc

        self.stdout.write(
            self.style.SUCCESS(f'Nutritionist created successfully: {user.email}')
        )
