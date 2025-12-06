"""
Core views - includes legal document views.
"""

from django.shortcuts import render
from django.views import View

from apps.core.models import LegalDocument


class TermsOfServiceView(View):
    """Display the Terms of Service page."""

    def get(self, request):
        document = LegalDocument.get_active('terms')

        if not document:
            return render(request, 'legal/not_found.html', {
                'document_type': 'Terms of Service'
            }, status=404)

        return render(request, 'legal/terms.html', {
            'document': document,
            'show_back_to_app': request.GET.get('app') == '1',
        })


class PrivacyPolicyView(View):
    """Display the Privacy Policy page."""

    def get(self, request):
        document = LegalDocument.get_active('privacy')

        if not document:
            return render(request, 'legal/not_found.html', {
                'document_type': 'Privacy Policy'
            }, status=404)

        return render(request, 'legal/privacy.html', {
            'document': document,
            'show_back_to_app': request.GET.get('app') == '1',
        })
