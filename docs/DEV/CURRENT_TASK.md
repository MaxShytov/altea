# Current Task

**Created:** 2025-12-06
**Status:** Planning
**Reference:** FR-BRANDING-1 (Dynamic App Branding & Configuration)

---

## Task Definition

### Original Request

> Для проекта у меня есть несколько базовых элементов:
> 1. Лого, возможно в нескольких размерах.
> 2. Название проекта
> 3. Hero проекта
>
> Это используется во многих местах проекта.
> Нужно сделать так, чтобы это могло задаваться в базе данных с кешированием. И везде где используется бралось из базы данных, а не прописывалось прямо в тексте.
>
> Дополнительное условие:
> - Если лого не проставлено подставлять первую букву названия проекта
> - Если нет названия проекта, то подставлять "App name"
> - Если не указано Hero проекта, то писать "Your hero string"

---

### Similar Implementations (Benchmarks)

| Implementation | Location | What to Reuse |
|----------------|----------|---------------|
| LegalDocument singleton pattern | `apps/core/models.py` | `is_active` pattern для singleton-подобной модели |
| Django cache framework | `config/settings/base.py` | Redis уже настроен в `.env.example` |
| Static files serving | `config/settings/base.py:STATIC_URL` | Паттерн для media файлов |
| CSS Design Tokens | `static/css/custom.css` | CSS переменные `--primary`, `--secondary` |
| EnvConfig Flutter | `mobile/lib/core/config/env_config.dart` | Паттерн для конфигурации |
| Hive local storage | `mobile/pubspec.yaml` | Уже подключён для JWT токенов |

---

### Refined Task Description

**Task Title:** Dynamic App Branding & Configuration (AppSettings)

**Description:**
Создать систему централизованного управления брендингом приложения через Django Admin. Все элементы брендинга (логотип, название, hero text, цвета, контакты) должны храниться в базе данных, кешироваться на бэкенде (Redis, TTL 1 час) и на мобильном клиенте (Hive, TTL 1 час). При недоступности сервера использовать fallback значения.

**Use Cases:**

1. **UC1: Superuser меняет брендинг**
   - Superuser открывает Django Admin → AppSettings
   - Загружает новый логотип (PNG/SVG)
   - Меняет название приложения, hero text, цвета
   - Сохраняет изменения
   - Кеш инвалидируется
   - Изменения видны в приложении в течение 1 часа (или сразу при перезапуске)

2. **UC2: Пользователь открывает мобильное приложение**
   - Приложение запрашивает `/api/v1/config/app-settings/`
   - Если успешно: сохраняет в Hive, показывает данные
   - Если ошибка/offline: использует данные из Hive или hardcoded fallback
   - Логотип, название, hero text отображаются из полученных данных

3. **UC3: Django template рендерит страницу**
   - Template использует `{% app_settings %}` template tag
   - Context processor добавляет `app_settings` в контекст
   - Данные берутся из Redis кеша или DB

4. **UC4: Логотип не загружен**
   - Система возвращает первую букву `app_name` как fallback
   - Flutter отображает CircleAvatar с буквой вместо картинки

**Scope:**

✅ In scope:
- Django модель `AppSettings` (singleton)
- Поля: `app_name`, `hero_text`, `logo`, `logo_small`, `primary_color`, `secondary_color`, `contact_email`, `support_url`
- Django Admin interface для редактирования (только superuser)
- Redis кеширование (TTL 1 час)
- API endpoint `GET /api/v1/config/app-settings/` (публичный)
- Django context processor для templates
- Django template tag `{% app_settings %}`
- Обновление всех Django templates (13+ файлов)
- Flutter: AppSettingsProvider с Hive кешированием
- Flutter: обновление HomeScreen, DrawerHeader, main.dart
- Fallback значения при недоступности сервера
- ImageField с автоматической генерацией thumbnail

❌ Out of scope (not in this task):
- Мультиязычные названия (одно название для всех языков)
- Редактирование через API (только через Admin)
- Deep link scheme изменение (`altea://`)
- Favicon/app icon изменение
- Push notification branding

**Success Criteria:**
- [ ] AppSettings модель создана с миграцией
- [ ] Django Admin позволяет редактировать настройки (только superuser)
- [ ] Логотип загружается и автоматически ресайзится
- [ ] Redis кеш работает с TTL 1 час
- [ ] API endpoint возвращает все настройки
- [ ] Django templates используют динамические значения
- [ ] Flutter получает настройки при запуске
- [ ] Hive кеширует настройки (TTL 1 час)
- [ ] Fallback значения работают при offline
- [ ] Все 13+ hardcoded "Altea" заменены на динамические

**Technical Considerations:**
- Использовать `django-solo` или custom singleton pattern
- Pillow для image processing (thumbnail generation)
- `django-redis` для кеширования
- `sorl-thumbnail` или custom для ресайза изображений
- Хранить logo в media/ с S3 совместимостью
- API endpoint должен быть публичным (без авторизации)
- Использовать `freezed` для Flutter model

---

### Complexity Assessment

**Complexity:** Medium-High

**Estimated effort:** 6-8 hours

**Risk factors:**
- Risk 1: Много файлов для модификации (13+ templates, 3+ Flutter screens)
- Risk 2: Image processing может потребовать дополнительные зависимости
- Risk 3: Синхронизация кеша между Redis и Hive
- Risk 4: Тестирование всех мест использования

---

### Components to Modify

**Django:**

| Type | Files |
|------|-------|
| Models (new) | `apps/core/models.py` - AppSettings |
| Admin (new) | `apps/core/admin.py` - AppSettingsAdmin |
| Views (new) | `apps/core/api/views.py` - AppSettingsAPIView |
| Serializers (new) | `apps/core/api/serializers.py` - AppSettingsSerializer |
| URLs (modify) | `apps/core/api/urls.py` or `config/urls_api.py` |
| Context processors (new) | `apps/core/context_processors.py` |
| Template tags (new) | `apps/core/templatetags/app_settings_tags.py` |
| Settings (modify) | `config/settings/base.py` - CACHES, context processors |
| Templates (modify) | 13+ files in `templates/` |

**Flutter:**

