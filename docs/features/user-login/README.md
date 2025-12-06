# User Login Feature

## Overview

User Login enables existing users to authenticate into the Altea platform using their email and password.

### Problem Statement

Registered users need a secure way to access the platform that:
- Validates credentials against stored user data
- Issues JWT tokens for session management
- Handles edge cases (wrong password, unverified email)
- Prevents brute force attacks through rate limiting

### Use Cases

| ID | Use Case | Actor |
|----|----------|-------|
| UC1 | Login with valid credentials | Verified User |
| UC2 | Handle invalid credentials | Any User |
| UC3 | Handle unverified email | Unverified User |
| UC4 | Navigate to registration | New User |
| UC5 | Navigate to forgot password | Forgetful User |

## User Flow

```
                           ┌─────────────────┐
                           │                 │
                           │  Login Screen   │
                           │                 │
                           └────────┬────────┘
                                    │
                           ┌────────▼────────┐
                           │  Enter email &  │
                           │    password     │
                           └────────┬────────┘
                                    │
                           ┌────────▼────────┐
                           │   Submit form   │
                           └────────┬────────┘
                                    │
        ┌───────────────────────────┼───────────────────────────┐
        │                           │                           │
┌───────▼───────┐          ┌────────▼────────┐         ┌────────▼────────┐
│   Success     │          │ Invalid Creds   │         │ Email Not       │
│   (200)       │          │    (401)        │         │ Verified (403)  │
└───────┬───────┘          └────────┬────────┘         └────────┬────────┘
        │                           │                           │
┌───────▼───────┐          ┌────────▼────────┐         ┌────────▼────────┐
│  Save tokens  │          │  Show error     │         │ Show error +    │
│  to storage   │          │  snackbar       │         │ "Resend" option │
└───────┬───────┘          └─────────────────┘         └─────────────────┘
        │
┌───────▼───────┐
│   Navigate    │
│ to Dashboard  │
└───────────────┘
```

## Screens

### 1. Login Screen

**Path:** `/login`
**File:** `mobile/lib/presentation/screens/auth/login_screen.dart`

#### UI Elements

| Element | Type | Validation/Action |
|---------|------|-------------------|
| Header | Text | "Welcome Back" + subtitle |
| Email | TextField | Required, valid email format |
| Password | PasswordField | Required, with show/hide toggle |
| Forgot Password | TextButton | Shows "coming soon" snackbar |
| Sign In | AppButton | Submits form, shows loading state |
| Register Link | TextButton | Navigates to `/register` |

#### Email Validation Regex

```dart
RegExp(r'^[\w\.\-\+]+@([\w\-]+\.)+[\w\-]{2,}$')
```

Supports:
- Standard emails: `user@example.com`
- Subdomains: `user@mail.example.com`
- Plus addressing: `user+tag@example.com`
- Long TLDs: `user@company.software`

#### States

| State | UI Behavior |
|-------|-------------|
| Initial | Form enabled, button active |
| Loading | Form disabled, button shows spinner |
| Error (401) | Form enabled, red snackbar "Invalid email or password" |
| Error (403) | Form enabled, red snackbar with "Resend" action |
| Error (429) | Form enabled, snackbar "Too many attempts" |
| Success | Navigate to `/dashboard`, save tokens |

#### Error Handling

| Error Code | Message | Action |
|------------|---------|--------|
| `invalid_credentials` | "Invalid email or password" | Show snackbar |
| `email_not_verified` | "Please verify your email" | Show snackbar with "Resend" button |
| `too_many_requests` | "Too many login attempts. Please try again later." | Show snackbar |
| `no_connection` | "No internet connection. Please check your network." | Show snackbar |

### 2. Dashboard Screen

**Path:** `/dashboard`
**File:** `mobile/lib/presentation/screens/dashboard/dashboard_screen.dart`

Placeholder screen showing "Dashboard - Coming Soon" with navigation drawer. See [Navigation & App Shell Feature](../navigation-app-shell/README.md) for details.

## API Integration

### Endpoints Used

| Endpoint | Method | Purpose |
|----------|--------|---------|
| `/api/v1/auth/login/` | POST | Authenticate user |

### Request/Response Examples

