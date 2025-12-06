"""
Core API URL configuration.
"""

from django.urls import path

from apps.core.api.views import (
    LegalDocumentListAPIView,
    TermsOfServiceAPIView,
    PrivacyPolicyAPIView,
    AcceptLegalDocumentsAPIView,
    CheckLegalUpdatesAPIView,
)

app_name = 'core-api'

urlpatterns = [
    # Legal documents
    path('legal/', LegalDocumentListAPIView.as_view(), name='legal-list'),
    path('legal/terms/', TermsOfServiceAPIView.as_view(), name='legal-terms'),
    path('legal/privacy/', PrivacyPolicyAPIView.as_view(), name='legal-privacy'),
    path('legal/accept/', AcceptLegalDocumentsAPIView.as_view(), name='legal-accept'),
    path('legal/check-updates/', CheckLegalUpdatesAPIView.as_view(), name='legal-check-updates'),
]
