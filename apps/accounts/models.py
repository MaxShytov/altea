"""
User model and authentication models.
"""

import hashlib
import random
import uuid

from django.conf import settings
from django.contrib.auth.models import AbstractUser
from django.db import models
from django.utils import timezone
from django.utils.translation import gettext_lazy as _
from django_countries.fields import CountryField

from apps.core.models import TimeStampedModel
from apps.core.validators import validate_swiss_phone


class User(AbstractUser):
    """
    Custom User model extending Django's AbstractUser.
    Uses email as the primary identifier instead of username.
    """

    # Override email to make it unique and required
    email = models.EmailField(
        _('email address'),
        unique=True,
        error_messages={
            'unique': _("A user with that email already exists."),
        }
    )

    # Email verification status
    is_verified = models.BooleanField(
        _('email verified'),
        default=False,
        help_text=_('Designates whether the user has verified their email address.')
    )

    # GDPR compliance: store date/time of Terms acceptance
    terms_accepted_at = models.DateTimeField(
        _('terms accepted at'),
        null=True,
        blank=True,
        help_text=_('Date and time when user accepted Terms & Conditions')
    )

    # Track which version of legal documents user accepted
    terms_version_accepted = models.CharField(
        _('terms version accepted'),
        max_length=20,
        blank=True,
        help_text=_('Version of Terms of Service user accepted')
    )

    privacy_version_accepted = models.CharField(
        _('privacy version accepted'),
        max_length=20,
        blank=True,
        help_text=_('Version of Privacy Policy user accepted')
    )

    # Additional fields
    phone = models.CharField(
        _('phone number'),
        max_length=20,
        blank=True,
        validators=[validate_swiss_phone],
        help_text=_('Swiss phone format: +41 XX XXX XX XX or 0XX XXX XX XX')
    )

    country = CountryField(
        _('country'),
        default='CH',  # Switzerland
        blank_label=_('Select country')
    )

    date_of_birth = models.DateField(
        _('date of birth'),
        null=True,
        blank=True
    )

    profile_picture = models.ImageField(
        _('profile picture'),
        upload_to='profile_pictures/%Y/%m/',
        null=True,
        blank=True
    )

    # Use email as username
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username', 'first_name', 'last_name']
    
    class Meta:
        verbose_name = _('user')
        verbose_name_plural = _('users')
        ordering = ['-date_joined']
    
    def __str__(self):
        return self.email
    
    def get_full_name(self):
        """Return the full name."""
        full_name = f"{self.first_name} {self.last_name}".strip()
        return full_name or self.email
    
    def get_short_name(self):
        """Return the short name."""
        return self.first_name or self.email.split('@')[0]
    
    @property
    def initials(self):
        """Return user initials (e.g., 'JD' for John Doe)."""
        if self.first_name and self.last_name:
            return f"{self.first_name[0]}{self.last_name[0]}".upper()
        return self.email[0].upper()


class PasswordResetToken(TimeStampedModel):
    """
    Model to store password reset tokens.
    Tokens expire after 1 hour (configurable via settings).
    """
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='password_reset_tokens',
        verbose_name=_('user')
    )

    token = models.CharField(
        _('token'),
        max_length=64,
        unique=True,
        db_index=True
    )

    expires_at = models.DateTimeField(
        _('expires at')
    )

    used_at = models.DateTimeField(
        _('used at'),
        null=True,
        blank=True,
        help_text=_('Date and time when token was used for password reset')
    )

    class Meta:
        verbose_name = _('password reset token')
        verbose_name_plural = _('password reset tokens')
        ordering = ['-created_at']

    def __str__(self):
        return f"Reset token for {self.user.email}"

    def is_valid(self):
        """Check if token is still valid (not used and not expired)."""
        from django.utils import timezone
        return self.used_at is None and timezone.now() < self.expires_at

    def mark_used(self):
        """Mark token as used and save."""
        from django.utils import timezone
        self.used_at = timezone.now()
        self.save(update_fields=['used_at', 'updated_at'])

    @classmethod
    def create_for_user(cls, user):
        """
        Create a new password reset token for the given user.
        Invalidates any existing unused tokens for this user.
        """
        import secrets
        from django.utils import timezone
        from django.conf import settings

        # Invalidate existing unused tokens
        cls.objects.filter(user=user, used_at__isnull=True).update(
            used_at=timezone.now()
        )

        # Get expiry hours from settings (default 1 hour for password reset)
        expiry_hours = getattr(settings, 'PASSWORD_RESET_TOKEN_EXPIRY_HOURS', 1)

        # Create new token
        token = cls.objects.create(
            user=user,
            token=secrets.token_urlsafe(32),
            expires_at=timezone.now() + timezone.timedelta(hours=expiry_hours)
        )
        return token


class EmailVerificationToken(TimeStampedModel):
    """
    Model to store email verification tokens.
    Tokens expire after configurable hours (default 24).
    """
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='email_verification_tokens',
        verbose_name=_('user')
    )

    token = models.CharField(
        _('token'),
        max_length=64,
        unique=True,
        db_index=True
    )

    expires_at = models.DateTimeField(
        _('expires at')
    )

    used_at = models.DateTimeField(
        _('used at'),
        null=True,
        blank=True,
        help_text=_('Date and time when token was used for verification')
    )

    class Meta:
        verbose_name = _('email verification token')
        verbose_name_plural = _('email verification tokens')
        ordering = ['-created_at']

    def __str__(self):
        return f"Verification token for {self.user.email}"

    def is_valid(self):
        """Check if token is still valid (not used and not expired)."""
        from django.utils import timezone
        return self.used_at is None and timezone.now() < self.expires_at

    def mark_used(self):
        """Mark token as used and save."""
        from django.utils import timezone
        self.used_at = timezone.now()
        self.save(update_fields=['used_at', 'updated_at'])

    @classmethod
    def create_for_user(cls, user):
        """
        Create a new verification token for the given user.
        Invalidates any existing unused tokens for this user.
        """
        import secrets
        from django.utils import timezone
        from django.conf import settings

        # Invalidate existing unused tokens
        cls.objects.filter(user=user, used_at__isnull=True).update(
            used_at=timezone.now()
        )

        # Get expiry hours from settings (default 24)
        expiry_hours = getattr(settings, 'EMAIL_VERIFICATION_TOKEN_EXPIRY_HOURS', 24)

        # Create new token
        token = cls.objects.create(
            user=user,
            token=secrets.token_urlsafe(32),
            expires_at=timezone.now() + timezone.timedelta(hours=expiry_hours)
        )
        return token