**Login Request:**
```json
{
  "email": "user@example.com",
  "password": "SecurePass123"
}
```

**Login Success (200):**
```json
{
  "access_token": "eyJ0eXAiOiJKV1QiLCJhbGc...",
  "refresh_token": "eyJ0eXAiOiJKV1QiLCJhbGc...",
  "user": {
    "id": "550e8400-e29b-41d4-a716-446655440000",
    "email": "user@example.com",
    "first_name": "Max",
    "last_name": "Mueller",
    "profile_completed": false,
    "language": "en"
  }
}
```

**Invalid Credentials (401):**
```json
{
  "detail": "Invalid credentials"
}
```

**Email Not Verified (403):**
```json
{
  "detail": "Please verify your email",
  "code": "email_not_verified"
}
```

**Rate Limited (429):**
```json
{
  "detail": "Request was throttled. Expected available in 900 seconds."
}
```

## State Management

### Provider

```dart
final loginProvider =
    StateNotifierProvider<LoginNotifier, LoginState>((ref) {
  return LoginNotifier(ref.watch(authRepositoryProvider));
});
```

### States (Freezed)

```dart
@freezed
class LoginState with _$LoginState {
  const factory LoginState.initial() = LoginInitial;
  const factory LoginState.loading() = LoginLoading;
  const factory LoginState.success({
    required UserModel user,
  }) = LoginSuccess;
  const factory LoginState.error({
    required String message,
    String? code,
  }) = LoginError;
}
```

### Additional Providers

| Provider | Type | Purpose |
|----------|------|---------|
| `loginProvider` | `StateNotifierProvider<LoginNotifier, LoginState>` | Login form state |
| `currentUserProvider` | `StateProvider<UserModel?>` | Authenticated user |
| `isAuthenticatedProvider` | `FutureProvider<bool>` | Check if logged in |

### Actions

| Method | Parameters | Description |
|--------|------------|-------------|
| `login()` | email, password | Authenticates user, saves tokens |
| `logout()` | - | Clears tokens and state |
| `reset()` | - | Resets to initial state |

### Error Parsing

The `LoginNotifier` parses API exceptions into user-friendly messages:

```dart
({String message, String? code}) _parseApiError(ApiException e) {
  return e.when(
    unauthorized: (message) => (
      message: message.isNotEmpty ? message : 'Invalid email or password',
      code: 'invalid_credentials',
    ),
    forbidden: (message) => (
      message: message.isNotEmpty ? message : 'Please verify your email',
      code: 'email_not_verified',
    ),
    // ... other cases
  );
}
```

## Component Diagram

```
┌────────────────────────────────────────────────────────────────────┐
│                        Presentation Layer                          │
├────────────────────────────────────────────────────────────────────┤
│                                                                    │
│  ┌──────────────────┐                                              │
│  │   LoginScreen    │                                              │
│  │ ConsumerStateful │                                              │
│  │     Widget       │                                              │
│  └────────┬─────────┘                                              │
│           │  ref.watch / ref.listen                                │
│           ▼                                                        │
│  ┌────────────────────────────────────────┐                        │
│  │           LoginNotifier                │                        │
│  │  (StateNotifier<LoginState>)           │                        │
│  └────────────────┬───────────────────────┘                        │
│                   │                                                │
└───────────────────┼────────────────────────────────────────────────┘
                    │
┌───────────────────┼────────────────────────────────────────────────┐
│                   │           Data Layer                           │
├───────────────────┼────────────────────────────────────────────────┤
│                   ▼                                                │
│  ┌────────────────────────────────────────┐                        │
│  │          AuthRepository                │                        │
│  │  login(), logout(), isLoggedIn()       │                        │
│  └─────┬──────────────────────┬───────────┘                        │
│        │                      │                                    │
│        ▼                      ▼                                    │
│  ┌─────────────────┐   ┌──────────────────┐                        │
│  │AuthRemoteData   │   │  TokenStorage    │                        │
│  │Source           │   │(SecureStorage)   │                        │
│  │POST /auth/login │   │ saveTokens()     │                        │
│  └────────┬────────┘   └──────────────────┘                        │
│           │                                                        │
└───────────┼────────────────────────────────────────────────────────┘
            │
            ▼
    ┌───────────────┐
    │  Django API   │
    └───────────────┘
```

