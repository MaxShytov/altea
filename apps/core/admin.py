"""
Core admin configuration - includes LegalDocument admin.
"""

from django.contrib import admin
from django.utils.html import mark_safe

from apps.core.models import LegalDocument


@admin.register(LegalDocument)
class LegalDocumentAdmin(admin.ModelAdmin):
    """Admin configuration for LegalDocument model."""

    list_display = [
        'title',
        'document_type',
        'version',
        'effective_date',
        'status_badge',
        'created_at',
    ]
    list_filter = ['document_type', 'is_active', 'effective_date']
    search_fields = ['title', 'version', 'content']
    readonly_fields = ['created_at', 'updated_at']
    ordering = ['-effective_date', 'document_type']

    fieldsets = (
        (None, {
            'fields': ('document_type', 'version', 'title')
        }),
        ('Content', {
            'fields': ('content',),
            'classes': ('wide',),
        }),
        ('Status', {
            'fields': ('effective_date', 'is_active')
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',),
        }),
    )

    @admin.display(description='Status')
    def status_badge(self, obj):
        """Display active status as a colored badge."""
        if obj.is_active:
            return mark_safe(
                '<span style="background-color: #28a745; color: white; '
                'padding: 3px 10px; border-radius: 12px; font-size: 11px;">Active</span>'
            )
        return mark_safe(
            '<span style="background-color: #6c757d; color: white; '
            'padding: 3px 10px; border-radius: 12px; font-size: 11px;">Inactive</span>'
        )

    def save_model(self, request, obj, form, change):
        """Override save to handle activation logic."""
        super().save_model(request, obj, form, change)

    class Media:
        css = {
            'all': ('admin/css/widgets.css',)
        }
