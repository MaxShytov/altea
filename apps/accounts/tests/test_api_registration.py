"""
API integration tests for registration endpoints.
"""

from datetime import timedelta
from unittest.mock import patch

from django.test import TestCase, override_settings
from django.urls import reverse
from django.utils import timezone
from rest_framework import status
from rest_framework.test import APITestCase, APIClient

from apps.accounts.models import User, EmailVerificationToken


class RegisterAPIViewTests(APITestCase):
    """Tests for POST /api/v1/auth/register/"""

    def setUp(self):
        """Set up test client."""
        self.client = APIClient()
        self.url = reverse('accounts_api:register')
        self.valid_data = {
            'email': 'newuser@example.com',
            'password': 'SecurePass123!',
            'password_confirm': 'SecurePass123!',
            'first_name': 'John',
            'last_name': 'Doe',
            'terms_accepted': True,
        }

    @override_settings(EMAIL_BACKEND='django.core.mail.backends.locmem.EmailBackend')
    @patch('apps.accounts.api.views.RegisterAPIView.throttle_classes', [])
    def test_register_success(self):
        """Test successful registration returns 201."""
        response = self.client.post(self.url, self.valid_data, format='json')

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertFalse(response.data['error'])
        self.assertIn('Registration successful', response.data['message'])
        self.assertIn('user', response.data)
        self.assertEqual(response.data['user']['email'], 'newuser@example.com')
        self.assertFalse(response.data['user']['is_verified'])

        # Verify user was created in database
        user = User.objects.get(email='newuser@example.com')
        self.assertEqual(user.first_name, 'John')
        self.assertEqual(user.last_name, 'Doe')
        self.assertFalse(user.is_verified)
        self.assertIsNotNone(user.terms_accepted_at)

    @override_settings(EMAIL_BACKEND='django.core.mail.backends.locmem.EmailBackend')
    @patch('apps.accounts.api.views.RegisterAPIView.throttle_classes', [])
    def test_register_creates_verification_token(self):
        """Test that registration creates verification token."""
        self.client.post(self.url, self.valid_data, format='json')

        user = User.objects.get(email='newuser@example.com')
        token = EmailVerificationToken.objects.filter(user=user).first()

        self.assertIsNotNone(token)
        self.assertTrue(token.is_valid())

    @patch('apps.accounts.api.views.RegisterAPIView.throttle_classes', [])
    def test_register_missing_email(self):
        """Test registration fails without email."""
        data = self.valid_data.copy()
        del data['email']

        response = self.client.post(self.url, data, format='json')

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertTrue(response.data['error'])
        self.assertIn('email', response.data['details'])

    @patch('apps.accounts.api.views.RegisterAPIView.throttle_classes', [])
    def test_register_invalid_email(self):
        """Test registration fails with invalid email."""
        data = self.valid_data.copy()
        data['email'] = 'invalid-email'

        response = self.client.post(self.url, data, format='json')

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('email', response.data['details'])

    @patch('apps.accounts.api.views.RegisterAPIView.throttle_classes', [])
    def test_register_duplicate_email(self):
        """Test registration fails with existing email."""
        User.objects.create_user(
            username='existing@example.com',
            email='existing@example.com',
            password='password123',
        )

        data = self.valid_data.copy()
        data['email'] = 'existing@example.com'

        response = self.client.post(self.url, data, format='json')

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('email', response.data['details'])
        self.assertIn('already exists', str(response.data['details']['email']))

    @patch('apps.accounts.api.views.RegisterAPIView.throttle_classes', [])
    def test_register_duplicate_email_case_insensitive(self):
        """Test email uniqueness is case insensitive."""
        User.objects.create_user(
            username='test@example.com',
            email='test@example.com',
            password='password123',
        )

        data = self.valid_data.copy()
        data['email'] = 'TEST@EXAMPLE.COM'

        response = self.client.post(self.url, data, format='json')

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('email', response.data['details'])

    @patch('apps.accounts.api.views.RegisterAPIView.throttle_classes', [])
    def test_register_short_password(self):
        """Test registration fails with short password."""
        data = self.valid_data.copy()
        data['password'] = 'short'
        data['password_confirm'] = 'short'

        response = self.client.post(self.url, data, format='json')

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('password', response.data['details'])

    @patch('apps.accounts.api.views.RegisterAPIView.throttle_classes', [])
    def test_register_password_mismatch(self):
        """Test registration fails when passwords don't match."""
        data = self.valid_data.copy()
        data['password_confirm'] = 'DifferentPass123!'

        response = self.client.post(self.url, data, format='json')

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('password_confirm', response.data['details'])
        self.assertIn('do not match', str(response.data['details']['password_confirm']))

    @patch('apps.accounts.api.views.RegisterAPIView.throttle_classes', [])
    def test_register_terms_not_accepted(self):
        """Test registration fails when terms not accepted."""
        data = self.valid_data.copy()
        data['terms_accepted'] = False

        response = self.client.post(self.url, data, format='json')

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('terms_accepted', response.data['details'])

    @patch('apps.accounts.api.views.RegisterAPIView.throttle_classes', [])
    def test_register_missing_first_name(self):
        """Test registration fails without first name."""
        data = self.valid_data.copy()
        del data['first_name']

        response = self.client.post(self.url, data, format='json')

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('first_name', response.data['details'])

    @patch('apps.accounts.api.views.RegisterAPIView.throttle_classes', [])
    def test_register_missing_last_name(self):
        """Test registration fails without last name."""
        data = self.valid_data.copy()
        del data['last_name']

        response = self.client.post(self.url, data, format='json')

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('last_name', response.data['details'])