## Token Storage

### TokenStorage Class

**File:** `mobile/lib/core/storage/token_storage.dart`

```dart
class TokenStorage {
  // Uses flutter_secure_storage
  Future<void> saveTokens({accessToken, refreshToken});
  Future<String?> getAccessToken();
  Future<String?> getRefreshToken();
  Future<bool> hasTokens();
  Future<void> clearTokens();
}
```

### Storage Security

| Platform | Implementation |
|----------|----------------|
| Android | `EncryptedSharedPreferences` |
| iOS | Keychain with `KeychainAccessibility.first_unlock` |

## File Structure

```
mobile/lib/
├── core/
│   ├── router/
│   │   └── app_router.dart           # /login, /dashboard routes
│   └── storage/
│       └── token_storage.dart        # SecureStorage wrapper
├── data/
│   ├── data_sources/
│   │   └── remote/
│   │       └── auth_remote_data_source.dart  # login() method
│   ├── models/
│   │   ├── auth_response.dart        # AuthResponse model
│   │   └── user_model.dart           # UserModel with login fields
│   └── repositories/
│       └── auth_repository.dart      # login(), logout(), isLoggedIn()
└── presentation/
    ├── providers/
    │   ├── login_provider.dart       # LoginNotifier, providers
    │   └── login_state.dart          # LoginState (freezed)
    ├── screens/
    │   └── auth/
    │       └── login_screen.dart     # Login UI
    └── widgets/
        ├── atoms/
        │   ├── app_button.dart       # Submit button
        │   └── app_text_field.dart   # Email field
        └── molecules/
            └── password_field.dart   # Password with toggle
```

## Testing

### Flutter Tests

```bash
cd mobile
flutter test
```

### Test Files

- `test/widget_test.dart` - Basic app test with login screen

### Test Coverage

| Category | Tests |
|----------|-------|
| Widget rendering | LoginScreen displays all elements |
| Navigation | Register link, dashboard redirect |
| State management | Loading, success, error states |

## Security Considerations

### Client-side

| Measure | Implementation |
|---------|----------------|
| Password obscuring | PasswordField with toggle |
| Token storage | flutter_secure_storage (encrypted) |
| HTTPS | Required for production API |
| State cleanup | Tokens cleared on logout |

### Server-side

| Measure | Implementation |
|---------|----------------|
| Rate limiting | 5 login attempts per 15 minutes per IP |
| Password validation | Django validators (min 8 chars, etc.) |
| Email enumeration prevention | Same error for wrong email and wrong password |
| Email verification | Required before login allowed |

## Navigation

### Routes

| Path | Name | Screen | Auth Required |
|------|------|--------|---------------|
| `/home` | home | `HomeScreen` | No |
| `/login` | login | `LoginScreen` | No |
| `/register` | register | `RegistrationScreen` | No |
| `/dashboard` | dashboard | `DashboardScreen` | Yes (future) |

### GoRouter Configuration

```dart
final appRouter = GoRouter(
  initialLocation: '/home',  // Home screen is initial (FR-NAV-1)
  routes: [
    GoRoute(
      path: '/home',
      name: 'home',
      builder: (context, state) => const HomeScreen(),
    ),
    GoRoute(
      path: '/login',
      name: 'login',
      builder: (context, state) => const LoginScreen(),
    ),
    GoRoute(
      path: '/dashboard',
      name: 'dashboard',
      builder: (context, state) => const DashboardScreen(),
    ),
    // ...
  ],
);
```

## Known Limitations

1. **No "Remember Me"** - Session management via token only
2. **No forgot password** - Shows "coming soon" message
3. **No biometric login** - Fingerprint/Face ID not implemented
4. **No social login** - Email/password only
5. **No auth redirect guard** - Dashboard accessible without login (relies on drawer state)

## Related Documentation

- [Technical Documentation](../../architecture/django-backend/workflows/user-login.md)
- [Navigation & App Shell Feature](../navigation-app-shell/README.md)
- [User Registration Feature](../user-registration/README.md)
- [Flutter App Architecture](../../architecture/flutter-apps/mobile-app.md)
