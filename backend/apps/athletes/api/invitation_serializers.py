from rest_framework import serializers


class InvitationActivationSerializer(serializers.Serializer):
    password = serializers.CharField(trim_whitespace=False, write_only=True)
    password_confirm = serializers.CharField(trim_whitespace=False, write_only=True)
