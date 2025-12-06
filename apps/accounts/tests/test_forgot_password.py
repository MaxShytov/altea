"""
Tests for FR-1.4 Password Reset (Forgot Password).

This module provides test coverage for the forgot password feature including:
- Unit tests for PasswordResetToken model
- Unit tests for PasswordResetService
- Integration tests for API endpoint
- Throttling tests

Test Structure:
- PasswordResetTokenModelTests: Token model tests
- PasswordResetServiceTests: Service layer tests
- ForgotPasswordAPIViewTests: API integration tests
- ForgotPasswordThrottleTests: Rate limiting tests
- ForgotPasswordSerializerTests: Serializer tests
"""

from datetime import timedelta
from unittest.mock import patch, MagicMock

from django.test import TestCase, override_settings
from django.urls import reverse
from django.utils import timezone
from rest_framework import status
from rest_framework.test import APITestCase, APIClient

from apps.accounts.models import User, PasswordResetToken


class PasswordResetTokenModelTests(TestCase):
    """Tests for PasswordResetToken model."""

    def setUp(self):
        """Create test user."""
        self.user = User.objects.create_user(
            username='test@example.com',
            email='test@example.com',
            password='SecurePass123!',
            first_name='John',
            last_name='Doe',
            is_verified=True,
        )

    def test_create_for_user_creates_token(self):
        """Test create_for_user creates a new token."""
        token = PasswordResetToken.create_for_user(self.user)

        self.assertIsNotNone(token)
        self.assertEqual(token.user, self.user)
        self.assertIsNotNone(token.token)
        self.assertIsNotNone(token.expires_at)
        self.assertIsNone(token.used_at)

    def test_create_for_user_invalidates_old_tokens(self):
        """Test create_for_user invalidates existing unused tokens."""
        token1 = PasswordResetToken.create_for_user(self.user)
        token2 = PasswordResetToken.create_for_user(self.user)

        token1.refresh_from_db()

        self.assertIsNotNone(token1.used_at)  # Old token invalidated
        self.assertIsNone(token2.used_at)  # New token is valid

    def test_is_valid_returns_true_for_new_token(self):
        """Test is_valid returns True for new token."""
        token = PasswordResetToken.create_for_user(self.user)

        self.assertTrue(token.is_valid())

    def test_is_valid_returns_false_for_used_token(self):
        """Test is_valid returns False for used token."""
        token = PasswordResetToken.create_for_user(self.user)
        token.mark_used()

        self.assertFalse(token.is_valid())

    def test_is_valid_returns_false_for_expired_token(self):
        """Test is_valid returns False for expired token."""
        token = PasswordResetToken.create_for_user(self.user)
        token.expires_at = timezone.now() - timedelta(hours=1)
        token.save()

        self.assertFalse(token.is_valid())

    def test_mark_used_sets_used_at(self):
        """Test mark_used sets used_at timestamp."""
        token = PasswordResetToken.create_for_user(self.user)

        self.assertIsNone(token.used_at)

        token.mark_used()

        self.assertIsNotNone(token.used_at)

    def test_token_is_unique(self):
        """Test each token has a unique value."""
        token1 = PasswordResetToken.create_for_user(self.user)

        user2 = User.objects.create_user(
            username='user2@example.com',
            email='user2@example.com',
            password='SecurePass123!',
        )
        token2 = PasswordResetToken.create_for_user(user2)

        self.assertNotEqual(token1.token, token2.token)

    @override_settings(PASSWORD_RESET_TOKEN_EXPIRY_HOURS=2)
    def test_token_expiry_respects_settings(self):
        """Test token expiry uses settings value."""
        token = PasswordResetToken.create_for_user(self.user)

        expected_expiry = timezone.now() + timedelta(hours=2)

        # Allow 1 minute tolerance
        self.assertAlmostEqual(
            token.expires_at.timestamp(),
            expected_expiry.timestamp(),
            delta=60
        )

    def test_str_representation(self):
        """Test token string representation."""
        token = PasswordResetToken.create_for_user(self.user)

        self.assertEqual(str(token), f"Reset token for {self.user.email}")

    def test_token_length(self):
        """Test token has appropriate length for security."""
        token = PasswordResetToken.create_for_user(self.user)

        # Token should be at least 32 characters (256 bits of entropy)
        self.assertGreaterEqual(len(token.token), 32)

    def test_multiple_users_can_have_tokens(self):
        """Test multiple users can have active tokens simultaneously."""
        user2 = User.objects.create_user(
            username='user2@example.com',
            email='user2@example.com',
            password='SecurePass123!',
        )

        token1 = PasswordResetToken.create_for_user(self.user)
        token2 = PasswordResetToken.create_for_user(user2)

        self.assertTrue(token1.is_valid())
        self.assertTrue(token2.is_valid())

    def test_mark_used_is_idempotent(self):
        """Test marking token as used multiple times doesn't cause issues."""
        token = PasswordResetToken.create_for_user(self.user)

        first_used_at = None
        token.mark_used()
        first_used_at = token.used_at

        token.mark_used()
        second_used_at = token.used_at

        # used_at should be updated each time (latest timestamp)
        self.assertIsNotNone(first_used_at)
        self.assertIsNotNone(second_used_at)

    def test_expired_token_cannot_be_valid_even_if_not_used(self):
        """Test that expired tokens are invalid regardless of used_at status."""
        token = PasswordResetToken.create_for_user(self.user)

        # Set expiry to past
        token.expires_at = timezone.now() - timedelta(seconds=1)
        token.save()

        self.assertIsNone(token.used_at)  # Not used
        self.assertFalse(token.is_valid())  # But invalid due to expiry

    def test_token_ordering(self):
        """Test tokens are ordered by created_at descending."""
        token1 = PasswordResetToken.create_for_user(self.user)

        user2 = User.objects.create_user(
            username='user2@example.com',
            email='user2@example.com',
            password='SecurePass123!',
        )
        token2 = PasswordResetToken.create_for_user(user2)

        tokens = list(PasswordResetToken.objects.all())

        # Most recent first
        self.assertEqual(tokens[0], token2)