class VerifyEmailAPIViewTests(APITestCase):
    """Tests for GET /api/v1/auth/verify-email/<token>/"""

    def setUp(self):
        """Create test user and token."""
        self.client = APIClient()
        self.user = User.objects.create_user(
            username='test@example.com',
            email='test@example.com',
            password='password123',
            first_name='John',
            last_name='Doe',
            is_verified=False,
        )
        self.token = EmailVerificationToken.create_for_user(self.user)

    def get_verify_url(self, token_string):
        """Build verification URL."""
        return reverse('accounts_api:verify_email', kwargs={'token': token_string})

    def test_verify_email_success(self):
        """Test successful email verification."""
        response = self.client.get(self.get_verify_url(self.token.token))

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        # Check for success indicator in the HTML response
        self.assertContains(response, 'Email Verified')

        # Check user is now verified
        self.user.refresh_from_db()
        self.assertTrue(self.user.is_verified)

        # Check token is marked as used
        self.token.refresh_from_db()
        self.assertIsNotNone(self.token.used_at)

    def test_verify_email_invalid_token(self):
        """Test verification with invalid token."""
        response = self.client.get(self.get_verify_url('invalid-token-string'))

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertContains(response, 'Invalid')

        # User should still be unverified
        self.user.refresh_from_db()
        self.assertFalse(self.user.is_verified)

    def test_verify_email_expired_token(self):
        """Test verification with expired token."""
        self.token.expires_at = timezone.now() - timedelta(hours=1)
        self.token.save()

        response = self.client.get(self.get_verify_url(self.token.token))

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertContains(response, 'expired')

    def test_verify_email_already_used_token(self):
        """Test verification with already used token."""
        self.token.mark_used()

        response = self.client.get(self.get_verify_url(self.token.token))

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertContains(response, 'already')

    def test_verify_email_returns_html(self):
        """Test that verify endpoint returns HTML page."""
        response = self.client.get(self.get_verify_url(self.token.token))

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response['Content-Type'], 'text/html; charset=utf-8')