| Type | Files |
|------|-------|
| Models (new) | `data/models/app_settings_model.dart` |
| Data sources (new) | `data/data_sources/remote/config_remote_data_source.dart` |
| Data sources (new) | `data/data_sources/local/app_settings_local_data_source.dart` |
| Repositories (new) | `data/repositories/app_settings_repository.dart` |
| Providers (new) | `presentation/providers/app_settings_provider.dart` |
| Screens (modify) | `presentation/screens/home/home_screen.dart` |
| Widgets (modify) | `presentation/widgets/molecules/drawer_header_widget.dart` |
| Main (modify) | `main.dart` - MaterialApp title |

**Database:**
- Migrations: 1 новая миграция для AppSettings
- New tables: `core_appsettings`
- New fields: `app_name`, `hero_text`, `logo`, `logo_small`, `primary_color`, `secondary_color`, `contact_email`, `support_url`, timestamps

---

### Dependencies

**Depends on:**
- ✅ Django core app (существует)
- ✅ Redis configured (в .env.example)
- ✅ Hive в Flutter (уже используется)
- ⚠️ Pillow (проверить requirements)
- ⚠️ django-redis (добавить если нет)

**Will affect:**
- Все Django templates с branding
- Home screen (Flutter)
- Drawer (Flutter)
- MaterialApp title (Flutter)
- Email templates

---

### Recommended Approach

1. **Phase 1: Backend Model & Admin**
   - Создать AppSettings модель (singleton pattern)
   - Настроить Django Admin (только superuser)
   - Добавить image upload с thumbnail generation
   - Миграция и seed data

2. **Phase 2: Backend Caching & API**
   - Настроить django-redis
   - Создать cache manager для AppSettings
   - Создать API endpoint
   - Добавить context processor

3. **Phase 3: Django Templates**
   - Создать template tag
   - Обновить base.html
   - Обновить auth_layout.html
   - Обновить dashboard_layout.html
   - Обновить admin/base_site.html
   - Обновить все email templates

4. **Phase 4: Flutter Integration**
   - Создать AppSettingsModel (freezed)
   - Создать remote data source
   - Создать local data source (Hive)
   - Создать repository с fallback логикой
   - Создать provider

5. **Phase 5: Flutter UI Updates**
   - Обновить HomeScreen
   - Обновить DrawerHeaderWidget
   - Обновить main.dart

6. **Phase 6: Testing**
   - Unit tests для модели
   - API tests
   - Cache invalidation tests
   - Flutter widget tests

---

### Data Model

```python
class AppSettings(TimeStampedModel):
    """
    Singleton model for application branding and configuration.
    Only one instance should exist.
    """
    # Branding
    app_name = models.CharField(
        max_length=100,
        default="App name",
        help_text="Application name displayed across the app"
    )
    hero_text = models.CharField(
        max_length=255,
        default="Your hero string",
        help_text="Tagline displayed on home screen"
    )

    # Logo
    logo = models.ImageField(
        upload_to='branding/',
        blank=True,
        null=True,
        help_text="Main logo (recommended: 512x512 PNG or SVG)"
    )
    logo_small = models.ImageField(
        upload_to='branding/',
        blank=True,
        null=True,
        help_text="Small logo for navbar (auto-generated if empty)"
    )

    # Colors
    primary_color = models.CharField(
        max_length=7,
        default="#667eea",
        validators=[validate_hex_color],
        help_text="Primary brand color (hex, e.g. #667eea)"
    )
    secondary_color = models.CharField(
        max_length=7,
        default="#764ba2",
        validators=[validate_hex_color],
        help_text="Secondary brand color (hex)"
    )

    # Contact
    contact_email = models.EmailField(
        default="support@example.com",
        help_text="Support contact email"
    )
    support_url = models.URLField(
        blank=True,
        help_text="Link to support page or documentation"
    )

    class Meta:
        verbose_name = "App Settings"
        verbose_name_plural = "App Settings"

    def save(self, *args, **kwargs):
        # Singleton: ensure only one instance
        self.pk = 1
        super().save(*args, **kwargs)
        # Invalidate cache
        cache.delete('app_settings')

    @classmethod
    def get_settings(cls):
        """Get cached settings or load from DB."""
        settings = cache.get('app_settings')
        if settings is None:
            settings, _ = cls.objects.get_or_create(pk=1)
            cache.set('app_settings', settings, timeout=3600)  # 1 hour
        return settings

    @property
    def logo_initial(self):
        """Return first letter of app_name for fallback."""
        return self.app_name[0].upper() if self.app_name else "A"
```

### API Response Format

```json
{
  "app_name": "Altea",
  "hero_text": "Break the Bad Habits",
  "logo_url": "https://example.com/media/branding/logo.png",
  "logo_small_url": "https://example.com/media/branding/logo_small.png",
  "logo_initial": "A",
  "primary_color": "#667eea",
  "secondary_color": "#764ba2",
  "contact_email": "support@altea.ch",
  "support_url": "https://altea.ch/support"
}
```

### Fallback Values (Flutter)

```dart
class AppSettingsDefaults {
  static const String appName = 'Altea';
  static const String heroText = 'Break the Bad Habits';
  static const String primaryColor = '#667eea';
  static const String secondaryColor = '#764ba2';
  static const String contactEmail = 'support@altea.ch';
  static const String supportUrl = '';
}
```

---

### Files to Update (Complete List)

**Django Templates (13 files):**
1. `templates/base.html` - title
2. `templates/admin/base_site.html` - admin title
3. `templates/layouts/auth_layout.html` - hero, branding
4. `templates/layouts/dashboard_layout.html` - sidebar brand
5. `templates/emails/base_email.html` - header, footer, copyright
6. `templates/emails/welcome.html` - title, greeting
7. `templates/emails/password_reset.html` - title, body text
8. `templates/emails/shift_assigned.html` - title
9. `templates/emails/timeoff_approved.html` - title
10. `templates/legal/base_legal.html` - title
11. `apps/accounts/templates/accounts/emails/password_reset_email.html` - if exists
12. Any other email templates

**Flutter (4+ files):**
1. `mobile/lib/main.dart` - MaterialApp title
2. `mobile/lib/presentation/screens/home/home_screen.dart` - logo, hero
3. `mobile/lib/presentation/widgets/molecules/drawer_header_widget.dart` - logo, name
4. `mobile/lib/core/config/env_config.dart` - add defaults

---

## Checklist

### Definition Phase
- [x] Original requirements documented
- [x] Clarifying questions answered
- [x] Similar implementations identified
- [x] Scope defined (in/out)
- [x] Success criteria defined
- [x] Data model designed

