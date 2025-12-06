"""
Core models - base models used across the application.
"""

import re
from io import BytesIO

from django.conf import settings
from django.core.cache import cache
from django.core.exceptions import ValidationError
from django.core.files.base import ContentFile
from django.db import models
from django.utils.translation import gettext_lazy as _
from PIL import Image


class TimeStampedModel(models.Model):
    """
    Abstract base model that provides self-updating
    'created_at' and 'updated_at' fields.
    """
    created_at = models.DateTimeField(
        _('created at'),
        auto_now_add=True,
        help_text=_('Date and time when the record was created')
    )
    updated_at = models.DateTimeField(
        _('updated at'),
        auto_now=True,
        help_text=_('Date and time when the record was last updated')
    )

    class Meta:
        abstract = True
        ordering = ['-created_at']


class ActiveManager(models.Manager):
    """Manager that returns only active (non-deleted) records."""
    
    def get_queryset(self):
        return super().get_queryset().filter(is_active=True)


class SoftDeleteModel(TimeStampedModel):
    """
    Abstract base model that provides soft delete functionality.
    Records are marked as inactive instead of being deleted.
    """
    is_active = models.BooleanField(
        _('active'),
        default=True,
        help_text=_('Designates whether this record should be treated as active.')
    )
    deleted_at = models.DateTimeField(
        _('deleted at'),
        null=True,
        blank=True,
        help_text=_('Date and time when the record was soft deleted')
    )

    objects = models.Manager()  # Default manager
    active_objects = ActiveManager()  # Manager for active records only

    class Meta:
        abstract = True

    def delete(self, using=None, keep_parents=False, hard=False):
        """
        Soft delete by default. Pass hard=True for actual deletion.
        """
        if hard:
            super().delete(using=using, keep_parents=keep_parents)
        else:
            from django.utils import timezone
            self.is_active = False
            self.deleted_at = timezone.now()
            self.save()

    def restore(self):
        """Restore a soft-deleted record."""
        self.is_active = True
        self.deleted_at = None
        self.save()


class LegalDocument(TimeStampedModel):
    """
    Model to store versioned legal documents (Terms of Service, Privacy Policy).
    Only one document of each type can be active at a time.
    """
    DOCUMENT_TYPES = [
        ('terms', _('Terms of Service')),
        ('privacy', _('Privacy Policy')),
    ]

    document_type = models.CharField(
        _('document type'),
        max_length=20,
        choices=DOCUMENT_TYPES,
        db_index=True,
        help_text=_('Type of legal document')
    )

    version = models.CharField(
        _('version'),
        max_length=20,
        help_text=_('Version number (e.g., "1.0", "2.0")')
    )

    title = models.CharField(
        _('title'),
        max_length=200,
        help_text=_('Document title displayed to users')
    )

    content = models.TextField(
        _('content'),
        help_text=_('HTML content of the document')
    )

    effective_date = models.DateField(
        _('effective date'),
        help_text=_('Date when this version becomes effective')
    )

    is_active = models.BooleanField(
        _('active'),
        default=False,
        help_text=_('Only one document per type can be active. '
                    'Activating this will deactivate others of the same type.')
    )

    class Meta:
        verbose_name = _('legal document')
        verbose_name_plural = _('legal documents')
        ordering = ['-effective_date']
        unique_together = ['document_type', 'version']

    def __str__(self):
        return f"{self.get_document_type_display()} v{self.version}"

    def save(self, *args, **kwargs):
        """Ensure only one active document per type."""
        if self.is_active:
            # Deactivate other documents of the same type
            LegalDocument.objects.filter(
                document_type=self.document_type,
                is_active=True
            ).exclude(pk=self.pk).update(is_active=False)
        super().save(*args, **kwargs)

    @classmethod
    def get_active(cls, document_type):
        """Get the currently active document of the specified type."""
        return cls.objects.filter(
            document_type=document_type,
            is_active=True
        ).first()


def validate_hex_color(value):
    """Validate that value is a valid hex color code."""
    if not re.match(r'^#[0-9A-Fa-f]{6}$', value):
        raise ValidationError(
            _('%(value)s is not a valid hex color. Use format #RRGGBB'),
            params={'value': value},
        )


