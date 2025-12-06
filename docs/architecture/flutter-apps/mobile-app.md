# Altea Mobile App

## Overview

Altea Mobile is a Flutter application for iOS and Android platforms. It provides the mobile client interface for the Altea healthcare scheduling platform.

### Tech Stack

| Technology | Version | Purpose |
|------------|---------|---------|
| Flutter | 3.x | UI framework |
| Dart | ^3.9.2 | Programming language |
| Riverpod | ^2.6.1 | State management |
| Dio | ^5.7.0 | HTTP client |
| GoRouter | ^14.6.2 | Navigation/routing |
| Freezed | ^2.5.7 | Immutable data classes |

## Architecture

The app follows **Clean Architecture** principles with clear separation of concerns:

```
lib/
├── main.dart                    # App entry point
├── core/                        # Core utilities and infrastructure
│   ├── config/                  # Environment configuration
│   ├── network/                 # API client, error handling
│   └── router/                  # GoRouter configuration
├── data/                        # Data layer
│   ├── data_sources/            # Remote/local data sources
│   │   └── remote/              # API calls
│   ├── models/                  # Data transfer objects (DTOs)
│   └── repositories/            # Repository implementations
└── presentation/                # UI layer
    ├── providers/               # Riverpod state management
    ├── screens/                 # Full-page widgets
    └── widgets/                 # Reusable UI components
        ├── atoms/               # Basic building blocks
        └── molecules/           # Composite components
```

### Layer Responsibilities

#### Core Layer (`lib/core/`)

Infrastructure and configuration that doesn't belong to any specific feature.

| Component | File | Purpose |
|-----------|------|---------|
| `EnvConfig` | `config/env_config.dart` | Environment variables (API URL, timeouts) |
| `ApiClient` | `network/api_client.dart` | Dio HTTP client with interceptors |
| `ApiException` | `network/api_exceptions.dart` | Typed error handling (freezed union) |
| `AppRouter` | `router/app_router.dart` | GoRouter configuration |

#### Data Layer (`lib/data/`)

Handles data operations and external communication.

```
┌─────────────────────────────────────────────────────────┐
│                    Repository                           │
│  - Abstracts data sources from business logic           │
│  - Coordinates between remote and local data            │
│  - Returns domain models                                │
└────────────────────────┬────────────────────────────────┘
                         │
         ┌───────────────┴───────────────┐
         │                               │
┌────────▼────────┐           ┌──────────▼──────────┐
│ RemoteDataSource │           │ LocalDataSource     │
│ (API calls)      │           │ (Cache, Prefs)      │
└─────────────────┘           └─────────────────────┘
```

**Key Components:**

| Component | File | Purpose |
|-----------|------|---------|
| `AuthRepository` | `repositories/auth_repository.dart` | Authentication operations |
| `AuthRemoteDataSource` | `data_sources/remote/auth_remote_data_source.dart` | API calls for auth |
| `UserModel` | `models/user_model.dart` | User data model (json_serializable) |
| `RegistrationRequest` | `models/registration_request.dart` | Registration DTO |

#### Presentation Layer (`lib/presentation/`)

UI components and state management.

```
┌─────────────────────────────────────────────────────────┐
│                      Screen                             │
│  - Full-page widgets                                    │
│  - Uses ConsumerStatefulWidget for state access         │
└────────────────────────┬────────────────────────────────┘
                         │ ref.watch/read
         ┌───────────────┴───────────────┐
         │                               │
┌────────▼────────┐           ┌──────────▼──────────┐
│ StateNotifier    │           │ Provider            │
│ (mutable state)  │           │ (computed/derived)  │
└────────┬────────┘           └─────────────────────┘
         │
┌────────▼────────┐
│ Repository       │
└─────────────────┘
```

**Widget Hierarchy (Atomic Design):**

| Level | Location | Examples |
|-------|----------|----------|
| Atoms | `widgets/atoms/` | `AppButton`, `AppTextField` |
| Molecules | `widgets/molecules/` | `PasswordField` (TextField + visibility toggle) |
| Organisms | `widgets/organisms/` | Form groups, card lists |
| Templates | `screens/` | Page layouts |
| Pages | `screens/` | Complete screens with data |

## State Management

Using **Riverpod** with `StateNotifier` pattern:

### Provider Types

```dart
// Simple provider for dependencies
final authRepositoryProvider = Provider<AuthRepository>((ref) {
  return AuthRepository(ref.watch(authRemoteDataSourceProvider));
});

// StateNotifierProvider for mutable state
final registrationProvider =
    StateNotifierProvider<RegistrationNotifier, RegistrationState>((ref) {
  return RegistrationNotifier(ref.watch(authRepositoryProvider));
});
```

### State Definition (Freezed)

```dart
@freezed
class RegistrationState with _$RegistrationState {
  const factory RegistrationState.initial() = RegistrationInitial;
  const factory RegistrationState.loading() = RegistrationLoading;
  const factory RegistrationState.success({
    required UserModel user,
    required String email,
  }) = RegistrationSuccess;
  const factory RegistrationState.error({
    required String message,
    @Default({}) Map<String, List<String>> fieldErrors,
  }) = RegistrationError;
}
```

### Using State in Widgets