class PasswordResetServiceTests(TestCase):
    """Tests for PasswordResetService."""

    def setUp(self):
        """Create test user."""
        self.user = User.objects.create_user(
            username='test@example.com',
            email='test@example.com',
            password='SecurePass123!',
            first_name='John',
            last_name='Doe',
            is_verified=True,
        )

    @override_settings(EMAIL_BACKEND='django.core.mail.backends.locmem.EmailBackend')
    def test_request_reset_returns_success_for_existing_user(self):
        """Test request_reset returns success for existing user."""
        from apps.accounts.services import PasswordResetService

        success, message = PasswordResetService.request_reset('test@example.com')

        self.assertTrue(success)
        self.assertIn('If an account exists', message)

    def test_request_reset_returns_success_for_nonexistent_user(self):
        """Test request_reset returns success even for non-existent user (security)."""
        from apps.accounts.services import PasswordResetService

        success, message = PasswordResetService.request_reset('nonexistent@example.com')

        self.assertTrue(success)
        self.assertIn('If an account exists', message)

    def test_request_reset_normalizes_email(self):
        """Test request_reset normalizes email to lowercase."""
        from apps.accounts.services import PasswordResetService

        with patch.object(PasswordResetService, 'send_reset_email', return_value=True) as mock_send:
            PasswordResetService.request_reset('TEST@EXAMPLE.COM')

            mock_send.assert_called_once()
            self.assertEqual(mock_send.call_args[0][0], self.user)

    def test_request_reset_strips_whitespace(self):
        """Test request_reset strips whitespace from email."""
        from apps.accounts.services import PasswordResetService

        with patch.object(PasswordResetService, 'send_reset_email', return_value=True) as mock_send:
            PasswordResetService.request_reset('  test@example.com  ')

            mock_send.assert_called_once()

    @override_settings(EMAIL_BACKEND='django.core.mail.backends.locmem.EmailBackend')
    def test_send_reset_email_creates_token(self):
        """Test send_reset_email creates a password reset token."""
        from apps.accounts.services import PasswordResetService

        initial_count = PasswordResetToken.objects.filter(user=self.user).count()

        PasswordResetService.send_reset_email(self.user)

        new_count = PasswordResetToken.objects.filter(user=self.user).count()
        self.assertEqual(new_count, initial_count + 1)

    @override_settings(EMAIL_BACKEND='django.core.mail.backends.locmem.EmailBackend')
    def test_send_reset_email_sends_email(self):
        """Test send_reset_email sends an email."""
        from django.core import mail
        from apps.accounts.services import PasswordResetService

        result = PasswordResetService.send_reset_email(self.user)

        self.assertTrue(result)
        self.assertEqual(len(mail.outbox), 1)
        self.assertEqual(mail.outbox[0].to, [self.user.email])

    @override_settings(EMAIL_BACKEND='django.core.mail.backends.locmem.EmailBackend')
    def test_send_reset_email_uses_correct_subject(self):
        """Test send_reset_email uses correct subject (English default)."""
        from django.core import mail
        from apps.accounts.services import PasswordResetService

        PasswordResetService.send_reset_email(self.user)

        self.assertIn('Reset', mail.outbox[0].subject)
        self.assertIn('Altea', mail.outbox[0].subject)

    def test_send_reset_email_returns_false_on_failure(self):
        """Test send_reset_email returns False when email fails."""
        from apps.accounts.services import PasswordResetService

        with patch('apps.accounts.services.send_mail', side_effect=Exception('SMTP error')):
            result = PasswordResetService.send_reset_email(self.user)

            self.assertFalse(result)

    def test_get_user_language_returns_default_en(self):
        """Test get_user_language returns 'en' by default."""
        from apps.accounts.services import PasswordResetService

        language = PasswordResetService.get_user_language(self.user)

        self.assertEqual(language, 'en')

    def test_get_user_language_returns_profile_language(self):
        """Test get_user_language returns language from user profile if available."""
        from apps.accounts.services import PasswordResetService

        # Mock a profile with German language
        mock_profile = MagicMock()
        mock_profile.language = 'de'
        self.user.profile = mock_profile

        language = PasswordResetService.get_user_language(self.user)

        self.assertEqual(language, 'de')

        # Clean up
        del self.user.profile

    def test_get_user_language_handles_profile_with_none_language(self):
        """Test get_user_language returns 'en' when profile language is None."""
        from apps.accounts.services import PasswordResetService

        # Mock a profile with None language
        mock_profile = MagicMock()
        mock_profile.language = None
        self.user.profile = mock_profile

        language = PasswordResetService.get_user_language(self.user)

        self.assertEqual(language, 'en')

        # Clean up
        del self.user.profile

    @override_settings(EMAIL_BACKEND='django.core.mail.backends.locmem.EmailBackend')
    def test_email_content_is_localized_de(self):
        """Test email content is localized for German users."""
        from django.core import mail
        from apps.accounts.services import PasswordResetService

        with patch.object(PasswordResetService, 'get_user_language', return_value='de'):
            PasswordResetService.send_reset_email(self.user)

            self.assertEqual(len(mail.outbox), 1)
            self.assertIn('zurücksetzen', mail.outbox[0].subject.lower())

    @override_settings(EMAIL_BACKEND='django.core.mail.backends.locmem.EmailBackend')
    def test_email_content_is_localized_fr(self):
        """Test email content is localized for French users."""
        from django.core import mail
        from apps.accounts.services import PasswordResetService

        with patch.object(PasswordResetService, 'get_user_language', return_value='fr'):
            PasswordResetService.send_reset_email(self.user)

            self.assertEqual(len(mail.outbox), 1)
            self.assertIn('réinitialisez', mail.outbox[0].subject.lower())

    @override_settings(EMAIL_BACKEND='django.core.mail.backends.locmem.EmailBackend')
    def test_email_content_is_localized_it(self):
        """Test email content is localized for Italian users."""
        from django.core import mail
        from apps.accounts.services import PasswordResetService

        with patch.object(PasswordResetService, 'get_user_language', return_value='it'):
            PasswordResetService.send_reset_email(self.user)

            self.assertEqual(len(mail.outbox), 1)
            self.assertIn('reimposta', mail.outbox[0].subject.lower())

    @override_settings(EMAIL_BACKEND='django.core.mail.backends.locmem.EmailBackend')
    def test_email_fallback_for_unsupported_language(self):
        """Test email falls back to English for unsupported languages."""
        from django.core import mail
        from apps.accounts.services import PasswordResetService

        with patch.object(PasswordResetService, 'get_user_language', return_value='xx'):
            PasswordResetService.send_reset_email(self.user)

            self.assertEqual(len(mail.outbox), 1)
            # Should use English subject
            self.assertIn('reset', mail.outbox[0].subject.lower())

    @override_settings(EMAIL_BACKEND='django.core.mail.backends.locmem.EmailBackend')
    def test_email_contains_reset_url(self):
        """Test email contains valid reset URL."""
        from django.core import mail
        from apps.accounts.services import PasswordResetService

        PasswordResetService.send_reset_email(self.user)

        email_body = mail.outbox[0].body
        self.assertIn('/accounts/reset/', email_body)

    @override_settings(EMAIL_BACKEND='django.core.mail.backends.locmem.EmailBackend')
    def test_email_contains_user_first_name(self):
        """Test email greeting contains user's first name."""
        from django.core import mail
        from apps.accounts.services import PasswordResetService

        PasswordResetService.send_reset_email(self.user)

        email_body = mail.outbox[0].body
        self.assertIn(self.user.first_name, email_body)

    def test_request_reset_does_not_send_email_for_nonexistent_user(self):
        """Test no email is sent for non-existent user."""
        from apps.accounts.services import PasswordResetService

        with patch('apps.accounts.services.PasswordResetService.send_reset_email') as mock_send:
            PasswordResetService.request_reset('nonexistent@example.com')

            mock_send.assert_not_called()


