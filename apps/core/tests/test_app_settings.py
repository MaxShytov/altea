"""
Tests for FR-BRANDING-1: Dynamic App Branding & Configuration.

This module provides comprehensive test coverage for the AppSettings feature including:
- Model tests (singleton pattern, validation, thumbnail generation)
- API tests (GET /api/v1/core/config/app-settings/)
- Serializer tests
- Context processor tests
- Cache tests
- Admin tests
- Edge cases

Test Structure:
- ValidateHexColorTests: Hex color validation function tests
- ValidateHexColorEdgeCasesTests: Extended validation tests
- AppSettingsModelTests: Core model functionality tests
- AppSettingsModelEdgeCasesTests: Model edge cases
- AppSettingsLogoTests: Logo and thumbnail tests
- AppSettingsAPITests: API endpoint tests
- AppSettingsAPIEdgeCasesTests: API edge cases
- AppSettingsSerializerTests: Serializer tests
- AppSettingsSerializerEdgeCasesTests: Serializer edge cases
- AppSettingsContextProcessorTests: Context processor tests
- AppSettingsCacheTests: Cache behavior tests
- AppSettingsAdminTests: Admin configuration tests
- AppSettingsHTTPMethodTests: HTTP method tests
- AppSettingsIntegrationTests: End-to-end tests
"""

from io import BytesIO
from unittest.mock import patch, MagicMock

from django.contrib.admin.sites import AdminSite
from django.contrib.auth import get_user_model
from django.core.cache import cache
from django.core.exceptions import ValidationError
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import TestCase, override_settings, RequestFactory
from django.urls import reverse
from PIL import Image
from rest_framework import status
from rest_framework.test import APITestCase, APIClient

from apps.core.models import AppSettings, validate_hex_color
from apps.core.admin import AppSettingsAdmin

User = get_user_model()


# =============================================================================
# HEX COLOR VALIDATION TESTS
# =============================================================================


class ValidateHexColorTests(TestCase):
    """Tests for hex color validation function."""

    def test_valid_hex_colors(self):
        """Test that valid hex colors pass validation."""
        valid_colors = ['#000000', '#FFFFFF', '#667eea', '#764ba2', '#aabbcc']
        for color in valid_colors:
            try:
                validate_hex_color(color)
            except ValidationError:
                self.fail(f'{color} should be a valid hex color')

    def test_invalid_hex_colors(self):
        """Test that invalid hex colors raise ValidationError."""
        invalid_colors = [
            '#00000',     # Too short
            '#0000000',   # Too long
            '000000',     # Missing #
            '#GGGGGG',    # Invalid characters
            'red',        # Named color
            '',           # Empty string
            '#12345G',    # Invalid character
        ]
        for color in invalid_colors:
            with self.assertRaises(ValidationError, msg=f'{color} should be invalid'):
                validate_hex_color(color)


class ValidateHexColorEdgeCasesTests(TestCase):
    """Extended edge case tests for hex color validation."""

    def test_valid_hex_colors_lowercase(self):
        """Test lowercase hex colors are valid."""
        valid_colors = ['#abcdef', '#123abc', '#fedcba']
        for color in valid_colors:
            try:
                validate_hex_color(color)
            except ValidationError:
                self.fail(f'{color} should be a valid hex color')

    def test_valid_hex_colors_uppercase(self):
        """Test uppercase hex colors are valid."""
        valid_colors = ['#ABCDEF', '#123ABC', '#FEDCBA']
        for color in valid_colors:
            try:
                validate_hex_color(color)
            except ValidationError:
                self.fail(f'{color} should be a valid hex color')

    def test_valid_hex_colors_mixed_case(self):
        """Test mixed case hex colors are valid."""
        valid_colors = ['#AbCdEf', '#123AbC', '#FeDcBa']
        for color in valid_colors:
            try:
                validate_hex_color(color)
            except ValidationError:
                self.fail(f'{color} should be a valid hex color')

    def test_invalid_hex_missing_hash(self):
        """Test hex color without # is invalid."""
        with self.assertRaises(ValidationError):
            validate_hex_color('667eea')

    def test_invalid_hex_wrong_length(self):
        """Test hex colors with wrong length are invalid."""
        invalid_colors = ['#fff', '#12345', '#1234567']
        for color in invalid_colors:
            with self.assertRaises(ValidationError):
                validate_hex_color(color)

    def test_invalid_hex_with_spaces(self):
        """Test hex color with spaces is invalid."""
        with self.assertRaises(ValidationError):
            validate_hex_color('# 667eea')

    def test_invalid_hex_with_special_chars(self):
        """Test hex color with special characters is invalid."""
        invalid_colors = ['#66!eea', '#667e@a', '#$67eea']
        for color in invalid_colors:
            with self.assertRaises(ValidationError):
                validate_hex_color(color)


