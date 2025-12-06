"""
Unit tests for accounts services.
"""

from datetime import timedelta
from unittest.mock import patch, MagicMock

from django.conf import settings
from django.core import mail
from django.test import TestCase, override_settings
from django.utils import timezone

from apps.accounts.models import User, EmailVerificationToken
from apps.accounts.services import RegistrationService, EmailVerificationService


class RegistrationServiceTests(TestCase):
    """Tests for RegistrationService."""

    def test_register_user_success(self):
        """Test successful user registration."""
        with patch.object(EmailVerificationService, 'send_verification', return_value=True):
            user = RegistrationService.register_user(
                email='test@example.com',
                password='SecurePass123!',
                first_name='John',
                last_name='Doe',
                terms_accepted=True,
            )

        self.assertIsNotNone(user)
        self.assertEqual(user.email, 'test@example.com')
        self.assertEqual(user.username, 'test@example.com')
        self.assertEqual(user.first_name, 'John')
        self.assertEqual(user.last_name, 'Doe')
        self.assertFalse(user.is_verified)
        self.assertIsNotNone(user.terms_accepted_at)
        self.assertTrue(user.check_password('SecurePass123!'))

    def test_register_user_sends_verification_email(self):
        """Test that registration sends verification email."""
        with patch.object(EmailVerificationService, 'send_verification', return_value=True) as mock_send:
            user = RegistrationService.register_user(
                email='test@example.com',
                password='SecurePass123!',
                first_name='John',
                last_name='Doe',
                terms_accepted=True,
            )

        mock_send.assert_called_once_with(user)

    def test_register_user_duplicate_email_fails(self):
        """Test that registration fails for duplicate email."""
        User.objects.create_user(
            username='existing@example.com',
            email='existing@example.com',
            password='password123',
        )

        with self.assertRaises(ValueError) as context:
            RegistrationService.register_user(
                email='existing@example.com',
                password='SecurePass123!',
                first_name='John',
                last_name='Doe',
                terms_accepted=True,
            )

        self.assertIn('already exists', str(context.exception))

    def test_register_user_duplicate_email_case_insensitive(self):
        """Test that email uniqueness check is case insensitive."""
        User.objects.create_user(
            username='test@example.com',
            email='test@example.com',
            password='password123',
        )

        with self.assertRaises(ValueError):
            RegistrationService.register_user(
                email='TEST@example.com',
                password='SecurePass123!',
                first_name='John',
                last_name='Doe',
                terms_accepted=True,
            )

    def test_register_user_terms_not_accepted_fails(self):
        """Test that registration fails when terms not accepted."""
        with self.assertRaises(ValueError) as context:
            RegistrationService.register_user(
                email='test@example.com',
                password='SecurePass123!',
                first_name='John',
                last_name='Doe',
                terms_accepted=False,
            )

        self.assertIn('Terms & Conditions', str(context.exception))