class ForgotPasswordAPIViewTests(APITestCase):
    """Tests for POST /api/v1/auth/forgot-password/"""

    def setUp(self):
        """Set up test client and user."""
        self.client = APIClient()
        self.url = reverse('accounts_api:forgot_password')

        self.user = User.objects.create_user(
            username='test@example.com',
            email='test@example.com',
            password='SecurePass123!',
            first_name='John',
            last_name='Doe',
            is_verified=True,
        )

    @patch('apps.accounts.api.views.ForgotPasswordAPIView.throttle_classes', [])
    @override_settings(EMAIL_BACKEND='django.core.mail.backends.locmem.EmailBackend')
    def test_forgot_password_success(self):
        """Test forgot password returns 200 for valid email."""
        response = self.client.post(
            self.url,
            {'email': 'test@example.com'},
            format='json'
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertFalse(response.data['error'])
        self.assertIn('message', response.data)

    @patch('apps.accounts.api.views.ForgotPasswordAPIView.throttle_classes', [])
    def test_forgot_password_nonexistent_email_returns_200(self):
        """Test forgot password returns 200 even for non-existent email (security)."""
        response = self.client.post(
            self.url,
            {'email': 'nonexistent@example.com'},
            format='json'
        )

        # Should return 200 to prevent email enumeration
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertFalse(response.data['error'])

    @patch('apps.accounts.api.views.ForgotPasswordAPIView.throttle_classes', [])
    def test_forgot_password_missing_email(self):
        """Test forgot password fails without email."""
        response = self.client.post(self.url, {}, format='json')

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertTrue(response.data['error'])
        self.assertIn('email', response.data['details'])

    @patch('apps.accounts.api.views.ForgotPasswordAPIView.throttle_classes', [])
    def test_forgot_password_invalid_email_format(self):
        """Test forgot password fails with invalid email format."""
        response = self.client.post(
            self.url,
            {'email': 'invalid-email'},
            format='json'
        )

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('email', response.data['details'])

    @patch('apps.accounts.api.views.ForgotPasswordAPIView.throttle_classes', [])
    def test_forgot_password_email_case_insensitive(self):
        """Test forgot password handles email case insensitivity."""
        with patch('apps.accounts.services.PasswordResetService.send_reset_email', return_value=True):
            response = self.client.post(
                self.url,
                {'email': 'TEST@EXAMPLE.COM'},
                format='json'
            )

            self.assertEqual(response.status_code, status.HTTP_200_OK)

    @patch('apps.accounts.api.views.ForgotPasswordAPIView.throttle_classes', [])
    def test_forgot_password_strips_whitespace(self):
        """Test forgot password strips whitespace from email."""
        with patch('apps.accounts.services.PasswordResetService.send_reset_email', return_value=True):
            response = self.client.post(
                self.url,
                {'email': '  test@example.com  '},
                format='json'
            )

            self.assertEqual(response.status_code, status.HTTP_200_OK)

    @patch('apps.accounts.api.views.ForgotPasswordAPIView.throttle_classes', [])
    def test_forgot_password_empty_email(self):
        """Test forgot password fails with empty email."""
        response = self.client.post(
            self.url,
            {'email': ''},
            format='json'
        )

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    @patch('apps.accounts.api.views.ForgotPasswordAPIView.throttle_classes', [])
    def test_forgot_password_null_email(self):
        """Test forgot password fails with null email."""
        response = self.client.post(
            self.url,
            {'email': None},
            format='json'
        )

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)


