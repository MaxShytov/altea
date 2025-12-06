"""
Business logic services for accounts app.
"""

import logging
from typing import Optional

from django.conf import settings
from django.core.mail import send_mail
from django.template.loader import render_to_string
from django.utils import timezone
from django.utils.html import strip_tags

from .models import User, EmailVerificationToken

logger = logging.getLogger(__name__)


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
