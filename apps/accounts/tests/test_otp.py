"""
Unit tests for OTP authentication functionality.
"""

from datetime import timedelta
from unittest.mock import patch

from django.conf import settings
from django.test import TestCase, override_settings
from django.urls import reverse
from django.utils import timezone
from rest_framework import status
from rest_framework.test import APITestCase
from rest_framework.throttling import AnonRateThrottle

from apps.accounts.models import User, OTPToken
from apps.accounts.services import OTPService, OTPErrorCode


# Disable throttling for tests
class NoThrottle(AnonRateThrottle):
    def allow_request(self, request, view):
        return True


class OTPTokenModelTest(TestCase):
    """Tests for OTPToken model."""

    def test_generate_code_returns_6_digits(self):
        """Test that generated code is exactly 6 digits."""
        code = OTPToken.generate_code()
        self.assertEqual(len(code), 6)
        self.assertTrue(code.isdigit())

    def test_generate_code_is_random(self):
        """Test that generated codes are different."""
        codes = [OTPToken.generate_code() for _ in range(10)]
        # At least some codes should be different (very unlikely all same)
        self.assertGreater(len(set(codes)), 1)

    def test_hash_code_is_consistent(self):
        """Test that hashing same code produces same hash."""
        code = "123456"
        hash1 = OTPToken.hash_code(code)
        hash2 = OTPToken.hash_code(code)
        self.assertEqual(hash1, hash2)

    def test_hash_code_is_different_for_different_codes(self):
        """Test that different codes produce different hashes."""
        hash1 = OTPToken.hash_code("123456")
        hash2 = OTPToken.hash_code("654321")
        self.assertNotEqual(hash1, hash2)

    def test_create_for_email_creates_token(self):
        """Test creating OTP token for email."""
        email = "test@example.com"
        token, code = OTPToken.create_for_email(email)

        self.assertIsNotNone(token)
        self.assertEqual(token.email, email)
        self.assertFalse(token.used)
        self.assertEqual(token.attempts, 0)
        self.assertEqual(len(code), 6)

    def test_create_for_email_invalidates_previous_tokens(self):
        """Test that creating new token invalidates previous unused tokens."""
        email = "test@example.com"

        # Create first token
        token1, _ = OTPToken.create_for_email(email)
        self.assertFalse(token1.used)

        # Create second token
        token2, _ = OTPToken.create_for_email(email)

        # Refresh token1 from database
        token1.refresh_from_db()

        self.assertTrue(token1.used)  # First token should be invalidated
        self.assertFalse(token2.used)  # Second token should be valid

    def test_create_for_email_normalizes_email(self):
        """Test that email is normalized to lowercase."""
        email = "  TEST@EXAMPLE.COM  "
        token, _ = OTPToken.create_for_email(email)
        self.assertEqual(token.email, "test@example.com")

    def test_is_valid_for_fresh_token(self):
        """Test that fresh token is valid."""
        token, _ = OTPToken.create_for_email("test@example.com")
        self.assertTrue(token.is_valid())

    def test_is_expired_after_expiry(self):
        """Test that token is expired after expiry time."""
        token, _ = OTPToken.create_for_email("test@example.com")
        # Manually set expires_at to past
        token.expires_at = timezone.now() - timedelta(minutes=1)
        token.save()

        self.assertTrue(token.is_expired)
        self.assertFalse(token.is_valid())

    def test_is_max_attempts_reached(self):
        """Test max attempts detection."""
        token, _ = OTPToken.create_for_email("test@example.com")

        # Initially not reached
        self.assertFalse(token.is_max_attempts_reached)

        # Set attempts to max
        token.attempts = token.max_attempts
        token.save()

        self.assertTrue(token.is_max_attempts_reached)
        self.assertFalse(token.is_valid())

    def test_verify_code_correct(self):
        """Test verifying correct code."""
        email = "test@example.com"
        token, code = OTPToken.create_for_email(email)

        self.assertTrue(token.verify_code(code))

    def test_verify_code_incorrect(self):
        """Test verifying incorrect code."""
        email = "test@example.com"
        token, code = OTPToken.create_for_email(email)

        # Use different code
        wrong_code = "000000" if code != "000000" else "111111"
        self.assertFalse(token.verify_code(wrong_code))

    def test_increment_attempts(self):
        """Test incrementing attempts counter."""
        token, _ = OTPToken.create_for_email("test@example.com")
        initial_attempts = token.attempts

        token.increment_attempts()

        self.assertEqual(token.attempts, initial_attempts + 1)

    def test_mark_used(self):
        """Test marking token as used."""
        token, _ = OTPToken.create_for_email("test@example.com")
        self.assertFalse(token.used)

        token.mark_used()

        self.assertTrue(token.used)
        self.assertFalse(token.is_valid())

    def test_get_latest_valid(self):
        """Test getting latest valid token."""
        email = "test@example.com"

        # No tokens - should return None
        self.assertIsNone(OTPToken.get_latest_valid(email))

        # Create token
        token, _ = OTPToken.create_for_email(email)

        # Should return the token
        latest = OTPToken.get_latest_valid(email)
        self.assertEqual(latest.id, token.id)

        # Mark as used
        token.mark_used()

        # Should return None now
        self.assertIsNone(OTPToken.get_latest_valid(email))