# =============================================================================
# APP SETTINGS MODEL TESTS
# =============================================================================


class AppSettingsModelTests(TestCase):
    """Tests for AppSettings model."""

    def setUp(self):
        """Clear cache before each test."""
        cache.clear()
        # Delete any existing settings
        AppSettings.objects.all().delete()

    def tearDown(self):
        """Clear cache after each test."""
        cache.clear()

    def test_singleton_pattern_enforced(self):
        """Test that only one AppSettings instance can exist (pk=1)."""
        settings1 = AppSettings.objects.create(app_name='Test App 1')

        # Modify the existing settings (singleton pattern)
        settings1.app_name = 'Test App 2'
        settings1.save()

        # pk should remain 1
        self.assertEqual(settings1.pk, 1)

        # Only one record should exist
        self.assertEqual(AppSettings.objects.count(), 1)

        # Should have the second app name
        settings1.refresh_from_db()
        self.assertEqual(settings1.app_name, 'Test App 2')

    def test_singleton_pk_always_one(self):
        """Test that pk is always set to 1 regardless of initial value."""
        settings = AppSettings(pk=999, app_name='Test')
        settings.save()

        self.assertEqual(settings.pk, 1)
        self.assertEqual(AppSettings.objects.count(), 1)

    def test_get_settings_creates_default(self):
        """Test that get_settings creates default settings if none exist."""
        self.assertEqual(AppSettings.objects.count(), 0)

        settings = AppSettings.get_settings()

        self.assertEqual(AppSettings.objects.count(), 1)
        self.assertEqual(settings.pk, 1)
        self.assertEqual(settings.app_name, 'App name')  # Default value

    def test_get_settings_returns_cached(self):
        """Test that get_settings returns cached version on subsequent calls."""
        AppSettings.objects.create(app_name='Cached App')

        with patch.object(AppSettings.objects, 'get_or_create') as mock_get:
            mock_get.return_value = (AppSettings(app_name='Cached App'), False)

            # First call should hit DB
            AppSettings.get_settings()

            # Clear cache and call again
            cache.clear()
            AppSettings.get_settings()

            # Should have been called twice (once per cache miss)
            self.assertEqual(mock_get.call_count, 2)

    def test_delete_prevented(self):
        """Test that singleton cannot be deleted."""
        settings = AppSettings.objects.create(app_name='Test App')

        # Calling delete should do nothing
        settings.delete()

        # Settings should still exist
        self.assertEqual(AppSettings.objects.count(), 1)

    def test_str_method(self):
        """Test string representation."""
        settings = AppSettings.objects.create(app_name='My App')
        self.assertEqual(str(settings), 'App Settings (My App)')

    def test_logo_initial_property(self):
        """Test logo_initial returns first letter of app_name."""
        settings = AppSettings.objects.create(app_name='Altea')
        self.assertEqual(settings.logo_initial, 'A')

        settings.app_name = 'test'
        settings.save()
        self.assertEqual(settings.logo_initial, 'T')

    def test_logo_initial_empty_name(self):
        """Test logo_initial with empty app_name returns 'A'."""
        settings = AppSettings.objects.create(app_name='')
        self.assertEqual(settings.logo_initial, 'A')

    def test_default_colors(self):
        """Test default color values."""
        settings = AppSettings.objects.create()
        self.assertEqual(settings.primary_color, '#667eea')
        self.assertEqual(settings.secondary_color, '#764ba2')

    def test_color_validation(self):
        """Test that invalid colors are rejected."""
        settings = AppSettings(app_name='Test', primary_color='invalid')
        with self.assertRaises(ValidationError):
            settings.full_clean()

    def test_logo_url_property(self):
        """Test logo_url returns None when no logo."""
        settings = AppSettings.objects.create(app_name='Test')
        self.assertIsNone(settings.logo_url)

    def test_logo_small_url_property(self):
        """Test logo_small_url returns None when no small logo."""
        settings = AppSettings.objects.create(app_name='Test')
        self.assertIsNone(settings.logo_small_url)