class ResendVerificationAPIViewTests(APITestCase):
    """Tests for POST /api/v1/auth/resend-verification/"""

    def setUp(self):
        """Create test user."""
        self.client = APIClient()
        self.url = reverse('accounts_api:resend_verification')
        self.user = User.objects.create_user(
            username='test@example.com',
            email='test@example.com',
            password='password123',
            is_verified=False,
        )

    @override_settings(EMAIL_BACKEND='django.core.mail.backends.locmem.EmailBackend')
    @patch('apps.accounts.api.views.ResendVerificationAPIView.throttle_classes', [])
    def test_resend_verification_success(self):
        """Test successful resend verification."""
        response = self.client.post(
            self.url,
            {'email': 'test@example.com'},
            format='json'
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertFalse(response.data['error'])
        self.assertIn('Verification email sent', response.data['message'])

    @patch('apps.accounts.api.views.ResendVerificationAPIView.throttle_classes', [])
    def test_resend_verification_missing_email(self):
        """Test resend fails without email."""
        response = self.client.post(self.url, {}, format='json')

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('email', response.data['details'])

    @patch('apps.accounts.api.views.ResendVerificationAPIView.throttle_classes', [])
    def test_resend_verification_invalid_email_format(self):
        """Test resend fails with invalid email format."""
        response = self.client.post(
            self.url,
            {'email': 'invalid-email'},
            format='json'
        )

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('email', response.data['details'])

    @patch('apps.accounts.api.views.ResendVerificationAPIView.throttle_classes', [])
    def test_resend_verification_nonexistent_email(self):
        """Test resend for non-existent email (security response)."""
        response = self.client.post(
            self.url,
            {'email': 'nonexistent@example.com'},
            format='json'
        )

        # Should return 200 for security (don't reveal if email exists)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertFalse(response.data['error'])

    @patch('apps.accounts.api.views.ResendVerificationAPIView.throttle_classes', [])
    def test_resend_verification_already_verified(self):
        """Test resend fails for already verified user."""
        self.user.is_verified = True
        self.user.save()

        response = self.client.post(
            self.url,
            {'email': 'test@example.com'},
            format='json'
        )

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertTrue(response.data['error'])
        self.assertIn('already verified', response.data['message'])

    @override_settings(EMAIL_BACKEND='django.core.mail.backends.locmem.EmailBackend')
    @patch('apps.accounts.api.views.ResendVerificationAPIView.throttle_classes', [])
    def test_resend_verification_creates_new_token(self):
        """Test that resend creates new token."""
        old_token = EmailVerificationToken.create_for_user(self.user)

        response = self.client.post(
            self.url,
            {'email': 'test@example.com'},
            format='json'
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)

        # Old token should be invalidated
        old_token.refresh_from_db()
        self.assertFalse(old_token.is_valid())

        # New token should exist
        new_token = EmailVerificationToken.objects.filter(
            user=self.user,
            used_at__isnull=True
        ).exclude(pk=old_token.pk).first()
        self.assertIsNotNone(new_token)
        self.assertTrue(new_token.is_valid())


class RateLimitingTests(APITestCase):
    """Tests for API rate limiting configuration."""

    def test_registration_throttle_classes_configured(self):
        """Test that registration view has throttle classes configured."""
        from apps.accounts.api.views import RegisterAPIView
        from apps.accounts.api.throttling import RegistrationThrottle

        self.assertIn(RegistrationThrottle, RegisterAPIView.throttle_classes)

    def test_resend_verification_throttle_classes_configured(self):
        """Test that resend verification view has throttle classes configured."""
        from apps.accounts.api.views import ResendVerificationAPIView
        from apps.accounts.api.throttling import ResendVerificationThrottle

        self.assertIn(ResendVerificationThrottle, ResendVerificationAPIView.throttle_classes)


class SerializerValidationTests(TestCase):
    """Tests for serializer validation edge cases."""

    def test_email_normalization(self):
        """Test that email is normalized to lowercase."""
        from apps.accounts.api.serializers import RegisterSerializer

        data = {
            'email': 'TEST@EXAMPLE.COM',
            'password': 'SecurePass123!',
            'password_confirm': 'SecurePass123!',
            'first_name': 'John',
            'last_name': 'Doe',
            'terms_accepted': True,
        }

        serializer = RegisterSerializer(data=data)
        self.assertTrue(serializer.is_valid())
        self.assertEqual(serializer.validated_data['email'], 'test@example.com')

    def test_password_minimum_length(self):
        """Test password minimum length validation."""
        from apps.accounts.api.serializers import RegisterSerializer

        data = {
            'email': 'test@example.com',
            'password': 'short',
            'password_confirm': 'short',
            'first_name': 'John',
            'last_name': 'Doe',
            'terms_accepted': True,
        }

        serializer = RegisterSerializer(data=data)
        self.assertFalse(serializer.is_valid())
        self.assertIn('password', serializer.errors)

    def test_password_confirm_required(self):
        """Test password confirmation is required."""
        from apps.accounts.api.serializers import RegisterSerializer

        data = {
            'email': 'test@example.com',
            'password': 'SecurePass123!',
            'first_name': 'John',
            'last_name': 'Doe',
            'terms_accepted': True,
        }

        serializer = RegisterSerializer(data=data)
        self.assertFalse(serializer.is_valid())
        self.assertIn('password_confirm', serializer.errors)

    def test_terms_must_be_accepted(self):
        """Test terms acceptance is required and must be True."""
        from apps.accounts.api.serializers import RegisterSerializer

        data = {
            'email': 'test@example.com',
            'password': 'SecurePass123!',
            'password_confirm': 'SecurePass123!',
            'first_name': 'John',
            'last_name': 'Doe',
            'terms_accepted': False,
        }

        serializer = RegisterSerializer(data=data)
        self.assertFalse(serializer.is_valid())
        self.assertIn('terms_accepted', serializer.errors)
