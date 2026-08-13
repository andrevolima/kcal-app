from django.contrib.auth import authenticate
from rest_framework.exceptions import AuthenticationFailed
from rest_framework_simplejwt.exceptions import TokenError
from rest_framework_simplejwt.serializers import TokenRefreshSerializer
from rest_framework_simplejwt.tokens import RefreshToken


INVALID_CREDENTIALS_MESSAGE = 'Unable to log in with the provided credentials.'
INVALID_REFRESH_MESSAGE = 'Refresh token is invalid or expired.'


def create_token_pair(*, email, password):
    user = authenticate(email=email, password=password)
    if user is None:
        raise AuthenticationFailed(INVALID_CREDENTIALS_MESSAGE)

    refresh = RefreshToken.for_user(user)
    return user, str(refresh.access_token), str(refresh)


def rotate_refresh_token(*, refresh_token):
    serializer = TokenRefreshSerializer(data={'refresh': refresh_token})
    try:
        serializer.is_valid(raise_exception=True)
    except TokenError as exc:
        raise AuthenticationFailed(INVALID_REFRESH_MESSAGE) from exc

    return serializer.validated_data['access'], serializer.validated_data['refresh']


def revoke_refresh_token(*, refresh_token):
    try:
        RefreshToken(refresh_token).blacklist()
    except TokenError as exc:
        raise AuthenticationFailed(INVALID_REFRESH_MESSAGE) from exc
