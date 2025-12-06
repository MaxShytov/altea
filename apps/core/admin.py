"""
Core admin configuration - includes LegalDocument and AppSettings admin.
"""

from django.contrib import admin
from django.utils.html import format_html, mark_safe

from apps.core.models import AppSettings, LegalDocument


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


@admin.register(AppSettings)
class AppSettingsAdmin(admin.ModelAdmin):
    """
    Admin for singleton AppSettings.
    Only superusers can access.
    """
    list_display = [
        'app_name',
        'hero_text',
        'logo_preview',
        'primary_color_preview',
        'updated_at',
    ]
    readonly_fields = [
        'created_at',
        'updated_at',
        'logo_preview_large',
        'logo_small_preview',
    ]

    fieldsets = (
        ('Branding', {
            'fields': ('app_name', 'hero_text'),
            'description': 'Main branding elements displayed across the application.',
        }),
        ('Logo', {
            'fields': ('logo', 'logo_preview_large', 'logo_small_preview'),
            'description': 'Upload a logo (recommended 512x512 PNG). '
                           'A small version will be auto-generated.',
        }),
        ('Colors', {
            'fields': ('primary_color', 'secondary_color'),
            'description': 'Brand colors used in the application. Use hex format (#RRGGBB).',
        }),
        ('Contact', {
            'fields': ('contact_email', 'support_url'),
            'description': 'Contact information displayed in emails and support sections.',
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',),
        }),
    )

    def has_add_permission(self, request):
        """Prevent adding if settings already exist."""
        return not AppSettings.objects.exists()

    def has_delete_permission(self, request, obj=None):
        """Prevent deletion of singleton."""
        return False

    def get_queryset(self, request):
        """Only superusers can see settings."""
        qs = super().get_queryset(request)
        if not request.user.is_superuser:
            return qs.none()
        return qs

    def has_view_permission(self, request, obj=None):
        return request.user.is_superuser

    def has_change_permission(self, request, obj=None):
        return request.user.is_superuser

    @admin.display(description='Logo')
    def logo_preview(self, obj):
        """Display logo thumbnail in list view."""
        if obj.logo:
            return format_html(
                '<img src="{}" style="max-height: 40px; max-width: 40px; '
                'border-radius: 4px;" />',
                obj.logo.url
            )
        return format_html(
            '<span style="display: inline-flex; align-items: center; '
            'justify-content: center; width: 40px; height: 40px; '
            'background: {}; color: white; border-radius: 4px; '
            'font-weight: bold; font-size: 20px;">{}</span>',
            obj.primary_color,
            obj.logo_initial
        )

    @admin.display(description='Logo Preview')
    def logo_preview_large(self, obj):
        """Display large logo preview in edit form."""
        if obj.logo:
            return format_html(
                '<img src="{}" style="max-height: 128px; max-width: 128px; '
                'border-radius: 8px;" />',
                obj.logo.url
            )
        return format_html(
            '<span style="display: inline-flex; align-items: center; '
            'justify-content: center; width: 128px; height: 128px; '
            'background: {}; color: white; border-radius: 8px; '
            'font-weight: bold; font-size: 64px;">{}</span>',
            obj.primary_color,
            obj.logo_initial
        )

    @admin.display(description='Small Logo (64x64)')
    def logo_small_preview(self, obj):
        """Display auto-generated small logo."""
        if obj.logo_small:
            return format_html(
                '<img src="{}" style="max-height: 64px; max-width: 64px; '
                'border-radius: 4px;" />',
                obj.logo_small.url
            )
        return 'Auto-generated when logo is uploaded'

    @admin.display(description='Primary Color')
    def primary_color_preview(self, obj):
        """Display color swatch with hex value."""
        return format_html(
            '<span style="display: inline-block; width: 20px; height: 20px; '
            'background: {}; border-radius: 3px; vertical-align: middle; '
            'margin-right: 8px;"></span>{}',
            obj.primary_color,
            obj.primary_color
        )