```dart
class RegistrationScreen extends ConsumerStatefulWidget {
  @override
  ConsumerState<RegistrationScreen> createState() => _RegistrationScreenState();
}

class _RegistrationScreenState extends ConsumerState<RegistrationScreen> {
  @override
  Widget build(BuildContext context) {
    // Watch state changes
    final state = ref.watch(registrationProvider);

    // Listen for side effects (navigation, snackbars)
    ref.listen<RegistrationState>(registrationProvider, (previous, next) {
      next.whenOrNull(
        success: (user, email) => context.go('/email-sent', extra: email),
        error: (message, _) => showSnackBar(message),
      );
    });

    // Access notifier for actions
    ref.read(registrationProvider.notifier).register(...);
  }
}
```

## Navigation

Using **GoRouter** for declarative routing:

```dart
final appRouter = GoRouter(
  initialLocation: '/register',
  routes: [
    GoRoute(
      path: '/register',
      name: 'register',
      builder: (context, state) => const RegistrationScreen(),
    ),
    GoRoute(
      path: '/email-sent',
      name: 'email-sent',
      builder: (context, state) {
        final email = state.extra as String? ?? '';
        return EmailSentScreen(email: email);
      },
    ),
  ],
);
```

### Current Routes

| Path | Name | Screen | Purpose |
|------|------|--------|---------|
| `/register` | register | `RegistrationScreen` | New user registration |
| `/email-sent` | email-sent | `EmailSentScreen` | Post-registration confirmation |
| `/login` | login | _PlaceholderScreen_ | User login (TODO) |
| `/terms` | terms | `TermsScreen` | Terms of Service |
| `/privacy` | privacy | `PrivacyScreen` | Privacy Policy |

## Networking

### API Client Configuration

```dart
final dioProvider = Provider<Dio>((ref) {
  final dio = Dio(BaseOptions(
    baseUrl: EnvConfig.apiBaseUrl,  // http://localhost:8000/api/v1
    connectTimeout: Duration(milliseconds: EnvConfig.apiTimeout),
    receiveTimeout: Duration(milliseconds: EnvConfig.apiTimeout),
    headers: {
      'Content-Type': 'application/json',
      'Accept': 'application/json',
    },
  ));

  dio.interceptors.add(_ErrorInterceptor());
  return dio;
});
```

### Error Handling

API errors are converted to typed `ApiException`:

```dart
@freezed
class ApiException with _$ApiException {
  const factory ApiException.badRequest(String message, Map<String, List<String>> fieldErrors) = BadRequestException;
  const factory ApiException.unauthorized(String message) = UnauthorizedException;
  const factory ApiException.forbidden(String message) = ForbiddenException;
  const factory ApiException.notFound(String message) = NotFoundException;
  const factory ApiException.tooManyRequests(String message) = TooManyRequestsException;
  const factory ApiException.serverError(String message) = ServerErrorException;
  const factory ApiException.timeout() = TimeoutException;
  const factory ApiException.noConnection() = NoConnectionException;
  const factory ApiException.cancelled() = CancelledException;
  const factory ApiException.unknown(String message) = UnknownException;
}
```

## Theming

Material 3 with `ColorScheme.fromSeed`:

```dart
MaterialApp.router(
  theme: ThemeData(
    colorScheme: ColorScheme.fromSeed(
      seedColor: const Color(0xFF2563EB), // Primary blue
      brightness: Brightness.light,
    ),
    useMaterial3: true,
  ),
  darkTheme: ThemeData(
    colorScheme: ColorScheme.fromSeed(
      seedColor: const Color(0xFF2563EB),
      brightness: Brightness.dark,
    ),
    useMaterial3: true,
  ),
);
```

## Code Generation

The project uses code generation for:

1. **Freezed** - Immutable data classes and unions
2. **json_serializable** - JSON serialization
3. **riverpod_generator** - Provider generation (optional)

### Running Code Generation

```bash
cd mobile

# One-time generation
dart run build_runner build

# Watch mode (development)
dart run build_runner watch

# Clean and rebuild
dart run build_runner build --delete-conflicting-outputs
```

### Generated Files

| Source | Generated | Purpose |
|--------|-----------|---------|
| `*.dart` with `@freezed` | `*.freezed.dart` | Immutable classes |
| `*.dart` with `@JsonSerializable` | `*.g.dart` | JSON serialization |

## Testing

```bash
cd mobile

# Run all tests
flutter test

# Run with coverage
flutter test --coverage

# Run specific test file
flutter test test/presentation/screens/auth/registration_screen_test.dart
```

### Test Structure

```
test/
├── widget_test.dart                  # Basic app test
└── presentation/
    └── screens/
        └── auth/
            └── registration_screen_test.dart  # Registration UI tests
```

## Development Commands

```bash
# Get dependencies
flutter pub get

# Run code generation
dart run build_runner build

# Analyze code
flutter analyze

# Run app
flutter run

# Run on specific device
flutter run -d <device_id>

# Build release
flutter build apk --release
flutter build ios --release
```

## Environment Configuration

`lib/core/config/env_config.dart`:

```dart
class EnvConfig {
  static const String apiBaseUrl = 'http://localhost:8000/api/v1';
  static const int apiTimeout = 30000;
  static const bool enableLogging = true;
}
```

For production, consider using `--dart-define` or environment-specific config files.

## Related Documentation

- [User Registration Workflow](../django-backend/workflows/user-registration.md)
- [User Registration Feature](../../features/user-registration/README.md)
