"""
Core URL configuration - includes legal document web pages.
"""

from django.urls import path

from apps.core.views import TermsOfServiceView, PrivacyPolicyView

app_name = 'core'

urlpatterns = [
    path('terms/', TermsOfServiceView.as_view(), name='terms'),
    path('privacy/', PrivacyPolicyView.as_view(), name='privacy'),
]
