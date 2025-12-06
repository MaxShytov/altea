"""
Admin configuration for accounts app.
"""

from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.utils.translation import gettext_lazy as _
from django.utils.html import format_html
from django.utils.safestring import mark_safe
from django.utils import timezone

from .models import User, PasswordResetToken, EmailVerificationToken


class CountryFilter(admin.SimpleListFilter):
    """Filter by country - shows only countries that have users."""
    title = _('country')
    parameter_name = 'country'

    def lookups(self, request, model_admin):
        countries = User.objects.exclude(
            country__isnull=True
        ).exclude(
            country=''
        ).values_list('country', flat=True).distinct()
        from django_countries import countries as all_countries
        country_dict = dict(all_countries)
        # Use set to remove duplicates, then sort by country name
        unique_countries = set(countries)
        return sorted(
            [(code, country_dict.get(code, code)) for code in unique_countries],
            key=lambda x: x[1]
        )

    def queryset(self, request, queryset):
        if self.value():
            return queryset.filter(country=self.value())
        return queryset


@admin.register(User)
class UserAdmin(BaseUserAdmin):
    """
    Custom User admin interface.
    """
    list_display = (
        'email',
        'get_full_name',
        'profile_picture_preview',
        'is_verified_status',
        'is_staff',
        'is_active',
        'date_joined'
    )
    list_filter = ('is_staff', 'is_active', 'is_verified', CountryFilter, 'date_joined')
    search_fields = ('email', 'first_name', 'last_name', 'username')
    ordering = ('-date_joined',)

    fieldsets = (
        (None, {
            'fields': ('email', 'username', 'password')
        }),
        (_('Personal Info'), {
            'fields': ('first_name', 'last_name', 'date_of_birth', 'profile_picture')
        }),
        (_('Contact Information'), {
            'fields': ('phone', 'country')
        }),
        (_('Verification & Compliance'), {
            'fields': ('is_verified', 'terms_accepted_at'),
            'description': _('Email verification status and GDPR compliance information')
        }),
        (_('Permissions'), {
            'fields': ('is_active', 'is_staff', 'is_superuser', 'groups', 'user_permissions')
        }),
        (_('Important Dates'), {
            'fields': ('last_login', 'date_joined')
        }),
    )

    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': (
                'email',
                'username',
                'first_name',
                'last_name',
                'password1',
                'password2',
                'is_verified',
                'is_staff',
                'is_active'
            ),
        }),
    )

    readonly_fields = ('date_joined', 'last_login', 'terms_accepted_at')

    actions = ['mark_as_verified', 'mark_as_unverified']

    def profile_picture_preview(self, obj):
        """Display profile picture thumbnail in admin."""
        if obj.profile_picture:
            return format_html(
                '<img src="{}" style="width: 40px; height: 40px; border-radius: 50%; object-fit: cover;" />',
                obj.profile_picture.url
            )
        initials = obj.initials or '?'
        return format_html(
            '<div style="width: 40px; height: 40px; border-radius: 50%; background-color: #667eea; color: white; display: flex; align-items: center; justify-content: center; font-weight: bold;">{}</div>',
            initials
        )
    profile_picture_preview.short_description = _('Picture')

    def is_verified_status(self, obj):
        """Display verification status with colored badge."""
        if obj.is_verified:
            return mark_safe(
                '<span style="background-color: #10b981; color: white; padding: 3px 8px; border-radius: 12px; font-size: 11px; font-weight: 600;">Verified</span>'
            )
        return mark_safe(
            '<span style="background-color: #f59e0b; color: white; padding: 3px 8px; border-radius: 12px; font-size: 11px; font-weight: 600;">Unverified</span>'
        )
    is_verified_status.short_description = _('Email Status')
    is_verified_status.admin_order_field = 'is_verified'

    @admin.action(description=_('Mark selected users as verified'))
    def mark_as_verified(self, request, queryset):
        updated = queryset.update(is_verified=True)
        self.message_user(request, _('%(count)d user(s) marked as verified.') % {'count': updated})

    @admin.action(description=_('Mark selected users as unverified'))
    def mark_as_unverified(self, request, queryset):
        updated = queryset.update(is_verified=False)
        self.message_user(request, _('%(count)d user(s) marked as unverified.') % {'count': updated})


@admin.register(PasswordResetToken)
class PasswordResetTokenAdmin(admin.ModelAdmin):
    """
    Admin interface for password reset tokens.
    """
    list_display = ('user', 'is_used_status', 'is_valid_status', 'created_at', 'expires_at')
    list_filter = ('created_at', 'expires_at')
    search_fields = ('user__email', 'token')
    readonly_fields = ('user', 'token', 'created_at', 'updated_at', 'expires_at', 'used_at')

    def is_used_status(self, obj):
        """Display if token has been used."""
        if obj.used_at is not None:
            return mark_safe('<span style="color: gray;">Used</span>')
        return mark_safe('<span style="color: green;">Not used</span>')
    is_used_status.short_description = _('Used')

    def is_valid_status(self, obj):
        """Display if token is valid."""
        if obj.is_valid():
            return mark_safe(
                '<span style="color: green; font-weight: bold;">✓ Valid</span>'
            )
        return mark_safe(
            '<span style="color: red; font-weight: bold;">✗ Invalid</span>'
        )
    is_valid_status.short_description = _('Status')

    def has_add_permission(self, request):
        """Disable manual creation of tokens."""
        return False


@admin.register(EmailVerificationToken)
class EmailVerificationTokenAdmin(admin.ModelAdmin):
    """
    Admin interface for email verification tokens.
    """
    list_display = ('user', 'token_preview', 'is_valid_status', 'created_at', 'expires_at', 'used_at')
    list_filter = ('created_at', 'expires_at', 'used_at')
    search_fields = ('user__email', 'user__first_name', 'user__last_name', 'token')
    readonly_fields = ('user', 'token', 'created_at', 'updated_at', 'expires_at', 'used_at')
    ordering = ('-created_at',)

    fieldsets = (
        (None, {
            'fields': ('user', 'token')
        }),
        (_('Token Status'), {
            'fields': ('expires_at', 'used_at')
        }),
        (_('Timestamps'), {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )

    def token_preview(self, obj):
        """Display truncated token for security."""
        return f"{obj.token[:8]}...{obj.token[-4:]}"
    token_preview.short_description = _('Token')

    def is_valid_status(self, obj):
        """Display if token is valid with colored badge."""
        if obj.is_valid():
            return mark_safe(
                '<span style="background-color: #10b981; color: white; padding: 3px 8px; border-radius: 12px; font-size: 11px; font-weight: 600;">Valid</span>'
            )
        elif obj.used_at:
            return mark_safe(
                '<span style="background-color: #6b7280; color: white; padding: 3px 8px; border-radius: 12px; font-size: 11px; font-weight: 600;">Used</span>'
            )
        else:
            return mark_safe(
                '<span style="background-color: #ef4444; color: white; padding: 3px 8px; border-radius: 12px; font-size: 11px; font-weight: 600;">Expired</span>'
            )
    is_valid_status.short_description = _('Status')

    def has_add_permission(self, request):
        """Disable manual creation of tokens."""
        return False

    def has_change_permission(self, request, obj=None):
        """Tokens should not be editable."""
        return False

    actions = ['invalidate_tokens']

    @admin.action(description=_('Invalidate selected tokens'))
    def invalidate_tokens(self, request, queryset):
        """Mark selected tokens as used (invalidate them)."""
        updated = queryset.filter(used_at__isnull=True).update(used_at=timezone.now())
        self.message_user(request, _('%(count)d token(s) invalidated.') % {'count': updated})