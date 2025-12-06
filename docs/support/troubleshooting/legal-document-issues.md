# Troubleshooting: Legal Document Issues

This guide helps support staff diagnose and resolve issues related to Terms of Service and Privacy Policy.

---

## Quick Diagnosis Checklist

When a user reports legal document issues, gather:

- [ ] User email address
- [ ] Device type and app version
- [ ] What they were trying to do
- [ ] Exact error message or behavior
- [ ] Screenshot if available

---

## Common Issues & Solutions

### 1. Legal Documents Not Loading

**Symptoms:**
- Blank page when viewing Terms/Privacy
- "Document not found" error
- Loading spinner that never completes

**Diagnosis Steps:**

1. **Check active documents exist:**
   ```python
   from apps.core.models import LegalDocument

   terms = LegalDocument.get_active('terms')
   privacy = LegalDocument.get_active('privacy')

   print(f"Terms: {terms}")
   print(f"Privacy: {privacy}")
   ```

2. **Check API response:**
   ```bash
   curl http://localhost:8000/api/v1/legal/terms/
   curl http://localhost:8000/api/v1/legal/privacy/
   ```

3. **Check web pages:**
   - Visit `/legal/terms/`
   - Visit `/legal/privacy/`

**Solutions:**

| Cause | Solution |
|-------|----------|
| No active documents | Run seed command or create in admin |
| Database issue | Check migrations applied |
| Network issue (mobile) | User should check internet connection |
| App cache | User should force close and reopen app |

**Seed documents:**
```bash
python manage.py seed_legal_documents
```

---

### 2. User Can't Accept Updated Terms

**Symptoms:**
- App keeps asking to accept terms
- "Accept" button doesn't work
- Loop back to acceptance screen

**Diagnosis Steps:**

1. **Check user's accepted versions:**
   ```python
   from apps.accounts.models import User

   user = User.objects.get(email__iexact='user@example.com')
   print(f"Terms accepted: {user.terms_version_accepted}")
   print(f"Privacy accepted: {user.privacy_version_accepted}")
   print(f"Accepted at: {user.terms_accepted_at}")
   ```

2. **Check current active versions:**
   ```python
   from apps.core.models import LegalDocument

   terms = LegalDocument.get_active('terms')
   privacy = LegalDocument.get_active('privacy')

   print(f"Current terms version: {terms.version if terms else None}")
   print(f"Current privacy version: {privacy.version if privacy else None}")
   ```

3. **Compare versions:**
   - Do user's accepted versions match current active versions?

**Solutions:**

| Cause | Solution |
|-------|----------|
| API error on accept | Check Django logs for errors |
| Network timeout | User should retry |
| Version mismatch | Manually update user's accepted version |
| Multiple active documents (bug) | Ensure only one active per type |

**Manually update acceptance:**
```python
from apps.accounts.models import User
from django.utils import timezone

user = User.objects.get(email__iexact='user@example.com')
user.terms_version_accepted = '1.0'  # Current active version
user.privacy_version_accepted = '1.0'
user.terms_accepted_at = timezone.now()
user.save()
```

---

### 3. Wrong Document Version Showing

**Symptoms:**
- Old version of terms displayed
- Content doesn't match what admin published

**Diagnosis Steps:**

1. **Check which documents are active:**
   ```python
   from apps.core.models import LegalDocument

   all_docs = LegalDocument.objects.all().order_by('document_type', '-version')
   for doc in all_docs:
       status = "ACTIVE" if doc.is_active else "inactive"
       print(f"{doc.document_type} v{doc.version} - {status}")
   ```

2. **Check for multiple active documents (should not happen):**
   ```python
   from apps.core.models import LegalDocument

   # Should return max 1 per type
   active_terms = LegalDocument.objects.filter(document_type='terms', is_active=True)
   print(f"Active terms count: {active_terms.count()}")
   ```

**Solutions:**

| Cause | Solution |
|-------|----------|
| New version not set as active | Activate in admin panel |
| Multiple active (data issue) | Deactivate extras |
| Cache issue | Clear Django cache |
| CDN cache (if applicable) | Purge CDN cache |

**Fix multiple active documents:**
```python
from apps.core.models import LegalDocument

# Keep only latest version active for terms
latest_terms = LegalDocument.objects.filter(
    document_type='terms',
    is_active=True
).order_by('-effective_date').first()

if latest_terms:
    # Deactivate all others
    LegalDocument.objects.filter(
        document_type='terms',
        is_active=True
    ).exclude(pk=latest_terms.pk).update(is_active=False)
```

