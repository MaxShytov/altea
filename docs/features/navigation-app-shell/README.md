# Navigation & App Shell Feature

## Overview

Navigation & App Shell provides the global navigation structure for the Altea mobile application, including a Home screen, Navigation Drawer, and automatic session restoration.

### Problem Statement

Users need a consistent navigation experience that:
- Provides a landing page (Home screen) when the app opens
- Shows relevant menu options based on authentication status
- Automatically restores sessions using stored tokens
- Allows easy logout with confirmation

### Use Cases

| ID | Use Case | Actor |
|----|----------|-------|
| UC1 | View Home screen on app launch | Any User |
| UC2 | Navigate using drawer (unauthenticated) | Guest |
| UC3 | Navigate using drawer (authenticated) | Logged-in User |
| UC4 | Automatic session restoration | Returning User |
| UC5 | Logout with confirmation | Logged-in User |
| UC6 | Access "Coming Soon" features | Logged-in User |

## User Flow

```
┌──────────────────────────────────────────────────────────────────────────────┐
│                              APP STARTUP                                      │
└──────────────────────────────────────────────────────────────────────────────┘
                                    │
                                    ▼
                        ┌───────────────────────┐
                        │  Check stored tokens  │
                        │   (AuthStateNotifier) │
                        └───────────┬───────────┘
                                    │
                    ┌───────────────┴───────────────┐
                    │                               │
            No tokens                        Has tokens
                    │                               │
                    │                               ▼
                    │                   ┌───────────────────────┐
                    │                   │   Call GET /me        │
                    │                   └───────────┬───────────┘
                    │                               │
                    │               ┌───────────────┴───────────────┐
                    │               │                               │
                    │          200 OK                         401 Error
                    │               │                               │
                    │               ▼                               │
                    │    ┌─────────────────────┐                    │
                    │    │ Set authenticated   │                    │
                    │    │ Show user in drawer │                    │
                    │    └─────────────────────┘                    │
                    │                                               │
                    └──────────────────┬────────────────────────────┘
                                       │
                                       ▼
                            ┌─────────────────────┐
                            │     Home Screen     │
                            │ (Logo + Hero text)  │
                            └─────────────────────┘
```

### Navigation Drawer States

```
┌──────────────────────────────────────┐    ┌──────────────────────────────────────┐
│     UNAUTHENTICATED DRAWER           │    │       AUTHENTICATED DRAWER           │
├──────────────────────────────────────┤    ├──────────────────────────────────────┤
│                                      │    │                                      │
│  ┌────┐                              │    │  ┌────┐                              │
│  │ A  │  Altea                       │    │  │ MM │  Max Mueller                 │
│  └────┘                              │    │  └────┘  max@example.com             │
│ ─────────────────────────────────────│    │ ─────────────────────────────────────│
│                                      │    │                                      │
│  🔑 Sign In                          │    │  🏠 Dashboard                        │
│                                      │    │                                      │
│  👤 Create Account                   │    │  👤 Profile         Coming Soon      │
│                                      │    │                                      │
│                                      │    │ ─────────────────────────────────────│
│                                      │    │                                      │
│                                      │    │  🚪 Log Out (red)                    │
│                                      │    │                                      │
└──────────────────────────────────────┘    └──────────────────────────────────────┘
```

## Screens

### 1. Home Screen

**Path:** `/home`
**File:** `mobile/lib/presentation/screens/home/home_screen.dart`

#### UI Elements

| Element | Type | Description |
|---------|------|-------------|
| AppBar | AppBar | Title "Altea", hamburger menu icon |
| Logo | Container | Large "A" letter, 120x120, primary color background |
| Hero Text | Text | "Break the Bad Habits", headlineMedium, bold |
| Get Started | AppButton | Primary button, navigates to `/login` |
| Drawer | AppDrawer | Navigation drawer accessible via hamburger |

#### Layout

```
┌────────────────────────────────┐
│ ☰                    Altea     │
├────────────────────────────────┤
│                                │
│         ┌──────────────┐       │
│         │              │       │
│         │      A       │       │
│         │              │       │
│         └──────────────┘       │
│                                │
│    Break the Bad Habits        │
│                                │
│      ┌──────────────────┐      │
│      │   Get Started    │      │
│      └──────────────────┘      │
│                                │
└────────────────────────────────┘
```

