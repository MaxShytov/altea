"""
API URL configuration for Altea project.
All API endpoints are versioned under /api/v1/
"""

from django.urls import path, include

urlpatterns = [
    path('auth/', include('apps.accounts.api.urls')),
    path('', include('apps.core.api.urls')),
]