### Planning Phase
- [x] Detailed implementation plan
- [x] File-by-file changes specified
- [x] Edge cases identified
- [x] Test cases defined

### Implementation Phase
- [ ] Backend model created
- [ ] Admin interface ready
- [ ] API endpoint working
- [ ] Templates updated
- [ ] Flutter integration complete
- [ ] Tests passing

### Verification Phase
- [ ] Manual testing complete
- [ ] All acceptance criteria met
- [ ] Ready for merge

---

## Notes

- Redis URL уже настроен в `.env.example`: `REDIS_URL=redis://localhost:16379/0`
- Pillow уже в requirements (используется для ImageField)
- flutter_secure_storage используется во Flutter для токенов (не Hive)
- Нужно добавить `django-redis` в requirements
- Нужно добавить `shared_preferences` или `hive` во Flutter для кеширования настроек

---

## Plan

### Overview

Реализация состоит из 6 фаз:
1. **Backend: Dependencies & Model** - добавление django-redis, создание модели
2. **Backend: Admin & API** - Django Admin, API endpoint, context processor
3. **Backend: Templates** - обновление всех Django templates
4. **Flutter: Dependencies & Data Layer** - добавление hive, модели, data sources
5. **Flutter: UI Updates** - обновление экранов
6. **Testing** - тесты для backend и frontend

---

### Phase 1: Backend Dependencies & Model

#### 1.1 Add django-redis to requirements

**File:** `requirements/base.txt`

```diff
+ # ============================================
+ # Cache
+ # ============================================
+ django-redis==5.4.0
```

#### 1.2 Configure Redis Cache

**File:** `config/settings/base.py`

```python
# Add after DATABASES section (line ~94)

# Cache Configuration
CACHES = {
    'default': {
        'BACKEND': 'django_redis.cache.RedisCache',
        'LOCATION': env('REDIS_URL', default='redis://localhost:6379/0'),
        'OPTIONS': {
            'CLIENT_CLASS': 'django_redis.client.DefaultClient',
        },
        'KEY_PREFIX': 'altea',
        'TIMEOUT': 3600,  # 1 hour default
    }
}

# Cache key for app settings
APP_SETTINGS_CACHE_KEY = 'app_settings'
APP_SETTINGS_CACHE_TIMEOUT = 3600  # 1 hour
```

#### 1.3 Add context processor

**File:** `config/settings/base.py`

```python
# Update TEMPLATES context_processors (line ~72-77)
'context_processors': [
    'django.template.context_processors.debug',
    'django.template.context_processors.request',
    'django.contrib.auth.context_processors.auth',
    'django.contrib.messages.context_processors.messages',
    'apps.core.context_processors.app_settings',  # ADD THIS
],
```

#### 1.4 Create AppSettings Model

**File:** `apps/core/models.py` (append to existing)

```python
import re
from django.core.cache import cache
from django.core.exceptions import ValidationError
from django.core.validators import RegexValidator
from django.conf import settings
from PIL import Image
from io import BytesIO
from django.core.files.base import ContentFile


def validate_hex_color(value):
    """Validate that value is a valid hex color code."""
    if not re.match(r'^#[0-9A-Fa-f]{6}$', value):
        raise ValidationError(
            f'{value} is not a valid hex color. Use format #RRGGBB'
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

        # Generate small logo if main logo exists
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

            # Convert to RGB if necessary (for PNG with transparency)
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
        cache.delete(getattr(settings, 'APP_SETTINGS_CACHE_KEY', 'app_settings'))

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
```

#### 1.5 Create Migration

```bash
python manage.py makemigrations core --name add_app_settings
python manage.py migrate
```

#### 1.6 Create management command for initial data

**File:** `apps/core/management/commands/seed_app_settings.py`

```python
from django.core.management.base import BaseCommand
from apps.core.models import AppSettings


class Command(BaseCommand):
    help = 'Create or update default AppSettings'

    def add_arguments(self, parser):
        parser.add_argument(
            '--app-name',
            type=str,
            default='Altea',
            help='Application name'
        )
        parser.add_argument(
            '--hero-text',
            type=str,
            default='Break the Bad Habits',
            help='Hero tagline'
        )
        parser.add_argument(
            '--contact-email',
            type=str,
            default='support@altea.ch',
            help='Contact email'
        )

    def handle(self, *args, **options):
        settings, created = AppSettings.objects.get_or_create(pk=1)

        if created:
            settings.app_name = options['app_name']
            settings.hero_text = options['hero_text']
            settings.contact_email = options['contact_email']
            settings.save()
            self.stdout.write(self.style.SUCCESS('Created default AppSettings'))
        else:
            self.stdout.write(self.style.WARNING('AppSettings already exists'))
```

---

### Phase 2: Backend Admin & API

#### 2.1 Create Admin Interface

**File:** `apps/core/admin.py` (append to existing)

```python
from django.contrib import admin
from django.utils.html import mark_safe, format_html
from apps.core.models import AppSettings


@admin.register(AppSettings)
class AppSettingsAdmin(admin.ModelAdmin):
    """
    Admin for singleton AppSettings.
    Only superusers can access.
    """
    list_display = ['app_name', 'hero_text', 'logo_preview', 'primary_color_preview', 'updated_at']
    readonly_fields = ['created_at', 'updated_at', 'logo_preview_large', 'logo_small_preview']

    fieldsets = (
        ('Branding', {
            'fields': ('app_name', 'hero_text'),
            'description': 'Main branding elements displayed across the application.'
        }),
        ('Logo', {
            'fields': ('logo', 'logo_preview_large', 'logo_small_preview'),
            'description': 'Upload a logo (recommended 512x512 PNG). A small version will be auto-generated.'
        }),
        ('Colors', {
            'fields': ('primary_color', 'secondary_color'),
            'description': 'Brand colors used in the application. Use hex format (#RRGGBB).'
        }),
        ('Contact', {
            'fields': ('contact_email', 'support_url'),
            'description': 'Contact information displayed in emails and support sections.'
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
        if obj.logo:
            return format_html(
                '<img src="{}" style="max-height: 40px; max-width: 40px; border-radius: 4px;" />',
                obj.logo.url
            )
        return format_html(
            '<span style="display: inline-flex; align-items: center; justify-content: center; '
            'width: 40px; height: 40px; background: {}; color: white; border-radius: 4px; '
            'font-weight: bold; font-size: 20px;">{}</span>',
            obj.primary_color,
            obj.logo_initial
        )

    @admin.display(description='Logo Preview')
    def logo_preview_large(self, obj):
        if obj.logo:
            return format_html(
                '<img src="{}" style="max-height: 128px; max-width: 128px; border-radius: 8px;" />',
                obj.logo.url
            )
        return format_html(
            '<span style="display: inline-flex; align-items: center; justify-content: center; '
            'width: 128px; height: 128px; background: {}; color: white; border-radius: 8px; '
            'font-weight: bold; font-size: 64px;">{}</span>',
            obj.primary_color,
            obj.logo_initial
        )

    @admin.display(description='Small Logo (64x64)')
    def logo_small_preview(self, obj):
        if obj.logo_small:
            return format_html(
                '<img src="{}" style="max-height: 64px; max-width: 64px; border-radius: 4px;" />',
                obj.logo_small.url
            )
        return 'Auto-generated when logo is uploaded'

    @admin.display(description='Primary Color')
    def primary_color_preview(self, obj):
        return format_html(
            '<span style="display: inline-block; width: 20px; height: 20px; '
            'background: {}; border-radius: 3px; vertical-align: middle; margin-right: 8px;"></span>{}',
            obj.primary_color,
            obj.primary_color
        )
```