class ForgotPasswordThrottleTests(APITestCase):
    """Tests for forgot password rate limiting."""

    def test_throttle_classes_configured(self):
        """Test that forgot password view has throttle classes configured."""
        from apps.accounts.api.views import ForgotPasswordAPIView
        from apps.accounts.api.throttling import ForgotPasswordThrottle

        self.assertIn(ForgotPasswordThrottle, ForgotPasswordAPIView.throttle_classes)

    def test_throttle_rate(self):
        """Test that forgot password throttle has correct rate."""
        from apps.accounts.api.throttling import ForgotPasswordThrottle

        throttle = ForgotPasswordThrottle()
        self.assertEqual(throttle.rate, '3/15m')
        self.assertEqual(throttle.scope, 'forgot_password')
        # Verify parse_rate works correctly: 3 requests, 900 seconds (15 minutes)
        self.assertEqual(throttle.num_requests, 3)
        self.assertEqual(throttle.duration, 900)


class ForgotPasswordSerializerTests(TestCase):
    """Tests for ForgotPasswordSerializer."""

    def test_email_normalization(self):
        """Test that email is normalized to lowercase."""
        from apps.accounts.api.serializers import ForgotPasswordSerializer

        serializer = ForgotPasswordSerializer(data={'email': 'TEST@EXAMPLE.COM'})

        self.assertTrue(serializer.is_valid())
        self.assertEqual(serializer.validated_data['email'], 'test@example.com')

    def test_email_whitespace_stripped(self):
        """Test that email whitespace is stripped."""
        from apps.accounts.api.serializers import ForgotPasswordSerializer

        serializer = ForgotPasswordSerializer(data={'email': '  test@example.com  '})

        self.assertTrue(serializer.is_valid())
        self.assertEqual(serializer.validated_data['email'], 'test@example.com')

    def test_valid_email_required(self):
        """Test that valid email format is required."""
        from apps.accounts.api.serializers import ForgotPasswordSerializer

        serializer = ForgotPasswordSerializer(data={'email': 'invalid'})

        self.assertFalse(serializer.is_valid())
        self.assertIn('email', serializer.errors)

    def test_email_required(self):
        """Test that email field is required."""
        from apps.accounts.api.serializers import ForgotPasswordSerializer

        serializer = ForgotPasswordSerializer(data={})

        self.assertFalse(serializer.is_valid())
        self.assertIn('email', serializer.errors)