### 2. Dashboard Screen (Placeholder)

**Path:** `/dashboard`
**File:** `mobile/lib/presentation/screens/dashboard/dashboard_screen.dart`

#### UI Elements

| Element | Type | Description |
|---------|------|-------------|
| AppBar | AppBar | Title "Dashboard", hamburger menu icon |
| Icon | Icon | `CupertinoIcons.chart_bar_fill`, 64px, primary color |
| Title | Text | "Dashboard", headlineMedium, bold |
| Subtitle | Text | "Coming Soon", bodyLarge, secondary color |
| Drawer | AppDrawer | Navigation drawer accessible via hamburger |

### 3. Navigation Drawer (AppDrawer)

**File:** `mobile/lib/presentation/widgets/organisms/app_drawer.dart`

#### Components

| Component | File | Purpose |
|-----------|------|---------|
| `DrawerHeaderWidget` | `widgets/molecules/drawer_header_widget.dart` | User avatar + info or app logo |
| `DrawerMenuItem` | `widgets/molecules/drawer_menu_item.dart` | Individual menu item with icon |

#### Menu Items

**Unauthenticated:**

| Icon | Title | Action |
|------|-------|--------|
| `arrow_right_circle_fill` | Sign In | Navigate to `/login` |
| `person_badge_plus_fill` | Create Account | Navigate to `/register` |

**Authenticated:**

| Icon | Title | State | Action |
|------|-------|-------|--------|
| `house_fill` | Dashboard | Normal | Navigate to `/dashboard` |
| `person_fill` | Profile | Disabled | Show "Coming Soon" snackbar |
| `square_arrow_right` | Log Out | Destructive (red) | Show confirmation dialog |

#### Logout Confirmation Dialog

```dart
CupertinoAlertDialog(
  title: "Log Out?",
  content: "Are you sure you want to log out?",
  actions: [
    CupertinoDialogAction(isDefaultAction: true, "Cancel"),
    CupertinoDialogAction(isDestructiveAction: true, "Log Out"),
  ],
)
```

**Flow:**
1. User taps Log Out
2. Confirmation dialog appears
3. If confirmed: Clear tokens → Navigate to `/home`
4. If cancelled: Close dialog, stay on current screen

## API Integration

### Endpoints Used

| Endpoint | Method | Purpose |
|----------|--------|---------|
| `/api/v1/auth/me/` | GET | Restore session on app start |

### Request/Response Examples

**Session Check Request:**
```http
GET /api/v1/auth/me/ HTTP/1.1
Authorization: Bearer eyJ0eXAiOiJKV1QiLCJhbGc...
```

**Session Valid (200):**
```json
{
  "id": "550e8400-e29b-41d4-a716-446655440000",
  "email": "max@example.com",
  "first_name": "Max",
  "last_name": "Mueller",
  "profile_completed": false,
  "language": "en"
}
```

**Session Invalid (401):**
```json
{
  "detail": "Given token not valid for any token type"
}
```

## State Management

### AuthStateProvider

**File:** `mobile/lib/presentation/providers/auth_state_provider.dart`

```dart
enum AuthStatus {
  unknown,        // Initial state, checking auth
  authenticated,  // User logged in
  unauthenticated // No valid session
}

@freezed
class AuthState with _$AuthState {
  const factory AuthState({
    @Default(AuthStatus.unknown) AuthStatus status,
    UserModel? user,
  }) = _AuthState;
}
```

### Provider

```dart
final authStateProvider =
    StateNotifierProvider<AuthStateNotifier, AuthState>((ref) {
  return AuthStateNotifier(ref.watch(authRepositoryProvider));
});
```

### Actions

| Method | Description |
|--------|-------------|
| `checkAuth()` | Called on init, validates stored token via `/me` |
| `setAuthenticated(user)` | Called after successful login |
| `logout()` | Clears tokens, sets state to unauthenticated |

### State Flow

```
App Start → AuthStatus.unknown
    │
    ▼
checkAuth()
    │
    ├─ Token valid → AuthStatus.authenticated + user
    │
    └─ No token / invalid → AuthStatus.unauthenticated
```