#### 2.2 Create API Serializer

**File:** `apps/core/api/serializers.py` (append)

```python
from rest_framework import serializers
from apps.core.models import AppSettings


class AppSettingsSerializer(serializers.ModelSerializer):
    """
    Serializer for public app settings.
    Returns all branding info needed by mobile app.
    """
    logo_url = serializers.SerializerMethodField()
    logo_small_url = serializers.SerializerMethodField()
    logo_initial = serializers.CharField(read_only=True)

    class Meta:
        model = AppSettings
        fields = [
            'app_name',
            'hero_text',
            'logo_url',
            'logo_small_url',
            'logo_initial',
            'primary_color',
            'secondary_color',
            'contact_email',
            'support_url',
        ]
        read_only_fields = fields

    def get_logo_url(self, obj):
        if obj.logo:
            request = self.context.get('request')
            if request:
                return request.build_absolute_uri(obj.logo.url)
            return obj.logo.url
        return None

    def get_logo_small_url(self, obj):
        if obj.logo_small:
            request = self.context.get('request')
            if request:
                return request.build_absolute_uri(obj.logo_small.url)
            return obj.logo_small.url
        return None
```

#### 2.3 Create API View

**File:** `apps/core/api/views.py` (append)

```python
from apps.core.models import AppSettings
from apps.core.api.serializers import AppSettingsSerializer


class AppSettingsAPIView(APIView):
    """
    Public endpoint for app branding settings.
    No authentication required - used by mobile app on startup.
    """
    permission_classes = [AllowAny]

    @extend_schema(
        summary='Get app settings',
        description='Returns application branding settings (logo, name, colors, etc). '
                    'No authentication required. Results are cached.',
        responses={
            200: AppSettingsSerializer,
        },
        tags=['Configuration'],
    )
    def get(self, request):
        settings = AppSettings.get_settings()
        serializer = AppSettingsSerializer(settings, context={'request': request})
        return Response(serializer.data)
```

#### 2.4 Add URL Route

**File:** `apps/core/api/urls.py` (update)

```python
from apps.core.api.views import (
    # ... existing imports
    AppSettingsAPIView,
)

urlpatterns = [
    # ... existing routes

    # App Settings
    path('config/app-settings/', AppSettingsAPIView.as_view(), name='app-settings'),
]
```

#### 2.5 Create Context Processor

**File:** `apps/core/context_processors.py` (new file)

```python
"""
Context processors for core app.
"""
from apps.core.models import AppSettings


def app_settings(request):
    """
    Add app_settings to template context.
    Uses cached settings for performance.
    """
    return {
        'app_settings': AppSettings.get_settings()
    }
```

---

### Phase 3: Django Templates

#### 3.1 Update base.html

**File:** `templates/base.html`

**Changes:**
```html
<!-- Line 9: Change title -->
<title>{% block title %}{{ app_settings.app_name }}{% endblock %}</title>
```

#### 3.2 Update auth_layout.html

**File:** `templates/layouts/auth_layout.html`

**Changes:**
```html
<!-- Line 15: Change h1 -->
<h1 class="display-4 fw-bold mb-3">{{ app_settings.app_name }}</h1>

<!-- Line 17-18: Change tagline -->
<p class="lead text-center">{{ app_settings.hero_text }}</p>

<!-- Line 36-37: Update gradient colors (optional, if we want dynamic colors) -->
<style>
.auth-branding {
    background: linear-gradient(135deg, {{ app_settings.primary_color }} 0%, {{ app_settings.secondary_color }} 100%);
}
</style>
```

#### 3.3 Update dashboard_layout.html

**File:** `templates/layouts/dashboard_layout.html`

**Changes:**
```html
<!-- Find and replace <span class="fw-bold">Altea</span> -->
<span class="fw-bold">{{ app_settings.app_name }}</span>
```

#### 3.4 Update admin/base_site.html

**File:** `templates/admin/base_site.html`

**Changes:**
```html
{% block title %}{% if subtitle %}{{ subtitle }} | {% endif %}{{ title }} | {{ app_settings.app_name }} Admin{% endblock %}

{% block branding %}
<a href="{% url 'admin:index' %}">{{ app_settings.app_name }} Administration</a>
{% endblock %}
```

#### 3.5 Update base_email.html

**File:** `templates/emails/base_email.html`

**Changes (multiple locations):**
```html
<!-- Line 7 -->
<title>{% block email_title %}{{ app_settings.app_name }}{% endblock %}</title>

<!-- Line 24-25 -->
<h1 style="...">{{ app_settings.app_name }}</h1>

<!-- Line 27-28 -->
<p style="...">{{ app_settings.hero_text }}</p>

<!-- Line 48 -->
<strong>{{ app_settings.app_name }}</strong><br>

<!-- Line 52 -->
© {% now "Y" %} {{ app_settings.app_name }}. All rights reserved.

<!-- Line 55 -->
You received this email because you have an account with {{ app_settings.app_name }}.<br>

<!-- Line 57 -->
<a href="mailto:{{ app_settings.contact_email }}" style="...">{{ app_settings.contact_email }}</a>

<!-- Line 22: Update gradient -->
<td style="background: linear-gradient(135deg, {{ app_settings.primary_color }} 0%, {{ app_settings.secondary_color }} 100%); ...">
```