---

### 4. "Check for Updates" Always Returns True

**Symptoms:**
- App constantly prompts for legal acceptance
- `needs_terms_update` or `needs_privacy_update` always true

**Diagnosis Steps:**

1. **Check user's stored versions:**
   ```python
   from apps.accounts.models import User

   user = User.objects.get(email__iexact='user@example.com')
   print(f"Stored terms version: '{user.terms_version_accepted}'")
   print(f"Stored privacy version: '{user.privacy_version_accepted}'")
   ```

2. **Check for empty/null values:**
   - Empty string `''` is different from actual version `'1.0'`

3. **Test the endpoint directly:**
   ```bash
   curl -H "Authorization: Bearer <token>" \
        http://localhost:8000/api/v1/legal/check-updates/
   ```

**Solutions:**

| Cause | Solution |
|-------|----------|
| User never accepted (new user) | User should accept documents |
| Empty string stored | Update to actual version |
| Version format mismatch | Ensure consistent versioning |
| Registration didn't save versions | Bug - check registration flow |

---

### 5. Legal Page Links Don't Open (Mobile)

**Symptoms:**
- Tapping "Terms of Service" does nothing
- Browser doesn't open
- App crashes when opening legal pages

**Diagnosis Steps:**

1. Check device/OS version
2. Check if `url_launcher` package is properly configured
3. Test URL directly in device browser

**Solutions:**

| Cause | Solution |
|-------|----------|
| url_launcher not configured | Check iOS Info.plist / Android manifest |
| Invalid URL | Check `EnvConfig.termsUrl` and `privacyUrl` |
| No browser on device | Edge case - use webview fallback |
| Old app version | Update app |

---

## Admin Panel Operations

### Creating a New Document Version

1. Go to **Admin > Core > Legal documents**
2. Click **Add Legal Document**
3. Fill in:
   - **Document type:** terms or privacy
   - **Version:** New version number (e.g., "2.0")
   - **Title:** "Terms of Service" or "Privacy Policy"
   - **Content:** Full HTML content
   - **Effective date:** When this version takes effect
   - **Is active:** Check to make this the current version
4. Click **Save**

**Important:** Setting `is_active=True` automatically deactivates previous versions.

### Viewing Document History

```python
from apps.core.models import LegalDocument

# All versions of terms
terms_history = LegalDocument.objects.filter(
    document_type='terms'
).order_by('-effective_date')

for doc in terms_history:
    status = "ACTIVE" if doc.is_active else "inactive"
    print(f"v{doc.version} ({doc.effective_date}) - {status}")
```

### Checking Who Accepted Which Version

```python
from apps.accounts.models import User
from django.db.models import Count

# Distribution of accepted terms versions
versions = User.objects.values('terms_version_accepted').annotate(
    count=Count('id')
).order_by('-count')

for v in versions:
    print(f"v{v['terms_version_accepted'] or 'None'}: {v['count']} users")
```

---

## API Diagnostics

### Test All Legal Endpoints

```bash
# List documents (public)
curl http://localhost:8000/api/v1/legal/

# Get terms (public)
curl http://localhost:8000/api/v1/legal/terms/

# Get privacy (public)
curl http://localhost:8000/api/v1/legal/privacy/

# Check updates (requires auth)
curl -H "Authorization: Bearer <token>" \
     http://localhost:8000/api/v1/legal/check-updates/

# Accept documents (requires auth)
curl -X POST \
     -H "Authorization: Bearer <token>" \
     -H "Content-Type: application/json" \
     -d '{"terms_version": "1.0", "privacy_version": "1.0"}' \
     http://localhost:8000/api/v1/legal/accept/
```

---

## Escalation Criteria

Escalate to engineering if:

- [ ] Documents missing after seed command
- [ ] Multiple active documents per type (data integrity issue)
- [ ] Accept endpoint consistently failing
- [ ] Legal content not rendering correctly
- [ ] Compliance concern (wrong content showing)

---

## Related Documentation

- [User Guide: Legal Documents](/docs/user-guides/en/mobile/legal-documents.md)
- [FAQ: Legal Documents](/docs/support/faqs/legal-documents.md)
- [Technical: Legal Documents](/docs/architecture/django-backend/workflows/legal-documents.md)

---

*Last updated: December 2025*
