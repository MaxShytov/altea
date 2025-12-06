# Troubleshooting: Registration Issues

This guide helps support staff diagnose and resolve common registration problems.

---

## Quick Diagnosis Checklist

When a user reports registration issues, gather this information:

- [ ] Email address used
- [ ] Device type and OS version
- [ ] App version
- [ ] Exact error message
- [ ] Screenshot if available
- [ ] When the issue started

---

## Common Issues & Solutions

### 1. Verification Email Not Received

**Symptoms:**
- User completed registration
- No email in inbox or spam

**Diagnosis Steps:**

1. **Check user exists in database:**
   ```bash
   python manage.py shell -c "from apps.accounts.models import User; print(User.objects.filter(email__iexact='user@example.com').exists())"
   ```

2. **Check token was created:**
   ```bash
   python manage.py shell -c "from apps.accounts.models import EmailVerificationToken; print(EmailVerificationToken.objects.filter(user__email__iexact='user@example.com').order_by('-created_at').first())"
   ```

3. **Check email logs** (console backend in dev):
   - Look for "Verification email sent to:" in Django logs

**Solutions:**

| Cause | Solution |
|-------|----------|
| Email in spam | Ask user to check spam/junk folder |
| Email blocked by provider | Try alternative email address |
| Token not created | Check `RegistrationService.register_user()` logs for errors |
| Email backend misconfigured | Verify `EMAIL_BACKEND` settings |

**Resend manually:**
```python
from apps.accounts.services import EmailVerificationService
from apps.accounts.models import User

user = User.objects.get(email__iexact='user@example.com')
EmailVerificationService.send_verification(user)
```

---

### 2. "Email Already Registered" Error

**Symptoms:**
- User gets error when trying to register
- User claims they never registered

**Diagnosis Steps:**

1. **Find the account:**
   ```python
   from apps.accounts.models import User
   user = User.objects.get(email__iexact='user@example.com')
   print(f"Created: {user.date_joined}")
   print(f"Verified: {user.is_verified}")
   print(f"Last login: {user.last_login}")
   ```

2. **Check if it's a duplicate attempt:**
   - Same user trying to register twice
   - Email typo on previous registration

**Solutions:**

| Cause | Solution |
|-------|----------|
| User forgot they registered | Help them reset password |
| Unverified old account | User can resend verification |
| Different person's email | Contact original owner (privacy issue) |
| Fraud/abuse | Investigate and potentially block |

---

### 3. Verification Link Invalid/Expired

**Symptoms:**
- User clicks link and sees "Invalid verification link"
- User sees "Link expired"

**Diagnosis Steps:**

1. **Find the token:**
   ```python
   from apps.accounts.models import EmailVerificationToken

   # By token string
   token = EmailVerificationToken.objects.filter(token='TOKEN_STRING').first()
   if token:
       print(f"User: {token.user.email}")
       print(f"Created: {token.created_at}")
       print(f"Expires: {token.expires_at}")
       print(f"Used at: {token.used_at}")
       print(f"Is valid: {token.is_valid()}")
   ```

**Solutions:**

| Cause | Solution |
|-------|----------|
| Token expired (>24h) | User should request new email |
| Token already used | User is already verified - try signing in |
| Token invalidated (new one requested) | User should use latest email |
| Token doesn't exist | Likely old/test token - request new email |

---

### 4. Password Validation Errors

**Symptoms:**
- Password rejected during registration
- User unsure why password is invalid

**Common Rejection Reasons:**

| Error | Cause | Solution |
|-------|-------|----------|
| "too short" | Less than 8 characters | Use 8+ characters |
| "too similar" | Contains email/name | Don't use personal info |
| "too common" | Known weak password | Choose unique password |
| "entirely numeric" | Only numbers | Add letters |

**Test password manually:**
```python
from django.contrib.auth.password_validation import validate_password
from apps.accounts.models import User

user = User(email='test@example.com', first_name='John', last_name='Doe')
try:
    validate_password('userpassword', user=user)
    print("Password is valid")
except Exception as e:
    print(f"Invalid: {e.messages}")
```

---

### 5. Rate Limit Exceeded (429 Error)

**Symptoms:**
- User gets "Request was throttled" error
- Usually after multiple failed attempts

**Diagnosis:**

Rate limits are:
- **Registration:** 5 requests/hour per IP
- **Resend verification:** 3 requests/hour per IP

**Solutions:**

| Cause | Solution |
|-------|----------|
| Legitimate user trying too many times | Wait 1 hour |
| Multiple users on same network (office/school) | Expected behavior |
| Abuse/bot | Monitor and consider blocking |

**Note:** Rate limits reset automatically. No manual action needed.

---

### 6. App Crashes/Freezes During Registration

**Symptoms:**
- App crashes when tapping "Create Account"
- Screen freezes, never completes

**Diagnosis Steps:**

1. Get device info:
   - iOS/Android
   - OS version
   - App version

2. Check if issue is widespread or isolated

3. Check backend logs for errors at registration time

**Solutions:**

| Cause | Solution |
|-------|----------|
| Old app version | Update to latest |
| Device compatibility | Check minimum requirements |
| Backend error | Check Django error logs |
| Network timeout | Check user's internet connection |

---

## Backend Diagnostics

### Check Recent Registrations

```python
from apps.accounts.models import User
from django.utils import timezone
from datetime import timedelta

recent = User.objects.filter(
    date_joined__gte=timezone.now() - timedelta(hours=24)
).order_by('-date_joined')

for u in recent[:10]:
    print(f"{u.email} | Verified: {u.is_verified} | {u.date_joined}")
```

### Check Verification Token Status

```python
from apps.accounts.models import EmailVerificationToken
from django.utils import timezone

# All tokens for a user
tokens = EmailVerificationToken.objects.filter(
    user__email__iexact='user@example.com'
).order_by('-created_at')

for t in tokens:
    status = "VALID" if t.is_valid() else ("USED" if t.used_at else "EXPIRED")
    print(f"{t.token[:20]}... | {status} | Created: {t.created_at}")
```

### Manually Verify User (Emergency Only)

Use only when email system is broken and user is confirmed legitimate:

```python
from apps.accounts.models import User

user = User.objects.get(email__iexact='user@example.com')
user.is_verified = True
user.save(update_fields=['is_verified'])
print(f"User {user.email} manually verified")
```

**Document this action in support ticket!**

---

## Escalation Criteria

Escalate to engineering if:

- [ ] Multiple users affected by same issue
- [ ] Email service appears down
- [ ] Errors in Django logs indicate system problem
- [ ] Rate limiting seems incorrect
- [ ] Security concern (fraud, abuse, potential breach)

---

## Related Documentation

- [User Guide: Registration](/docs/user-guides/en/mobile/registration.md)
- [FAQ: Registration](/docs/support/faqs/registration.md)
- [Technical: User Registration](/docs/architecture/django-backend/workflows/user-registration.md)

---

*Last updated: December 2025*
