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


class CustomRateThrottle(AnonRateThrottle):
    """
    Base throttle class with custom rate parsing.

    Supports formats:
    - '5/15m' -> 5 requests per 15 minutes
    - '10/h' -> 10 requests per hour
    - Standard DRF formats (s/m/h/d)
    """

    def parse_rate(self, rate):
        """Parse rate string like '5/15m' (5 requests per 15 minutes)."""
        if rate is None:
            return (None, None)

        num, period = rate.split('/')
        num_requests = int(num)

        # Check if period starts with a number (e.g., '15m', '30s')
        if period[0].isdigit():
            # Extract number and unit
            duration_num = ''
            for char in period:
                if char.isdigit():
                    duration_num += char
                else:
                    break
            unit = period[len(duration_num):]
            duration_num = int(duration_num)

            # Map unit to seconds
            unit_seconds = {'s': 1, 'm': 60, 'h': 3600, 'd': 86400}
            duration = duration_num * unit_seconds.get(unit, 60)
        else:
            # Standard DRF format (s/m/h/d)
            duration = {'s': 1, 'm': 60, 'h': 3600, 'd': 86400}[period[0]]

        return (num_requests, duration)


class LoginThrottle(CustomRateThrottle):
    """
    Throttle for login endpoint.
    Limits login attempts to prevent brute force attacks.
    Rate: 5 requests per 15 minutes per IP.
    """
    rate = '5/15m'
    scope = 'login'


class ForgotPasswordThrottle(CustomRateThrottle):
    """
    Throttle for forgot password endpoint.
    Limits password reset requests to prevent email spam.
    Rate: 3 requests per 15 minutes per IP.
    """
    rate = '3/15m'
    scope = 'forgot_password'