class AppSettings(TimeStampedModel):
    """
    Singleton model for application branding and configuration.
    Only one instance should exist (pk=1).
    """
    # Branding
    app_name = models.CharField(
        _('application name'),
        max_length=100,
        default='App name',
        help_text=_('Application name displayed across the app')
    )
    hero_text = models.CharField(
        _('hero text'),
        max_length=255,
        default='Your hero string',
        help_text=_('Tagline displayed on home screen and emails')
    )

    # Logo
    logo = models.ImageField(
        _('logo'),
        upload_to='branding/',
        blank=True,
        null=True,
        help_text=_('Main logo (recommended: 512x512 PNG, max 2MB)')
    )
    logo_small = models.ImageField(
        _('small logo'),
        upload_to='branding/',
        blank=True,
        null=True,
        editable=False,
        help_text=_('Auto-generated small version (64x64)')
    )

    # Colors
    primary_color = models.CharField(
        _('primary color'),
        max_length=7,
        default='#667eea',
        validators=[validate_hex_color],
        help_text=_('Primary brand color (hex, e.g. #667eea)')
    )
    secondary_color = models.CharField(
        _('secondary color'),
        max_length=7,
        default='#764ba2',
        validators=[validate_hex_color],
        help_text=_('Secondary brand color (hex, e.g. #764ba2)')
    )

    # Contact Information
    contact_email = models.EmailField(
        _('contact email'),
        default='support@example.com',
        help_text=_('Support contact email shown in app and emails')
    )
    support_url = models.URLField(
        _('support URL'),
        blank=True,
        default='',
        help_text=_('Link to support page or documentation')
    )

    class Meta:
        verbose_name = _('App Settings')
        verbose_name_plural = _('App Settings')

    def __str__(self):
        return f"App Settings ({self.app_name})"

    def save(self, *args, **kwargs):
        """
        Enforce singleton pattern and generate thumbnail.
        """
        # Singleton: always use pk=1
        self.pk = 1

        # Check if logo changed and we need to regenerate thumbnail
        if self.pk:
            try:
                old_instance = AppSettings.objects.get(pk=1)
                if self.logo and self.logo != old_instance.logo:
                    # Logo changed, clear old small logo to regenerate
                    self.logo_small = None
            except AppSettings.DoesNotExist:
                pass

        # Generate small logo if main logo exists and small doesn't
        if self.logo and not self.logo_small:
            self._generate_small_logo()

        super().save(*args, **kwargs)

        # Invalidate cache after save
        self._invalidate_cache()

    def delete(self, *args, **kwargs):
        """Prevent deletion of singleton."""
        pass  # Do nothing - singleton cannot be deleted

    def _generate_small_logo(self):
        """Generate 64x64 thumbnail from main logo."""
        if not self.logo:
            return

        try:
            img = Image.open(self.logo)
            img.thumbnail((64, 64), Image.Resampling.LANCZOS)

            # Handle different image modes
            if img.mode in ('RGBA', 'P'):
                img = img.convert('RGBA')
                format_ext = 'PNG'
            else:
                img = img.convert('RGB')
                format_ext = 'JPEG'

            # Save to BytesIO
            thumb_io = BytesIO()
            img.save(thumb_io, format=format_ext, quality=90)
            thumb_io.seek(0)

            # Generate filename
            original_name = self.logo.name.split('/')[-1]
            name_without_ext = original_name.rsplit('.', 1)[0]
            thumb_name = f"{name_without_ext}_small.{format_ext.lower()}"

            # Save to field
            self.logo_small.save(
                thumb_name,
                ContentFile(thumb_io.read()),
                save=False
            )
        except Exception:
            # If thumbnail generation fails, continue without it
            pass

    def _invalidate_cache(self):
        """Clear the cached settings."""
        cache_key = getattr(settings, 'APP_SETTINGS_CACHE_KEY', 'app_settings')
        cache.delete(cache_key)

    @classmethod
    def get_settings(cls):
        """
        Get cached settings or load from DB.
        Creates default settings if none exist.
        """
        cache_key = getattr(settings, 'APP_SETTINGS_CACHE_KEY', 'app_settings')
        cache_timeout = getattr(settings, 'APP_SETTINGS_CACHE_TIMEOUT', 3600)

        cached = cache.get(cache_key)
        if cached is not None:
            return cached

        # Get or create settings
        obj, _ = cls.objects.get_or_create(pk=1)
        cache.set(cache_key, obj, timeout=cache_timeout)
        return obj

    @property
    def logo_initial(self):
        """Return first letter of app_name for fallback logo."""
        if self.app_name:
            return self.app_name[0].upper()
        return 'A'

    @property
    def logo_url(self):
        """Return logo URL or None."""
        if self.logo:
            return self.logo.url
        return None

    @property
    def logo_small_url(self):
        """Return small logo URL or None."""
        if self.logo_small:
            return self.logo_small.url
        return None