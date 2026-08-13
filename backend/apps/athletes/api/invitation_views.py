from django.conf import settings
from django.shortcuts import get_object_or_404
from rest_framework import status
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework.throttling import ScopedRateThrottle
from rest_framework.views import APIView

from apps.accounts.api.csrf import enforce_csrf
from apps.athletes.invitations import (
    activate_invitation,
    create_invitation,
    get_invitation_by_token,
    get_invitation_state,
)
from apps.athletes.selectors import get_nutritionist_athletes

from .invitation_serializers import InvitationActivationSerializer
from .permissions import CanAccessAthlete, IsNutritionist


class AthleteInviteView(APIView):
    permission_classes = [IsNutritionist, CanAccessAthlete]
    throttle_classes = [ScopedRateThrottle]
    throttle_scope = 'athlete_invitation_issue'

    def post(self, request, pk):
        athlete = get_object_or_404(
            get_nutritionist_athletes(nutritionist=request.user),
            pk=pk,
        )
        self.check_object_permissions(request, athlete)
        invitation, raw_token = create_invitation(
            athlete=athlete,
            nutritionist=request.user,
        )
        data = {
            'status': 'pending',
            'expires_at': invitation.expires_at,
        }
        if settings.ATHLETE_INVITATION_EXPOSE_LINK:
            data['invitation_url'] = (
                f'{settings.FRONTEND_URL}/activate/{raw_token}'
            )
        return Response(data, status=status.HTTP_201_CREATED)


class InvitationDetailView(APIView):
    permission_classes = [AllowAny]
    throttle_classes = [ScopedRateThrottle]
    throttle_scope = 'athlete_invitation_validate'

    def get(self, request, token):
        invitation = get_invitation_by_token(token)
        if invitation is None:
            return Response({'valid': False, 'reason': 'invalid'})
        state = get_invitation_state(invitation)
        data = {'valid': state == 'valid'}
        if state == 'valid':
            data['expires_at'] = invitation.expires_at
        else:
            data['reason'] = state
        return Response(data)


class InvitationActivateView(APIView):
    permission_classes = [AllowAny]
    throttle_classes = [ScopedRateThrottle]
    throttle_scope = 'athlete_invitation_activate'

    def post(self, request, token):
        enforce_csrf(request)
        serializer = InvitationActivationSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        activate_invitation(token=token, **serializer.validated_data)
        return Response({'activated': True}, status=status.HTTP_200_OK)
