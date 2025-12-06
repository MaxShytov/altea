"""
Business logic services for accounts app.
"""

import logging
from dataclasses import dataclass
from enum import Enum
from typing import Optional

from django.conf import settings
from django.contrib.auth import authenticate
from django.core.mail import send_mail
from django.template.loader import render_to_string
from django.utils import timezone
from django.utils.html import strip_tags

from .models import User, EmailVerificationToken, PasswordResetToken

logger = logging.getLogger(__name__)


class AuthErrorCode(str, Enum):
    """Error codes for authentication failures."""
    INVALID_CREDENTIALS = 'invalid_credentials'
    EMAIL_NOT_VERIFIED = 'email_not_verified'


@dataclass
class AuthResult:
    """Result of authentication attempt."""
    success: bool
    user: Optional[User] = None
    error_message: Optional[str] = None
    error_code: Optional[AuthErrorCode] = None


class AuthenticationService:
    """
    Service for handling user authentication business logic.
    """

    @staticmethod
    def authenticate_user(email: str, password: str) -> AuthResult:
        """
        Authenticate user with email and password.

        Args:
            email: User's email address
            password: User's password

        Returns:
            AuthResult with success status, user, or error details
        """
        # Normalize email to lowercase
        email = email.lower().strip()

        # Log authentication attempt (without password)
        logger.info(f"Login attempt: email={email}")

        # Try to find user
        try:
            user = User.objects.get(email__iexact=email)
        except User.DoesNotExist:
            logger.warning(f"Login failed: user not found, email={email}")
            return AuthResult(
                success=False,
                error_message="Invalid credentials",
                error_code=AuthErrorCode.INVALID_CREDENTIALS,
            )

        # Check password using Django's authenticate
        authenticated_user = authenticate(username=email, password=password)

        if authenticated_user is None:
            logger.warning(f"Login failed: invalid password, user_id={user.id}")
            return AuthResult(
                success=False,
                error_message="Invalid credentials",
                error_code=AuthErrorCode.INVALID_CREDENTIALS,
            )

        # Check if email is verified
        if not user.is_verified:
            logger.warning(f"Login failed: email not verified, user_id={user.id}")
            return AuthResult(
                success=False,
                user=user,
                error_message="Please verify your email",
                error_code=AuthErrorCode.EMAIL_NOT_VERIFIED,
            )

        logger.info(f"Login successful: user_id={user.id}")
        return AuthResult(success=True, user=user)


class RegistrationService:
    """
    Service for handling user registration business logic.
    """

    @staticmethod
    def register_user(
        email: str,
        password: str,
        first_name: str,
        last_name: str,
        terms_accepted: bool = True
    ) -> User:
        """
        Register a new user and send verification email.

        Args:
            email: User's email address
            password: User's password (already validated)
            first_name: User's first name
            last_name: User's last name
            terms_accepted: Whether user accepted Terms & Conditions

        Returns:
            Created User instance

        Raises:
            ValueError: If email already exists or terms not accepted
        """
        if not terms_accepted:
            raise ValueError("Terms & Conditions must be accepted")

        # Check if email already exists (case insensitive)
        if User.objects.filter(email__iexact=email).exists():
            raise ValueError("A user with that email already exists.")

        # Create user with is_verified=False
        user = User.objects.create_user(
            username=email,  # Use email as username
            email=email,
            password=password,
            first_name=first_name,
            last_name=last_name,
            is_verified=False,
            terms_accepted_at=timezone.now() if terms_accepted else None,
        )

        # Send verification email
        EmailVerificationService.send_verification(user)

        logger.info(f"User registered: user_id={user.id}")
        return user