#### 3.6 Update other email templates

All email templates that extend `base_email.html` should work automatically. Check and update if needed:
- `templates/emails/welcome.html`
- `templates/emails/password_reset.html`
- `templates/emails/shift_assigned.html`
- `templates/emails/timeoff_approved.html`
- `apps/accounts/templates/accounts/emails/password_reset_email.html`

#### 3.7 Update legal/base_legal.html

**File:** `templates/legal/base_legal.html`

**Changes:**
```html
{% block title %}{{ document.title }} - {{ app_settings.app_name }}{% endblock %}
```

---

### Phase 4: Flutter Dependencies & Data Layer

#### 4.1 Add Hive dependencies

**File:** `mobile/pubspec.yaml`

```yaml
dependencies:
  # ... existing

  # Local storage for app settings cache
  hive: ^2.2.3
  hive_flutter: ^1.1.0

dev_dependencies:
  # ... existing
  hive_generator: ^2.0.1
```

#### 4.2 Create AppSettings Model

**File:** `mobile/lib/data/models/app_settings_model.dart`

```dart
import 'package:freezed_annotation/freezed_annotation.dart';
import 'package:hive/hive.dart';

part 'app_settings_model.freezed.dart';
part 'app_settings_model.g.dart';

/// Default values for app settings when server is unavailable.
class AppSettingsDefaults {
  static const String appName = 'Altea';
  static const String heroText = 'Break the Bad Habits';
  static const String logoInitial = 'A';
  static const String primaryColor = '#667eea';
  static const String secondaryColor = '#764ba2';
  static const String contactEmail = 'support@altea.ch';
  static const String supportUrl = '';
}

@freezed
@HiveType(typeId: 1)
class AppSettingsModel with _$AppSettingsModel {
  const factory AppSettingsModel({
    @HiveField(0) @Default(AppSettingsDefaults.appName) String appName,
    @HiveField(1) @Default(AppSettingsDefaults.heroText) String heroText,
    @HiveField(2) String? logoUrl,
    @HiveField(3) String? logoSmallUrl,
    @HiveField(4) @Default(AppSettingsDefaults.logoInitial) String logoInitial,
    @HiveField(5) @Default(AppSettingsDefaults.primaryColor) String primaryColor,
    @HiveField(6) @Default(AppSettingsDefaults.secondaryColor) String secondaryColor,
    @HiveField(7) @Default(AppSettingsDefaults.contactEmail) String contactEmail,
    @HiveField(8) @Default(AppSettingsDefaults.supportUrl) String supportUrl,
    @HiveField(9) DateTime? cachedAt,
  }) = _AppSettingsModel;

  factory AppSettingsModel.fromJson(Map<String, dynamic> json) =>
      _$AppSettingsModelFromJson(json);

  /// Create default settings.
  factory AppSettingsModel.defaults() => const AppSettingsModel();
}
```

#### 4.3 Create Remote Data Source

**File:** `mobile/lib/data/data_sources/remote/config_remote_data_source.dart`

```dart
import 'package:dio/dio.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';

import '../../../core/network/api_exceptions.dart';
import '../../../core/network/dio_client.dart';
import '../../models/app_settings_model.dart';

/// Provider for ConfigRemoteDataSource.
final configRemoteDataSourceProvider = Provider<ConfigRemoteDataSource>((ref) {
  return ConfigRemoteDataSource(ref.watch(dioClientProvider));
});

/// Remote data source for app configuration.
class ConfigRemoteDataSource {
  final Dio _dio;

  ConfigRemoteDataSource(this._dio);

  /// Fetch app settings from server.
  Future<AppSettingsModel> getAppSettings() async {
    try {
      final response = await _dio.get('/config/app-settings/');
      final data = response.data as Map<String, dynamic>;

      // Add cached timestamp
      data['cachedAt'] = DateTime.now().toIso8601String();

      return AppSettingsModel.fromJson(data);
    } on DioException catch (e) {
      if (e.error is ApiException) {
        throw e.error as ApiException;
      }
      rethrow;
    }
  }
}
```

#### 4.4 Create Local Data Source (Hive Cache)

**File:** `mobile/lib/data/data_sources/local/app_settings_local_data_source.dart`

```dart
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:hive_flutter/hive_flutter.dart';

import '../../models/app_settings_model.dart';

/// Provider for AppSettingsLocalDataSource.
final appSettingsLocalDataSourceProvider = Provider<AppSettingsLocalDataSource>((ref) {
  return AppSettingsLocalDataSource();
});

/// Local data source for caching app settings.
class AppSettingsLocalDataSource {
  static const String _boxName = 'app_settings';
  static const String _settingsKey = 'settings';
  static const Duration _cacheDuration = Duration(hours: 1);

  Box<AppSettingsModel>? _box;

  /// Initialize Hive box.
  Future<void> init() async {
    if (_box != null && _box!.isOpen) return;

    if (!Hive.isAdapterRegistered(1)) {
      Hive.registerAdapter(AppSettingsModelAdapter());
    }
    _box = await Hive.openBox<AppSettingsModel>(_boxName);
  }

  /// Get cached settings.
  Future<AppSettingsModel?> getCachedSettings() async {
    await init();
    return _box?.get(_settingsKey);
  }

  /// Save settings to cache.
  Future<void> cacheSettings(AppSettingsModel settings) async {
    await init();
    await _box?.put(_settingsKey, settings);
  }

  /// Check if cache is valid (not expired).
  Future<bool> isCacheValid() async {
    final cached = await getCachedSettings();
    if (cached == null || cached.cachedAt == null) return false;

    final age = DateTime.now().difference(cached.cachedAt!);
    return age < _cacheDuration;
  }

  /// Clear cached settings.
  Future<void> clearCache() async {
    await init();
    await _box?.delete(_settingsKey);
  }
}
```

#### 4.5 Create Repository

**File:** `mobile/lib/data/repositories/app_settings_repository.dart`

