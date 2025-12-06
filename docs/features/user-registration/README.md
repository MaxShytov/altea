# User Registration Feature

## Overview

User Registration enables new users to create accounts in the Altea platform with email verification.

### Problem Statement

New users need a secure, GDPR-compliant way to create accounts that:
- Validates email ownership through verification
- Ensures password security
- Captures consent for Terms of Service and Privacy Policy
- Prevents spam and abuse through rate limiting

### Use Cases

| ID | Use Case | Actor |
|----|----------|-------|
| UC1 | Register new account | New User |
| UC2 | Verify email address | New User |
| UC3 | Resend verification email | Unverified User |
| UC4 | View Terms of Service | New User |
| UC5 | View Privacy Policy | New User |

## User Flow

```
┌─────────────┐     ┌─────────────┐     ┌─────────────┐     ┌─────────────┐
│             │     │             │     │             │     │             │
│  Register   │────▶│ Email Sent  │────▶│   Verify    │────▶│   Login     │
│   Screen    │     │   Screen    │     │   (Email)   │     │   Screen    │
│             │     │             │     │             │     │             │
└─────────────┘     └─────────────┘     └─────────────┘     └─────────────┘
      │                   │
      │                   │ [Resend]
      │                   ▼
      │             ┌─────────────┐
      │ [Terms]     │   Resend    │
      │ [Privacy]   │ Verification│
      ▼             └─────────────┘
┌─────────────┐
│   Legal     │
│  Documents  │
└─────────────┘
```

## Screens

### 1. Registration Screen

**Path:** `/register`
**File:** `mobile/lib/presentation/screens/auth/registration_screen.dart`

#### UI Elements

| Element | Type | Validation |
|---------|------|------------|
| Email | TextField | Required, valid format, unique |
| First Name | TextField | Required, min 2 chars |
| Last Name | TextField | Required, min 2 chars |
| Password | PasswordField | Required, min 8 chars |
| Confirm Password | PasswordField | Must match password |
| Terms Checkbox | Checkbox | Must be checked |
| Terms Link | TextButton | Opens /terms |
| Privacy Link | TextButton | Opens /privacy |
| Create Account | Button | Submits form |
| Sign In Link | TextButton | Navigates to /login |

#### States

| State | UI Behavior |
|-------|-------------|
| Initial | Form enabled, button active |
| Loading | Form disabled, button shows spinner |
| Error | Form enabled, snackbar with error, field errors shown |
| Success | Navigate to /email-sent |

#### Email Validation Regex

```dart
RegExp(r'^[\w\.\-\+]+@([\w\-]+\.)+[\w\-]{2,}$')
```

Supports:
- Standard emails: `user@example.com`
- Subdomains: `user@mail.example.com`
- Plus addressing: `user+tag@example.com`
- Long TLDs: `user@company.software`

### 2. Email Sent Screen

**Path:** `/email-sent`
**File:** `mobile/lib/presentation/screens/auth/email_sent_screen.dart`

#### UI Elements

| Element | Type | Action |
|---------|------|--------|
| Icon | Icon | Email icon in circle |
| Title | Text | "Check your email" |
| Email Display | Text | Shows submitted email |
| Instructions | Text | Verification instructions |
| Resend Button | Button | Triggers resend API |
| Back to Sign In | Button | Navigates to /login |
| Help Text | Text | Spam folder hint |

#### Resend Behavior

- Shows loading state during API call
- On success: Shows green snackbar, updates icon to checkmark
- On failure: Shows red snackbar with error message
- Rate limited: 3 requests/hour per IP

### 3. Email Verification Page

**Path:** `/api/v1/auth/verify-email/{token}/` (browser)
**File:** `apps/accounts/templates/accounts/verify_email.html`

HTML page rendered by Django for email link clicks.

#### States

| State | Message | Action |
|-------|---------|--------|
| Success | "Email verified successfully!" | Shows deep link button |
| Invalid Token | "Invalid verification link" | Shows error |
| Expired Token | "Link has expired" | Shows resend option |
| Already Used | "Already verified" | Shows login link |

#### Deep Link

`altea://verified` - Opens app after successful verification

### 4. Terms Screen

**Path:** `/terms`
**File:** `mobile/lib/presentation/screens/legal/terms_screen.dart`

Fetches and displays current Terms of Service from API.

### 5. Privacy Screen

**Path:** `/privacy`
**File:** `mobile/lib/presentation/screens/legal/privacy_screen.dart`

Fetches and displays current Privacy Policy from API.

## API Integration

### Endpoints Used

| Endpoint | Method | Purpose |
|----------|--------|---------|
| `/api/v1/auth/register/` | POST | Create account |
| `/api/v1/auth/resend-verification/` | POST | Resend email |
| `/api/v1/legal/documents/terms-of-service/` | GET | Fetch terms |
| `/api/v1/legal/documents/privacy-policy/` | GET | Fetch privacy |

### Request/Response Examples

