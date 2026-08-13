from datetime import timedelta

from django.conf import settings
from django.core.cache import cache
from django.test import override_settings
from rest_framework import status
from rest_framework.settings import api_settings
from rest_framework.test import APIClient, APITestCase
from rest_framework.throttling import SimpleRateThrottle
from rest_framework_simplejwt.tokens import AccessToken, RefreshToken

from apps.accounts.models import User


class AuthenticationApiTests(APITestCase):
    csrf_url = '/api/v1/auth/csrf/'
    login_url = '/api/v1/auth/login/'
    refresh_url = '/api/v1/auth/refresh/'
    logout_url = '/api/v1/auth/logout/'
    me_url = '/api/v1/auth/me/'
    password = 'a-strong-test-password'

    def setUp(self):
        cache.clear()
        self.client = APIClient(enforce_csrf_checks=True)
        self.nutritionist = User.objects.create_user(
            email='nutritionist@example.com',
            password=self.password,
            role=User.Role.NUTRITIONIST,
        )
        self.athlete = User.objects.create_user(
            email='athlete@example.com',
            password=self.password,
            role=User.Role.ATHLETE,
        )

    def csrf_headers(self):
        self.client.get(self.csrf_url)
        return {'HTTP_X_CSRFTOKEN': self.client.cookies['csrftoken'].value}

    def login(self, email='nutritionist@example.com', password=None):
        return self.client.post(
            self.login_url,
            {'email': email, 'password': password or self.password},
            format='json',
            **self.csrf_headers(),
        )

    def authorize(self, access):
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {access}')

    def test_valid_login_sets_httponly_refresh_cookie(self):
        response = self.login()

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('access', response.data)
        self.assertEqual(response.data['user']['role'], User.Role.NUTRITIONIST)
        self.assertNotIn('refresh', response.data)
        self.assertNotIn('password', response.data)
        cookie = response.cookies[settings.JWT_REFRESH_COOKIE_NAME]
        self.assertTrue(cookie['httponly'])
        self.assertEqual(cookie['path'], '/api/v1/auth/')

    def test_invalid_password_and_unknown_email_share_generic_error(self):
        invalid_password = self.login(password='incorrect-password')
        unknown_email = self.login(email='missing@example.com')

        self.assertEqual(invalid_password.status_code, status.HTTP_401_UNAUTHORIZED)
        self.assertEqual(unknown_email.status_code, status.HTTP_401_UNAUTHORIZED)
        self.assertEqual(invalid_password.data, unknown_email.data)
        self.assertNotIn('nutritionist@example.com', str(invalid_password.data))

    def test_inactive_user_cannot_login(self):
        self.athlete.is_active = False
        self.athlete.save(update_fields=['is_active'])

        response = self.login(email=self.athlete.email)

        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_login_requires_csrf(self):
        response = self.client.post(
            self.login_url,
            {'email': self.nutritionist.email, 'password': self.password},
            format='json',
        )

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_private_endpoint_requires_access_token(self):
        response = self.client.get(self.me_url)

        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_private_endpoint_accepts_valid_access_and_returns_roles(self):
        nutritionist_login = self.login()
        self.authorize(nutritionist_login.data['access'])
        nutritionist_response = self.client.get(self.me_url)

        self.client.credentials()
        athlete_login = self.login(email=self.athlete.email)
        self.authorize(athlete_login.data['access'])
        athlete_response = self.client.get(self.me_url)

        self.assertEqual(nutritionist_response.status_code, status.HTTP_200_OK)
        self.assertEqual(
            set(nutritionist_response.data), {'id', 'email', 'role'}
        )
        self.assertEqual(nutritionist_response.data['role'], User.Role.NUTRITIONIST)
        self.assertEqual(athlete_response.data['role'], User.Role.ATHLETE)

    def test_expired_and_invalid_access_tokens_are_rejected(self):
        expired = AccessToken.for_user(self.nutritionist)
        expired.set_exp(lifetime=timedelta(seconds=-1))

        self.authorize(str(expired))
        expired_response = self.client.get(self.me_url)
        self.authorize('not-a-token')
        invalid_response = self.client.get(self.me_url)

        self.assertEqual(expired_response.status_code, status.HTTP_401_UNAUTHORIZED)
        self.assertEqual(invalid_response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_refresh_rotates_and_blacklists_previous_token(self):
        login_response = self.login()
        original = login_response.cookies[settings.JWT_REFRESH_COOKIE_NAME].value

        response = self.client.post(
            self.refresh_url, format='json', **self.csrf_headers()
        )
        rotated = response.cookies[settings.JWT_REFRESH_COOKIE_NAME].value

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('access', response.data)
        self.assertNotEqual(original, rotated)

        self.client.cookies[settings.JWT_REFRESH_COOKIE_NAME] = original
        reused = self.client.post(
            self.refresh_url, format='json', **self.csrf_headers()
        )
        self.assertEqual(reused.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_invalid_and_expired_refresh_tokens_are_rejected(self):
        headers = self.csrf_headers()
        self.client.cookies[settings.JWT_REFRESH_COOKIE_NAME] = 'invalid'
        invalid = self.client.post(self.refresh_url, format='json', **headers)

        expired_token = RefreshToken.for_user(self.nutritionist)
        expired_token.set_exp(lifetime=timedelta(seconds=-1))
        self.client.cookies[settings.JWT_REFRESH_COOKIE_NAME] = str(expired_token)
        expired = self.client.post(self.refresh_url, format='json', **headers)

        self.assertEqual(invalid.status_code, status.HTTP_401_UNAUTHORIZED)
        self.assertEqual(expired.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_logout_revokes_refresh_token(self):
        login_response = self.login()
        refresh = login_response.cookies[settings.JWT_REFRESH_COOKIE_NAME].value
        headers = self.csrf_headers()

        response = self.client.post(self.logout_url, format='json', **headers)

        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.client.cookies[settings.JWT_REFRESH_COOKIE_NAME] = refresh
        reused = self.client.post(self.refresh_url, format='json', **headers)
        self.assertEqual(reused.status_code, status.HTTP_401_UNAUTHORIZED)


LOW_THROTTLE_SETTINGS = {
    **settings.REST_FRAMEWORK,
    'DEFAULT_THROTTLE_RATES': {
        **settings.REST_FRAMEWORK['DEFAULT_THROTTLE_RATES'],
        'anon': '1/minute',
        'user': '1/minute',
        'auth_login': '1/minute',
        'token_refresh': '1/minute',
    },
}


@override_settings(REST_FRAMEWORK=LOW_THROTTLE_SETTINGS)
class AuthenticationThrottleTests(APITestCase):
    csrf_url = AuthenticationApiTests.csrf_url
    login_url = AuthenticationApiTests.login_url
    refresh_url = AuthenticationApiTests.refresh_url
    me_url = AuthenticationApiTests.me_url
    password = AuthenticationApiTests.password

    def setUp(self):
        api_settings.reload()
        self.original_throttle_rates = SimpleRateThrottle.THROTTLE_RATES
        SimpleRateThrottle.THROTTLE_RATES = (
            LOW_THROTTLE_SETTINGS['DEFAULT_THROTTLE_RATES']
        )
        cache.clear()
        self.client = APIClient(enforce_csrf_checks=True)
        self.nutritionist = User.objects.create_user(
            email='nutritionist@example.com',
            password=self.password,
            role=User.Role.NUTRITIONIST,
        )

    def tearDown(self):
        SimpleRateThrottle.THROTTLE_RATES = self.original_throttle_rates
        super().tearDown()

    def csrf_headers(self):
        self.client.get(self.csrf_url)
        return {'HTTP_X_CSRFTOKEN': self.client.cookies['csrftoken'].value}

    def login(self, password=None):
        return self.client.post(
            self.login_url,
            {
                'email': self.nutritionist.email,
                'password': password or self.password,
            },
            format='json',
            **self.csrf_headers(),
        )

    def authorize(self, access):
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {access}')

    def test_login_throttle_blocks_excess_requests(self):
        self.login(password='incorrect-password')
        response = self.login(password='incorrect-password')
        self.assertEqual(response.status_code, status.HTTP_429_TOO_MANY_REQUESTS)
        self.assertIn('Retry-After', response)

    def test_refresh_throttle_blocks_excess_requests(self):
        self.login()
        headers = self.csrf_headers()
        first = self.client.post(self.refresh_url, format='json', **headers)
        second = self.client.post(self.refresh_url, format='json', **headers)
        self.assertEqual(first.status_code, status.HTTP_200_OK)
        self.assertEqual(second.status_code, status.HTTP_429_TOO_MANY_REQUESTS)

    def test_anonymous_throttle_blocks_excess_requests(self):
        self.client.get(self.csrf_url)
        response = self.client.get(self.csrf_url)
        self.assertEqual(response.status_code, status.HTTP_429_TOO_MANY_REQUESTS)

    def test_authenticated_throttle_blocks_excess_requests(self):
        access = str(RefreshToken.for_user(self.nutritionist).access_token)
        self.authorize(access)
        self.client.get(self.me_url)
        response = self.client.get(self.me_url)
        self.assertEqual(response.status_code, status.HTTP_429_TOO_MANY_REQUESTS)