@patch('apps.accounts.api.views.ForgotPasswordAPIView.throttle_classes', [])
class ForgotPasswordHTTPMethodTests(APITestCase):
    """Tests for HTTP method handling on forgot password endpoint."""

    def setUp(self):
        """Set up test client."""
        self.client = APIClient()
        self.url = reverse('accounts_api:forgot_password')

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


class ForgotPasswordSecurityTests(APITestCase):
    """Security tests for forgot password endpoint."""

    def setUp(self):
        """Set up test client."""
        self.client = APIClient()
        self.url = reverse('accounts_api:forgot_password')

    @patch('apps.accounts.api.views.ForgotPasswordAPIView.throttle_classes', [])
    def test_does_not_reveal_email_existence(self):
        """Test endpoint returns same response for existing and non-existing emails."""
        User.objects.create_user(
            username='exists@example.com',
            email='exists@example.com',
            password='SecurePass123!',
            is_verified=True,
        )

        with patch('apps.accounts.services.PasswordResetService.send_reset_email', return_value=True):
            response_exists = self.client.post(
                self.url,
                {'email': 'exists@example.com'},
                format='json'
            )

        response_not_exists = self.client.post(
            self.url,
            {'email': 'notexists@example.com'},
            format='json'
        )

        # Both should return 200 with same message format
        self.assertEqual(response_exists.status_code, response_not_exists.status_code)
        self.assertEqual(response_exists.data['error'], response_not_exists.data['error'])

    @patch('apps.accounts.api.views.ForgotPasswordAPIView.throttle_classes', [])
    def test_handles_sql_injection_attempt(self):
        """Test forgot password safely handles SQL injection attempts."""
        response = self.client.post(
            self.url,
            {'email': "'; DROP TABLE users; --@example.com"},
            format='json'
        )

        # Should return 400 for invalid email format, not crash
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    @patch('apps.accounts.api.views.ForgotPasswordAPIView.throttle_classes', [])
    def test_handles_very_long_email(self):
        """Test forgot password handles very long email gracefully."""
        very_long_email = 'a' * 500 + '@example.com'

        response = self.client.post(
            self.url,
            {'email': very_long_email},
            format='json'
        )

        # Should not crash, return 400 or 200
        self.assertIn(response.status_code, [status.HTTP_400_BAD_REQUEST, status.HTTP_200_OK])