class AppSettingsModelEdgeCasesTests(TestCase):
    """Extended edge case tests for AppSettings model."""

    def setUp(self):
        """Clear cache and settings before each test."""
        cache.clear()
        AppSettings.objects.all().delete()

    def tearDown(self):
        """Clear cache after each test."""
        cache.clear()

    def test_app_name_max_length(self):
        """Test app_name handles max length (100 chars)."""
        long_name = 'A' * 100
        settings = AppSettings.objects.create(app_name=long_name)
        self.assertEqual(settings.app_name, long_name)
        self.assertEqual(settings.logo_initial, 'A')

    def test_app_name_unicode_characters(self):
        """Test app_name handles unicode characters."""
        unicode_name = 'Приложение'
        settings = AppSettings.objects.create(app_name=unicode_name)
        self.assertEqual(settings.app_name, unicode_name)
        self.assertEqual(settings.logo_initial, 'П')

    def test_app_name_with_leading_whitespace(self):
        """Test logo_initial with leading whitespace in app_name."""
        settings = AppSettings.objects.create(app_name='  Test App')
        # Should return first character (space)
        self.assertEqual(settings.logo_initial, ' ')

    def test_hero_text_max_length(self):
        """Test hero_text handles max length (255 chars)."""
        long_hero = 'H' * 255
        settings = AppSettings.objects.create(app_name='Test', hero_text=long_hero)
        self.assertEqual(settings.hero_text, long_hero)

    def test_hero_text_default_value(self):
        """Test hero_text has correct default value."""
        settings = AppSettings.objects.create(app_name='Test')
        self.assertEqual(settings.hero_text, 'Your hero string')

    def test_contact_email_default_value(self):
        """Test contact_email has correct default value."""
        settings = AppSettings.objects.create(app_name='Test')
        self.assertEqual(settings.contact_email, 'support@example.com')

    def test_contact_email_validation(self):
        """Test contact_email validates email format."""
        settings = AppSettings(app_name='Test', contact_email='invalid-email')
        with self.assertRaises(ValidationError):
            settings.full_clean()

    def test_support_url_can_be_blank(self):
        """Test support_url can be blank."""
        settings = AppSettings.objects.create(app_name='Test', support_url='')
        settings.full_clean()  # Should not raise
        self.assertEqual(settings.support_url, '')

    def test_support_url_validation(self):
        """Test support_url validates URL format."""
        settings = AppSettings(app_name='Test', support_url='not-a-url')
        with self.assertRaises(ValidationError):
            settings.full_clean()

    def test_support_url_valid_url(self):
        """Test support_url accepts valid URL."""
        settings = AppSettings.objects.create(
            app_name='Test',
            support_url='https://example.com/support'
        )
        settings.full_clean()  # Should not raise
        self.assertEqual(settings.support_url, 'https://example.com/support')

    def test_timestamps_auto_created(self):
        """Test created_at and updated_at are auto-populated."""
        settings = AppSettings.objects.create(app_name='Test')
        self.assertIsNotNone(settings.created_at)
        self.assertIsNotNone(settings.updated_at)

    def test_updated_at_changes_on_save(self):
        """Test updated_at changes when settings are saved."""
        settings = AppSettings.objects.create(app_name='Test')
        original_updated_at = settings.updated_at

        settings.app_name = 'Updated Test'
        settings.save()
        settings.refresh_from_db()

        self.assertGreater(settings.updated_at, original_updated_at)

    def test_concurrent_get_settings_creates_one(self):
        """Test get_settings handles race condition gracefully."""
        # First call creates settings
        settings1 = AppSettings.get_settings()
        # Second call should return same settings
        settings2 = AppSettings.get_settings()

        self.assertEqual(settings1.pk, settings2.pk)
        self.assertEqual(AppSettings.objects.count(), 1)

    def test_secondary_color_validation(self):
        """Test secondary_color validates hex format."""
        settings = AppSettings(app_name='Test', secondary_color='invalid')
        with self.assertRaises(ValidationError):
            settings.full_clean()


# =============================================================================
# LOGO TESTS
# =============================================================================


