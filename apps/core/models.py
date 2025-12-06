"""
Core models - base models used across the application.
"""

from django.db import models
from django.utils.translation import gettext_lazy as _


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