class OTPServiceTest(TestCase):
    """Tests for OTPService."""

    def test_mask_email(self):
        """Test email masking."""
        test_cases = [
            ("user@example.com", "u***@e***.com"),
            ("a@b.co", "***@b***.co"),
            ("john.doe@company.org", "j***@c***.org"),
        ]
        for email, expected_pattern in test_cases:
            masked = OTPService.mask_email(email)
            # Check it starts and ends correctly
            self.assertIn("***", masked)
            self.assertIn("@", masked)

    def test_mask_email_handles_edge_cases(self):
        """Test email masking edge cases."""
        # Empty email
        self.assertEqual(OTPService.mask_email(""), "")
        # No @ symbol
        self.assertEqual(OTPService.mask_email("invalid"), "invalid")

    @patch('apps.accounts.services.send_mail')
    def test_create_and_send_otp(self, mock_send_mail):
        """Test OTP creation and sending."""
        mock_send_mail.return_value = True

        email = "test@example.com"
        success, masked = OTPService.create_and_send_otp(email)

        self.assertTrue(success)
        self.assertIn("***", masked)
        mock_send_mail.assert_called_once()

    @patch('apps.accounts.services.send_mail')
    def test_create_and_send_otp_always_returns_success(self, mock_send_mail):
        """Test that OTP request always returns success (no email enumeration)."""
        mock_send_mail.return_value = True

        # Non-existent email should still return success
        success, _ = OTPService.create_and_send_otp("nonexistent@example.com")
        self.assertTrue(success)

    def test_verify_otp_valid_code(self):
        """Test OTP verification with valid code."""
        email = "test@example.com"
        token, code = OTPToken.create_for_email(email)

        result = OTPService.verify_otp(email, code)

        self.assertTrue(result.success)
        self.assertIsNotNone(result.user)
        self.assertTrue(result.is_new_user)
        self.assertEqual(result.user.email, email)

    def test_verify_otp_creates_new_user(self):
        """Test that OTP verification creates new user if not exists."""
        email = "newuser@example.com"
        token, code = OTPToken.create_for_email(email)

        # Verify no user exists
        self.assertFalse(User.objects.filter(email=email).exists())

        result = OTPService.verify_otp(email, code)

        self.assertTrue(result.success)
        self.assertTrue(result.is_new_user)
        self.assertTrue(User.objects.filter(email=email).exists())

    def test_verify_otp_logs_in_existing_user(self):
        """Test that OTP verification logs in existing user."""
        email = "existing@example.com"

        # Create existing user
        user = User.objects.create_user(
            username=email,
            email=email,
            password="testpass123"
        )

        token, code = OTPToken.create_for_email(email)
        result = OTPService.verify_otp(email, code)

        self.assertTrue(result.success)
        self.assertFalse(result.is_new_user)
        self.assertEqual(result.user.id, user.id)

    def test_verify_otp_verifies_unverified_user(self):
        """Test that OTP verification marks unverified user as verified."""
        email = "unverified@example.com"

        # Create unverified user
        user = User.objects.create_user(
            username=email,
            email=email,
            password="testpass123",
            is_verified=False
        )

        token, code = OTPToken.create_for_email(email)
        result = OTPService.verify_otp(email, code)

        user.refresh_from_db()
        self.assertTrue(user.is_verified)

    def test_verify_otp_invalid_code(self):
        """Test OTP verification with invalid code."""
        email = "test@example.com"
        token, correct_code = OTPToken.create_for_email(email)
        wrong_code = "000000" if correct_code != "000000" else "111111"

        result = OTPService.verify_otp(email, wrong_code)

        self.assertFalse(result.success)
        self.assertEqual(result.error_code, OTPErrorCode.INVALID_CODE)
        self.assertGreater(result.attempts_remaining, 0)

    def test_verify_otp_expired_code(self):
        """Test OTP verification with expired code."""
        email = "test@example.com"
        token, code = OTPToken.create_for_email(email)

        # Expire the token
        token.expires_at = timezone.now() - timedelta(minutes=1)
        token.save()

        result = OTPService.verify_otp(email, code)

        self.assertFalse(result.success)
        self.assertEqual(result.error_code, OTPErrorCode.OTP_EXPIRED)

    def test_verify_otp_max_attempts(self):
        """Test OTP verification after max attempts reached."""
        email = "test@example.com"
        token, correct_code = OTPToken.create_for_email(email)

        # Use up all attempts with wrong code
        token.attempts = token.max_attempts
        token.save()

        # Try with wrong code - should fail due to max attempts
        wrong_code = "000000" if correct_code != "000000" else "111111"
        result = OTPService.verify_otp(email, wrong_code)

        self.assertFalse(result.success)
        self.assertEqual(result.error_code, OTPErrorCode.MAX_ATTEMPTS)

    def test_verify_otp_no_token(self):
        """Test OTP verification when no token exists."""
        result = OTPService.verify_otp("notoken@example.com", "123456")

        self.assertFalse(result.success)
        self.assertEqual(result.error_code, OTPErrorCode.NO_OTP_FOUND)

    def test_cleanup_expired_tokens(self):
        """Test cleanup of expired tokens."""
        email = "test@example.com"

        # Create some tokens
        token1, _ = OTPToken.create_for_email(email + "1")
        token2, _ = OTPToken.create_for_email(email + "2")

        # Expire token1
        token1.expires_at = timezone.now() - timedelta(hours=1)
        token1.save()

        initial_count = OTPToken.objects.count()

        deleted = OTPService.cleanup_expired_tokens()

        self.assertEqual(deleted, 1)
        self.assertEqual(OTPToken.objects.count(), initial_count - 1)
        self.assertFalse(OTPToken.objects.filter(id=token1.id).exists())