class EmailVerificationServiceTests(TestCase):
    """Tests for EmailVerificationService."""

    def setUp(self):
        """Create test user."""
        self.user = User.objects.create_user(
            username='test@example.com',
            email='test@example.com',
            password='password123',
            first_name='John',
            last_name='Doe',
            is_verified=False,
        )

    def test_create_token_success(self):
        """Test successful token creation."""
        token = EmailVerificationService.create_token(self.user)

        self.assertIsNotNone(token)
        self.assertEqual(token.user, self.user)
        self.assertIsNotNone(token.token)
        self.assertIsNone(token.used_at)
        self.assertTrue(token.is_valid())

    def test_create_token_invalidates_old_tokens(self):
        """Test that creating new token invalidates old ones."""
        old_token = EmailVerificationService.create_token(self.user)
        old_token_string = old_token.token

        new_token = EmailVerificationService.create_token(self.user)

        # Refresh old token from database
        old_token.refresh_from_db()
        self.assertIsNotNone(old_token.used_at)
        self.assertFalse(old_token.is_valid())
        self.assertTrue(new_token.is_valid())
        self.assertNotEqual(old_token_string, new_token.token)

    @override_settings(
        EMAIL_BACKEND='django.core.mail.backends.locmem.EmailBackend',
        SITE_URL='http://testserver'
    )
    def test_send_verification_email(self):
        """Test that verification email is sent."""
        result = EmailVerificationService.send_verification(self.user)

        self.assertTrue(result)
        self.assertEqual(len(mail.outbox), 1)
        email = mail.outbox[0]
        self.assertEqual(email.to, ['test@example.com'])
        self.assertIn('Verify your Altea account', email.subject)
        self.assertIn('verify-email', email.body)

    def test_verify_token_success(self):
        """Test successful token verification."""
        token = EmailVerificationService.create_token(self.user)

        success, message, user = EmailVerificationService.verify_token(token.token)

        self.assertTrue(success)
        self.assertIn('verified successfully', message)
        self.assertEqual(user, self.user)

        # Refresh user and token from database
        self.user.refresh_from_db()
        token.refresh_from_db()

        self.assertTrue(self.user.is_verified)
        self.assertIsNotNone(token.used_at)

    def test_verify_token_invalid_token(self):
        """Test verification with invalid token."""
        success, message, user = EmailVerificationService.verify_token('invalid-token')

        self.assertFalse(success)
        self.assertIn('Invalid', message)
        self.assertIsNone(user)

    def test_verify_token_already_used(self):
        """Test verification with already used token."""
        token = EmailVerificationService.create_token(self.user)
        token.mark_used()

        success, message, user = EmailVerificationService.verify_token(token.token)

        self.assertFalse(success)
        self.assertIn('already been used', message)
        self.assertEqual(user, self.user)

    def test_verify_token_expired(self):
        """Test verification with expired token."""
        token = EmailVerificationService.create_token(self.user)
        # Manually expire the token
        token.expires_at = timezone.now() - timedelta(hours=1)
        token.save()

        success, message, user = EmailVerificationService.verify_token(token.token)

        self.assertFalse(success)
        self.assertIn('expired', message)
        self.assertEqual(user, self.user)

    @override_settings(EMAIL_BACKEND='django.core.mail.backends.locmem.EmailBackend')
    def test_resend_verification_success(self):
        """Test successful resend verification."""
        success, message = EmailVerificationService.resend_verification('test@example.com')

        self.assertTrue(success)
        self.assertIn('Verification email sent', message)
        self.assertEqual(len(mail.outbox), 1)

    def test_resend_verification_nonexistent_email(self):
        """Test resend for non-existent email (security: same response)."""
        success, message = EmailVerificationService.resend_verification('nonexistent@example.com')

        # Should return success for security (don't reveal if email exists)
        self.assertTrue(success)
        self.assertIn('If this email is registered', message)

    def test_resend_verification_already_verified(self):
        """Test resend for already verified user."""
        self.user.is_verified = True
        self.user.save()

        success, message = EmailVerificationService.resend_verification('test@example.com')

        self.assertFalse(success)
        self.assertIn('already verified', message)


class EmailVerificationTokenModelTests(TestCase):
    """Tests for EmailVerificationToken model."""

    def setUp(self):
        """Create test user."""
        self.user = User.objects.create_user(
            username='test@example.com',
            email='test@example.com',
            password='password123',
        )

    def test_token_creation(self):
        """Test token creation via class method."""
        token = EmailVerificationToken.create_for_user(self.user)

        self.assertIsNotNone(token.token)
        self.assertEqual(len(token.token), 43)  # secrets.token_urlsafe(32) produces 43 chars
        self.assertIsNone(token.used_at)
        self.assertTrue(token.expires_at > timezone.now())

    def test_token_is_valid(self):
        """Test is_valid method."""
        token = EmailVerificationToken.create_for_user(self.user)

        self.assertTrue(token.is_valid())

    def test_token_is_valid_after_use(self):
        """Test is_valid returns False after token is used."""
        token = EmailVerificationToken.create_for_user(self.user)
        token.mark_used()

        self.assertFalse(token.is_valid())

    def test_token_is_valid_after_expiry(self):
        """Test is_valid returns False after token expires."""
        token = EmailVerificationToken.create_for_user(self.user)
        token.expires_at = timezone.now() - timedelta(hours=1)
        token.save()

        self.assertFalse(token.is_valid())

    def test_mark_used(self):
        """Test mark_used method."""
        token = EmailVerificationToken.create_for_user(self.user)
        self.assertIsNone(token.used_at)

        token.mark_used()
        token.refresh_from_db()

        self.assertIsNotNone(token.used_at)

    @override_settings(EMAIL_VERIFICATION_TOKEN_EXPIRY_HOURS=48)
    def test_token_expiry_from_settings(self):
        """Test that token expiry respects settings."""
        token = EmailVerificationToken.create_for_user(self.user)

        expected_expiry = timezone.now() + timedelta(hours=48)
        # Allow 1 minute tolerance
        self.assertAlmostEqual(
            token.expires_at.timestamp(),
            expected_expiry.timestamp(),
            delta=60
        )