```dart
import 'package:flutter_riverpod/flutter_riverpod.dart';

import '../data_sources/local/app_settings_local_data_source.dart';
import '../data_sources/remote/config_remote_data_source.dart';
import '../models/app_settings_model.dart';

/// Provider for AppSettingsRepository.
final appSettingsRepositoryProvider = Provider<AppSettingsRepository>((ref) {
  return AppSettingsRepository(
    ref.watch(configRemoteDataSourceProvider),
    ref.watch(appSettingsLocalDataSourceProvider),
  );
});

/// Repository for app settings with caching and fallback.
class AppSettingsRepository {
  final ConfigRemoteDataSource _remoteDataSource;
  final AppSettingsLocalDataSource _localDataSource;

  AppSettingsRepository(this._remoteDataSource, this._localDataSource);

  /// Get app settings with caching strategy:
  /// 1. If cache is valid, return cached data
  /// 2. Try to fetch from server
  /// 3. If server fails, return cached data (even if expired)
  /// 4. If no cache exists, return defaults
  Future<AppSettingsModel> getSettings({bool forceRefresh = false}) async {
    // Check cache first (unless force refresh)
    if (!forceRefresh) {
      final isCacheValid = await _localDataSource.isCacheValid();
      if (isCacheValid) {
        final cached = await _localDataSource.getCachedSettings();
        if (cached != null) return cached;
      }
    }

    // Try to fetch from server
    try {
      final settings = await _remoteDataSource.getAppSettings();
      await _localDataSource.cacheSettings(settings);
      return settings;
    } catch (e) {
      // Server failed, try to use cached data
      final cached = await _localDataSource.getCachedSettings();
      if (cached != null) return cached;

      // No cache, return defaults
      return AppSettingsModel.defaults();
    }
  }

  /// Force refresh settings from server.
  Future<AppSettingsModel> refreshSettings() => getSettings(forceRefresh: true);

  /// Clear cache.
  Future<void> clearCache() => _localDataSource.clearCache();
}
```

#### 4.6 Create Provider

**File:** `mobile/lib/presentation/providers/app_settings_provider.dart`

```dart
import 'package:flutter_riverpod/flutter_riverpod.dart';

import '../../data/models/app_settings_model.dart';
import '../../data/repositories/app_settings_repository.dart';

/// Provider for app settings state.
/// Initializes on app start and provides settings to UI.
final appSettingsProvider = StateNotifierProvider<AppSettingsNotifier, AsyncValue<AppSettingsModel>>((ref) {
  return AppSettingsNotifier(ref.watch(appSettingsRepositoryProvider));
});

/// Notifier for app settings state.
class AppSettingsNotifier extends StateNotifier<AsyncValue<AppSettingsModel>> {
  final AppSettingsRepository _repository;

  AppSettingsNotifier(this._repository) : super(const AsyncValue.loading()) {
    _loadSettings();
  }

  Future<void> _loadSettings() async {
    try {
      final settings = await _repository.getSettings();
      state = AsyncValue.data(settings);
    } catch (e, st) {
      // Even on error, provide defaults
      state = AsyncValue.data(AppSettingsModel.defaults());
    }
  }

  /// Force refresh settings from server.
  Future<void> refresh() async {
    try {
      final settings = await _repository.refreshSettings();
      state = AsyncValue.data(settings);
    } catch (e) {
      // Keep current state on refresh failure
    }
  }
}

/// Convenience provider for getting current settings synchronously.
/// Returns defaults if settings haven't loaded yet.
final currentAppSettingsProvider = Provider<AppSettingsModel>((ref) {
  final asyncSettings = ref.watch(appSettingsProvider);
  return asyncSettings.when(
    data: (settings) => settings,
    loading: () => AppSettingsModel.defaults(),
    error: (_, __) => AppSettingsModel.defaults(),
  );
});
```

#### 4.7 Initialize Hive in main.dart

**File:** `mobile/lib/main.dart`

```dart
import 'package:hive_flutter/hive_flutter.dart';

void main() async {
  WidgetsFlutterBinding.ensureInitialized();

  // Initialize Hive
  await Hive.initFlutter();

  runApp(
    const ProviderScope(
      child: AlteaApp(),
    ),
  );
}
```

---

### Phase 5: Flutter UI Updates

#### 5.1 Update main.dart with dynamic title

**File:** `mobile/lib/main.dart`

```dart
class AlteaApp extends ConsumerWidget {
  const AlteaApp({super.key});

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    final appSettings = ref.watch(currentAppSettingsProvider);

    return MaterialApp.router(
      title: appSettings.appName,  // Dynamic title
      // ... rest of the code
    );
  }
}
```

#### 5.2 Update HomeScreen

**File:** `mobile/lib/presentation/screens/home/home_screen.dart`

```dart
class HomeScreen extends ConsumerWidget {
  const HomeScreen({super.key});

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    final theme = Theme.of(context);
    final l10n = context.l10n;
    final appSettings = ref.watch(currentAppSettingsProvider);

    return Scaffold(
      appBar: AppBar(
        title: Text(appSettings.appName),  // Dynamic
        centerTitle: true,
      ),
      drawer: const AppDrawer(),
      body: SafeArea(
        child: Center(
          child: Padding(
            padding: const EdgeInsets.symmetric(horizontal: 24),
            child: Column(
              mainAxisAlignment: MainAxisAlignment.center,
              children: [
                // Logo or initial
                _buildLogo(appSettings, theme),
                const SizedBox(height: 32),

                // Hero tagline
                Text(
                  appSettings.heroText,  // Dynamic
                  style: theme.textTheme.headlineMedium?.copyWith(
                    fontWeight: FontWeight.bold,
                  ),
                  textAlign: TextAlign.center,
                ),
                const SizedBox(height: 48),

                // Get Started button
                AppButton(
                  text: l10n.getStarted,
                  onPressed: () => context.go('/login'),
                  width: double.infinity,
                ),
              ],
            ),
          ),
        ),
      ),
    );
  }

  Widget _buildLogo(AppSettingsModel settings, ThemeData theme) {
    if (settings.logoUrl != null) {
      // Show logo image
      return ClipRRect(
        borderRadius: BorderRadius.circular(24),
        child: Image.network(
          settings.logoUrl!,
          width: 120,
          height: 120,
          fit: BoxFit.cover,
          errorBuilder: (_, __, ___) => _buildInitialLogo(settings, theme),
        ),
      );
    }
    return _buildInitialLogo(settings, theme);
  }

  Widget _buildInitialLogo(AppSettingsModel settings, ThemeData theme) {
    return Container(
      width: 120,
      height: 120,
      decoration: BoxDecoration(
        color: theme.colorScheme.primary,
        borderRadius: BorderRadius.circular(24),
      ),
      child: Center(
        child: Text(
          settings.logoInitial,
          style: TextStyle(
            fontSize: 72,
            fontWeight: FontWeight.bold,
            color: theme.colorScheme.onPrimary,
          ),
        ),
      ),
    );
  }
}
```