## Component Diagram

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                           Presentation Layer                                 │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                             │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐                      │
│  │  HomeScreen  │  │ LoginScreen  │  │DashboardScreen│                      │
│  └──────┬───────┘  └──────┬───────┘  └──────┬───────┘                      │
│         │                 │                 │                               │
│         └────────────────┬┴─────────────────┘                               │
│                          │                                                  │
│                          ▼                                                  │
│              ┌────────────────────────┐                                     │
│              │       AppDrawer        │                                     │
│              │      (organism)        │                                     │
│              └───────────┬────────────┘                                     │
│                          │                                                  │
│         ┌────────────────┴────────────────┐                                 │
│         │                                 │                                 │
│         ▼                                 ▼                                 │
│  ┌──────────────────┐          ┌────────────────────┐                      │
│  │DrawerHeaderWidget│          │  DrawerMenuItem    │                      │
│  │   (molecule)     │          │    (molecule)      │                      │
│  └────────────────┬─┘          └────────────────────┘                      │
│                   │                                                         │
│                   │ ref.watch                                               │
│                   ▼                                                         │
│         ┌─────────────────────────────────────┐                            │
│         │         AuthStateNotifier           │                            │
│         │   (StateNotifier<AuthState>)        │                            │
│         └────────────────┬────────────────────┘                            │
│                          │                                                  │
└──────────────────────────┼──────────────────────────────────────────────────┘
                           │
┌──────────────────────────┼──────────────────────────────────────────────────┐
│                          │           Data Layer                             │
├──────────────────────────┼──────────────────────────────────────────────────┤
│                          ▼                                                  │
│         ┌────────────────────────────────────────┐                         │
│         │           AuthRepository               │                         │
│         │  getCurrentUser(), logout()            │                         │
│         └─────────┬──────────────────┬───────────┘                         │
│                   │                  │                                      │
│                   ▼                  ▼                                      │
│        ┌─────────────────┐  ┌──────────────────┐                           │
│        │AuthRemoteData   │  │  TokenStorage    │                           │
│        │Source           │  │ (SecureStorage)  │                           │
│        │GET /auth/me     │  │ clearTokens()    │                           │
│        └────────┬────────┘  └──────────────────┘                           │
│                 │                                                           │
└─────────────────┼───────────────────────────────────────────────────────────┘
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
│   ├── extensions/
│   │   └── build_context_extensions.dart  # l10n extension
│   └── router/
│       └── app_router.dart                # /home, /dashboard routes
├── data/
│   ├── data_sources/
│   │   └── remote/
│   │       └── auth_remote_data_source.dart  # getCurrentUser()
│   └── repositories/
│       └── auth_repository.dart              # getCurrentUser(), logout()
├── l10n/
│   ├── app_en.arb      # English strings
│   ├── app_de.arb      # German strings
│   ├── app_fr.arb      # French strings
│   └── app_it.arb      # Italian strings
└── presentation/
    ├── providers/
    │   └── auth_state_provider.dart    # AuthStateNotifier, AuthState
    ├── screens/
    │   ├── dashboard/
    │   │   └── dashboard_screen.dart   # Dashboard placeholder
    │   └── home/
    │       └── home_screen.dart        # Home landing page
    └── widgets/
        ├── molecules/
        │   ├── drawer_header_widget.dart  # Avatar + user info
        │   └── drawer_menu_item.dart      # Menu item with icon
        └── organisms/
            └── app_drawer.dart            # Navigation drawer
