# App Branding Feature

## Overview

App Branding enables centralized management of application branding elements (logo, name, colors, contact information) from a single location in Django Admin.

### Problem Statement

Previously, the application name "Altea" and other branding elements were hardcoded across 13+ Django templates and Flutter screens. This made it difficult to:
- Change branding without code modifications
- Maintain consistency across platforms
- Support white-labeling or rebranding

### Use Cases

| ID | Use Case | Actor |
|----|----------|-------|
| UC1 | Update application branding | Superuser |
| UC2 | View branding in mobile app | End User |
| UC3 | View branding in emails | End User |
| UC4 | Work offline with cached branding | End User |

## User Flow

```
┌─────────────────────────────────────────────────────────────────┐
│                        SUPERUSER                                 │
└─────────────────────────────────────────────────────────────────┘
         │
         │ 1. Login to Django Admin
         ▼
┌─────────────────────┐
│   Django Admin      │
│   /admin/           │
└──────────┬──────────┘
           │ 2. Navigate to Core > App Settings
           ▼
┌─────────────────────┐      ┌─────────────────────┐
│  App Settings Form  │      │    Logo Upload      │
│  - App Name         │──────│    - Main Logo      │
│  - Hero Text        │      │    - Auto-thumbnail │
│  - Colors           │      └─────────────────────┘
│  - Contact Info     │
└──────────┬──────────┘
           │ 3. Save Changes
           ▼
┌─────────────────────┐
│  Cache Invalidated  │
│  (Redis cleared)    │
└──────────┬──────────┘
           │
           ▼
┌─────────────────────────────────────────────────────────────────┐
│                     CHANGES PROPAGATE TO:                        │
├─────────────────────┬─────────────────────┬─────────────────────┤
│  Django Templates   │   Flutter App       │   Email Templates   │
│  (Immediate)        │   (Within 1 hour)   │   (Immediate)       │
└─────────────────────┴─────────────────────┴─────────────────────┘
```

## Screens

### 1. Django Admin - App Settings

**Path:** `/admin/core/appsettings/1/change/`
**Access:** Superuser only

#### Form Fields