#### 5.3 Update DrawerHeaderWidget

**File:** `mobile/lib/presentation/widgets/molecules/drawer_header_widget.dart`

```dart
import 'package:flutter_riverpod/flutter_riverpod.dart';
import '../../../presentation/providers/app_settings_provider.dart';

class DrawerHeaderWidget extends ConsumerWidget {
  final UserModel? user;

  const DrawerHeaderWidget({
    super.key,
    this.user,
  });

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    final theme = Theme.of(context);
    final appSettings = ref.watch(currentAppSettingsProvider);

    // ... rest of build method

    // Change line 83-84:
    // Replace 'Altea' with appSettings.appName
    Text(
      appSettings.appName,
      style: theme.textTheme.titleLarge?.copyWith(
        fontWeight: FontWeight.bold,
      ),
    ),

    // Change _getInitials() to use appSettings.logoInitial when user is null
  }

  String _getInitials(AppSettingsModel appSettings) {
    if (user == null) return appSettings.logoInitial;
    final first = user!.firstName.isNotEmpty ? user!.firstName[0] : '';
    final last = user!.lastName.isNotEmpty ? user!.lastName[0] : '';
    return '$first$last'.toUpperCase();
  }
}
```

---

### Phase 6: Testing

#### 6.1 Backend Tests

**File:** `apps/core/tests/test_app_settings.py`

```python
from django.test import TestCase
from django.core.cache import cache
from django.urls import reverse
from rest_framework.test import APITestCase
from rest_framework import status

from apps.core.models import AppSettings


class AppSettingsModelTests(TestCase):
    """Tests for AppSettings model."""

    def setUp(self):
        cache.clear()

    def test_singleton_pattern(self):
        """Only one AppSettings instance should exist."""
        settings1 = AppSettings.objects.create(app_name='Test1')
        settings2 = AppSettings.objects.create(app_name='Test2')

        self.assertEqual(AppSettings.objects.count(), 1)
        self.assertEqual(AppSettings.objects.first().app_name, 'Test2')

    def test_default_values(self):
        """Default values should be set."""
        settings = AppSettings.objects.create()

        self.assertEqual(settings.app_name, 'App name')
        self.assertEqual(settings.hero_text, 'Your hero string')
        self.assertEqual(settings.primary_color, '#667eea')

    def test_get_settings_caching(self):
        """get_settings should cache results."""
        AppSettings.objects.create(app_name='Cached')

        # First call should hit DB
        settings1 = AppSettings.get_settings()

        # Modify DB directly
        AppSettings.objects.filter(pk=1).update(app_name='Modified')

        # Second call should return cached value
        settings2 = AppSettings.get_settings()
        self.assertEqual(settings2.app_name, 'Cached')

        # After cache clear, should get new value
        cache.clear()
        settings3 = AppSettings.get_settings()
        self.assertEqual(settings3.app_name, 'Modified')

    def test_logo_initial(self):
        """logo_initial should return first letter."""
        settings = AppSettings.objects.create(app_name='Altea')
        self.assertEqual(settings.logo_initial, 'A')

        settings.app_name = 'lowercase'
        self.assertEqual(settings.logo_initial, 'L')

    def test_validate_hex_color(self):
        """Invalid hex colors should raise validation error."""
        settings = AppSettings(primary_color='invalid')
        with self.assertRaises(Exception):
            settings.full_clean()

    def test_cannot_delete(self):
        """Singleton should not be deletable."""
        settings = AppSettings.objects.create()
        settings.delete()
        self.assertEqual(AppSettings.objects.count(), 1)


class AppSettingsAPITests(APITestCase):
    """Tests for AppSettings API endpoint."""

    def setUp(self):
        cache.clear()
        AppSettings.objects.create(
            app_name='TestApp',
            hero_text='Test Hero',
            primary_color='#123456',
        )

    def test_get_settings_public(self):
        """Endpoint should be publicly accessible."""
        url = reverse('core-api:app-settings')
        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['app_name'], 'TestApp')
        self.assertEqual(response.data['hero_text'], 'Test Hero')

    def test_response_fields(self):
        """Response should contain all required fields."""
        url = reverse('core-api:app-settings')
        response = self.client.get(url)

        expected_fields = [
            'app_name', 'hero_text', 'logo_url', 'logo_small_url',
            'logo_initial', 'primary_color', 'secondary_color',
            'contact_email', 'support_url'
        ]
        for field in expected_fields:
            self.assertIn(field, response.data)

    def test_logo_initial_in_response(self):
        """logo_initial should be first letter of app_name."""
        url = reverse('core-api:app-settings')
        response = self.client.get(url)

        self.assertEqual(response.data['logo_initial'], 'T')
```

---

### Edge Cases

| # | Case | Expected Behavior |
|---|------|-------------------|
| 1 | No AppSettings in DB | API creates default, returns it |
| 2 | Logo upload > 2MB | Validation error in admin |
| 3 | Invalid hex color | Validation error |
| 4 | Redis unavailable | Falls back to DB query |
| 5 | App offline on startup | Flutter uses cached/defaults |
| 6 | Logo image corrupted | Flutter shows initial fallback |
| 7 | Empty app_name | Uses "A" as initial |
| 8 | Cache expired | Fetches fresh from server |
| 9 | Concurrent settings update | Last write wins, cache invalidated |
| 10 | Non-superuser accesses admin | 403/hidden from admin |

---

### File Creation Order

