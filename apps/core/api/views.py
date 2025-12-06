"""
Core API views - includes legal document and app settings endpoints.
"""

from django.utils import timezone
from rest_framework import status
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from drf_spectacular.utils import extend_schema, OpenApiResponse

from apps.core.models import AppSettings, LegalDocument
from apps.core.api.serializers import (
    AppSettingsSerializer,
    LegalDocumentSerializer,
    LegalDocumentListSerializer,
    AcceptLegalDocumentsSerializer,
)


class AppSettingsAPIView(APIView):
    """
    Get application branding and configuration settings.
    Public endpoint - no authentication required.
    Cached server-side for 1 hour.
    """
    permission_classes = [AllowAny]

    @extend_schema(
        summary='Get app settings',
        description='Returns application branding configuration including logo, '
                    'app name, colors, and contact information. '
                    'This endpoint is public and cached server-side.',
        responses={
            200: AppSettingsSerializer,
        },
        tags=['Config'],
    )
    def get(self, request):
        settings = AppSettings.get_settings()
        serializer = AppSettingsSerializer(settings, context={'request': request})
        return Response(serializer.data)


class LegalDocumentListAPIView(APIView):
    """
    List all active legal documents.
    Returns lightweight data without full content.
    """
    permission_classes = [AllowAny]

    @extend_schema(
        summary='List active legal documents',
        description='Returns a list of all currently active legal documents (Terms, Privacy) without full content.',
        responses={
            200: LegalDocumentListSerializer(many=True),
        },
        tags=['Legal'],
    )
    def get(self, request):
        documents = LegalDocument.objects.filter(is_active=True)
        serializer = LegalDocumentListSerializer(documents, many=True)
        return Response(serializer.data)


class TermsOfServiceAPIView(APIView):
    """
    Get the currently active Terms of Service.
    """
    permission_classes = [AllowAny]

    @extend_schema(
        summary='Get Terms of Service',
        description='Returns the currently active Terms of Service document with full content.',
        responses={
            200: LegalDocumentSerializer,
            404: OpenApiResponse(description='No active Terms of Service found'),
        },
        tags=['Legal'],
    )
    def get(self, request):
        document = LegalDocument.get_active('terms')

        if not document:
            return Response(
                {'error': True, 'message': 'Terms of Service not found'},
                status=status.HTTP_404_NOT_FOUND
            )

        serializer = LegalDocumentSerializer(document)
        return Response(serializer.data)


class PrivacyPolicyAPIView(APIView):
    """
    Get the currently active Privacy Policy.
    """
    permission_classes = [AllowAny]

    @extend_schema(
        summary='Get Privacy Policy',
        description='Returns the currently active Privacy Policy document with full content.',
        responses={
            200: LegalDocumentSerializer,
            404: OpenApiResponse(description='No active Privacy Policy found'),
        },
        tags=['Legal'],
    )
    def get(self, request):
        document = LegalDocument.get_active('privacy')

        if not document:
            return Response(
                {'error': True, 'message': 'Privacy Policy not found'},
                status=status.HTTP_404_NOT_FOUND
            )

        serializer = LegalDocumentSerializer(document)
        return Response(serializer.data)


class AcceptLegalDocumentsAPIView(APIView):
    """
    Accept legal documents (update user's accepted versions).
    Requires authentication.
    """
    permission_classes = [IsAuthenticated]

    @extend_schema(
        summary='Accept legal documents',
        description='Updates the authenticated user\'s accepted legal document versions. '
                    'Use this when user accepts new versions of Terms or Privacy Policy.',
        request=AcceptLegalDocumentsSerializer,
        responses={
            200: OpenApiResponse(description='Legal documents accepted successfully'),
            400: OpenApiResponse(description='Validation error'),
            401: OpenApiResponse(description='Authentication required'),
        },
        tags=['Legal'],
    )
    def post(self, request):
        serializer = AcceptLegalDocumentsSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        user = request.user
        updated_fields = []

        terms_version = serializer.validated_data.get('terms_version')
        if terms_version:
            user.terms_version_accepted = terms_version
            user.terms_accepted_at = timezone.now()
            updated_fields.extend(['terms_version_accepted', 'terms_accepted_at'])

        privacy_version = serializer.validated_data.get('privacy_version')
        if privacy_version:
            user.privacy_version_accepted = privacy_version
            updated_fields.append('privacy_version_accepted')

        if updated_fields:
            user.save(update_fields=updated_fields)

        return Response({
            'message': 'Legal documents accepted successfully',
            'terms_version_accepted': user.terms_version_accepted,
            'privacy_version_accepted': user.privacy_version_accepted,
        })


class CheckLegalUpdatesAPIView(APIView):
    """
    Check if user needs to accept updated legal documents.
    Requires authentication.
    """
    permission_classes = [IsAuthenticated]

    @extend_schema(
        summary='Check for legal document updates',
        description='Returns whether the authenticated user needs to accept new versions '
                    'of Terms of Service or Privacy Policy.',
        responses={
            200: OpenApiResponse(
                description='Legal update status',
                examples=[{
                    'needs_terms_update': True,
                    'needs_privacy_update': False,
                    'current_terms_version': '2.0',
                    'current_privacy_version': '1.0',
                    'user_terms_version': '1.0',
                    'user_privacy_version': '1.0',
                }]
            ),
            401: OpenApiResponse(description='Authentication required'),
        },
        tags=['Legal'],
    )
    def get(self, request):
        user = request.user

        current_terms = LegalDocument.get_active('terms')
        current_privacy = LegalDocument.get_active('privacy')

        current_terms_version = current_terms.version if current_terms else None
        current_privacy_version = current_privacy.version if current_privacy else None

        needs_terms_update = (
            current_terms_version and
            user.terms_version_accepted != current_terms_version
        )
        needs_privacy_update = (
            current_privacy_version and
            user.privacy_version_accepted != current_privacy_version
        )

        return Response({
            'needs_terms_update': needs_terms_update,
            'needs_privacy_update': needs_privacy_update,
            'current_terms_version': current_terms_version,
            'current_privacy_version': current_privacy_version,
            'user_terms_version': user.terms_version_accepted or None,
            'user_privacy_version': user.privacy_version_accepted or None,
        })
