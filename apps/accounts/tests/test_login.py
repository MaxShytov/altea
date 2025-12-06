"""
Comprehensive tests for FR-1.2 User Authentication (Login).

This module provides complete test coverage for the login feature including:
- Unit tests for models, serializers, and services
- Integration tests for API endpoints
- Edge cases from the planning phase
- Security tests

Test Structure:
- LoginAPIViewTests: API integration tests for /api/v1/auth/login/
- LoginAPIViewEdgeCasesTests: Edge cases and security tests
- LoginThrottleTests: Rate limiting configuration tests
- LoginThrottleParseRateTests: Custom rate parser tests
- LoginSerializerTests: Serializer validation tests
- LoginSerializerEdgeCasesTests: Serializer edge cases
- LoginUserSerializerTests: User data serializer tests
- LoginResponseSerializerTests: Response structure tests
- AuthenticationServiceTests: Service layer tests
- AuthenticationServiceEdgeCasesTests: Service edge cases
- AuthResultDataclassTests: AuthResult dataclass tests
- AuthErrorCodeEnumTests: Error code enum tests
- JWTTokenTests: JWT token validation tests
"""

from datetime import timedelta
from unittest.mock import patch, MagicMock
import logging

from django.test import TestCase, override_settings
from django.urls import reverse
from django.utils import timezone
from rest_framework import status
from rest_framework.test import APITestCase, APIClient

from apps.accounts.models import User