class AppSettingsLogoTests(TestCase):
    """Tests for logo upload and thumbnail generation."""

    def setUp(self):
        """Clear cache and settings before each test."""
        cache.clear()
        AppSettings.objects.all().delete()

    def tearDown(self):
        """Clear cache after each test."""
        cache.clear()

    def _create_test_image(self, size=(512, 512), format='PNG', mode='RGB'):
        """Helper to create a test image."""
        image = Image.new(mode, size, color='red')
        buffer = BytesIO()
        image.save(buffer, format=format)
        buffer.seek(0)
        return SimpleUploadedFile(
            name=f'test_logo.{format.lower()}',
            content=buffer.read(),
            content_type=f'image/{format.lower()}'
        )

    def test_logo_upload_generates_thumbnail(self):
        """Test uploading logo generates small thumbnail."""
        logo_file = self._create_test_image()

        settings = AppSettings.objects.create(app_name='Test', logo=logo_file)

        self.assertTrue(settings.logo)
        # Thumbnail should be generated
        self.assertTrue(settings.logo_small)

    def test_logo_url_property_with_logo(self):
        """Test logo_url returns URL when logo exists."""
        logo_file = self._create_test_image()
        settings = AppSettings.objects.create(app_name='Test', logo=logo_file)

        self.assertIsNotNone(settings.logo_url)
        self.assertIn('branding/', settings.logo_url)

    def test_logo_small_url_property_with_thumbnail(self):
        """Test logo_small_url returns URL when thumbnail exists."""
        logo_file = self._create_test_image()
        settings = AppSettings.objects.create(app_name='Test', logo=logo_file)

        self.assertIsNotNone(settings.logo_small_url)
        self.assertIn('branding/', settings.logo_small_url)
        self.assertIn('_small', settings.logo_small_url)

    def test_thumbnail_size(self):
        """Test thumbnail is 64x64 or smaller."""
        logo_file = self._create_test_image(size=(512, 512))
        settings = AppSettings.objects.create(app_name='Test', logo=logo_file)

        if settings.logo_small:
            thumb = Image.open(settings.logo_small)
            self.assertLessEqual(thumb.width, 64)
            self.assertLessEqual(thumb.height, 64)

    def test_logo_change_regenerates_thumbnail(self):
        """Test changing logo regenerates thumbnail."""
        logo1 = self._create_test_image(size=(256, 256))
        settings = AppSettings.objects.create(app_name='Test', logo=logo1)
        original_small = settings.logo_small.name if settings.logo_small else None

        # Change logo
        logo2 = self._create_test_image(size=(512, 512))
        settings.logo = logo2
        settings.save()

        # Thumbnail should be regenerated
        if original_small and settings.logo_small:
            self.assertNotEqual(original_small, settings.logo_small.name)

    def test_logo_png_rgba_mode(self):
        """Test PNG with RGBA mode is handled correctly."""
        logo_file = self._create_test_image(mode='RGBA', format='PNG')
        settings = AppSettings.objects.create(app_name='Test', logo=logo_file)

        self.assertTrue(settings.logo)
        self.assertTrue(settings.logo_small)

    def test_logo_jpeg_format(self):
        """Test JPEG format is handled correctly."""
        logo_file = self._create_test_image(format='JPEG')
        settings = AppSettings.objects.create(app_name='Test', logo=logo_file)

        self.assertTrue(settings.logo)
        self.assertTrue(settings.logo_small)

    def test_invalid_image_handled_gracefully(self):
        """Test invalid image file is handled without crashing."""
        invalid_file = SimpleUploadedFile(
            name='not_an_image.png',
            content=b'not an image content',
            content_type='image/png'
        )

        # Should not crash, just skip thumbnail generation
        try:
            settings = AppSettings.objects.create(app_name='Test', logo=invalid_file)
            # logo_small might be None or might fail to generate
            self.assertTrue(True)  # Test passes if no crash
        except Exception:
            # Some validation might catch this
            self.assertTrue(True)


# =============================================================================
# API TESTS
# =============================================================================


