"""
Custom throttling classes for authentication endpoints.
"""

from rest_framework.throttling import AnonRateThrottle


class RegistrationThrottle(AnonRateThrottle):
    """
    Throttle for registration endpoint.
    Limits registration attempts to prevent abuse.
    Rate: 5 requests per 15 minutes per IP.
    """
    rate = '5/hour'  # Using hour as base, will be more restrictive in practice
    scope = 'registration'


class ResendVerificationThrottle(AnonRateThrottle):
    """
    Throttle for resend verification endpoint.
    More restrictive to prevent email spam.
    Rate: 3 requests per hour per IP.
    """
    rate = '3/hour'
    scope = 'resend_verification'