| Field | Type | Description |
|-------|------|-------------|
| App Name | Text | Application name (max 100 chars) |
| Hero Text | Text | Tagline for home screen (max 255 chars) |
| Logo | File Upload | Main logo (recommended 512x512 PNG) |
| Logo Preview | Read-only | Shows current logo or initial |
| Small Logo | Read-only | Auto-generated 64x64 thumbnail |
| Primary Color | Text | Hex color code (#RRGGBB) |
| Secondary Color | Text | Hex color code (#RRGGBB) |
| Contact Email | Email | Support email address |
| Support URL | URL | Link to support page (optional) |

#### Validation

| Rule | Error Message |
|------|---------------|
| Invalid hex color | "X is not a valid hex color. Use format #RRGGBB" |
| Invalid email | Standard Django email validation |
| Invalid URL | Standard Django URL validation |

### 2. Flutter Mobile - Home Screen

**Path:** `/home`
**File:** `mobile/lib/presentation/screens/home/home_screen.dart`

#### Dynamic Elements

| Element | Source | Fallback |
|---------|--------|----------|
| App Title | `appSettings.appName` | "Altea" |
| Hero Text | `appSettings.heroText` | "Break the Bad Habits" |
| Logo | `appSettings.logoUrl` | Initial letter circle |

### 3. Flutter Mobile - Drawer Header

**Path:** Drawer menu
**File:** `mobile/lib/presentation/widgets/molecules/drawer_header_widget.dart`

#### Dynamic Elements

| Element | Source | Fallback |
|---------|--------|----------|
| Logo Circle | Gradient with `appSettings.logoInitial` | "A" |
| App Name | `appSettings.appName` | "Altea" |

## API Integration

### Endpoints Used

| Endpoint | Method | Purpose |
|----------|--------|---------|
| `/api/v1/config/app-settings/` | GET | Fetch branding settings |

### Request/Response

**Request:**
```http
GET /api/v1/config/app-settings/ HTTP/1.1
Host: api.altea.ch
Accept: application/json
```

**Response 200:**
```json
{
    "app_name": "Altea",
    "hero_text": "Break the Bad Habits",
    "logo_url": "https://api.altea.ch/media/branding/logo.png",
    "logo_small_url": "https://api.altea.ch/media/branding/logo_small.png",
    "logo_initial": "A",
    "primary_color": "#667eea",
    "secondary_color": "#764ba2",
    "contact_email": "support@altea.ch",
    "support_url": "https://altea.ch/support",
    "updated_at": "2025-12-07T10:30:00Z"
}
```

## State Management

### Provider

```dart
// App settings provider with caching
final appSettingsProvider = StateNotifierProvider<AppSettingsNotifier, AsyncValue<AppSettingsModel>>(...);

// Convenience provider for synchronous access
final currentAppSettingsProvider = Provider<AppSettingsModel>(...);
```

### States

| State | Description |
|-------|-------------|
| `AsyncValue.loading()` | Initial load in progress |
| `AsyncValue.data(settings)` | Settings loaded successfully |
| `AsyncValue.error(e, st)` | Load failed (uses defaults) |

### Actions

| Method | Purpose |
|--------|---------|
| `_loadSettings()` | Load from cache or API |
| `refresh()` | Force reload from API |

## Component Diagram

```
┌────────────────────────────────────────────────────────────────────┐
│                        Presentation Layer                           │
├────────────────────────────────────────────────────────────────────┤
│                                                                     │
│  ┌───────────────┐    ┌───────────────┐    ┌───────────────┐       │
│  │  HomeScreen   │    │ DrawerHeader  │    │  main.dart    │       │
│  └───────┬───────┘    └───────┬───────┘    └───────┬───────┘       │
│          │                    │                    │                │
│          └────────────────────┼────────────────────┘                │
│                               │ ref.watch                           │
│                               ▼                                     │
│  ┌─────────────────────────────────────────────────────────────┐   │
│  │              currentAppSettingsProvider                      │   │
│  │         (Returns AppSettingsModel synchronously)             │   │
│  └───────────────────────────┬─────────────────────────────────┘   │
│                               │                                     │
└───────────────────────────────┼─────────────────────────────────────┘
                                │
┌───────────────────────────────┼─────────────────────────────────────┐
│                               │          Data Layer                  │
├───────────────────────────────┼─────────────────────────────────────┤
│                               ▼                                     │
│  ┌─────────────────────────────────────────────────────────────┐   │
│  │               AppSettingsRepository                          │   │
│  │  getSettings(), refreshSettings(), clearCache()              │   │
│  └───────────────────────────┬─────────────────────────────────┘   │
│                               │                                     │
│          ┌────────────────────┼────────────────────┐               │
│          │                    │                    │                │
│          ▼                    ▼                    │                │
│  ┌───────────────┐    ┌───────────────┐           │                │
│  │ RemoteSource  │    │ LocalSource   │           │                │
│  │ (API calls)   │    │ (SharedPrefs) │           │                │
│  └───────┬───────┘    └───────────────┘           │                │
│          │                                         │                │
└──────────┼─────────────────────────────────────────┘                │
           │                                                          │
           ▼                                                          │
   ┌───────────────┐                                                  │
   │  Django API   │                                                  │
   └───────────────┘                                                  │
```

## File Structure

### Django Backend

```
apps/core/
├── admin.py                        # AppSettingsAdmin
├── api/
│   ├── serializers.py              # AppSettingsSerializer
│   ├── urls.py                     # Route configuration
│   └── views.py                    # AppSettingsAPIView
├── context_processors.py           # Template context
├── models.py                       # AppSettings model
└── tests/
    └── test_app_settings.py        # 88 tests
```

### Flutter Mobile

```
mobile/lib/
├── data/
│   ├── data_sources/
│   │   ├── local/
│   │   │   └── app_settings_local_data_source.dart
│   │   └── remote/
│   │       └── config_remote_data_source.dart
│   ├── models/
│   │   └── app_settings_model.dart
│   └── repositories/
│       └── app_settings_repository.dart
└── presentation/
    ├── providers/
    │   └── app_settings_provider.dart
    ├── screens/
    │   └── home/
    │       └── home_screen.dart
    └── widgets/
        └── molecules/
            └── drawer_header_widget.dart
```

### Django Templates Updated

```
templates/
├── admin/
│   └── base_site.html             # Admin title
├── base.html                       # Page title
├── emails/
│   ├── base_email.html            # Email branding
│   ├── password_reset.html
│   ├── password_reset_subject.txt
│   ├── shift_assigned.html
│   ├── timeoff_approved.html
│   └── welcome.html
├── layouts/
│   ├── auth_layout.html           # Auth pages branding
│   └── dashboard_layout.html      # Dashboard sidebar
└── legal/
    ├── base_legal.html
    └── not_found.html
```

## Testing

### Backend Tests

```bash
# Run all tests (88 tests)
python3 manage.py test apps.core.tests.test_app_settings --keepdb -v 2

# With coverage
python3 -m coverage run --source=apps.core manage.py test apps.core.tests.test_app_settings --keepdb
python3 -m coverage report -m
```

### Coverage: 82%

| Component | Coverage |
|-----------|----------|
| models.py | 88% |
| admin.py | 82% |
| context_processors.py | 100% |

## Security Considerations

### Access Control
- Django Admin: Superuser only
- API Endpoint: Public (no sensitive data)
- No CSRF required for GET endpoint

### Data Validation
- Hex colors validated with regex
- Email validated with Django EmailValidator
- URLs validated with Django URLValidator
- Images validated by Pillow

## Known Limitations

1. **No SVG Support** - Logo must be raster image (PNG, JPEG)
2. **Synchronous Thumbnail** - Generated during request (not async)
3. **Single Instance** - No multi-tenancy support
4. **1-Hour Cache** - Changes take up to 1 hour to propagate to mobile

## Related Documentation

- [Technical Documentation](../../architecture/django-backend/workflows/app-branding.md)
- [Mobile App Architecture](../../architecture/flutter-apps/mobile-app.md)
- [User Registration](../user-registration/README.md) - Uses dynamic branding in emails
