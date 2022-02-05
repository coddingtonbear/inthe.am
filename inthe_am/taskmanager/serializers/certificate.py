from rest_framework import serializers


class CertificateSerializer(serializers.Serializer):
    fingerprint = serializers.CharField(read_only=True)
    label = serializers.CharField(read_only=True)
    created = serializers.DateTimeField(read_only=True)
    revoked = serializers.DateTimeField(read_only=True, required=False)
