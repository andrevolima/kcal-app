from rest_framework import serializers

from apps.athletes.models import Athlete
from apps.athletes.invitations import get_invitation_state


class AthleteCreateSerializer(serializers.Serializer):
    email = serializers.EmailField()
    first_name = serializers.CharField(max_length=150, required=False, allow_blank=True)
    last_name = serializers.CharField(max_length=150, required=False, allow_blank=True)


class AthleteUpdateSerializer(serializers.Serializer):
    first_name = serializers.CharField(max_length=150, required=False, allow_blank=True)
    last_name = serializers.CharField(max_length=150, required=False, allow_blank=True)


class AthleteSerializer(serializers.ModelSerializer):
    email = serializers.EmailField(source='user.email', read_only=True)
    first_name = serializers.CharField(source='user.first_name', read_only=True)
    last_name = serializers.CharField(source='user.last_name', read_only=True)
    onboarding_status = serializers.SerializerMethodField()

    def get_onboarding_status(self, athlete):
        if athlete.user.has_usable_password():
            return 'activated'
        if any(
            get_invitation_state(invitation) == 'valid'
            for invitation in athlete.invitations.all()
        ):
            return 'pending'
        return 'not_invited'

    class Meta:
        model = Athlete
        fields = (
            'id',
            'email',
            'first_name',
            'last_name',
            'is_active',
            'onboarding_status',
            'created_at',
            'updated_at',
        )
        read_only_fields = fields