class EmailVerificationService:
    """
    Service for handling email verification business logic.
    """

    @staticmethod
    def create_token(user: User) -> EmailVerificationToken:
        """
        Create a new verification token for the user.
        Invalidates any existing tokens.

        Args:
            user: User instance

        Returns:
            New EmailVerificationToken instance
        """
        return EmailVerificationToken.create_for_user(user)

    @staticmethod
    def send_verification(user: User, request=None) -> bool:
        """
        Create token and send verification email.

        Args:
            user: User instance
            request: Optional HTTP request for building absolute URL

        Returns:
            True if email was sent successfully
        """
        token = EmailVerificationService.create_token(user)

        # Build verification URL
        base_url = getattr(settings, 'SITE_URL', 'http://localhost:8000')
        verification_url = f"{base_url}/api/v1/auth/verify-email/{token.token}/"

        # Render email template
        context = {
            'user': user,
            'verification_url': verification_url,
            'expiry_hours': getattr(settings, 'EMAIL_VERIFICATION_TOKEN_EXPIRY_HOURS', 24),
        }

        html_message = render_to_string(
            'accounts/emails/verification_email.html',
            context
        )
        plain_message = strip_tags(html_message)

        try:
            send_mail(
                subject='Verify your Altea account',
                message=plain_message,
                from_email=settings.DEFAULT_FROM_EMAIL,
                recipient_list=[user.email],
                html_message=html_message,
                fail_silently=False,
            )
            logger.info(f"Verification email sent: user_id={user.id}")
            return True
        except Exception as e:
            logger.error(f"Failed to send verification email: user_id={user.id}, error={e}")
            return False

    @staticmethod
    def verify_token(token_string: str) -> tuple[bool, str, Optional[User]]:
        """
        Verify email using token.

        Args:
            token_string: Token string from URL

        Returns:
            Tuple of (success, message, user)
        """
        try:
            token = EmailVerificationToken.objects.select_related('user').get(
                token=token_string
            )
        except EmailVerificationToken.DoesNotExist:
            return False, 'Invalid verification link.', None

        if token.used_at is not None:
            return False, 'This verification link has already been used.', token.user

        if timezone.now() > token.expires_at:
            return False, 'This verification link has expired.', token.user

        # Mark token as used and verify user
        token.mark_used()
        token.user.is_verified = True
        token.user.save(update_fields=['is_verified'])

        logger.info(f"Email verified: user_id={token.user.id}")
        return True, 'Email verified successfully!', token.user

    @staticmethod
    def resend_verification(email: str) -> tuple[bool, str]:
        """
        Resend verification email.

        Args:
            email: User's email address

        Returns:
            Tuple of (success, message)
        """
        try:
            user = User.objects.get(email__iexact=email)
        except User.DoesNotExist:
            # Don't reveal if email exists for security
            return True, 'If this email is registered, a verification link has been sent.'

        if user.is_verified:
            return False, 'This email is already verified.'

        # Send new verification email
        success = EmailVerificationService.send_verification(user)

        if success:
            return True, 'Verification email sent. Please check your inbox.'
        else:
            return False, 'Failed to send verification email. Please try again later.'