```

## Localization

### New Strings Added

| Key | EN | DE | FR | IT |
|-----|----|----|----|----|
| `appName` | Altea | Altea | Altea | Altea |
| `heroTagline` | Break the Bad Habits | Brechen Sie die schlechten Gewohnheiten | Brisez les mauvaises habitudes | Rompi le cattive abitudini |
| `menu` | Menu | Menü | Menu | Menu |
| `dashboard` | Dashboard | Dashboard | Tableau de bord | Pannello |
| `profile` | Profile | Profil | Profil | Profilo |
| `logOut` | Log Out | Abmelden | Se déconnecter | Disconnetti |
| `logOutConfirmTitle` | Log Out? | Abmelden? | Se déconnecter? | Disconnettersi? |
| `logOutConfirmMessage` | Are you sure you want to log out? | Möchten Sie sich wirklich abmelden? | Êtes-vous sûr de vouloir vous déconnecter? | Sei sicuro di voler disconnetterti? |
| `cancel` | Cancel | Abbrechen | Annuler | Annulla |
| `confirm` | Confirm | Bestätigen | Confirmer | Conferma |
| `comingSoon` | Coming Soon | Demnächst | Bientôt disponible | Prossimamente |
| `home` | Home | Startseite | Accueil | Home |
| `getStarted` | Get Started | Loslegen | Commencer | Inizia |

## Navigation

### Routes

| Path | Name | Screen | Purpose |
|------|------|--------|---------|
| `/home` | home | `HomeScreen` | Landing page (initial) |
| `/login` | login | `LoginScreen` | User login |
| `/register` | register | `RegistrationScreen` | User registration |
| `/dashboard` | dashboard | `DashboardScreen` | Authenticated user's main screen |
| `/terms` | terms | `TermsScreen` | Terms of Service |
| `/privacy` | privacy | `PrivacyScreen` | Privacy Policy |

### GoRouter Configuration

```dart
final appRouter = GoRouter(
  initialLocation: '/home',  // Changed from /login
  routes: [
    GoRoute(path: '/home', builder: (_,_) => const HomeScreen()),
    GoRoute(path: '/dashboard', builder: (_,_) => const DashboardScreen()),
    // ... other routes
  ],
);
```

## Testing

### Manual Test Cases

| # | Test | Steps | Expected |
|---|------|-------|----------|
| T1 | Home screen displays | Launch app | See logo "A", hero text, Get Started |
| T2 | Drawer opens | Tap hamburger | Drawer slides in |
| T3 | Drawer closes (tap scrim) | Tap outside drawer | Drawer closes |
| T4 | Drawer closes (swipe) | Swipe left | Drawer closes |
| T5 | Unauthenticated menu | Open drawer (no login) | See Sign In, Create Account |
| T6 | Navigate to login | Drawer → Sign In | Navigate to /login |
| T7 | Navigate to register | Drawer → Create Account | Navigate to /register |
| T8 | Authenticated menu | Login, open drawer | See avatar, name, Dashboard, Profile, Log Out |
| T9 | Profile disabled | Tap Profile | Show "Coming Soon" snackbar |
| T10 | Logout cancel | Tap Log Out → Cancel | Dialog closes, stay on page |
| T11 | Logout confirm | Tap Log Out → Confirm | Navigate to /home, show unauthenticated menu |
| T12 | Session restoration | Login, close app, reopen | Still authenticated, see user in drawer |
| T13 | Expired token handling | Wait for token expiry, reopen | Unauthenticated state, see Sign In menu |
| T14 | Localization (DE) | Change device to German | Menu items in German |

### Backend Tests

```bash
# /me endpoint tests
python manage.py test apps.accounts.tests.test_me --keepdb
```

44 tests covering authentication, edge cases, HTTP methods, security.

## Security Considerations

### Client-side

| Measure | Implementation |
|---------|----------------|
| Token storage | flutter_secure_storage (encrypted) |
| Auto-logout | Clear tokens on 401 from /me |
| Confirmation | Logout requires explicit confirmation |

### Server-side

| Measure | Implementation |
|---------|----------------|
| Authentication | JWT Bearer token required for /me |
| Token validation | SimpleJWT validates expiration, signature |
| User state check | Deleted/inactive users return 401 |

## Known Limitations

1. **No offline mode** - Requires network for session check
2. **No biometric unlock** - Uses stored tokens only
3. **Profile screen placeholder** - Shows "Coming Soon"
4. **Dashboard placeholder** - Shows "Coming Soon"
5. **No deep linking to dashboard** - Only /home deep link supported
6. **No auth guards** - Dashboard accessible via direct URL (relies on drawer state)

## Related Documentation

- [Current User Endpoint (Technical)](../../architecture/django-backend/workflows/current-user.md)
- [User Login Feature](../user-login/README.md)
- [User Registration Feature](../user-registration/README.md)
- [Flutter App Architecture](../../architecture/flutter-apps/mobile-app.md)
