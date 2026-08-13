from datetime import timedelta

from django.conf import settings
from django.core.cache import cache
from django.test import TestCase
from django.utils import timezone
from rest_framework import status
from rest_framework.exceptions import ValidationError
from rest_framework.settings import api_settings
from rest_framework.test import APIClient, APITestCase
from rest_framework.throttling import SimpleRateThrottle
from rest_framework_simplejwt.tokens import RefreshToken

from apps.accounts.models import User
from apps.athletes.invitations import (
    activate_invitation,
    create_invitation,
    get_invitation_by_token,
    get_invitation_state,
)
from apps.athletes.services import create_athlete


class InvitationServiceTests(TestCase):
    def setUp(self):
        self.nutritionist = User.objects.create_user(
            email='nutritionist@example.com',
            password='test-password',
            role=User.Role.NUTRITIONIST,
        )
        self.athlete = create_athlete(
            nutritionist=self.nutritionist,
            email='athlete@example.com',
        )

    def test_raw_token_is_not_stored(self):
        invitation, token = create_invitation(
            athlete=self.athlete,
            nutritionist=self.nutritionist,
        )

        self.assertNotEqual(invitation.token_hash, token)
        self.assertNotIn(token, invitation.token_hash)
        self.assertEqual(len(invitation.token_hash), 64)
        self.assertEqual(get_invitation_by_token(token), invitation)

    def test_new_invitation_revokes_previous(self):
        previous, previous_token = create_invitation(
            athlete=self.athlete,
            nutritionist=self.nutritionist,
        )
        current, _ = create_invitation(
            athlete=self.athlete,
            nutritionist=self.nutritionist,
        )

        previous.refresh_from_db()
        self.assertIsNotNone(previous.revoked_at)
        self.assertEqual(get_invitation_state(previous), 'revoked')
        self.assertEqual(get_invitation_state(current), 'valid')
        self.assertEqual(
            get_invitation_state(get_invitation_by_token(previous_token)), 'revoked'
        )

    def test_invitation_states(self):
        invitation, _ = create_invitation(
            athlete=self.athlete,
            nutritionist=self.nutritionist,
        )
        invitation.expires_at = timezone.now() - timedelta(seconds=1)
        invitation.save(update_fields=['expires_at'])
        self.assertEqual(get_invitation_state(invitation), 'expired')

        invitation.expires_at = timezone.now() + timedelta(hours=1)
        invitation.used_at = timezone.now()
        invitation.save(update_fields=['expires_at', 'used_at'])
        self.assertEqual(get_invitation_state(invitation), 'used')

    def test_activation_sets_hashed_password_and_consumes_invitation(self):
        invitation, token = create_invitation(
            athlete=self.athlete,
            nutritionist=self.nutritionist,
        )

        activate_invitation(
            token=token,
            password='A-strong-first-password-2026!',
            password_confirm='A-strong-first-password-2026!',
        )

        invitation.refresh_from_db()
        self.athlete.user.refresh_from_db()
        self.assertIsNotNone(invitation.used_at)
        self.assertTrue(
            self.athlete.user.check_password('A-strong-first-password-2026!')
        )
        self.assertTrue(self.athlete.user.has_usable_password())

    def test_invalid_password_rolls_back_consumption(self):
        invitation, token = create_invitation(
            athlete=self.athlete,
            nutritionist=self.nutritionist,
        )

        with self.assertRaises(ValidationError):
            activate_invitation(
                token=token,
                password='123',
                password_confirm='123',
            )

        invitation.refresh_from_db()
        self.athlete.user.refresh_from_db()
        self.assertIsNone(invitation.used_at)
        self.assertFalse(self.athlete.user.has_usable_password())