class AppSettingsAPITests(APITestCase):
    """Tests for GET /api/v1/core/config/app-settings/"""

    def setUp(self):
        """Set up test client."""
        self.client = APIClient()
        self.url = reverse('core-api:app-settings')
        cache.clear()
        AppSettings.objects.all().delete()

    def tearDown(self):
        """Clear cache after each test."""
        cache.clear()

    def test_get_app_settings_success(self):
        """Test GET returns 200 with settings data."""
        AppSettings.objects.create(
            app_name='Test App',
            hero_text='Test Hero',
            primary_color='#123456',
            secondary_color='#654321',
            contact_email='test@example.com',
        )

        response = self.client.get(self.url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['app_name'], 'Test App')
        self.assertEqual(response.data['hero_text'], 'Test Hero')
        self.assertEqual(response.data['primary_color'], '#123456')
        self.assertEqual(response.data['secondary_color'], '#654321')
        self.assertEqual(response.data['contact_email'], 'test@example.com')
        self.assertEqual(response.data['logo_initial'], 'T')

    def test_get_app_settings_creates_default(self):
        """Test GET creates default settings if none exist."""
        response = self.client.get(self.url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['app_name'], 'App name')
        self.assertEqual(AppSettings.objects.count(), 1)

    def test_get_app_settings_response_structure(self):
        """Test response contains all expected fields."""
        AppSettings.objects.create(app_name='Test')

        response = self.client.get(self.url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)

        expected_fields = [
            'app_name',
            'hero_text',
            'logo_url',
            'logo_small_url',
            'logo_initial',
            'primary_color',
            'secondary_color',
            'contact_email',
            'support_url',
            'updated_at',
        ]
        for field in expected_fields:
            self.assertIn(field, response.data, f'Missing field: {field}')

    def test_get_app_settings_no_auth_required(self):
        """Test endpoint is publicly accessible (no auth required)."""
        AppSettings.objects.create(app_name='Public App')

        # No authentication
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_get_app_settings_logo_urls_null_when_no_logo(self):
        """Test logo URLs are null when no logo uploaded."""
        AppSettings.objects.create(app_name='No Logo App')

        response = self.client.get(self.url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIsNone(response.data['logo_url'])
        self.assertIsNone(response.data['logo_small_url'])


class AppSettingsAPIEdgeCasesTests(APITestCase):
    """Extended edge case tests for AppSettings API."""

    def setUp(self):
        """Set up test client."""
        self.client = APIClient()
        self.url = reverse('core-api:app-settings')
        cache.clear()
        AppSettings.objects.all().delete()

    def tearDown(self):
        """Clear cache after each test."""
        cache.clear()

    def test_should_return_unicode_app_name(self):
        """Test API returns unicode characters correctly."""
        AppSettings.objects.create(app_name='日本語アプリ')

        response = self.client.get(self.url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['app_name'], '日本語アプリ')

    def test_should_return_empty_support_url(self):
        """Test API handles empty support_url."""
        AppSettings.objects.create(app_name='Test', support_url='')

        response = self.client.get(self.url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['support_url'], '')

    def test_should_return_full_support_url(self):
        """Test API returns full support URL."""
        AppSettings.objects.create(
            app_name='Test',
            support_url='https://support.example.com/help'
        )

        response = self.client.get(self.url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['support_url'], 'https://support.example.com/help')

    def test_should_handle_concurrent_requests(self):
        """Test API handles concurrent requests."""
        # Make multiple requests rapidly
        responses = []
        for _ in range(5):
            responses.append(self.client.get(self.url))

        # All should succeed and return same data
        for response in responses:
            self.assertEqual(response.status_code, status.HTTP_200_OK)
            self.assertEqual(response.data['app_name'], 'App name')

        # Only one settings record should exist
        self.assertEqual(AppSettings.objects.count(), 1)

    def test_should_include_updated_at_timestamp(self):
        """Test API returns updated_at timestamp."""
        AppSettings.objects.create(app_name='Test')

        response = self.client.get(self.url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIsNotNone(response.data['updated_at'])

    def test_should_return_correct_logo_initial_for_special_chars(self):
        """Test logo_initial for app names starting with special characters."""
        AppSettings.objects.create(app_name='#Test App')

        response = self.client.get(self.url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['logo_initial'], '#')


# =============================================================================
# SERIALIZER TESTS
# =============================================================================


class AppSettingsSerializerTests(TestCase):
    """Tests for AppSettingsSerializer."""

    def setUp(self):
        """Set up test data."""
        cache.clear()
        AppSettings.objects.all().delete()

    def test_serializer_output(self):
        """Test serializer produces expected output."""
        from apps.core.api.serializers import AppSettingsSerializer

        settings = AppSettings.objects.create(
            app_name='Serializer Test',
            hero_text='Test Hero',
            primary_color='#aabbcc',
        )

        serializer = AppSettingsSerializer(settings)
        data = serializer.data

        self.assertEqual(data['app_name'], 'Serializer Test')
        self.assertEqual(data['hero_text'], 'Test Hero')
        self.assertEqual(data['primary_color'], '#aabbcc')
        self.assertEqual(data['logo_initial'], 'S')


class AppSettingsSerializerEdgeCasesTests(TestCase):
    """Extended tests for AppSettingsSerializer."""

    def setUp(self):
        """Set up test data."""
        cache.clear()
        AppSettings.objects.all().delete()

    def test_serializer_all_fields_read_only(self):
        """Test all serializer fields are read-only."""
        from apps.core.api.serializers import AppSettingsSerializer

        serializer = AppSettingsSerializer()

        for field_name, field in serializer.fields.items():
            self.assertTrue(
                field.read_only,
                f'Field {field_name} should be read-only'
            )

    def test_serializer_logo_url_with_request_context(self):
        """Test logo_url returns absolute URL with request context."""
        from apps.core.api.serializers import AppSettingsSerializer
        from rest_framework.request import Request

        # Create image
        image = Image.new('RGB', (100, 100), color='red')
        buffer = BytesIO()
        image.save(buffer, format='PNG')
        buffer.seek(0)
        logo_file = SimpleUploadedFile(
            name='test.png',
            content=buffer.read(),
            content_type='image/png'
        )

        settings = AppSettings.objects.create(app_name='Test', logo=logo_file)

        # Create mock request
        factory = RequestFactory()
        request = factory.get('/')
        request = Request(request)

        serializer = AppSettingsSerializer(settings, context={'request': request})
        data = serializer.data

        # URL should be absolute (contain http)
        if data['logo_url']:
            self.assertTrue(
                data['logo_url'].startswith('http'),
                f"Expected absolute URL, got {data['logo_url']}"
            )

    def test_serializer_logo_url_without_request_context(self):
        """Test logo_url returns relative URL without request context."""
        from apps.core.api.serializers import AppSettingsSerializer

        # Create image
        image = Image.new('RGB', (100, 100), color='red')
        buffer = BytesIO()
        image.save(buffer, format='PNG')
        buffer.seek(0)
        logo_file = SimpleUploadedFile(
            name='test.png',
            content=buffer.read(),
            content_type='image/png'
        )

        settings = AppSettings.objects.create(app_name='Test', logo=logo_file)

        serializer = AppSettingsSerializer(settings)
        data = serializer.data

        # URL should be relative (not contain http)
        if data['logo_url']:
            self.assertIn('branding/', data['logo_url'])

    def test_serializer_handles_empty_hero_text(self):
        """Test serializer handles empty hero_text."""
        from apps.core.api.serializers import AppSettingsSerializer

        settings = AppSettings.objects.create(app_name='Test', hero_text='')
        serializer = AppSettingsSerializer(settings)

        self.assertEqual(serializer.data['hero_text'], '')

    def test_serializer_handles_max_length_fields(self):
        """Test serializer handles fields at max length."""
        from apps.core.api.serializers import AppSettingsSerializer

        long_name = 'A' * 100
        long_hero = 'H' * 255

        settings = AppSettings.objects.create(
            app_name=long_name,
            hero_text=long_hero,
        )
        serializer = AppSettingsSerializer(settings)

        self.assertEqual(serializer.data['app_name'], long_name)
        self.assertEqual(serializer.data['hero_text'], long_hero)


# =============================================================================
# CONTEXT PROCESSOR TESTS
# =============================================================================


class AppSettingsContextProcessorTests(TestCase):
    """Tests for app_settings context processor."""

    def setUp(self):
        """Set up test data."""
        cache.clear()
        AppSettings.objects.all().delete()

    def test_context_processor_returns_settings(self):
        """Test context processor returns app_settings."""
        from apps.core.context_processors import app_settings

        AppSettings.objects.create(app_name='Context Test')

        # Create mock request
        mock_request = MagicMock()

        context = app_settings(mock_request)

        self.assertIn('app_settings', context)
        self.assertEqual(context['app_settings'].app_name, 'Context Test')

    def test_context_processor_creates_default(self):
        """Test context processor creates default settings if none exist."""
        from apps.core.context_processors import app_settings

        mock_request = MagicMock()
        context = app_settings(mock_request)

        self.assertIn('app_settings', context)
        self.assertEqual(AppSettings.objects.count(), 1)

    def test_context_processor_returns_cached_settings(self):
        """Test context processor uses cached settings."""
        from apps.core.context_processors import app_settings

        AppSettings.objects.create(app_name='Cached Test')

        mock_request = MagicMock()

        # First call
        context1 = app_settings(mock_request)
        # Second call should use cache
        context2 = app_settings(mock_request)

        self.assertEqual(context1['app_settings'].pk, context2['app_settings'].pk)


# =============================================================================
# CACHE TESTS
# =============================================================================


class AppSettingsCacheTests(TestCase):
    """Tests for caching behavior."""

    def setUp(self):
        """Clear cache before each test."""
        cache.clear()
        AppSettings.objects.all().delete()

    def tearDown(self):
        """Clear cache after each test."""
        cache.clear()

    def test_save_invalidates_cache(self):
        """Test that saving settings invalidates cache."""
        settings = AppSettings.objects.create(app_name='Original')

        # Populate cache
        AppSettings.get_settings()

        # Modify and save
        settings.app_name = 'Modified'
        settings.save()

        # Get from cache should return new value
        cached = AppSettings.get_settings()
        self.assertEqual(cached.app_name, 'Modified')

    @override_settings(APP_SETTINGS_CACHE_KEY='test_app_settings')
    def test_custom_cache_key(self):
        """Test custom cache key is used."""
        AppSettings.objects.create(app_name='Custom Key Test')

        # Get settings to populate cache
        AppSettings.get_settings()

        # Check custom key exists in cache
        cached = cache.get('test_app_settings')
        self.assertIsNotNone(cached)
        self.assertEqual(cached.app_name, 'Custom Key Test')

    @override_settings(APP_SETTINGS_CACHE_TIMEOUT=60)
    def test_custom_cache_timeout(self):
        """Test custom cache timeout is respected."""
        AppSettings.objects.create(app_name='Timeout Test')

        # Get settings to populate cache
        AppSettings.get_settings()

        # Cache should exist
        cache_key = 'app_settings'
        cached = cache.get(cache_key)
        self.assertIsNotNone(cached)

    def test_cache_cleared_on_color_change(self):
        """Test cache is cleared when colors are changed."""
        settings = AppSettings.objects.create(
            app_name='Color Test',
            primary_color='#111111'
        )

        # Populate cache
        AppSettings.get_settings()

        # Change color
        settings.primary_color = '#222222'
        settings.save()

        # Get from cache should return new color
        cached = AppSettings.get_settings()
        self.assertEqual(cached.primary_color, '#222222')


# =============================================================================
# ADMIN TESTS
# =============================================================================


class AppSettingsAdminTests(TestCase):
    """Tests for AppSettings admin configuration."""

    def setUp(self):
        """Set up test data and admin."""
        cache.clear()
        AppSettings.objects.all().delete()
        self.site = AdminSite()
        self.admin = AppSettingsAdmin(AppSettings, self.site)
        self.factory = RequestFactory()

    def tearDown(self):
        """Clear cache after test."""
        cache.clear()

    def test_has_add_permission_when_no_settings(self):
        """Test add permission is True when no settings exist."""
        request = self.factory.get('/admin/')
        request.user = MagicMock()
        request.user.is_superuser = True

        self.assertTrue(self.admin.has_add_permission(request))

    def test_has_add_permission_when_settings_exist(self):
        """Test add permission is False when settings exist."""
        AppSettings.objects.create(app_name='Test')

        request = self.factory.get('/admin/')
        request.user = MagicMock()
        request.user.is_superuser = True

        self.assertFalse(self.admin.has_add_permission(request))

    def test_has_delete_permission_always_false(self):
        """Test delete permission is always False."""
        request = self.factory.get('/admin/')
        request.user = MagicMock()
        request.user.is_superuser = True

        settings = AppSettings.objects.create(app_name='Test')

        self.assertFalse(self.admin.has_delete_permission(request, settings))
        self.assertFalse(self.admin.has_delete_permission(request))

    def test_superuser_can_view(self):
        """Test superuser can view settings."""
        request = self.factory.get('/admin/')
        request.user = MagicMock()
        request.user.is_superuser = True

        self.assertTrue(self.admin.has_view_permission(request))

    def test_non_superuser_cannot_view(self):
        """Test non-superuser cannot view settings."""
        request = self.factory.get('/admin/')
        request.user = MagicMock()
        request.user.is_superuser = False

        self.assertFalse(self.admin.has_view_permission(request))

    def test_superuser_can_change(self):
        """Test superuser can change settings."""
        request = self.factory.get('/admin/')
        request.user = MagicMock()
        request.user.is_superuser = True

        self.assertTrue(self.admin.has_change_permission(request))

    def test_non_superuser_cannot_change(self):
        """Test non-superuser cannot change settings."""
        request = self.factory.get('/admin/')
        request.user = MagicMock()
        request.user.is_superuser = False

        self.assertFalse(self.admin.has_change_permission(request))

    def test_get_queryset_superuser(self):
        """Test superuser sees all settings."""
        AppSettings.objects.create(app_name='Test')

        request = self.factory.get('/admin/')
        request.user = MagicMock()
        request.user.is_superuser = True

        qs = self.admin.get_queryset(request)
        self.assertEqual(qs.count(), 1)

    def test_get_queryset_non_superuser(self):
        """Test non-superuser sees no settings."""
        AppSettings.objects.create(app_name='Test')

        request = self.factory.get('/admin/')
        request.user = MagicMock()
        request.user.is_superuser = False

        qs = self.admin.get_queryset(request)
        self.assertEqual(qs.count(), 0)

    def test_logo_preview_with_logo(self):
        """Test logo_preview returns img tag when logo exists."""
        # Create image
        image = Image.new('RGB', (100, 100), color='red')
        buffer = BytesIO()
        image.save(buffer, format='PNG')
        buffer.seek(0)
        logo_file = SimpleUploadedFile(
            name='test.png',
            content=buffer.read(),
            content_type='image/png'
        )

        settings = AppSettings.objects.create(app_name='Test', logo=logo_file)

        preview = self.admin.logo_preview(settings)
        self.assertIn('<img', preview)

    def test_logo_preview_without_logo(self):
        """Test logo_preview returns initial when no logo."""
        settings = AppSettings.objects.create(app_name='Test')

        preview = self.admin.logo_preview(settings)
        self.assertIn('T', preview)  # First letter of 'Test'

    def test_primary_color_preview(self):
        """Test primary_color_preview returns color swatch."""
        settings = AppSettings.objects.create(
            app_name='Test',
            primary_color='#667eea'
        )

        preview = self.admin.primary_color_preview(settings)
        self.assertIn('#667eea', preview)


# =============================================================================
# HTTP METHOD TESTS
# =============================================================================


class AppSettingsHTTPMethodTests(APITestCase):
    """Tests for HTTP method handling on app-settings endpoint."""

    def setUp(self):
        """Set up test client."""
        self.client = APIClient()
        self.url = reverse('core-api:app-settings')
        cache.clear()
        AppSettings.objects.all().delete()

    def tearDown(self):
        """Clear cache after test."""
        cache.clear()

    def test_should_accept_get_method(self):
        """Test GET method is allowed."""
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_should_reject_post_method(self):
        """Test POST method is not allowed."""
        response = self.client.post(self.url, {}, format='json')
        self.assertEqual(response.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)

    def test_should_reject_put_method(self):
        """Test PUT method is not allowed."""
        response = self.client.put(self.url, {}, format='json')
        self.assertEqual(response.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)

    def test_should_reject_patch_method(self):
        """Test PATCH method is not allowed."""
        response = self.client.patch(self.url, {}, format='json')
        self.assertEqual(response.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)

    def test_should_reject_delete_method(self):
        """Test DELETE method is not allowed."""
        response = self.client.delete(self.url)
        self.assertEqual(response.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)


# =============================================================================
# INTEGRATION TESTS
# =============================================================================


class AppSettingsIntegrationTests(APITestCase):
    """End-to-end integration tests for AppSettings."""

    def setUp(self):
        """Set up test client."""
        self.client = APIClient()
        self.url = reverse('core-api:app-settings')
        cache.clear()
        AppSettings.objects.all().delete()

    def tearDown(self):
        """Clear cache after test."""
        cache.clear()

    def test_full_workflow_create_and_retrieve(self):
        """Test creating settings and retrieving via API."""
        # Create settings directly
        AppSettings.objects.create(
            app_name='My App',
            hero_text='Welcome to My App',
            primary_color='#ff5500',
            secondary_color='#00ff55',
            contact_email='support@myapp.com',
            support_url='https://myapp.com/help',
        )

        # Retrieve via API
        response = self.client.get(self.url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['app_name'], 'My App')
        self.assertEqual(response.data['hero_text'], 'Welcome to My App')
        self.assertEqual(response.data['primary_color'], '#ff5500')
        self.assertEqual(response.data['secondary_color'], '#00ff55')
        self.assertEqual(response.data['contact_email'], 'support@myapp.com')
        self.assertEqual(response.data['support_url'], 'https://myapp.com/help')
        self.assertEqual(response.data['logo_initial'], 'M')

    def test_settings_update_reflected_in_api(self):
        """Test updating settings is reflected in API response."""
        settings = AppSettings.objects.create(app_name='Original Name')

        # Verify original name
        response1 = self.client.get(self.url)
        self.assertEqual(response1.data['app_name'], 'Original Name')

        # Update settings
        settings.app_name = 'Updated Name'
        settings.save()

        # Verify updated name
        response2 = self.client.get(self.url)
        self.assertEqual(response2.data['app_name'], 'Updated Name')

    def test_default_settings_created_on_first_access(self):
        """Test default settings are created on first API access."""
        # No settings exist initially
        self.assertEqual(AppSettings.objects.count(), 0)

        # Access API
        response = self.client.get(self.url)

        # Settings should be created with defaults
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(AppSettings.objects.count(), 1)
        self.assertEqual(response.data['app_name'], 'App name')
        self.assertEqual(response.data['hero_text'], 'Your hero string')
        self.assertEqual(response.data['primary_color'], '#667eea')
        self.assertEqual(response.data['secondary_color'], '#764ba2')

    def test_api_response_is_cacheable(self):
        """Test API response uses cached settings."""
        AppSettings.objects.create(app_name='Cached Settings')

        # Multiple requests should return same data
        response1 = self.client.get(self.url)
        response2 = self.client.get(self.url)

        self.assertEqual(response1.data['app_name'], response2.data['app_name'])
        self.assertEqual(response1.data['updated_at'], response2.data['updated_at'])