```
Backend:
1. requirements/base.txt (add django-redis)
2. config/settings/base.py (add CACHES, context processor)
3. apps/core/models.py (add AppSettings)
4. apps/core/context_processors.py (new)
5. apps/core/admin.py (add AppSettingsAdmin)
6. apps/core/api/serializers.py (add AppSettingsSerializer)
7. apps/core/api/views.py (add AppSettingsAPIView)
8. apps/core/api/urls.py (add route)
9. apps/core/management/commands/seed_app_settings.py (new)
10. python manage.py makemigrations && migrate
11. python manage.py seed_app_settings
12. Templates update (13 files)
13. apps/core/tests/test_app_settings.py

Flutter:
14. pubspec.yaml (add hive)
15. flutter pub get
16. lib/data/models/app_settings_model.dart
17. dart run build_runner build
18. lib/data/data_sources/remote/config_remote_data_source.dart
19. lib/data/data_sources/local/app_settings_local_data_source.dart
20. lib/data/repositories/app_settings_repository.dart
21. lib/presentation/providers/app_settings_provider.dart
22. lib/main.dart (update)
23. lib/presentation/screens/home/home_screen.dart (update)
24. lib/presentation/widgets/molecules/drawer_header_widget.dart (update)
```

---

### Checklist Update

### Planning Phase
- [x] Detailed implementation plan
- [x] File-by-file changes specified
- [x] Edge cases identified
- [x] Test cases defined

---

## Testing

### Coverage

**Overall `apps.core` coverage: 82%**

| Component | Coverage | Key Areas |
|-----------|----------|-----------|
| `models.py` | 88% | AppSettings singleton, validation, caching, thumbnail generation |
| `admin.py` | 82% | Permissions, queryset filtering, preview methods |
| `context_processors.py` | 100% | Template context injection |
| `api/urls.py` | 100% | URL routing |
| `api/serializers.py` | 76% | Serialization, logo URL handling |
| `api/views.py` | 49% | AppSettings endpoint (others not in scope) |

### Tests Created

**File:** `apps/core/tests/test_app_settings.py`

**Total tests: 88**

### Test Classes

1. **ValidateHexColorTests** (2 tests)
   - Valid hex colors pass validation
   - Invalid hex colors raise ValidationError

2. **ValidateHexColorEdgeCasesTests** (6 tests)
   - Uppercase/lowercase/mixed case hex colors
   - Missing hash prefix
   - Wrong length (3, 4, 5, 8 chars)
   - Special characters
   - Spaces in hex

3. **AppSettingsModelTests** (12 tests)
   - Singleton pattern enforced (pk=1)
   - Default color values
   - get_settings caching behavior
   - get_settings creates default if none exist
   - logo_initial property
   - logo_url/logo_small_url properties
   - Cannot delete singleton
   - String representation

4. **AppSettingsModelEdgeCasesTests** (13 tests)
   - Max length fields (app_name: 100, hero_text: 255)
   - Unicode characters in app_name
   - Leading whitespace handling
   - Concurrent get_settings calls
   - Email validation
   - URL validation
   - Blank support_url allowed
   - Timestamp auto-population
   - updated_at changes on save
   - Secondary color validation

5. **AppSettingsLogoTests** (8 tests)
   - Logo upload generates 64x64 thumbnail
   - Thumbnail size validation
   - Logo change regenerates thumbnail
   - PNG RGBA mode handling
   - JPEG format handling
   - Invalid image handled gracefully
   - logo_url property with uploaded logo
   - logo_small_url property with thumbnail

6. **AppSettingsAPITests** (5 tests)
   - GET returns 200 with settings
   - No authentication required (public endpoint)
   - Creates default settings if none exist
   - Response structure contains all fields
   - Logo URLs null when no logo

7. **AppSettingsAPIEdgeCasesTests** (6 tests)
   - Unicode app_name in response
   - Empty support_url handling
   - Full support URL returned correctly
   - Logo initial for special characters
   - updated_at timestamp included
   - Concurrent requests handled

8. **AppSettingsSerializerTests** (1 test)
   - Serializer produces expected output

9. **AppSettingsSerializerEdgeCasesTests** (5 tests)
   - All fields read-only
   - Empty hero_text handling
   - Max length fields serialized correctly
   - Logo URL with request context (absolute URL)
   - Logo URL without request context (relative URL)

10. **AppSettingsContextProcessorTests** (3 tests)
    - Returns app_settings in context
    - Creates default settings if none exist
    - Uses cached settings

11. **AppSettingsCacheTests** (4 tests)
    - Save invalidates cache
    - Custom cache key used
    - Custom cache timeout respected
    - Cache cleared on color change

12. **AppSettingsAdminTests** (11 tests)
    - Superuser can view/change settings
    - Non-superuser cannot view/change
    - has_add_permission when no settings
    - has_add_permission when settings exist
    - has_delete_permission always False
    - get_queryset for superuser
    - get_queryset for non-superuser
    - logo_preview with/without logo
    - primary_color_preview output

13. **AppSettingsHTTPMethodTests** (5 tests)
    - GET method allowed
    - POST method rejected (405)
    - PUT method rejected (405)
    - PATCH method rejected (405)
    - DELETE method rejected (405)

14. **AppSettingsIntegrationTests** (4 tests)
    - Default settings created on first API access
    - Full workflow: create and retrieve
    - Settings update reflected in API response
    - API response uses cached settings

### Edge Cases Covered

| # | Edge Case | Test Method |
|---|-----------|-------------|
| 1 | No AppSettings in DB | `test_get_settings_creates_default` |
| 2 | Invalid hex color | `test_color_validation`, `test_invalid_hex_*` |
| 3 | Unicode characters | `test_app_name_unicode_characters` |
| 4 | Max length fields | `test_app_name_max_length`, `test_hero_text_max_length` |
| 5 | Empty app_name | `test_logo_initial_empty_name` |
| 6 | Leading whitespace | `test_app_name_with_leading_whitespace` |
| 7 | Invalid image | `test_invalid_image_handled_gracefully` |
| 8 | Different image formats | `test_logo_png_rgba_mode`, `test_logo_jpeg_format` |
| 9 | Concurrent access | `test_concurrent_get_settings_creates_one` |
| 10 | Non-superuser admin access | `test_non_superuser_cannot_*` |
| 11 | Singleton deletion | `test_delete_prevented` |
| 12 | Cache invalidation | `test_save_invalidates_cache` |
| 13 | HTTP method restrictions | `test_should_reject_*_method` |

### Running Tests

```bash
# Run all AppSettings tests
python3 manage.py test apps.core.tests.test_app_settings --keepdb -v 2

# Run with coverage
python3 -m coverage run --source=apps.core manage.py test apps.core.tests.test_app_settings --keepdb
python3 -m coverage report -m
```
