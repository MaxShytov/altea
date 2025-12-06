"""
Context processors for core app.
"""

from apps.core.models import AppSettings


def app_settings(request):
    """
    Add app_settings to template context.
    Uses cached settings for performance.
    """
    return {
        'app_settings': AppSettings.get_settings()
    }
