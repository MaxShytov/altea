"""
Core API serializers - includes legal document serializers.
"""

from rest_framework import serializers

from apps.core.models import LegalDocument


class LegalDocumentSerializer(serializers.ModelSerializer):
    """Serializer for LegalDocument model."""

    document_type_display = serializers.CharField(
        source='get_document_type_display',
        read_only=True
    )

    class Meta:
        model = LegalDocument
        fields = [
            'id',
            'document_type',
            'document_type_display',
            'version',
            'title',
            'content',
            'effective_date',
        ]
        read_only_fields = fields


class LegalDocumentListSerializer(serializers.ModelSerializer):
    """Lightweight serializer for listing legal documents (without content)."""

    document_type_display = serializers.CharField(
        source='get_document_type_display',
        read_only=True
    )

    class Meta:
        model = LegalDocument
        fields = [
            'id',
            'document_type',
            'document_type_display',
            'version',
            'title',
            'effective_date',
        ]
        read_only_fields = fields


class AcceptLegalDocumentsSerializer(serializers.Serializer):
    """Serializer for accepting legal documents."""

    terms_version = serializers.CharField(
        required=False,
        allow_blank=True,
        help_text='Version of Terms of Service to accept'
    )
    privacy_version = serializers.CharField(
        required=False,
        allow_blank=True,
        help_text='Version of Privacy Policy to accept'
    )

    def validate(self, attrs):
        """Ensure at least one version is provided."""
        if not attrs.get('terms_version') and not attrs.get('privacy_version'):
            raise serializers.ValidationError(
                'At least one of terms_version or privacy_version must be provided.'
            )
        return attrs

    def validate_terms_version(self, value):
        """Validate that the terms version exists and is active."""
        if value:
            document = LegalDocument.objects.filter(
                document_type='terms',
                version=value,
                is_active=True
            ).first()
            if not document:
                raise serializers.ValidationError(
                    f'Terms of Service version "{value}" not found or not active.'
                )
        return value

    def validate_privacy_version(self, value):
        """Validate that the privacy version exists and is active."""
        if value:
            document = LegalDocument.objects.filter(
                document_type='privacy',
                version=value,
                is_active=True
            ).first()
            if not document:
                raise serializers.ValidationError(
                    f'Privacy Policy version "{value}" not found or not active.'
                )
        return value