class PasswordResetService:
    """
    Service for handling password reset business logic.
    """

    # Localized email content
    EMAIL_CONTENT = {
        'en': {
            'subject': 'Reset your Altea password',
            'greeting': 'Hi',
            'intro': 'We received a request to reset your password for your Altea account.',
            'instruction': 'Click the button below to reset your password:',
            'button': 'Reset Password',
            'expiry': 'This link will expire in {hours} hour(s). If you did not request a password reset, you can safely ignore this email.',
            'fallback': "If the button doesn't work, copy and paste this link into your browser:",
        },
        'de': {
            'subject': 'Altea Passwort zurücksetzen',
            'greeting': 'Hallo',
            'intro': 'Wir haben eine Anfrage erhalten, das Passwort für Ihr Altea-Konto zurückzusetzen.',
            'instruction': 'Klicken Sie auf die Schaltfläche unten, um Ihr Passwort zurückzusetzen:',
            'button': 'Passwort zurücksetzen',
            'expiry': 'Dieser Link läuft in {hours} Stunde(n) ab. Wenn Sie kein Zurücksetzen des Passworts angefordert haben, können Sie diese E-Mail ignorieren.',
            'fallback': 'Wenn die Schaltfläche nicht funktioniert, kopieren Sie diesen Link und fügen Sie ihn in Ihren Browser ein:',
        },
        'fr': {
            'subject': 'Réinitialisez votre mot de passe Altea',
            'greeting': 'Bonjour',
            'intro': 'Nous avons reçu une demande de réinitialisation du mot de passe de votre compte Altea.',
            'instruction': 'Cliquez sur le bouton ci-dessous pour réinitialiser votre mot de passe:',
            'button': 'Réinitialiser le mot de passe',
            'expiry': 'Ce lien expirera dans {hours} heure(s). Si vous n\'avez pas demandé de réinitialisation de mot de passe, vous pouvez ignorer cet e-mail.',
            'fallback': 'Si le bouton ne fonctionne pas, copiez et collez ce lien dans votre navigateur:',
        },
        'it': {
            'subject': 'Reimposta la tua password Altea',
            'greeting': 'Ciao',
            'intro': 'Abbiamo ricevuto una richiesta di reimpostazione della password per il tuo account Altea.',
            'instruction': 'Clicca sul pulsante qui sotto per reimpostare la tua password:',
            'button': 'Reimposta password',
            'expiry': 'Questo link scadrà tra {hours} ora/e. Se non hai richiesto la reimpostazione della password, puoi ignorare questa email.',
            'fallback': 'Se il pulsante non funziona, copia e incolla questo link nel tuo browser:',
        },
    }

    @staticmethod
    def get_user_language(user: User) -> str:
        """Get user's preferred language, defaulting to 'en'."""
        # Try to get language from UserProfile if it exists
        if hasattr(user, 'profile') and user.profile:
            return user.profile.language or 'en'
        return 'en'

    @staticmethod
    def request_reset(email: str) -> tuple[bool, str]:
        """
        Request a password reset for the given email.

        Always returns success to prevent email enumeration.

        Args:
            email: User's email address

        Returns:
            Tuple of (success, message)
        """
        email = email.lower().strip()

        try:
            user = User.objects.get(email__iexact=email)
        except User.DoesNotExist:
            # Don't reveal if email exists - security best practice
            logger.info(f"Password reset requested for non-existent email: {email}")
            return True, 'If an account exists with this email, you will receive password reset instructions.'

        # Send password reset email
        success = PasswordResetService.send_reset_email(user)

        if success:
            logger.info(f"Password reset email sent: user_id={user.id}")
        else:
            logger.error(f"Failed to send password reset email: user_id={user.id}")

        # Always return success message (security)
        return True, 'If an account exists with this email, you will receive password reset instructions.'

    @staticmethod
    def send_reset_email(user: User) -> bool:
        """
        Create token and send password reset email.

        Args:
            user: User instance

        Returns:
            True if email was sent successfully
        """
        token = PasswordResetToken.create_for_user(user)

        # Build reset URL (uses Django's web view)
        base_url = getattr(settings, 'SITE_URL', 'http://localhost:8000')

        # Use Django's UID-based URL for password reset
        from django.utils.http import urlsafe_base64_encode
        from django.utils.encoding import force_bytes
        from django.contrib.auth.tokens import default_token_generator

        uid = urlsafe_base64_encode(force_bytes(user.pk))
        django_token = default_token_generator.make_token(user)
        reset_url = f"{base_url}/accounts/reset/{uid}/{django_token}/"

        # Get localized content
        language = PasswordResetService.get_user_language(user)
        content = PasswordResetService.EMAIL_CONTENT.get(language, PasswordResetService.EMAIL_CONTENT['en'])

        expiry_hours = getattr(settings, 'PASSWORD_RESET_TOKEN_EXPIRY_HOURS', 1)

        # Render email template
        context = {
            'user': user,
            'reset_url': reset_url,
            'expiry_hours': expiry_hours,
            'content': content,
        }

        html_message = render_to_string(
            'accounts/emails/password_reset_email.html',
            context
        )
        plain_message = strip_tags(html_message)

        try:
            send_mail(
                subject=content['subject'],
                message=plain_message,
                from_email=settings.DEFAULT_FROM_EMAIL,
                recipient_list=[user.email],
                html_message=html_message,
                fail_silently=False,
            )
            return True
        except Exception as e:
            logger.error(f"Failed to send password reset email: user_id={user.id}, error={e}")
            return False