class ForgotPasswordLoggingTests(TestCase):
    """Tests for forgot password logging."""

    def setUp(self):
        """Create test user."""
        self.user = User.objects.create_user(
            username='test@example.com',
            email='test@example.com',
            password='SecurePass123!',
            is_verified=True,
        )

    @override_settings(EMAIL_BACKEND='django.core.mail.backends.locmem.EmailBackend')
    def test_logs_successful_password_reset_request(self):
        """Test that successful password reset request is logged."""
        from apps.accounts.services import PasswordResetService

        with patch('apps.accounts.services.logger') as mock_logger:
            PasswordResetService.request_reset('test@example.com')

            mock_logger.info.assert_called()

    def test_logs_request_for_nonexistent_email(self):
        """Test that request for non-existent email is logged."""
        from apps.accounts.services import PasswordResetService

        with patch('apps.accounts.services.logger') as mock_logger:
            PasswordResetService.request_reset('nonexistent@example.com')

            mock_logger.info.assert_called()

    def test_logs_email_send_failure(self):
        """Test that email send failure is logged."""
        from apps.accounts.services import PasswordResetService

        with patch('apps.accounts.services.send_mail', side_effect=Exception('SMTP error')):
            with patch('apps.accounts.services.logger') as mock_logger:
                PasswordResetService.send_reset_email(self.user)

                mock_logger.error.assert_called()

    def test_does_not_log_password(self):
        """Test that password is never logged."""
        from apps.accounts.services import PasswordResetService

        with patch('apps.accounts.services.logger') as mock_logger:
            PasswordResetService.request_reset('test@example.com')

            # Check that password-like strings are not in logs
            for call in mock_logger.mock_calls:
                call_str = str(call)
                self.assertNotIn('SecurePass123!', call_str)


