from django.core.cache import cache
from rest_framework import status
from rest_framework.test import APITestCase
from rest_framework_simplejwt.tokens import RefreshToken

from apps.accounts.models import User
from apps.athletes.models import Athlete
from apps.athletes.services import create_athlete


class AthleteApiTests(APITestCase):
    list_url = '/api/v1/athletes/'

    def setUp(self):
        cache.clear()
        self.nutritionist_a = self.create_user(
            'nutritionist-a@example.com', User.Role.NUTRITIONIST
        )
        self.nutritionist_b = self.create_user(
            'nutritionist-b@example.com', User.Role.NUTRITIONIST
        )
        self.athlete_a = create_athlete(
            nutritionist=self.nutritionist_a,
            email='athlete-a@example.com',
            first_name='Athlete',
            last_name='A',
        )
        self.athlete_b = create_athlete(
            nutritionist=self.nutritionist_b,
            email='athlete-b@example.com',
            first_name='Athlete',
            last_name='B',
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

    @staticmethod
    def detail_url(athlete):
        return f'/api/v1/athletes/{athlete.pk}/'

    @staticmethod
    def deactivate_url(athlete):
        return f'/api/v1/athletes/{athlete.pk}/deactivate/'

    def test_nutritionist_creates_athlete_in_own_portfolio_without_injection(self):
        self.authenticate(self.nutritionist_a)
        response = self.client.post(
            self.list_url,
            {
                'email': 'new-athlete@example.com',
                'first_name': 'New',
                'last_name': 'Athlete',
                'nutritionist_id': self.nutritionist_b.id,
                'role': User.Role.NUTRITIONIST,
                'is_staff': True,
                'is_superuser': True,
            },
            format='json',
        )

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        athlete = Athlete.objects.get(user__email='new-athlete@example.com')
        self.assertEqual(athlete.nutritionist, self.nutritionist_a)
        self.assertEqual(athlete.user.role, User.Role.ATHLETE)
        self.assertFalse(athlete.user.is_staff)
        self.assertFalse(athlete.user.is_superuser)
        self.assertFalse(athlete.user.has_usable_password())

    def test_nutritionist_lists_only_own_athletes(self):
        self.authenticate(self.nutritionist_a)
        response = self.client.get(self.list_url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['count'], 1)
        self.assertEqual(response.data['results'][0]['id'], self.athlete_a.id)

    def test_nutritionist_accesses_and_updates_own_athlete(self):
        self.authenticate(self.nutritionist_a)
        detail = self.client.get(self.detail_url(self.athlete_a))
        updated = self.client.patch(
            self.detail_url(self.athlete_a),
            {'first_name': 'Updated'},
            format='json',
        )

        self.assertEqual(detail.status_code, status.HTTP_200_OK)
        self.assertEqual(updated.status_code, status.HTTP_200_OK)
        self.assertEqual(updated.data['first_name'], 'Updated')

    def test_cross_tenant_access_update_and_deactivation_return_404(self):
        self.authenticate(self.nutritionist_a)

        responses = (
            self.client.get(self.detail_url(self.athlete_b)),
            self.client.patch(
                self.detail_url(self.athlete_b),
                {'first_name': 'Intrusion'},
                format='json',
            ),
            self.client.post(self.deactivate_url(self.athlete_b)),
        )

        self.assertTrue(
            all(response.status_code == status.HTTP_404_NOT_FOUND for response in responses)
        )
        self.athlete_b.refresh_from_db()
        self.athlete_b.user.refresh_from_db()
        self.assertEqual(self.athlete_b.user.first_name, 'Athlete')
        self.assertTrue(self.athlete_b.is_active)

    def test_athlete_cannot_list_create_update_or_deactivate(self):
        self.athlete_a.user.set_password('test-password')
        self.athlete_a.user.save(update_fields=['password'])
        self.authenticate(self.athlete_a.user)

        responses = (
            self.client.get(self.list_url),
            self.client.post(
                self.list_url, {'email': 'injected@example.com'}, format='json'
            ),
            self.client.patch(
                self.detail_url(self.athlete_a),
                {'first_name': 'Changed'},
                format='json',
            ),
            self.client.post(self.deactivate_url(self.athlete_a)),
        )

        self.assertTrue(
            all(response.status_code == status.HTTP_403_FORBIDDEN for response in responses)
        )

    def test_athlete_reads_only_own_detail(self):
        self.authenticate(self.athlete_a.user)

        own = self.client.get(self.detail_url(self.athlete_a))
        other = self.client.get(self.detail_url(self.athlete_b))

        self.assertEqual(own.status_code, status.HTTP_200_OK)
        self.assertEqual(other.status_code, status.HTTP_404_NOT_FOUND)

    def test_deactivation_preserves_data_and_user_active_state(self):
        self.authenticate(self.nutritionist_a)
        response = self.client.post(self.deactivate_url(self.athlete_a))

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.athlete_a.refresh_from_db()
        self.athlete_a.user.refresh_from_db()
        self.assertFalse(self.athlete_a.is_active)
        self.assertTrue(self.athlete_a.user.is_active)
        self.assertTrue(Athlete.objects.filter(pk=self.athlete_a.pk).exists())

    def test_patch_cannot_change_email_or_administrative_fields(self):
        self.authenticate(self.nutritionist_a)
        original_email = self.athlete_a.user.email

        response = self.client.patch(
            self.detail_url(self.athlete_a),
            {
                'email': 'changed@example.com',
                'role': User.Role.NUTRITIONIST,
                'is_staff': True,
                'first_name': 'Allowed',
            },
            format='json',
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.athlete_a.user.refresh_from_db()
        self.assertEqual(self.athlete_a.user.email, original_email)
        self.assertEqual(self.athlete_a.user.role, User.Role.ATHLETE)
        self.assertFalse(self.athlete_a.user.is_staff)
        self.assertEqual(self.athlete_a.user.first_name, 'Allowed')

    def test_unauthenticated_requests_are_denied(self):
        responses = (
            self.client.get(self.list_url),
            self.client.post(
                self.list_url, {'email': 'new@example.com'}, format='json'
            ),
            self.client.get(self.detail_url(self.athlete_a)),
        )
        self.assertTrue(
            all(response.status_code == status.HTTP_401_UNAUTHORIZED for response in responses)
        )