class InvitationApiTests(APITestCase):
    csrf_url = '/api/v1/auth/csrf/'
    password = 'A-strong-first-password-2026!'

    def setUp(self):
        cache.clear()
        self.client = APIClient(enforce_csrf_checks=True)
        self.nutritionist_a = self.create_user(
            'nutritionist-a@example.com', User.Role.NUTRITIONIST
        )
        self.nutritionist_b = self.create_user(
            'nutritionist-b@example.com', User.Role.NUTRITIONIST
        )
        self.athlete_a = create_athlete(
            nutritionist=self.nutritionist_a,
            email='athlete-a@example.com',
        )
        self.athlete_b = create_athlete(
            nutritionist=self.nutritionist_b,
            email='athlete-b@example.com',
        )

    @staticmethod
    def create_user(email, role):
        return User.objects.create_user(
            email=email,
            password='test-password',
            role=role,
        )

    def authenticate(self, user):
        access = RefreshToken.for_user(user).access_token
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {access}')

    def csrf_headers(self):
        self.client.get(self.csrf_url)
        return {'HTTP_X_CSRFTOKEN': self.client.cookies['csrftoken'].value}

    @staticmethod
    def invite_url(athlete):
        return f'/api/v1/athletes/{athlete.pk}/invite/'

    @staticmethod
    def detail_url(token):
        return f'/api/v1/auth/invitations/{token}/'

    @staticmethod
    def activate_url(token):
        return f'/api/v1/auth/invitations/{token}/activate/'

    def issue_invitation(self):
        self.authenticate(self.nutritionist_a)
        response = self.client.post(self.invite_url(self.athlete_a))
        token = response.data['invitation_url'].rsplit('/', 1)[-1]
        return response, token

    def test_nutritionist_issues_invitation_for_owned_athlete(self):
        response, token = self.issue_invitation()

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data['status'], 'pending')
        self.assertTrue(get_invitation_by_token(token))

    def test_cross_tenant_athlete_and_anonymous_cannot_issue(self):
        self.authenticate(self.nutritionist_a)
        cross_tenant = self.client.post(self.invite_url(self.athlete_b))
        self.authenticate(self.athlete_a.user)
        athlete = self.client.post(self.invite_url(self.athlete_a))
        self.client.credentials()
        anonymous = self.client.post(self.invite_url(self.athlete_a))

        self.assertEqual(cross_tenant.status_code, status.HTTP_404_NOT_FOUND)
        self.assertEqual(athlete.status_code, status.HTTP_403_FORBIDDEN)
        self.assertEqual(anonymous.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_public_validation_handles_valid_invalid_expired_used_and_revoked(self):
        _, valid_token = self.issue_invitation()
        valid = self.client.get(self.detail_url(valid_token))
        invalid = self.client.get(self.detail_url('not-a-real-token'))

        invitation = get_invitation_by_token(valid_token)
        invitation.expires_at = timezone.now() - timedelta(seconds=1)
        invitation.save(update_fields=['expires_at'])
        expired = self.client.get(self.detail_url(valid_token))

        invitation.expires_at = timezone.now() + timedelta(hours=1)
        invitation.used_at = timezone.now()
        invitation.save(update_fields=['expires_at', 'used_at'])
        used = self.client.get(self.detail_url(valid_token))

        invitation.used_at = None
        invitation.revoked_at = timezone.now()
        invitation.save(update_fields=['used_at', 'revoked_at'])
        revoked = self.client.get(self.detail_url(valid_token))

        self.assertTrue(valid.data['valid'])
        self.assertEqual(invalid.data['reason'], 'invalid')
        self.assertEqual(expired.data['reason'], 'expired')
        self.assertEqual(used.data['reason'], 'used')
        self.assertEqual(revoked.data['reason'], 'revoked')

    def test_activation_rejects_mismatch_and_requires_csrf(self):
        _, token = self.issue_invitation()
        self.client.credentials()
        mismatch = self.client.post(
            self.activate_url(token),
            {'password': self.password, 'password_confirm': 'different'},
            format='json',
            **self.csrf_headers(),
        )
        no_csrf_client = APIClient(enforce_csrf_checks=True)
        no_csrf = no_csrf_client.post(
            self.activate_url(token),
            {'password': self.password, 'password_confirm': self.password},
            format='json',
        )

        self.assertEqual(mismatch.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(no_csrf.status_code, status.HTTP_403_FORBIDDEN)

    def test_activation_allows_normal_jwt_login_and_prevents_reuse(self):
        _, token = self.issue_invitation()
        self.client.credentials()
        headers = self.csrf_headers()
        activated = self.client.post(
            self.activate_url(token),
            {'password': self.password, 'password_confirm': self.password},
            format='json',
            **headers,
        )
        reused = self.client.post(
            self.activate_url(token),
            {'password': self.password, 'password_confirm': self.password},
            format='json',
            **headers,
        )
        login = self.client.post(
            '/api/v1/auth/login/',
            {'email': self.athlete_a.user.email, 'password': self.password},
            format='json',
            **headers,
        )

        self.assertEqual(activated.status_code, status.HTTP_200_OK)
        self.assertEqual(reused.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(login.status_code, status.HTTP_200_OK)
        self.assertEqual(login.data['user']['role'], User.Role.ATHLETE)

    def test_new_invitation_invalidates_previous_and_activated_user_cannot_reinvite(self):
        _, previous_token = self.issue_invitation()
        _, current_token = self.issue_invitation()
        previous = self.client.get(self.detail_url(previous_token))
        self.assertEqual(previous.data['reason'], 'revoked')

        self.client.credentials()
        self.client.post(
            self.activate_url(current_token),
            {'password': self.password, 'password_confirm': self.password},
            format='json',
            **self.csrf_headers(),
        )
        self.authenticate(self.nutritionist_a)
        reinvite = self.client.post(self.invite_url(self.athlete_a))
        self.assertEqual(reinvite.status_code, status.HTTP_400_BAD_REQUEST)


class InvitationThrottleTests(APITestCase):
    csrf_url = InvitationApiTests.csrf_url
    password = InvitationApiTests.password

    def setUp(self):
        api_settings.reload()
        self.original_rates = SimpleRateThrottle.THROTTLE_RATES
        SimpleRateThrottle.THROTTLE_RATES = {
            **settings.REST_FRAMEWORK['DEFAULT_THROTTLE_RATES'],
            'athlete_invitation_issue': '1/minute',
            'athlete_invitation_validate': '1/minute',
            'athlete_invitation_activate': '1/minute',
        }
        cache.clear()
        self.client = APIClient(enforce_csrf_checks=True)
        self.nutritionist_a = User.objects.create_user(
            email='nutritionist@example.com',
            password='test-password',
            role=User.Role.NUTRITIONIST,
        )
        self.athlete_a = create_athlete(
            nutritionist=self.nutritionist_a,
            email='athlete@example.com',
        )

    def tearDown(self):
        SimpleRateThrottle.THROTTLE_RATES = self.original_rates
        super().tearDown()

    def authenticate(self, user):
        access = RefreshToken.for_user(user).access_token
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {access}')

    def csrf_headers(self):
        self.client.get(self.csrf_url)
        return {'HTTP_X_CSRFTOKEN': self.client.cookies['csrftoken'].value}

    @staticmethod
    def invite_url(athlete):
        return f'/api/v1/athletes/{athlete.pk}/invite/'

    @staticmethod
    def detail_url(token):
        return f'/api/v1/auth/invitations/{token}/'

    @staticmethod
    def activate_url(token):
        return f'/api/v1/auth/invitations/{token}/activate/'

    def issue_invitation(self):
        self.authenticate(self.nutritionist_a)
        response = self.client.post(self.invite_url(self.athlete_a))
        token = response.data['invitation_url'].rsplit('/', 1)[-1]
        return response, token

    def test_invitation_endpoints_are_throttled(self):
        _, token = self.issue_invitation()
        issue_limited = self.client.post(self.invite_url(self.athlete_a))

        self.client.credentials()
        self.client.get(self.detail_url(token))
        validate_limited = self.client.get(self.detail_url(token))

        headers = self.csrf_headers()
        self.client.post(
            self.activate_url('invalid-one'),
            {'password': self.password, 'password_confirm': self.password},
            format='json',
            **headers,
        )
        activate_limited = self.client.post(
            self.activate_url('invalid-two'),
            {'password': self.password, 'password_confirm': self.password},
            format='json',
            **headers,
        )

        self.assertEqual(issue_limited.status_code, status.HTTP_429_TOO_MANY_REQUESTS)
        self.assertEqual(validate_limited.status_code, status.HTTP_429_TOO_MANY_REQUESTS)
        self.assertEqual(activate_limited.status_code, status.HTTP_429_TOO_MANY_REQUESTS)