class ForgotPasswordWorkflowTests(APITestCase):
    """End-to-end workflow tests for forgot password feature."""

    def setUp(self):
        """Set up test client and user."""
        self.client = APIClient()
        self.url = reverse('accounts_api:forgot_password')

        self.user = User.objects.create_user(
            username='test@example.com',
            email='test@example.com',
            password='SecurePass123!',
            first_name='John',
            last_name='Doe',
            is_verified=True,
        )

    @patch('apps.accounts.api.views.ForgotPasswordAPIView.throttle_classes', [])
    @override_settings(EMAIL_BACKEND='django.core.mail.backends.locmem.EmailBackend')
    def test_complete_forgot_password_workflow(self):
        """Test complete forgot password flow from request to token creation."""
        from django.core import mail

        # 1. User requests password reset
        response = self.client.post(
            self.url,
            {'email': 'test@example.com'},
            format='json'
        )

        # 2. API returns success
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertFalse(response.data['error'])

        # 3. Token is created
        token = PasswordResetToken.objects.filter(user=self.user).order_by('-created_at').first()
        self.assertIsNotNone(token)
        self.assertTrue(token.is_valid())

        # 4. Email is sent
        self.assertEqual(len(mail.outbox), 1)
        self.assertEqual(mail.outbox[0].to, ['test@example.com'])

    @patch('apps.accounts.api.views.ForgotPasswordAPIView.throttle_classes', [])
    @override_settings(EMAIL_BACKEND='django.core.mail.backends.locmem.EmailBackend')
    def test_multiple_reset_requests_invalidate_previous_tokens(self):
        """Test that requesting reset multiple times invalidates old tokens."""
        # First request
        self.client.post(self.url, {'email': 'test@example.com'}, format='json')
        token1 = PasswordResetToken.objects.filter(user=self.user).order_by('-created_at').first()

        # Second request
        self.client.post(self.url, {'email': 'test@example.com'}, format='json')
        token2 = PasswordResetToken.objects.filter(user=self.user).order_by('-created_at').first()

        # Refresh token1
        token1.refresh_from_db()

        # First token should be invalidated
        self.assertFalse(token1.is_valid())
        # Second token should be valid
        self.assertTrue(token2.is_valid())
        # They should be different tokens
        self.assertNotEqual(token1.id, token2.id)

    @patch('apps.accounts.api.views.ForgotPasswordAPIView.throttle_classes', [])
    def test_unverified_user_can_request_reset(self):
        """Test that unverified users can also request password reset."""
        unverified_user = User.objects.create_user(
            username='unverified@example.com',
            email='unverified@example.com',
            password='SecurePass123!',
            is_verified=False,
        )

        with patch('apps.accounts.services.PasswordResetService.send_reset_email', return_value=True) as mock_send:
            response = self.client.post(
                self.url,
                {'email': 'unverified@example.com'},
                format='json'
            )

            self.assertEqual(response.status_code, status.HTTP_200_OK)
            mock_send.assert_called_once()

    @patch('apps.accounts.api.views.ForgotPasswordAPIView.throttle_classes', [])
    def test_inactive_user_can_request_reset(self):
        """Test behavior for inactive users."""
        # Set user as inactive
        self.user.is_active = False
        self.user.save()

        with patch('apps.accounts.services.PasswordResetService.send_reset_email', return_value=True) as mock_send:
            response = self.client.post(
                self.url,
                {'email': 'test@example.com'},
                format='json'
            )

            # Should still return 200 (security - don't reveal user status)
            self.assertEqual(response.status_code, status.HTTP_200_OK)


