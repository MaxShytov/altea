# Current User Endpoint

## Overview

### What This Feature Solves
The Current User endpoint (`/me`) provides a way for the mobile app to retrieve the authenticated user's data using a JWT token. This enables session restoration on app startup without requiring users to re-enter credentials.

### Use Cases
1. **UC1: Session Restoration** - App starts with stored tokens, validates and retrieves user data
2. **UC2: Token Validation** - Verify if stored access token is still valid
3. **UC3: User Profile Display** - Get current user data for UI (drawer header, profile screens)

### Where Used in System
- Flutter mobile app: `AuthStateNotifier.checkAuth()` on app startup
- Navigation drawer: User avatar and name display
- Any screen needing current user context

## Architecture

### Components

#### Django Apps
- **accounts** - Core authentication app containing User model and API endpoints
- **rest_framework_simplejwt** - JWT token validation via `IsAuthenticated` permission

#### API Endpoints

| Method | Endpoint | View | Purpose |
|--------|----------|------|---------|
| GET | `/api/v1/auth/me/` | `MeAPIView` | Get current authenticated user data |

### Flow Diagram

```mermaid
sequenceDiagram
    participant App as Flutter App
    participant Storage as SecureStorage
    participant API as Django API
    participant JWT as SimpleJWT
    participant DB as Database

    Note over App: App startup
    App->>Storage: getAccessToken()
    Storage-->>App: access_token (or null)

    alt No token stored
        App->>App: Set state: unauthenticated
    else Token exists
        App->>API: GET /api/v1/auth/me/<br/>Authorization: Bearer {token}
        API->>JWT: Validate token

        alt Token valid
            JWT-->>API: User from token
            API->>DB: Get user by ID

            alt User exists & active
                DB-->>API: User data
                API-->>App: 200 OK + user
                App->>App: Set state: authenticated
            else User deleted/inactive
                API-->>App: 401 Unauthorized
                App->>Storage: clearTokens()
                App->>App: Set state: unauthenticated
            end
        else Token invalid/expired
            JWT-->>API: Invalid token
            API-->>App: 401 Unauthorized
            App->>Storage: clearTokens()
            App->>App: Set state: unauthenticated
        end
    end
```

## Implementation Details

### Key Patterns

1. **Minimal View** - Simple GET endpoint that relies on DRF's authentication handling
2. **Reuses Login Serializer** - Returns same user structure as login endpoint for consistency
3. **No Custom Logic** - All validation handled by SimpleJWT's `IsAuthenticated` permission

### API

#### Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/v1/auth/me/` | Get current authenticated user |

#### Request/Response Examples

**Request:**
```http
GET /api/v1/auth/me/ HTTP/1.1
Host: api.altea.ch
Authorization: Bearer eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9...
```

**Response 200 (Success):**
```json
{
    "id": "550e8400-e29b-41d4-a716-446655440000",
    "email": "user@example.com",
    "first_name": "Max",
    "last_name": "Mueller",
    "profile_completed": false,
    "language": "en"
}
```

**Response 401 (Not Authenticated):**
```json
{
    "detail": "Authentication credentials were not provided."
}
```

**Response 401 (Invalid Token):**
```json
{
    "detail": "Given token not valid for any token type",
    "code": "token_not_valid",
    "messages": [
        {
            "token_class": "AccessToken",
            "token_type": "access",
            "message": "Token is invalid or expired"
        }
    ]
}
```

### HTTP Methods

| Method | Allowed | Response |
|--------|---------|----------|
| GET | Yes | 200 with user data |
| POST | No | 405 Method Not Allowed |
| PUT | No | 405 Method Not Allowed |
| PATCH | No | 405 Method Not Allowed |
| DELETE | No | 405 Method Not Allowed |

## Security

### Authentication

| Aspect | Implementation |
|--------|----------------|
| Authentication | JWT Bearer token required |
| Permission | `IsAuthenticated` - only authenticated users |
| Token Validation | SimpleJWT validates expiration, signature |

### Edge Cases Handled

| Scenario | Response |
|----------|----------|
| No Authorization header | 401 Unauthorized |
| Malformed Authorization header | 401 Unauthorized |
| Expired token | 401 Unauthorized |
| Invalid token signature | 401 Unauthorized |
| User deleted after token issued | 401 Unauthorized |
| User inactive (`is_active=False`) | 401 Unauthorized |
| User unverified (`is_verified=False`) | 200 OK (token still valid) |

## File Structure

```
apps/accounts/
├── api/
│   ├── serializers.py    # LoginUserSerializer (reused) (L186-224)
│   ├── urls.py           # me/ route (L13)
│   └── views.py          # MeAPIView (L270-297)
└── tests/
    └── test_me.py        # 44 tests
```

## Testing

### Running Tests

```bash
# All /me endpoint tests
python manage.py test apps.accounts.tests.test_me --keepdb

# With coverage
coverage run --source=apps.accounts manage.py test apps.accounts.tests.test_me --keepdb
coverage report
```

### Test Coverage

| Component | Coverage |
|-----------|----------|
| MeAPIView | 100% |

### Test Structure

| Test Class | Tests | Description |
|------------|-------|-------------|
| `MeAPIViewTests` | 4 | Basic functionality |
| `MeAPIViewEdgeCasesTests` | 11 | Deleted user, inactive, unicode, empty names |
| `MeAPIViewHTTPMethodTests` | 5 | HTTP method restrictions |
| `MeAPIViewAuthenticationTests` | 6 | Token validation scenarios |
| `MeAPIViewSecurityTests` | 4 | SQL injection, malformed tokens |
| `MeEndpointIntegrationTests` | 2 | Login → /me workflow |

### Key Test Scenarios

| Scenario | Expected Result |
|----------|-----------------|
| Valid token | 200 + user data |
| No token | 401 Unauthorized |
| Expired token | 401 Unauthorized |
| Invalid token | 401 Unauthorized |
| User deleted | 401 Unauthorized |
| User inactive | 401 Unauthorized |
| Very long name (150 chars) | 200 + truncated display |

## Performance Considerations

| Aspect | Details |
|--------|---------|
| Database Queries | 1 query for user lookup (by ID from token) |
| Caching | No caching (always returns fresh data) |
| Response Size | ~150 bytes JSON |

## Dependencies

### Internal
- `User` model from `apps/accounts`
- `LoginUserSerializer` from `apps/accounts/api/serializers`

### External
- `rest_framework_simplejwt` - Token validation
- `rest_framework` - `IsAuthenticated` permission

## Known Limitations

1. **No token refresh on /me** - Client must handle token refresh separately
2. **No rate limiting** - Protected by authentication requirement
3. **No partial data** - Returns all fields, no field selection

## Related Documentation

- [User Login](./user-login.md) - Login and token generation
- [Navigation & App Shell Feature](../../../features/navigation-app-shell/README.md) - UI documentation