class OTPToken(TimeStampedModel):
    """
    Model for storing OTP (One-Time Password) tokens for passwordless authentication.

    Tokens are 6-digit numeric codes sent via email for login/registration.
    - Expires after OTP_EXPIRY_MINUTES (default: 1 minute)
    - Max OTP_MAX_ATTEMPTS verification attempts (default: 5)
    - Code is stored as SHA256 hash for security
    """

    id = models.UUIDField(
        primary_key=True,
        default=uuid.uuid4,
        editable=False
    )

    email = models.EmailField(
        _('email'),
        db_index=True,
        help_text=_('Email address for OTP verification')
    )

    code_hash = models.CharField(
        _('code hash'),
        max_length=128,
        help_text=_('SHA256 hash of the OTP code')
    )

    expires_at = models.DateTimeField(
        _('expires at'),
        db_index=True,
        help_text=_('Date and time when the OTP expires')
    )

    attempts = models.PositiveIntegerField(
        _('attempts'),
        default=0,
        help_text=_('Number of verification attempts made')
    )

    used = models.BooleanField(
        _('used'),
        default=False,
        db_index=True,
        help_text=_('Whether the OTP has been successfully used')
    )

    ip_address = models.GenericIPAddressField(
        _('IP address'),
        null=True,
        blank=True,
        help_text=_('IP address from which OTP was requested')
    )

    class Meta:
        verbose_name = _('OTP token')
        verbose_name_plural = _('OTP tokens')
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['email', 'used', '-created_at']),
        ]

    def __str__(self) -> str:
        return f"OTP for {self.email} (expires: {self.expires_at})"

    @property
    def max_attempts(self) -> int:
        """Get max allowed attempts from settings."""
        return getattr(settings, 'OTP_MAX_ATTEMPTS', 5)

    @property
    def is_expired(self) -> bool:
        """Check if OTP has expired."""
        return timezone.now() >= self.expires_at

    @property
    def is_max_attempts_reached(self) -> bool:
        """Check if max verification attempts reached."""
        return self.attempts >= self.max_attempts

    @property
    def attempts_remaining(self) -> int:
        """Get number of remaining verification attempts."""
        return max(0, self.max_attempts - self.attempts)

    def is_valid(self) -> bool:
        """
        Check if token is still valid for verification.

        Returns:
            True if token can be used for verification.
        """
        return (
            not self.used and
            not self.is_expired and
            not self.is_max_attempts_reached
        )

    def verify_code(self, code: str) -> bool:
        """
        Verify if the provided code matches this token.

        Args:
            code: The 6-digit OTP code to verify.

        Returns:
            True if code is valid, False otherwise.
        """
        code_hash = hashlib.sha256(code.encode()).hexdigest()
        return code_hash == self.code_hash

    def increment_attempts(self) -> None:
        """Increment the attempts counter."""
        self.attempts += 1
        self.save(update_fields=['attempts', 'updated_at'])

    def mark_used(self) -> None:
        """Mark OTP as successfully used."""
        self.used = True
        self.save(update_fields=['used', 'updated_at'])

    @classmethod
    def generate_code(cls) -> str:
        """
        Generate a 6-digit OTP code.

        Returns:
            String of 6 random digits.
        """
        return str(random.randint(100000, 999999))

    @classmethod
    def hash_code(cls, code: str) -> str:
        """
        Hash OTP code using SHA256.

        Args:
            code: The plain text OTP code.

        Returns:
            SHA256 hash of the code.
        """
        return hashlib.sha256(code.encode()).hexdigest()

    @classmethod
    def create_for_email(cls, email: str, ip_address: str = None) -> tuple['OTPToken', str]:
        """
        Create a new OTP token for the given email.
        Invalidates any existing unused tokens for this email.

        Args:
            email: Email address to create OTP for.
            ip_address: IP address of the requester.

        Returns:
            Tuple of (OTPToken instance, plain text code).
        """
        # Normalize email
        email = email.lower().strip()

        # Invalidate existing unused tokens for this email
        cls.objects.filter(email=email, used=False).update(used=True)

        # Generate new code
        code = cls.generate_code()
        code_hash = cls.hash_code(code)

        # Get expiry minutes from settings (default 1 minute)
        expiry_minutes = getattr(settings, 'OTP_EXPIRY_MINUTES', 1)

        # Create new token
        token = cls.objects.create(
            email=email,
            code_hash=code_hash,
            expires_at=timezone.now() + timezone.timedelta(minutes=expiry_minutes),
            ip_address=ip_address,
        )

        return token, code

    @classmethod
    def get_latest_valid(cls, email: str) -> 'OTPToken':
        """
        Get the latest valid OTP token for the given email.

        Args:
            email: Email address to look up.

        Returns:
            OTPToken instance or None if no valid token exists.
        """
        email = email.lower().strip()
        return cls.objects.filter(
            email=email,
            used=False,
            expires_at__gt=timezone.now(),
        ).order_by('-created_at').first()