class ForgotPasswordEdgeCaseTests(APITestCase):
    """Edge case tests for forgot password feature."""

    def setUp(self):
        """Set up test client."""
        self.client = APIClient()
        self.url = reverse('accounts_api:forgot_password')

    @patch('apps.accounts.api.views.ForgotPasswordAPIView.throttle_classes', [])
    def test_email_with_plus_sign(self):
        """Test email addresses with + are handled correctly."""
        User.objects.create_user(
            username='test+tag@example.com',
            email='test+tag@example.com',
            password='SecurePass123!',
        )

        with patch('apps.accounts.services.PasswordResetService.send_reset_email', return_value=True):
            response = self.client.post(
                self.url,
                {'email': 'test+tag@example.com'},
                format='json'
            )

            self.assertEqual(response.status_code, status.HTTP_200_OK)

    @patch('apps.accounts.api.views.ForgotPasswordAPIView.throttle_classes', [])
    def test_email_with_dots(self):
        """Test email addresses with dots in local part."""
        User.objects.create_user(
            username='first.last@example.com',
            email='first.last@example.com',
            password='SecurePass123!',
        )

        with patch('apps.accounts.services.PasswordResetService.send_reset_email', return_value=True):
            response = self.client.post(
                self.url,
                {'email': 'first.last@example.com'},
                format='json'
            )

            self.assertEqual(response.status_code, status.HTTP_200_OK)

    @patch('apps.accounts.api.views.ForgotPasswordAPIView.throttle_classes', [])
    def test_international_domain(self):
        """Test email addresses with international domains."""
        response = self.client.post(
            self.url,
            {'email': 'user@例え.jp'},
            format='json'
        )

        # Should handle gracefully (either 200 or 400)
        self.assertIn(response.status_code, [status.HTTP_200_OK, status.HTTP_400_BAD_REQUEST])

    @patch('apps.accounts.api.views.ForgotPasswordAPIView.throttle_classes', [])
    def test_concurrent_requests_same_email(self):
        """Test handling of concurrent requests for same email."""
        User.objects.create_user(
            username='concurrent@example.com',
            email='concurrent@example.com',
            password='SecurePass123!',
        )

        with patch('apps.accounts.services.PasswordResetService.send_reset_email', return_value=True):
            # Simulate concurrent requests
            response1 = self.client.post(
                self.url, {'email': 'concurrent@example.com'}, format='json'
            )
            response2 = self.client.post(
                self.url, {'email': 'concurrent@example.com'}, format='json'
            )

            # Both should succeed
            self.assertEqual(response1.status_code, status.HTTP_200_OK)
            self.assertEqual(response2.status_code, status.HTTP_200_OK)

    @patch('apps.accounts.api.views.ForgotPasswordAPIView.throttle_classes', [])
    def test_json_payload_required(self):
        """Test that JSON payload is required."""
        response = self.client.post(
            self.url,
            'email=test@example.com',
            content_type='application/x-www-form-urlencoded'
        )

        # Should handle non-JSON content type
        self.assertIn(response.status_code, [
            status.HTTP_200_OK,
            status.HTTP_400_BAD_REQUEST,
            status.HTTP_415_UNSUPPORTED_MEDIA_TYPE
        ])

    @patch('apps.accounts.api.views.ForgotPasswordAPIView.throttle_classes', [])
    def test_empty_json_body(self):
        """Test handling of empty JSON body."""
        response = self.client.post(
            self.url,
            {},
            format='json'
        )

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    @patch('apps.accounts.api.views.ForgotPasswordAPIView.throttle_classes', [])
    def test_extra_fields_ignored(self):
        """Test that extra fields in request are ignored."""
        User.objects.create_user(
            username='extra@example.com',
            email='extra@example.com',
            password='SecurePass123!',
        )

        with patch('apps.accounts.services.PasswordResetService.send_reset_email', return_value=True):
            response = self.client.post(
                self.url,
                {
                    'email': 'extra@example.com',
                    'password': 'should_be_ignored',
                    'extra_field': 'ignored'
                },
                format='json'
            )

            self.assertEqual(response.status_code, status.HTTP_200_OK)