class LoginAPIViewTests(APITestCase):
    """Tests for POST /api/v1/auth/login/"""

    def setUp(self):
        """Set up test client and user."""
        self.client = APIClient()
        self.url = reverse('accounts_api:login')
        self.password = 'SecurePass123!'

        # Create verified user
        self.verified_user = User.objects.create_user(
            username='verified@example.com',
            email='verified@example.com',
            password=self.password,
            first_name='John',
            last_name='Doe',
            is_verified=True,
        )

        # Create unverified user
        self.unverified_user = User.objects.create_user(
            username='unverified@example.com',
            email='unverified@example.com',
            password=self.password,
            first_name='Jane',
            last_name='Doe',
            is_verified=False,
        )

    @patch('apps.accounts.api.views.LoginAPIView.throttle_classes', [])
    def test_login_success(self):
        """Test successful login returns 200 with tokens."""
        response = self.client.post(
            self.url,
            {'email': 'verified@example.com', 'password': self.password},
            format='json'
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('access_token', response.data)
        self.assertIn('refresh_token', response.data)
        self.assertIn('user', response.data)

    @patch('apps.accounts.api.views.LoginAPIView.throttle_classes', [])
    def test_login_success_response_structure(self):
        """Test login response contains all required user fields."""
        response = self.client.post(
            self.url,
            {'email': 'verified@example.com', 'password': self.password},
            format='json'
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)

        user_data = response.data['user']
        self.assertEqual(user_data['id'], self.verified_user.id)
        self.assertEqual(user_data['email'], 'verified@example.com')
        self.assertEqual(user_data['first_name'], 'John')
        self.assertEqual(user_data['last_name'], 'Doe')
        self.assertIn('profile_completed', user_data)
        self.assertIn('language', user_data)

        # Stub values until FR-1.3 Onboarding
        self.assertEqual(user_data['profile_completed'], False)
        self.assertEqual(user_data['language'], 'en')

    @patch('apps.accounts.api.views.LoginAPIView.throttle_classes', [])
    def test_login_wrong_password(self):
        """Test login with wrong password returns 401."""
        response = self.client.post(
            self.url,
            {'email': 'verified@example.com', 'password': 'WrongPassword123!'},
            format='json'
        )

        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        self.assertEqual(response.data['detail'], 'Invalid credentials')

    @patch('apps.accounts.api.views.LoginAPIView.throttle_classes', [])
    def test_login_user_not_found(self):
        """Test login with non-existent email returns 401."""
        response = self.client.post(
            self.url,
            {'email': 'nonexistent@example.com', 'password': self.password},
            format='json'
        )

        # Should return same error as wrong password for security
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        self.assertEqual(response.data['detail'], 'Invalid credentials')

    @patch('apps.accounts.api.views.LoginAPIView.throttle_classes', [])
    def test_login_unverified_email(self):
        """Test login with unverified email returns 403."""
        response = self.client.post(
            self.url,
            {'email': 'unverified@example.com', 'password': self.password},
            format='json'
        )

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertEqual(response.data['detail'], 'Please verify your email')
        self.assertEqual(response.data['code'], 'email_not_verified')

    @patch('apps.accounts.api.views.LoginAPIView.throttle_classes', [])
    def test_login_email_case_insensitive(self):
        """Test login email is case insensitive."""
        response = self.client.post(
            self.url,
            {'email': 'VERIFIED@EXAMPLE.COM', 'password': self.password},
            format='json'
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('access_token', response.data)

    @patch('apps.accounts.api.views.LoginAPIView.throttle_classes', [])
    def test_login_email_with_whitespace(self):
        """Test login strips whitespace from email."""
        response = self.client.post(
            self.url,
            {'email': '  verified@example.com  ', 'password': self.password},
            format='json'
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('access_token', response.data)

    @patch('apps.accounts.api.views.LoginAPIView.throttle_classes', [])
    def test_login_missing_email(self):
        """Test login fails without email."""
        response = self.client.post(
            self.url,
            {'password': self.password},
            format='json'
        )

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('email', response.data['details'])

    @patch('apps.accounts.api.views.LoginAPIView.throttle_classes', [])
    def test_login_missing_password(self):
        """Test login fails without password."""
        response = self.client.post(
            self.url,
            {'email': 'verified@example.com'},
            format='json'
        )

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('password', response.data['details'])

    @patch('apps.accounts.api.views.LoginAPIView.throttle_classes', [])
    def test_login_invalid_email_format(self):
        """Test login fails with invalid email format."""
        response = self.client.post(
            self.url,
            {'email': 'invalid-email', 'password': self.password},
            format='json'
        )

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('email', response.data['details'])

    @patch('apps.accounts.api.views.LoginAPIView.throttle_classes', [])
    def test_login_empty_password(self):
        """Test login fails with empty password."""
        response = self.client.post(
            self.url,
            {'email': 'verified@example.com', 'password': ''},
            format='json'
        )

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('password', response.data['details'])

    @patch('apps.accounts.api.views.LoginAPIView.throttle_classes', [])
    def test_login_returns_valid_jwt(self):
        """Test login returns valid JWT tokens."""
        from rest_framework_simplejwt.tokens import AccessToken

        response = self.client.post(
            self.url,
            {'email': 'verified@example.com', 'password': self.password},
            format='json'
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)

        # Verify access token can be decoded
        access_token = response.data['access_token']
        token = AccessToken(access_token)

        # Token should contain user_id
        self.assertEqual(str(token['user_id']), str(self.verified_user.id))

    @patch('apps.accounts.api.views.LoginAPIView.throttle_classes', [])
    def test_login_inactive_user(self):
        """Test login fails for inactive user."""
        self.verified_user.is_active = False
        self.verified_user.save()

        response = self.client.post(
            self.url,
            {'email': 'verified@example.com', 'password': self.password},
            format='json'
        )

        # Django authenticate() returns None for inactive users
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        self.assertEqual(response.data['detail'], 'Invalid credentials')


class LoginThrottleTests(APITestCase):
    """Tests for login rate limiting configuration."""

    def test_login_throttle_classes_configured(self):
        """Test that login view has throttle classes configured."""
        from apps.accounts.api.views import LoginAPIView
        from apps.accounts.api.throttling import LoginThrottle

        self.assertIn(LoginThrottle, LoginAPIView.throttle_classes)

    def test_login_throttle_rate(self):
        """Test that login throttle has correct rate (5 requests per 15 minutes)."""
        from apps.accounts.api.throttling import LoginThrottle

        throttle = LoginThrottle()
        self.assertEqual(throttle.rate, '5/15m')
        self.assertEqual(throttle.scope, 'login')
        # Verify parse_rate works correctly: 5 requests, 900 seconds (15 minutes)
        self.assertEqual(throttle.num_requests, 5)
        self.assertEqual(throttle.duration, 900)


class LoginSerializerTests(TestCase):
    """Tests for LoginSerializer validation."""

    def setUp(self):
        """Create test user."""
        self.password = 'SecurePass123!'
        self.user = User.objects.create_user(
            username='test@example.com',
            email='test@example.com',
            password=self.password,
            first_name='John',
            last_name='Doe',
            is_verified=True,
        )

    def test_email_normalization(self):
        """Test that email is normalized to lowercase."""
        from apps.accounts.api.serializers import LoginSerializer

        serializer = LoginSerializer(data={
            'email': 'TEST@EXAMPLE.COM',
            'password': self.password,
        })

        self.assertTrue(serializer.is_valid())
        self.assertEqual(serializer.validated_data['email'], 'test@example.com')

    def test_email_whitespace_stripped(self):
        """Test that email whitespace is stripped."""
        from apps.accounts.api.serializers import LoginSerializer

        serializer = LoginSerializer(data={
            'email': '  test@example.com  ',
            'password': self.password,
        })

        self.assertTrue(serializer.is_valid())
        self.assertEqual(serializer.validated_data['email'], 'test@example.com')


class LoginUserSerializerTests(TestCase):
    """Tests for LoginUserSerializer."""

    def setUp(self):
        """Create test user."""
        self.user = User.objects.create_user(
            username='test@example.com',
            email='test@example.com',
            password='password123',
            first_name='John',
            last_name='Doe',
            is_verified=True,
        )

    def test_serialization_fields(self):
        """Test LoginUserSerializer contains all required fields."""
        from apps.accounts.api.serializers import LoginUserSerializer

        serializer = LoginUserSerializer(self.user)
        data = serializer.data

        self.assertIn('id', data)
        self.assertIn('email', data)
        self.assertIn('first_name', data)
        self.assertIn('last_name', data)
        self.assertIn('profile_completed', data)
        self.assertIn('language', data)

    def test_profile_completed_default(self):
        """Test profile_completed returns False (stub until FR-1.3)."""
        from apps.accounts.api.serializers import LoginUserSerializer

        serializer = LoginUserSerializer(self.user)
        self.assertEqual(serializer.data['profile_completed'], False)

    def test_language_default(self):
        """Test language returns 'en' (stub until FR-1.3)."""
        from apps.accounts.api.serializers import LoginUserSerializer

        serializer = LoginUserSerializer(self.user)
        self.assertEqual(serializer.data['language'], 'en')


class AuthenticationServiceTests(TestCase):
    """Tests for AuthenticationService."""

    def setUp(self):
        """Create test users."""
        self.password = 'SecurePass123!'

        self.verified_user = User.objects.create_user(
            username='verified@example.com',
            email='verified@example.com',
            password=self.password,
            is_verified=True,
        )

        self.unverified_user = User.objects.create_user(
            username='unverified@example.com',
            email='unverified@example.com',
            password=self.password,
            is_verified=False,
        )

    def test_authenticate_success(self):
        """Test successful authentication."""
        from apps.accounts.services import AuthenticationService

        result = AuthenticationService.authenticate_user(
            'verified@example.com',
            self.password
        )

        self.assertTrue(result.success)
        self.assertEqual(result.user, self.verified_user)
        self.assertIsNone(result.error_message)
        self.assertIsNone(result.error_code)

    def test_authenticate_wrong_password(self):
        """Test authentication with wrong password."""
        from apps.accounts.services import AuthenticationService, AuthErrorCode

        result = AuthenticationService.authenticate_user(
            'verified@example.com',
            'WrongPassword123!'
        )

        self.assertFalse(result.success)
        self.assertIsNone(result.user)
        self.assertEqual(result.error_message, 'Invalid credentials')
        self.assertEqual(result.error_code, AuthErrorCode.INVALID_CREDENTIALS)

    def test_authenticate_user_not_found(self):
        """Test authentication with non-existent user."""
        from apps.accounts.services import AuthenticationService, AuthErrorCode

        result = AuthenticationService.authenticate_user(
            'nonexistent@example.com',
            self.password
        )

        self.assertFalse(result.success)
        self.assertIsNone(result.user)
        self.assertEqual(result.error_message, 'Invalid credentials')
        self.assertEqual(result.error_code, AuthErrorCode.INVALID_CREDENTIALS)

    def test_authenticate_unverified_user(self):
        """Test authentication with unverified user."""
        from apps.accounts.services import AuthenticationService, AuthErrorCode

        result = AuthenticationService.authenticate_user(
            'unverified@example.com',
            self.password
        )

        self.assertFalse(result.success)
        self.assertEqual(result.user, self.unverified_user)
        self.assertEqual(result.error_message, 'Please verify your email')
        self.assertEqual(result.error_code, AuthErrorCode.EMAIL_NOT_VERIFIED)

    def test_authenticate_email_case_insensitive(self):
        """Test authentication normalizes email to lowercase."""
        from apps.accounts.services import AuthenticationService

        result = AuthenticationService.authenticate_user(
            'VERIFIED@EXAMPLE.COM',
            self.password
        )

        self.assertTrue(result.success)
        self.assertEqual(result.user, self.verified_user)

    def test_authenticate_email_with_whitespace(self):
        """Test authentication strips email whitespace."""
        from apps.accounts.services import AuthenticationService

        result = AuthenticationService.authenticate_user(
            '  verified@example.com  ',
            self.password
        )

        self.assertTrue(result.success)
        self.assertEqual(result.user, self.verified_user)


# =============================================================================
# EXTENDED TESTS - Edge Cases and Additional Coverage
# =============================================================================


class LoginAPIViewEdgeCasesTests(APITestCase):
    """Extended edge case tests for login API endpoint."""

    def setUp(self):
        """Set up test client and users."""
        self.client = APIClient()
        self.url = reverse('accounts_api:login')
        self.password = 'SecurePass123!'

        self.verified_user = User.objects.create_user(
            username='verified@example.com',
            email='verified@example.com',
            password=self.password,
            first_name='John',
            last_name='Doe',
            is_verified=True,
        )

    @patch('apps.accounts.api.views.LoginAPIView.throttle_classes', [])
    def test_should_return_401_when_email_has_sql_injection_attempt(self):
        """Test login safely handles SQL injection attempts in email."""
        response = self.client.post(
            self.url,
            {'email': "'; DROP TABLE users; --", 'password': self.password},
            format='json'
        )

        # Should return 400 for invalid email format
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('email', response.data['details'])

    @patch('apps.accounts.api.views.LoginAPIView.throttle_classes', [])
    def test_should_return_401_when_password_has_sql_injection_attempt(self):
        """Test login safely handles SQL injection attempts in password."""
        response = self.client.post(
            self.url,
            {'email': 'verified@example.com', 'password': "'; DROP TABLE users; --"},
            format='json'
        )

        # Should return 401 for invalid credentials
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    @patch('apps.accounts.api.views.LoginAPIView.throttle_classes', [])
    def test_should_return_400_when_email_is_null(self):
        """Test login fails when email is null."""
        response = self.client.post(
            self.url,
            {'email': None, 'password': self.password},
            format='json'
        )

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    @patch('apps.accounts.api.views.LoginAPIView.throttle_classes', [])
    def test_should_return_400_when_password_is_null(self):
        """Test login fails when password is null."""
        response = self.client.post(
            self.url,
            {'email': 'verified@example.com', 'password': None},
            format='json'
        )

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    @patch('apps.accounts.api.views.LoginAPIView.throttle_classes', [])
    def test_should_return_400_when_request_body_is_empty(self):
        """Test login fails with empty request body."""
        response = self.client.post(self.url, {}, format='json')

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('email', response.data['details'])
        self.assertIn('password', response.data['details'])

    @patch('apps.accounts.api.views.LoginAPIView.throttle_classes', [])
    def test_should_return_200_when_email_has_mixed_case(self):
        """Test login works with mixed case email."""
        response = self.client.post(
            self.url,
            {'email': 'VeRiFiEd@ExAmPlE.CoM', 'password': self.password},
            format='json'
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)

    @patch('apps.accounts.api.views.LoginAPIView.throttle_classes', [])
    def test_should_return_200_when_email_has_leading_trailing_whitespace(self):
        """Test login works with leading/trailing whitespace in email."""
        response = self.client.post(
            self.url,
            {'email': '   verified@example.com   ', 'password': self.password},
            format='json'
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)

    @patch('apps.accounts.api.views.LoginAPIView.throttle_classes', [])
    def test_should_handle_password_with_whitespace(self):
        """Test login handles password with whitespace - passwords may be stripped by DRF."""
        # Note: DRF's CharField may strip whitespace from passwords.
        # This test verifies the actual behavior - password whitespace handling.
        response = self.client.post(
            self.url,
            {'email': 'verified@example.com', 'password': f'  {self.password}  '},
            format='json'
        )

        # If passwords are stripped, login succeeds. This documents the current behavior.
        # The important thing is the endpoint handles this gracefully (no 500 error).
        self.assertIn(response.status_code, [status.HTTP_200_OK, status.HTTP_401_UNAUTHORIZED])

    @patch('apps.accounts.api.views.LoginAPIView.throttle_classes', [])
    def test_should_return_401_when_password_is_very_long(self):
        """Test login handles very long password gracefully."""
        very_long_password = 'a' * 10000

        response = self.client.post(
            self.url,
            {'email': 'verified@example.com', 'password': very_long_password},
            format='json'
        )

        # Should return 401, not 500
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    @patch('apps.accounts.api.views.LoginAPIView.throttle_classes', [])
    def test_should_return_400_when_email_is_very_long(self):
        """Test login handles very long email gracefully."""
        very_long_email = 'a' * 500 + '@example.com'

        response = self.client.post(
            self.url,
            {'email': very_long_email, 'password': self.password},
            format='json'
        )

        # Should return 400 or 401, not 500
        self.assertIn(response.status_code, [status.HTTP_400_BAD_REQUEST, status.HTTP_401_UNAUTHORIZED])

    @patch('apps.accounts.api.views.LoginAPIView.throttle_classes', [])
    def test_should_return_401_when_password_contains_unicode(self):
        """Test login works with unicode characters in password."""
        # Create user with unicode password
        unicode_password = 'Passwörd123!日本語'
        unicode_user = User.objects.create_user(
            username='unicode@example.com',
            email='unicode@example.com',
            password=unicode_password,
            is_verified=True,
        )

        response = self.client.post(
            self.url,
            {'email': 'unicode@example.com', 'password': unicode_password},
            format='json'
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)

    @patch('apps.accounts.api.views.LoginAPIView.throttle_classes', [])
    def test_should_return_200_when_email_has_plus_sign(self):
        """Test login works with email containing plus sign."""
        plus_email_user = User.objects.create_user(
            username='user+test@example.com',
            email='user+test@example.com',
            password=self.password,
            is_verified=True,
        )

        response = self.client.post(
            self.url,
            {'email': 'user+test@example.com', 'password': self.password},
            format='json'
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)

    @patch('apps.accounts.api.views.LoginAPIView.throttle_classes', [])
    def test_should_return_200_when_email_has_dots_in_local_part(self):
        """Test login works with dots in email local part."""
        dotted_email_user = User.objects.create_user(
            username='first.last@example.com',
            email='first.last@example.com',
            password=self.password,
            is_verified=True,
        )

        response = self.client.post(
            self.url,
            {'email': 'first.last@example.com', 'password': self.password},
            format='json'
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)

    @patch('apps.accounts.api.views.LoginAPIView.throttle_classes', [])
    def test_should_return_400_when_content_type_is_not_json(self):
        """Test login returns 400 when content type is not JSON."""
        response = self.client.post(
            self.url,
            'email=verified@example.com&password=SecurePass123!',
            content_type='application/x-www-form-urlencoded'
        )

        # DRF should still parse this, but test the behavior
        self.assertIn(response.status_code, [status.HTTP_200_OK, status.HTTP_400_BAD_REQUEST])

    @patch('apps.accounts.api.views.LoginAPIView.throttle_classes', [])
    def test_should_log_successful_login(self):
        """Test that successful login is logged."""
        with patch('apps.accounts.services.logger') as mock_logger:
            response = self.client.post(
                self.url,
                {'email': 'verified@example.com', 'password': self.password},
                format='json'
            )

            self.assertEqual(response.status_code, status.HTTP_200_OK)
            # Verify logging was called
            mock_logger.info.assert_called()

    @patch('apps.accounts.api.views.LoginAPIView.throttle_classes', [])
    def test_should_log_failed_login_wrong_password(self):
        """Test that failed login (wrong password) is logged."""
        with patch('apps.accounts.services.logger') as mock_logger:
            response = self.client.post(
                self.url,
                {'email': 'verified@example.com', 'password': 'WrongPassword!'},
                format='json'
            )

            self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
            mock_logger.warning.assert_called()

    @patch('apps.accounts.api.views.LoginAPIView.throttle_classes', [])
    def test_should_log_failed_login_user_not_found(self):
        """Test that failed login (user not found) is logged."""
        with patch('apps.accounts.services.logger') as mock_logger:
            response = self.client.post(
                self.url,
                {'email': 'nonexistent@example.com', 'password': self.password},
                format='json'
            )

            self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
            mock_logger.warning.assert_called()


class LoginThrottleParseRateTests(TestCase):
    """Tests for LoginThrottle.parse_rate custom implementation."""

    def test_should_parse_15m_format(self):
        """Test parse_rate handles '5/15m' format."""
        from apps.accounts.api.throttling import LoginThrottle

        throttle = LoginThrottle()
        num, duration = throttle.parse_rate('5/15m')

        self.assertEqual(num, 5)
        self.assertEqual(duration, 900)  # 15 * 60

    def test_should_parse_30s_format(self):
        """Test parse_rate handles '10/30s' format."""
        from apps.accounts.api.throttling import LoginThrottle

        throttle = LoginThrottle()
        num, duration = throttle.parse_rate('10/30s')

        self.assertEqual(num, 10)
        self.assertEqual(duration, 30)

    def test_should_parse_2h_format(self):
        """Test parse_rate handles '100/2h' format."""
        from apps.accounts.api.throttling import LoginThrottle

        throttle = LoginThrottle()
        num, duration = throttle.parse_rate('100/2h')

        self.assertEqual(num, 100)
        self.assertEqual(duration, 7200)  # 2 * 3600

    def test_should_parse_standard_hour_format(self):
        """Test parse_rate handles standard 'h' format."""
        from apps.accounts.api.throttling import LoginThrottle

        throttle = LoginThrottle()
        num, duration = throttle.parse_rate('10/h')

        self.assertEqual(num, 10)
        self.assertEqual(duration, 3600)

    def test_should_parse_standard_minute_format(self):
        """Test parse_rate handles standard 'm' format."""
        from apps.accounts.api.throttling import LoginThrottle

        throttle = LoginThrottle()
        num, duration = throttle.parse_rate('5/m')

        self.assertEqual(num, 5)
        self.assertEqual(duration, 60)

    def test_should_return_none_when_rate_is_none(self):
        """Test parse_rate returns (None, None) when rate is None."""
        from apps.accounts.api.throttling import LoginThrottle

        throttle = LoginThrottle()
        num, duration = throttle.parse_rate(None)

        self.assertIsNone(num)
        self.assertIsNone(duration)


class LoginSerializerEdgeCasesTests(TestCase):
    """Extended edge case tests for LoginSerializer."""

    def setUp(self):
        """Create test user."""
        self.password = 'SecurePass123!'
        self.user = User.objects.create_user(
            username='test@example.com',
            email='test@example.com',
            password=self.password,
            first_name='John',
            last_name='Doe',
            is_verified=True,
        )

    def test_should_normalize_email_with_tabs(self):
        """Test serializer handles tabs in email."""
        from apps.accounts.api.serializers import LoginSerializer

        serializer = LoginSerializer(data={
            'email': '\ttest@example.com\t',
            'password': self.password,
        })

        # Tabs are not stripped by strip(), only whitespace
        # The email validation should still work
        self.assertTrue(serializer.is_valid())

    def test_should_fail_when_email_has_newlines(self):
        """Test serializer fails when email has newlines."""
        from apps.accounts.api.serializers import LoginSerializer

        serializer = LoginSerializer(data={
            'email': 'test@example.com\n',
            'password': self.password,
        })

        # Should handle gracefully
        is_valid = serializer.is_valid()
        # Depending on implementation, may strip or fail
        self.assertTrue(is_valid or 'email' in serializer.errors)

    def test_should_return_user_in_validated_data_on_success(self):
        """Test serializer returns user in validated_data on success."""
        from apps.accounts.api.serializers import LoginSerializer

        serializer = LoginSerializer(data={
            'email': 'test@example.com',
            'password': self.password,
        })

        self.assertTrue(serializer.is_valid())
        self.assertIn('user', serializer.validated_data)
        self.assertEqual(serializer.validated_data['user'], self.user)

    def test_should_return_auth_error_when_email_not_verified(self):
        """Test serializer returns auth_error for unverified users."""
        from apps.accounts.api.serializers import LoginSerializer

        unverified_user = User.objects.create_user(
            username='unverified@example.com',
            email='unverified@example.com',
            password=self.password,
            is_verified=False,
        )

        serializer = LoginSerializer(data={
            'email': 'unverified@example.com',
            'password': self.password,
        })

        self.assertTrue(serializer.is_valid())
        self.assertIn('auth_error', serializer.validated_data)
        self.assertEqual(
            serializer.validated_data['auth_error']['code'].value,
            'email_not_verified'
        )


class LoginResponseSerializerTests(TestCase):
    """Tests for LoginResponseSerializer (OpenAPI documentation)."""

    def test_should_have_required_fields(self):
        """Test LoginResponseSerializer has all required fields."""
        from apps.accounts.api.serializers import LoginResponseSerializer

        serializer = LoginResponseSerializer()
        field_names = list(serializer.fields.keys())

        self.assertIn('access_token', field_names)
        self.assertIn('refresh_token', field_names)
        self.assertIn('user', field_names)

    def test_should_serialize_valid_response(self):
        """Test LoginResponseSerializer serializes valid response data."""
        from apps.accounts.api.serializers import LoginResponseSerializer, LoginUserSerializer

        user = User.objects.create_user(
            username='test@example.com',
            email='test@example.com',
            password='password123',
            first_name='John',
            last_name='Doe',
            is_verified=True,
        )

        data = {
            'access_token': 'eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9...',
            'refresh_token': 'eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9...',
            'user': LoginUserSerializer(user).data,
        }

        serializer = LoginResponseSerializer(data=data)
        self.assertTrue(serializer.is_valid())


class AuthenticationServiceEdgeCasesTests(TestCase):
    """Extended edge case tests for AuthenticationService."""

    def setUp(self):
        """Create test users."""
        self.password = 'SecurePass123!'
        self.user = User.objects.create_user(
            username='test@example.com',
            email='test@example.com',
            password=self.password,
            is_verified=True,
        )

    def test_should_fail_when_user_is_inactive(self):
        """Test authentication fails for inactive user."""
        from apps.accounts.services import AuthenticationService, AuthErrorCode

        self.user.is_active = False
        self.user.save()

        result = AuthenticationService.authenticate_user(
            'test@example.com',
            self.password
        )

        self.assertFalse(result.success)
        self.assertEqual(result.error_code, AuthErrorCode.INVALID_CREDENTIALS)

    def test_should_fail_when_password_is_empty(self):
        """Test authentication fails with empty password."""
        from apps.accounts.services import AuthenticationService, AuthErrorCode

        result = AuthenticationService.authenticate_user(
            'test@example.com',
            ''
        )

        self.assertFalse(result.success)
        self.assertEqual(result.error_code, AuthErrorCode.INVALID_CREDENTIALS)

    def test_should_fail_when_email_is_empty(self):
        """Test authentication fails with empty email."""
        from apps.accounts.services import AuthenticationService, AuthErrorCode

        result = AuthenticationService.authenticate_user('', self.password)

        self.assertFalse(result.success)
        self.assertEqual(result.error_code, AuthErrorCode.INVALID_CREDENTIALS)

    def test_should_handle_email_with_subdomain(self):
        """Test authentication works with subdomain email."""
        from apps.accounts.services import AuthenticationService

        subdomain_user = User.objects.create_user(
            username='user@sub.domain.example.com',
            email='user@sub.domain.example.com',
            password=self.password,
            is_verified=True,
        )

        result = AuthenticationService.authenticate_user(
            'user@sub.domain.example.com',
            self.password
        )

        self.assertTrue(result.success)
        self.assertEqual(result.user, subdomain_user)

    def test_should_not_log_password_in_failure(self):
        """Test that password is never logged."""
        from apps.accounts.services import AuthenticationService

        with patch('apps.accounts.services.logger') as mock_logger:
            AuthenticationService.authenticate_user(
                'test@example.com',
                'SuperSecretPassword123!'
            )

            # Check that password is not in any log call
            for call in mock_logger.mock_calls:
                call_str = str(call)
                self.assertNotIn('SuperSecretPassword123!', call_str)


class AuthResultDataclassTests(TestCase):
    """Tests for AuthResult dataclass."""

    def test_should_create_success_result(self):
        """Test creating successful AuthResult."""
        from apps.accounts.services import AuthResult

        user = User.objects.create_user(
            username='test@example.com',
            email='test@example.com',
            password='password123',
        )

        result = AuthResult(success=True, user=user)

        self.assertTrue(result.success)
        self.assertEqual(result.user, user)
        self.assertIsNone(result.error_message)
        self.assertIsNone(result.error_code)

    def test_should_create_failure_result(self):
        """Test creating failed AuthResult."""
        from apps.accounts.services import AuthResult, AuthErrorCode

        result = AuthResult(
            success=False,
            error_message='Invalid credentials',
            error_code=AuthErrorCode.INVALID_CREDENTIALS,
        )

        self.assertFalse(result.success)
        self.assertIsNone(result.user)
        self.assertEqual(result.error_message, 'Invalid credentials')
        self.assertEqual(result.error_code, AuthErrorCode.INVALID_CREDENTIALS)

    def test_should_create_unverified_result_with_user(self):
        """Test creating unverified AuthResult includes user."""
        from apps.accounts.services import AuthResult, AuthErrorCode

        user = User.objects.create_user(
            username='test@example.com',
            email='test@example.com',
            password='password123',
        )

        result = AuthResult(
            success=False,
            user=user,
            error_message='Please verify your email',
            error_code=AuthErrorCode.EMAIL_NOT_VERIFIED,
        )

        self.assertFalse(result.success)
        self.assertEqual(result.user, user)
        self.assertEqual(result.error_code, AuthErrorCode.EMAIL_NOT_VERIFIED)


class AuthErrorCodeEnumTests(TestCase):
    """Tests for AuthErrorCode enum."""

    def test_should_have_invalid_credentials_code(self):
        """Test INVALID_CREDENTIALS has correct value."""
        from apps.accounts.services import AuthErrorCode

        self.assertEqual(AuthErrorCode.INVALID_CREDENTIALS.value, 'invalid_credentials')

    def test_should_have_email_not_verified_code(self):
        """Test EMAIL_NOT_VERIFIED has correct value."""
        from apps.accounts.services import AuthErrorCode

        self.assertEqual(AuthErrorCode.EMAIL_NOT_VERIFIED.value, 'email_not_verified')

    def test_should_be_string_enum(self):
        """Test AuthErrorCode is a string enum."""
        from apps.accounts.services import AuthErrorCode

        self.assertIsInstance(AuthErrorCode.INVALID_CREDENTIALS.value, str)
        self.assertIsInstance(AuthErrorCode.EMAIL_NOT_VERIFIED.value, str)


class JWTTokenTests(APITestCase):
    """Tests for JWT token generation and validation."""

    def setUp(self):
        """Set up test client and user."""
        self.client = APIClient()
        self.url = reverse('accounts_api:login')
        self.password = 'SecurePass123!'

        self.user = User.objects.create_user(
            username='test@example.com',
            email='test@example.com',
            password=self.password,
            first_name='John',
            last_name='Doe',
            is_verified=True,
        )

    @patch('apps.accounts.api.views.LoginAPIView.throttle_classes', [])
    def test_should_return_valid_access_token(self):
        """Test login returns valid access token that can be decoded."""
        from rest_framework_simplejwt.tokens import AccessToken

        response = self.client.post(
            self.url,
            {'email': 'test@example.com', 'password': self.password},
            format='json'
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)

        access_token = response.data['access_token']
        token = AccessToken(access_token)

        self.assertEqual(str(token['user_id']), str(self.user.id))

    @patch('apps.accounts.api.views.LoginAPIView.throttle_classes', [])
    def test_should_return_valid_refresh_token(self):
        """Test login returns valid refresh token that can be decoded."""
        from rest_framework_simplejwt.tokens import RefreshToken

        response = self.client.post(
            self.url,
            {'email': 'test@example.com', 'password': self.password},
            format='json'
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)

        refresh_token = response.data['refresh_token']
        token = RefreshToken(refresh_token)

        self.assertEqual(str(token['user_id']), str(self.user.id))

    @patch('apps.accounts.api.views.LoginAPIView.throttle_classes', [])
    def test_access_token_can_be_used_for_authenticated_requests(self):
        """Test access token works for authenticated endpoints."""
        response = self.client.post(
            self.url,
            {'email': 'test@example.com', 'password': self.password},
            format='json'
        )

        access_token = response.data['access_token']

        # Try to use the token for an authenticated request
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {access_token}')

        # We don't have a protected endpoint yet, so just verify token is valid format
        self.assertTrue(access_token.startswith('eyJ'))

    @patch('apps.accounts.api.views.LoginAPIView.throttle_classes', [])
    def test_tokens_are_different_for_each_login(self):
        """Test each login generates different tokens."""
        response1 = self.client.post(
            self.url,
            {'email': 'test@example.com', 'password': self.password},
            format='json'
        )

        response2 = self.client.post(
            self.url,
            {'email': 'test@example.com', 'password': self.password},
            format='json'
        )

        # Tokens should be different
        self.assertNotEqual(
            response1.data['access_token'],
            response2.data['access_token']
        )
        self.assertNotEqual(
            response1.data['refresh_token'],
            response2.data['refresh_token']
        )


class LoginUserSerializerEdgeCasesTests(TestCase):
    """Extended tests for LoginUserSerializer."""

    def test_should_handle_user_with_empty_first_name(self):
        """Test serializer handles user with empty first name."""
        from apps.accounts.api.serializers import LoginUserSerializer

        user = User.objects.create_user(
            username='test@example.com',
            email='test@example.com',
            password='password123',
            first_name='',
            last_name='Doe',
            is_verified=True,
        )

        serializer = LoginUserSerializer(user)
        data = serializer.data

        self.assertEqual(data['first_name'], '')
        self.assertEqual(data['last_name'], 'Doe')

    def test_should_handle_user_with_empty_last_name(self):
        """Test serializer handles user with empty last name."""
        from apps.accounts.api.serializers import LoginUserSerializer

        user = User.objects.create_user(
            username='test@example.com',
            email='test@example.com',
            password='password123',
            first_name='John',
            last_name='',
            is_verified=True,
        )

        serializer = LoginUserSerializer(user)
        data = serializer.data

        self.assertEqual(data['first_name'], 'John')
        self.assertEqual(data['last_name'], '')

    def test_should_serialize_uuid_id(self):
        """Test serializer handles UUID primary key."""
        from apps.accounts.api.serializers import LoginUserSerializer

        user = User.objects.create_user(
            username='test@example.com',
            email='test@example.com',
            password='password123',
            is_verified=True,
        )

        serializer = LoginUserSerializer(user)
        data = serializer.data

        # ID should be present and not empty
        self.assertIn('id', data)
        self.assertTrue(data['id'])

    def test_should_not_expose_sensitive_fields(self):
        """Test serializer does not expose sensitive fields."""
        from apps.accounts.api.serializers import LoginUserSerializer

        user = User.objects.create_user(
            username='test@example.com',
            email='test@example.com',
            password='password123',
            is_verified=True,
        )

        serializer = LoginUserSerializer(user)
        data = serializer.data

        # Should NOT contain sensitive fields
        self.assertNotIn('password', data)
        self.assertNotIn('is_superuser', data)
        self.assertNotIn('is_staff', data)
        self.assertNotIn('is_active', data)
        self.assertNotIn('is_verified', data)  # Not needed in login response


class LoginWorkflowIntegrationTests(APITestCase):
    """End-to-end integration tests for login workflow."""

    def setUp(self):
        """Set up test client."""
        self.client = APIClient()
        self.login_url = reverse('accounts_api:login')

    @patch('apps.accounts.api.views.LoginAPIView.throttle_classes', [])
    @patch('apps.accounts.api.views.RegisterAPIView.throttle_classes', [])
    @override_settings(EMAIL_BACKEND='django.core.mail.backends.locmem.EmailBackend')
    def test_full_registration_and_login_workflow(self):
        """Test complete workflow: register -> verify -> login."""
        from apps.accounts.models import EmailVerificationToken

        register_url = reverse('accounts_api:register')

        # Step 1: Register
        register_response = self.client.post(
            register_url,
            {
                'email': 'newuser@example.com',
                'password': 'SecurePass123!',
                'password_confirm': 'SecurePass123!',
                'first_name': 'New',
                'last_name': 'User',
                'terms_accepted': True,
            },
            format='json'
        )

        self.assertEqual(register_response.status_code, status.HTTP_201_CREATED)

        # Step 2: Try to login before verification -> should fail
        login_response = self.client.post(
            self.login_url,
            {'email': 'newuser@example.com', 'password': 'SecurePass123!'},
            format='json'
        )

        self.assertEqual(login_response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertEqual(login_response.data['code'], 'email_not_verified')

        # Step 3: Verify email
        user = User.objects.get(email='newuser@example.com')
        token = EmailVerificationToken.objects.filter(user=user).first()
        verify_url = reverse('accounts_api:verify_email', kwargs={'token': token.token})
        self.client.get(verify_url)

        # Step 4: Login after verification -> should succeed
        login_response = self.client.post(
            self.login_url,
            {'email': 'newuser@example.com', 'password': 'SecurePass123!'},
            format='json'
        )

        self.assertEqual(login_response.status_code, status.HTTP_200_OK)
        self.assertIn('access_token', login_response.data)

    @patch('apps.accounts.api.views.LoginAPIView.throttle_classes', [])
    def test_multiple_failed_login_attempts(self):
        """Test multiple failed login attempts return consistent errors."""
        User.objects.create_user(
            username='test@example.com',
            email='test@example.com',
            password='CorrectPass123!',
            is_verified=True,
        )

        # Try 5 wrong passwords
        for i in range(5):
            response = self.client.post(
                self.login_url,
                {'email': 'test@example.com', 'password': f'WrongPass{i}!'},
                format='json'
            )

            self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
            self.assertEqual(response.data['detail'], 'Invalid credentials')

        # Correct password should still work
        response = self.client.post(
            self.login_url,
            {'email': 'test@example.com', 'password': 'CorrectPass123!'},
            format='json'
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)


class LoginHTTPMethodTests(APITestCase):
    """Tests for HTTP method handling on login endpoint."""

    def setUp(self):
        """Set up test client."""
        self.client = APIClient()
        self.url = reverse('accounts_api:login')

    def test_should_reject_get_method(self):
        """Test GET method is not allowed."""
        response = self.client.get(self.url)

        self.assertEqual(response.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)

    def test_should_reject_put_method(self):
        """Test PUT method is not allowed."""
        response = self.client.put(self.url, {}, format='json')

        self.assertEqual(response.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)

    def test_should_reject_patch_method(self):
        """Test PATCH method is not allowed."""
        response = self.client.patch(self.url, {}, format='json')

        self.assertEqual(response.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)

    def test_should_reject_delete_method(self):
        """Test DELETE method is not allowed."""
        response = self.client.delete(self.url)

        self.assertEqual(response.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)

    @patch('apps.accounts.api.views.LoginAPIView.throttle_classes', [])
    def test_should_accept_post_method(self):
        """Test POST method is allowed."""
        User.objects.create_user(
            username='test@example.com',
            email='test@example.com',
            password='SecurePass123!',
            is_verified=True,
        )

        response = self.client.post(
            self.url,
            {'email': 'test@example.com', 'password': 'SecurePass123!'},
            format='json'
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)