**Registration Request:**
```json
{
  "email": "user@example.com",
  "password": "SecurePass123",
  "password_confirm": "SecurePass123",
  "first_name": "John",
  "last_name": "Doe",
  "terms_accepted": true
}
```

**Registration Success (201):**
```json
{
  "error": false,
  "message": "Registration successful...",
  "user": {
    "id": 1,
    "email": "user@example.com",
    "first_name": "John",
    "last_name": "Doe",
    "is_verified": false
  }
}
```

**Validation Error (400):**
```json
{
  "error": true,
  "message": "Validation failed",
  "details": {
    "email": ["A user with that email already exists."],
    "password": ["This password is too short."]
  }
}
```

**Rate Limited (429):**
```json
{
  "error": true,
  "message": "Request was throttled. Expected available in 3600 seconds."
}
```

## State Management

### Provider

```dart
final registrationProvider =
    StateNotifierProvider<RegistrationNotifier, RegistrationState>(...);
```

### States (Freezed)

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

### Actions

| Method | Parameters | Description |
|--------|------------|-------------|
| `register()` | email, password, passwordConfirm, firstName, lastName, termsAccepted | Creates new account |
| `resendVerification()` | email | Returns `(bool success, String? errorMessage)` |
| `reset()` | - | Resets to initial state |

## Component Diagram

```
┌────────────────────────────────────────────────────────────────────┐
│                        Presentation Layer                          │
├────────────────────────────────────────────────────────────────────┤
│                                                                    │
│  ┌──────────────────┐    ┌──────────────────┐                     │
│  │RegistrationScreen│    │  EmailSentScreen │                     │
│  └────────┬─────────┘    └────────┬─────────┘                     │
│           │                       │                                │
│           │  ref.watch/read       │                                │
│           ▼                       ▼                                │
│  ┌────────────────────────────────────────┐                       │
│  │       RegistrationNotifier             │                       │
│  │  (StateNotifier<RegistrationState>)    │                       │
│  └────────────────┬───────────────────────┘                       │
│                   │                                                │
└───────────────────┼────────────────────────────────────────────────┘
                    │
┌───────────────────┼────────────────────────────────────────────────┐
│                   │           Data Layer                           │
├───────────────────┼────────────────────────────────────────────────┤
│                   ▼                                                │
│  ┌────────────────────────────────────────┐                       │
│  │           AuthRepository               │                       │
│  │  register(), resendVerification()      │                       │
│  └────────────────┬───────────────────────┘                       │
│                   │                                                │
│                   ▼                                                │
│  ┌────────────────────────────────────────┐                       │
│  │       AuthRemoteDataSource             │                       │
│  │  POST /auth/register/                  │                       │
│  │  POST /auth/resend-verification/       │                       │
│  └────────────────┬───────────────────────┘                       │
│                   │                                                │
└───────────────────┼────────────────────────────────────────────────┘
                    │
                    ▼
            ┌───────────────┐
            │  Django API   │
            └───────────────┘
```

## File Structure

```
mobile/lib/
├── core/
│   └── network/
│       ├── api_client.dart           # Dio configuration
│       └── api_exceptions.dart       # Error types
├── data/
│   ├── data_sources/
│   │   └── remote/
│   │       └── auth_remote_data_source.dart
│   ├── models/
│   │   ├── registration_request.dart
│   │   ├── registration_response.dart
│   │   └── user_model.dart
│   └── repositories/
│       └── auth_repository.dart
└── presentation/
    ├── providers/
    │   ├── auth_provider.dart        # RegistrationNotifier
    │   └── registration_state.dart   # State definitions
    ├── screens/
    │   ├── auth/
    │   │   ├── registration_screen.dart
    │   │   └── email_sent_screen.dart
    │   └── legal/
    │       ├── terms_screen.dart
    │       └── privacy_screen.dart
    └── widgets/
        ├── atoms/
        │   ├── app_button.dart
        │   └── app_text_field.dart
        └── molecules/
            └── password_field.dart
```

## Testing

### Flutter Tests

```bash
cd mobile
flutter test
```

Test files:
- `test/presentation/screens/auth/registration_screen_test.dart`

### Test Coverage

| Category | Tests |
|----------|-------|
| Form Rendering | Header, fields, checkbox, links |
| Navigation | Login link, terms link, privacy link |
| Text Input | Email, names validation |

## Security Considerations

### Client-side

- Password fields obscure text
- Form data not persisted in state on navigation away
- HTTPS required for API calls in production

### Server-side

- Rate limiting: 5 registrations/hour per IP
- Password validation (Django validators)
- Email verification required before account activation
- GDPR compliance with timestamp and version tracking

## Known Limitations

1. **No password strength indicator** - Consider adding visual feedback
2. **No social login** - Email-only registration currently
3. **No remember me** - Session management not implemented
4. **No password recovery** - To be implemented in login feature

## Related Documentation

- [Django User Registration Workflow](../../architecture/django-backend/workflows/user-registration.md)
- [Flutter App Architecture](../../architecture/flutter-apps/mobile-app.md)
- [Legal Documents Workflow](../../architecture/django-backend/workflows/legal-documents.md)