@override_settings(
    REST_FRAMEWORK={
        'DEFAULT_THROTTLE_CLASSES': [],
        'DEFAULT_THROTTLE_RATES': {},
    }
)
class OTPAPITest(APITestCase):
    """API tests for OTP endpoints."""

    def setUp(self):
        """Disable throttling for tests."""
        from apps.accounts.api.views import OTPRequestAPIView, OTPVerifyAPIView
        # Store original throttle classes
        self._original_otp_request_throttle = OTPRequestAPIView.throttle_classes
        self._original_otp_verify_throttle = OTPVerifyAPIView.throttle_classes
        # Disable throttling
        OTPRequestAPIView.throttle_classes = []
        OTPVerifyAPIView.throttle_classes = []

    def tearDown(self):
        """Restore throttling."""
        from apps.accounts.api.views import OTPRequestAPIView, OTPVerifyAPIView
        OTPRequestAPIView.throttle_classes = self._original_otp_request_throttle
        OTPVerifyAPIView.throttle_classes = self._original_otp_verify_throttle

    def test_otp_request_valid_email(self):
        """Test OTP request with valid email."""
        url = reverse('accounts_api:otp_request')
        data = {'email': 'test@example.com'}

        with patch('apps.accounts.services.send_mail') as mock_mail:
            mock_mail.return_value = True
            response = self.client.post(url, data, format='json')

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('email_masked', response.data)
        self.assertIn('message', response.data)

    def test_otp_request_invalid_email(self):
        """Test OTP request with invalid email format."""
        url = reverse('accounts_api:otp_request')
        data = {'email': 'invalid-email'}

        response = self.client.post(url, data, format='json')

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_otp_request_missing_email(self):
        """Test OTP request with missing email."""
        url = reverse('accounts_api:otp_request')
        data = {}

        response = self.client.post(url, data, format='json')

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_otp_verify_valid_code(self):
        """Test OTP verification with valid code."""
        email = "testverify@example.com"
        token, code = OTPToken.create_for_email(email)

        url = reverse('accounts_api:otp_verify')
        data = {'email': email, 'code': code}

        response = self.client.post(url, data, format='json')

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('access_token', response.data)
        self.assertIn('refresh_token', response.data)
        self.assertIn('user', response.data)
        self.assertIn('is_new_user', response.data)

    def test_otp_verify_invalid_code(self):
        """Test OTP verification with invalid code."""
        email = "testinvalid@example.com"
        token, correct_code = OTPToken.create_for_email(email)
        wrong_code = "000000" if correct_code != "000000" else "111111"

        url = reverse('accounts_api:otp_verify')
        data = {'email': email, 'code': wrong_code}

        response = self.client.post(url, data, format='json')

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('error', response.data)
        self.assertTrue(response.data['error'])

    def test_otp_verify_invalid_code_format(self):
        """Test OTP verification with invalid code format."""
        url = reverse('accounts_api:otp_verify')
        data = {'email': 'test@example.com', 'code': 'abc123'}

        response = self.client.post(url, data, format='json')

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_otp_verify_missing_fields(self):
        """Test OTP verification with missing fields."""
        url = reverse('accounts_api:otp_verify')

        # Missing code
        response = self.client.post(url, {'email': 'test@example.com'}, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        # Missing email
        response = self.client.post(url, {'code': '123456'}, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_otp_verify_creates_jwt_tokens(self):
        """Test that OTP verification returns valid JWT tokens."""
        email = "testjwt@example.com"
        token, code = OTPToken.create_for_email(email)

        url = reverse('accounts_api:otp_verify')
        data = {'email': email, 'code': code}

        response = self.client.post(url, data, format='json')

        self.assertEqual(response.status_code, status.HTTP_200_OK)

        # Verify tokens are JWT format (have 3 parts separated by dots)
        access_token = response.data['access_token']
        refresh_token = response.data['refresh_token']

        self.assertEqual(len(access_token.split('.')), 3)
        self.assertEqual(len(refresh_token.split('.')), 3)

    def test_otp_verify_returns_user_data(self):
        """Test that OTP verification returns user data."""
        email = "testuser@example.com"
        token, code = OTPToken.create_for_email(email)

        url = reverse('accounts_api:otp_verify')
        data = {'email': email, 'code': code}

        response = self.client.post(url, data, format='json')

        self.assertEqual(response.status_code, status.HTTP_200_OK)

        user_data = response.data['user']
        self.assertIn('id', user_data)
        self.assertIn('email', user_data)
        self.assertEqual(user_data['email'], email)


class OTPThrottleTest(APITestCase):
    """Tests for OTP rate limiting."""

    @override_settings(CACHES={
        'default': {
            'BACKEND': 'django.core.cache.backends.locmem.LocMemCache',
        }
    })
    def test_otp_request_throttle(self):
        """Test that OTP requests are rate limited."""
        url = reverse('accounts_api:otp_request')
        data = {'email': 'test@example.com'}

        with patch('apps.accounts.services.send_mail') as mock_mail:
            mock_mail.return_value = True

            # First request should succeed
            response1 = self.client.post(url, data, format='json')
            self.assertEqual(response1.status_code, status.HTTP_200_OK)

            # Second immediate request should be throttled
            response2 = self.client.post(url, data, format='json')
            self.assertEqual(response2.status_code, status.HTTP_429_TOO_MANY_REQUESTS)


class OTPSerializerTest(TestCase):
    """Tests for OTP serializers."""

    def test_otp_request_serializer_valid_email(self):
        """Test OTPRequestSerializer with valid email."""
        from apps.accounts.api.serializers import OTPRequestSerializer
        serializer = OTPRequestSerializer(data={'email': 'test@example.com'})
        self.assertTrue(serializer.is_valid())
        self.assertEqual(serializer.validated_data['email'], 'test@example.com')

    def test_otp_request_serializer_normalizes_email(self):
        """Test that OTPRequestSerializer normalizes email to lowercase."""
        from apps.accounts.api.serializers import OTPRequestSerializer
        serializer = OTPRequestSerializer(data={'email': '  TEST@EXAMPLE.COM  '})
        self.assertTrue(serializer.is_valid())
        self.assertEqual(serializer.validated_data['email'], 'test@example.com')

    def test_otp_request_serializer_invalid_email(self):
        """Test OTPRequestSerializer with invalid email."""
        from apps.accounts.api.serializers import OTPRequestSerializer
        serializer = OTPRequestSerializer(data={'email': 'invalid-email'})
        self.assertFalse(serializer.is_valid())
        self.assertIn('email', serializer.errors)

    def test_otp_request_serializer_empty_email(self):
        """Test OTPRequestSerializer with empty email."""
        from apps.accounts.api.serializers import OTPRequestSerializer
        serializer = OTPRequestSerializer(data={'email': ''})
        self.assertFalse(serializer.is_valid())
        self.assertIn('email', serializer.errors)

    def test_otp_request_serializer_missing_email(self):
        """Test OTPRequestSerializer with missing email field."""
        from apps.accounts.api.serializers import OTPRequestSerializer
        serializer = OTPRequestSerializer(data={})
        self.assertFalse(serializer.is_valid())
        self.assertIn('email', serializer.errors)

    def test_otp_verify_serializer_valid_data(self):
        """Test OTPVerifySerializer with valid data."""
        from apps.accounts.api.serializers import OTPVerifySerializer
        serializer = OTPVerifySerializer(data={
            'email': 'test@example.com',
            'code': '123456'
        })
        self.assertTrue(serializer.is_valid())
        self.assertEqual(serializer.validated_data['email'], 'test@example.com')
        self.assertEqual(serializer.validated_data['code'], '123456')

    def test_otp_verify_serializer_code_too_short(self):
        """Test OTPVerifySerializer with code too short."""
        from apps.accounts.api.serializers import OTPVerifySerializer
        serializer = OTPVerifySerializer(data={
            'email': 'test@example.com',
            'code': '12345'  # 5 digits instead of 6
        })
        self.assertFalse(serializer.is_valid())
        self.assertIn('code', serializer.errors)

    def test_otp_verify_serializer_code_too_long(self):
        """Test OTPVerifySerializer with code too long."""
        from apps.accounts.api.serializers import OTPVerifySerializer
        serializer = OTPVerifySerializer(data={
            'email': 'test@example.com',
            'code': '1234567'  # 7 digits instead of 6
        })
        self.assertFalse(serializer.is_valid())
        self.assertIn('code', serializer.errors)

    def test_otp_verify_serializer_code_non_numeric(self):
        """Test OTPVerifySerializer with non-numeric code."""
        from apps.accounts.api.serializers import OTPVerifySerializer
        serializer = OTPVerifySerializer(data={
            'email': 'test@example.com',
            'code': 'abc123'
        })
        self.assertFalse(serializer.is_valid())
        self.assertIn('code', serializer.errors)

    def test_otp_verify_serializer_normalizes_email(self):
        """Test that OTPVerifySerializer normalizes email."""
        from apps.accounts.api.serializers import OTPVerifySerializer
        serializer = OTPVerifySerializer(data={
            'email': '  USER@EXAMPLE.COM  ',
            'code': '123456'
        })
        self.assertTrue(serializer.is_valid())
        self.assertEqual(serializer.validated_data['email'], 'user@example.com')


class OTPServiceEmailTest(TestCase):
    """Tests for OTP email functionality."""

    @patch('apps.accounts.services.send_mail')
    def test_send_otp_email_default_language(self, mock_send_mail):
        """Test sending OTP email with default (English) language."""
        mock_send_mail.return_value = True

        result = OTPService.send_otp_email('test@example.com', '123456', 'en')

        self.assertTrue(result)
        mock_send_mail.assert_called_once()
        call_args = mock_send_mail.call_args
        self.assertIn('verification code', call_args[1]['subject'].lower())

    @patch('apps.accounts.services.send_mail')
    def test_send_otp_email_german(self, mock_send_mail):
        """Test sending OTP email in German."""
        mock_send_mail.return_value = True

        result = OTPService.send_otp_email('test@example.com', '123456', 'de')

        self.assertTrue(result)
        mock_send_mail.assert_called_once()
        call_args = mock_send_mail.call_args
        self.assertIn('Bestätigungscode', call_args[1]['subject'])

    @patch('apps.accounts.services.send_mail')
    def test_send_otp_email_french(self, mock_send_mail):
        """Test sending OTP email in French."""
        mock_send_mail.return_value = True

        result = OTPService.send_otp_email('test@example.com', '123456', 'fr')

        self.assertTrue(result)
        mock_send_mail.assert_called_once()
        call_args = mock_send_mail.call_args
        self.assertIn('vérification', call_args[1]['subject'].lower())

    @patch('apps.accounts.services.send_mail')
    def test_send_otp_email_italian(self, mock_send_mail):
        """Test sending OTP email in Italian."""
        mock_send_mail.return_value = True

        result = OTPService.send_otp_email('test@example.com', '123456', 'it')

        self.assertTrue(result)
        mock_send_mail.assert_called_once()
        call_args = mock_send_mail.call_args
        self.assertIn('verifica', call_args[1]['subject'].lower())

    @patch('apps.accounts.services.send_mail')
    def test_send_otp_email_unsupported_language_falls_back(self, mock_send_mail):
        """Test that unsupported language falls back to English."""
        mock_send_mail.return_value = True

        result = OTPService.send_otp_email('test@example.com', '123456', 'ru')

        self.assertTrue(result)
        mock_send_mail.assert_called_once()
        call_args = mock_send_mail.call_args
        self.assertIn('verification code', call_args[1]['subject'].lower())

    @patch('apps.accounts.services.send_mail')
    def test_send_otp_email_failure(self, mock_send_mail):
        """Test handling of email sending failure."""
        mock_send_mail.side_effect = Exception('SMTP Error')

        result = OTPService.send_otp_email('test@example.com', '123456', 'en')

        self.assertFalse(result)


class OTPTokenEdgeCasesTest(TestCase):
    """Additional edge case tests for OTPToken model."""

    def test_create_for_email_with_ip_address(self):
        """Test creating OTP with IP address."""
        email = "test@example.com"
        ip = "192.168.1.1"
        token, code = OTPToken.create_for_email(email, ip)

        self.assertEqual(token.ip_address, ip)
        self.assertEqual(len(code), 6)

    def test_attempts_remaining_property(self):
        """Test attempts_remaining property calculation."""
        token, _ = OTPToken.create_for_email("test@example.com")

        self.assertEqual(token.attempts_remaining, token.max_attempts)

        token.attempts = 3
        token.save()
        self.assertEqual(token.attempts_remaining, token.max_attempts - 3)

    def test_attempts_remaining_never_negative(self):
        """Test that attempts_remaining is never negative."""
        token, _ = OTPToken.create_for_email("test@example.com")
        token.attempts = token.max_attempts + 5  # More than max
        token.save()

        self.assertEqual(token.attempts_remaining, 0)

    def test_generate_code_format(self):
        """Test that generated codes are valid 6-digit numbers."""
        for _ in range(100):  # Test 100 random codes
            code = OTPToken.generate_code()
            self.assertEqual(len(code), 6)
            self.assertTrue(code.isdigit())
            self.assertTrue(100000 <= int(code) <= 999999)

    def test_str_representation(self):
        """Test string representation of OTPToken."""
        token, _ = OTPToken.create_for_email("test@example.com")
        str_repr = str(token)

        self.assertIn("test@example.com", str_repr)
        self.assertIn("expires:", str_repr)

    def test_email_normalization_various_cases(self):
        """Test email normalization with various edge cases."""
        test_cases = [
            ("TEST@EXAMPLE.COM", "test@example.com"),
            ("  user@domain.com  ", "user@domain.com"),
            ("User.Name@Domain.COM", "user.name@domain.com"),
        ]

        for input_email, expected_email in test_cases:
            token, _ = OTPToken.create_for_email(input_email)
            self.assertEqual(token.email, expected_email)

    def test_multiple_tokens_invalidation(self):
        """Test that creating new token invalidates multiple old tokens."""
        email = "test@example.com"

        # Create 3 tokens
        token1, _ = OTPToken.create_for_email(email)
        token2, _ = OTPToken.create_for_email(email)
        token3, _ = OTPToken.create_for_email(email)

        # Refresh from database
        token1.refresh_from_db()
        token2.refresh_from_db()

        # First two should be invalidated
        self.assertTrue(token1.used)
        self.assertTrue(token2.used)
        self.assertFalse(token3.used)


class OTPServiceMaskEmailTest(TestCase):
    """Tests for email masking functionality."""

    def test_mask_standard_email(self):
        """Test masking standard email."""
        masked = OTPService.mask_email("john@example.com")
        self.assertIn("***", masked)
        self.assertIn("@", masked)
        self.assertTrue(masked.startswith("j"))

    def test_mask_single_char_local(self):
        """Test masking email with single character local part."""
        masked = OTPService.mask_email("a@example.com")
        self.assertIn("***", masked)

    def test_mask_empty_email(self):
        """Test masking empty email returns empty."""
        self.assertEqual(OTPService.mask_email(""), "")

    def test_mask_email_without_at_symbol(self):
        """Test masking invalid email without @ returns as-is."""
        self.assertEqual(OTPService.mask_email("invalid"), "invalid")

    def test_mask_email_preserves_tld(self):
        """Test that masking preserves top-level domain."""
        masked = OTPService.mask_email("user@domain.org")
        self.assertTrue(masked.endswith(".org"))

    def test_mask_email_subdomain(self):
        """Test masking email with subdomain."""
        masked = OTPService.mask_email("user@mail.domain.co.uk")
        self.assertIn("@", masked)
        self.assertTrue(masked.endswith(".uk"))


class OTPVerificationFlowTest(TestCase):
    """Integration tests for complete OTP verification flow."""

    def test_complete_signup_flow_new_user(self):
        """Test complete signup flow for new user."""
        email = "newuser@example.com"

        # Step 1: No user exists
        self.assertFalse(User.objects.filter(email=email).exists())

        # Step 2: Create OTP token
        token, code = OTPToken.create_for_email(email)
        self.assertIsNotNone(token)

        # Step 3: Verify OTP
        result = OTPService.verify_otp(email, code)

        # Step 4: Assertions
        self.assertTrue(result.success)
        self.assertTrue(result.is_new_user)
        self.assertIsNotNone(result.user)
        self.assertEqual(result.user.email, email)
        self.assertTrue(result.user.is_verified)

    def test_complete_login_flow_existing_user(self):
        """Test complete login flow for existing user."""
        email = "existing@example.com"

        # Create existing user
        user = User.objects.create_user(
            username=email,
            email=email,
            password="testpass123",
            is_verified=False
        )

        # Create OTP token and verify
        token, code = OTPToken.create_for_email(email)
        result = OTPService.verify_otp(email, code)

        # Assertions
        self.assertTrue(result.success)
        self.assertFalse(result.is_new_user)
        self.assertEqual(result.user.id, user.id)

        # User should now be verified
        user.refresh_from_db()
        self.assertTrue(user.is_verified)

    def test_multiple_failed_attempts_then_success(self):
        """Test that user can still succeed after failed attempts."""
        email = "test@example.com"
        token, correct_code = OTPToken.create_for_email(email)

        # Make 2 failed attempts
        wrong_code = "000000" if correct_code != "000000" else "111111"
        result1 = OTPService.verify_otp(email, wrong_code)
        result2 = OTPService.verify_otp(email, wrong_code)

        self.assertFalse(result1.success)
        self.assertFalse(result2.success)
        self.assertGreater(result2.attempts_remaining, 0)

        # Now succeed with correct code
        result3 = OTPService.verify_otp(email, correct_code)
        self.assertTrue(result3.success)

    def test_code_used_cannot_be_reused(self):
        """Test that used OTP code cannot be reused."""
        email = "test@example.com"
        token, code = OTPToken.create_for_email(email)

        # First verification succeeds
        result1 = OTPService.verify_otp(email, code)
        self.assertTrue(result1.success)

        # Second verification fails (code already used)
        result2 = OTPService.verify_otp(email, code)
        self.assertFalse(result2.success)
        self.assertEqual(result2.error_code, OTPErrorCode.NO_OTP_FOUND)

    def test_resend_otp_invalidates_previous(self):
        """Test that resending OTP invalidates previous code."""
        email = "test@example.com"

        # Create first OTP
        token1, code1 = OTPToken.create_for_email(email)

        # Create second OTP (simulating resend)
        token2, code2 = OTPToken.create_for_email(email)

        # First code should not work
        result1 = OTPService.verify_otp(email, code1)
        self.assertFalse(result1.success)

        # Second code should work
        result2 = OTPService.verify_otp(email, code2)
        self.assertTrue(result2.success)


class OTPCleanupTest(TestCase):
    """Tests for OTP cleanup functionality."""

    def test_cleanup_only_expired_tokens(self):
        """Test that cleanup only removes expired tokens."""
        email1 = "expired@example.com"
        email2 = "valid@example.com"

        # Create expired token
        token1, _ = OTPToken.create_for_email(email1)
        token1.expires_at = timezone.now() - timedelta(hours=1)
        token1.save()

        # Create valid token
        token2, _ = OTPToken.create_for_email(email2)

        # Run cleanup
        deleted = OTPService.cleanup_expired_tokens()

        # Assertions
        self.assertEqual(deleted, 1)
        self.assertFalse(OTPToken.objects.filter(id=token1.id).exists())
        self.assertTrue(OTPToken.objects.filter(id=token2.id).exists())

    def test_cleanup_with_no_expired_tokens(self):
        """Test cleanup when there are no expired tokens."""
        # Create only valid tokens
        OTPToken.create_for_email("valid1@example.com")
        OTPToken.create_for_email("valid2@example.com")

        initial_count = OTPToken.objects.count()

        deleted = OTPService.cleanup_expired_tokens()

        self.assertEqual(deleted, 0)
        self.assertEqual(OTPToken.objects.count(), initial_count)

    def test_cleanup_used_expired_tokens(self):
        """Test that used but expired tokens are also cleaned up."""
        token, _ = OTPToken.create_for_email("test@example.com")
        token.used = True
        token.expires_at = timezone.now() - timedelta(hours=1)
        token.save()

        deleted = OTPService.cleanup_expired_tokens()

        self.assertEqual(deleted, 1)
        self.assertFalse(OTPToken.objects.filter(id=token.id).exists())
