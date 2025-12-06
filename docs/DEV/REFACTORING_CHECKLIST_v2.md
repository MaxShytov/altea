# Altea - Refactoring Checklist (Enhanced)

**Version:** 2.0 | **Last Updated:** December 2025

**Purpose:** Comprehensive code review checklist for post-implementation refactoring

**Usage:** Go through each section and identify issues with severity levels:
- 🔴 **Critical** - Must fix before merge (security, data integrity, major bugs)
- 🟡 **Major** - Should fix (performance, maintainability, code quality)
- 🟢 **Minor** - Nice to have (cosmetic, minor optimizations)

---

## 1. Code Quality Basics

### 1.1 DRY (Don't Repeat Yourself)

#### ✅ Check for:

- [ ] **Code duplication** (>5 lines repeated)
  - Severity: 🟡 Major
  - Same logic in multiple places
  - Repeated validations
  - Duplicate business rules

#### 🎯 Actions:

Extract common code to:
- `apps/core/utils.py` for utility functions
- `apps/[app]/services.py` for business logic
- Base classes for shared behavior
- Mixins for reusable patterns

#### Example:

```python
# ❌ Bad: Duplication
# In views.py
if addiction.addiction_type not in ['alcohol', 'drugs', 'tobacco']:
    raise ValidationError("Invalid type")

# In services.py
if addiction.addiction_type not in ['alcohol', 'drugs', 'tobacco']:
    raise ValidationError("Invalid type")

# ✅ Good: Extracted
# In validators.py
def validate_addiction_type(addiction_type):
    valid_types = ['alcohol', 'drugs', 'tobacco', 'gambling', 'smartphone']
    if addiction_type not in valid_types:
        raise ValidationError(f"Invalid type. Must be one of: {valid_types}")
```

---

### 1.2 Naming Conventions ⭐

#### ✅ Check for:

**Variables:**
- [ ] `snake_case`, descriptive names
  - `❌ d = datetime.now()` → `✅ current_datetime = datetime.now()`
  - `❌ tmp` → `✅ temporary_event_data`
  - `❌ x, y, z` → `✅ start_date, end_date, duration`

**Functions:**
- [ ] `snake_case`, verb-based names
  - `✅ get_addictions()`, `calculate_sobriety_days()`, `validate_consumption_amount()`
  - `❌ addictions()`, `days()`, `check()`

**Classes:**
- [ ] `PascalCase`, noun-based names
  - `✅ UserAddiction`, `ConsumptionEvent`, `AddictionService`
  - `❌ user_addiction`, `event`, `service`

**Constants:**
- [ ] `UPPER_CASE`
  - `✅ MAX_SOBRIETY_STREAK`, `DEFAULT_LANGUAGE`, `ADDICTION_TYPES`
  - `❌ maxStreak`, `defaultLang`, `types`

**Boolean variables:**
- [ ] Prefixes: `is_`, `has_`, `can_`, `should_`
  - `✅ is_primary`, `has_events`, `can_edit`, `should_notify`
  - `❌ primary`, `events`, `edit`, `notify`

#### 🎯 Django-specific:

- [ ] Models: Singular nouns (`UserAddiction`, not `UserAddictions`)
- [ ] Managers: plural or descriptive (`objects`, `active_objects`)
- [ ] Querysets: verb-based methods (`with_events()`, `for_user()`, `active()`)
- [ ] Related names: plural (`user.addictions`, not `user.addiction_set`)

#### 🎯 Flutter-specific:

- [ ] Widgets: descriptive names (`AddictionCard`, not `Card`)
- [ ] Providers: ends with `Provider` (auto-generated with Riverpod)
- [ ] Private members: starts with `_` (`_apiClient`, `_fetchData()`)
- [ ] Files: `snake_case` (`addiction_list_screen.dart`, not `AddictionListScreen.dart`)

---

### 1.3 Function/Method Length ⭐

#### ✅ Check for:

- [ ] **Functions > 50 lines**
  - Severity: 🟡 Major
  - Action: Split into smaller functions
  - Extract helper methods

- [ ] **Functions > 100 lines**
  - Severity: 🔴 Critical
  - Action: Definitely refactor
  - Probably violates SRP

- [ ] **Classes > 300 lines**
  - Severity: 🟡 Major
  - Action: Consider splitting responsibilities
  - Check if doing too many things

#### 🎯 Actions:

```python
# ❌ Bad: 150-line function
def process_consumption_event(event_data):
    # Validate data (20 lines)
    # Calculate statistics (30 lines)
    # Update streaks (25 lines)
    # Send notifications (20 lines)
    # Log analytics (15 lines)
    # Update triggers (20 lines)
    # Generate recommendations (20 lines)

# ✅ Good: Split into focused functions
def process_consumption_event(event_data):
    validated_data = _validate_event_data(event_data)
    event = _create_event(validated_data)
    _update_statistics(event)
    _update_streaks(event)
    _send_notifications(event)
    _log_analytics(event)
    return event

def _validate_event_data(data): ...
def _create_event(data): ...
def _update_statistics(event): ...
```

---

### 1.4 Complexity ⭐

#### ✅ Check for:

- [ ] **Nested if-statements (>3 levels)**
  - Severity: 🟡 Major
  
  ```python
  # ❌ Bad: Deep nesting (>3 levels)
  def can_log_event(user, addiction):
      if user:
          if user.is_active:
              if user.has_addiction(addiction):
                  if addiction.is_active:
                      return True
      return False
  
  # ✅ Good: Early returns (Guard Clauses)
  def can_log_event(user, addiction):
      if not user or not user.is_active:
          return False
      if not user.has_addiction(addiction):
          return False
      if not addiction.is_active:
          return False
      return True
  
  # ✅ Even Better: Single expression
  def can_log_event(user, addiction):
      return (
          user and user.is_active and
          user.has_addiction(addiction) and
          addiction.is_active
      )
  ```

- [ ] **Long method chains**
  - Severity: 🟢 Minor
  
  ```python
  # ❌ Hard to read
  result = obj.method1().method2().method3().method4().method5()
  
  # ✅ Better: Intermediate variables
  step1 = obj.method1().method2()
  step2 = step1.method3().method4()
  result = step2.method5()
  ```

- [ ] **Complex boolean expressions**
  - Severity: 🟡 Major
  
  ```python
  # ❌ Bad: Complex condition
  if user.role == 'admin' or (user.role == 'therapist' and user.verified) or (user.role == 'patient' and user.has_permission('view_analytics') and addiction.shared_with_user(user)):
      show_analytics()
  
  # ✅ Good: Extract to method
  def can_view_analytics(user, addiction):
      if user.role == 'admin':
          return True
      if user.role == 'therapist' and user.verified:
          return True
      if user.role == 'patient':
          return user.has_permission('view_analytics') and addiction.shared_with_user(user)
      return False
  
  if can_view_analytics(user, addiction):
      show_analytics()
  ```

#### 🎯 Cyclomatic Complexity:

- [ ] Functions with complexity > 10: 🟡 Major
- [ ] Functions with complexity > 20: 🔴 Critical
- Tool: `radon cc apps/` (Python)

---

### 1.5 Comments and Documentation

#### ✅ Check for:

- [ ] **Public methods without docstrings**
  - Severity: 🟡 Major
  
  ```python
  def calculate_sobriety_duration(addiction: UserAddiction) -> timedelta:
      """
      Calculate duration since sobriety start date.
      
      Args:
          addiction: User's addiction record with sobriety_start_date
          
      Returns:
          Duration as timedelta object
          
      Raises:
          ValueError: If sobriety_start_date is in the future
      
      Example:
          >>> addiction = UserAddiction(sobriety_start_date=date(2025, 1, 1))
          >>> duration = calculate_sobriety_duration(addiction)
          >>> duration.days
          340
      """
      if addiction.sobriety_start_date > timezone.now():
          raise ValueError("Sobriety start date cannot be in the future")
      return timezone.now() - addiction.sobriety_start_date
  ```

- [ ] **Complex logic without comments**
  - Severity: 🟡 Major
  - Add inline comments explaining **WHY**, not WHAT
  
  ```python
  # ❌ Bad: Explaining WHAT (obvious)
  # Loop through addictions
  for addiction in addictions:
      # Calculate days
      days = calculate_days(addiction)
  
  # ✅ Good: Explaining WHY (non-obvious)
  # We need to recalculate streaks because timezone changes affect day boundaries
  for addiction in addictions:
      days = calculate_days(addiction)
  ```

- [ ] **Outdated comments**
  - Severity: 🟢 Minor
  - Update or remove
  
  ```python
  # ❌ Outdated
  # TODO: Add support for multiple addictions (already done!)
  
  # ✅ Remove outdated comments
  ```

- [ ] **Commented-out code**
  - Severity: 🟢 Minor
  - Remove (Git history preserves it)
  
  ```python
  # ❌ Bad
  # def old_calculate_method():
  #     return old_logic()
  
  # ✅ Good: Just delete it
  ```

#### 🎯 Type Hints (Python 3.12+):

- [ ] Add type hints for function parameters and returns
  - Severity: 🟡 Major
  
  ```python
  from __future__ import annotations
  from typing import Optional, List
  
  def get_user_addictions(
      user_id: str,
      include_inactive: bool = False
  ) -> List[UserAddiction]:
      """Get all addictions for a user."""
      queryset = UserAddiction.objects.filter(user_id=user_id)
      if not include_inactive:
          queryset = queryset.filter(is_active=True)
      return list(queryset)
  ```

---

## 2. Architecture

### 2.1 Layer Separation (Django) ⭐

#### ✅ Check for:

- [ ] **Business logic in Models**
  - Severity: 🟡 Major
  
  ```python
  # ❌ Bad: Business logic in model
  class UserAddiction(TimeStampedModel):
      def calculate_recommended_goals(self):
          # Complex AI logic, HTTP requests, etc.
          
  # ✅ Good: Business logic in service
  # apps/addictions/services.py
  def calculate_recommended_goals(addiction: UserAddiction) -> dict:
      # Complex AI logic here
      return recommendations
  ```

- [ ] **Business logic in Views**
  - Severity: 🟡 Major
  - Extract to `services.py`
  
  ```python
  # ❌ Bad: Business logic in viewset
  class AddictionViewSet(viewsets.ModelViewSet):
      def create(self, request):
          addiction = UserAddiction.objects.create(...)
          # 50 lines of business logic
          send_notification(...)
          calculate_statistics(...)
          update_recommendations(...)
  
  # ✅ Good: Thin controller
  class AddictionViewSet(viewsets.ModelViewSet):
      def create(self, request):
          serializer = self.get_serializer(data=request.data)
          serializer.is_valid(raise_exception=True)
          addiction = AddictionService.create_addiction(
              user=request.user,
              data=serializer.validated_data
          )
          return Response(self.get_serializer(addiction).data, status=201)
  ```

- [ ] **Database queries in Serializers**
  - Severity: 🟡 Major
  - Move to ViewSet with `select_related`/`prefetch_related`
  
  ```python
  # ❌ Bad: N+1 queries in serializer
  class AddictionSerializer(serializers.ModelSerializer):
      recent_events = serializers.SerializerMethodField()
      
      def get_recent_events(self, obj):
          return obj.events.all()[:5]  # Query for each addiction!
  
  # ✅ Good: Prefetch in viewset
  class AddictionViewSet(viewsets.ModelViewSet):
      def get_queryset(self):
          return UserAddiction.objects.prefetch_related(
              Prefetch('events', queryset=ConsumptionEvent.objects.all()[:5])
          )
  ```

- [ ] **HTTP logic in Services**
  - Severity: 🟡 Major
  - Services should be HTTP-agnostic (no Request/Response objects)
  
  ```python
  # ❌ Bad: HTTP-aware service
  def create_addiction(request):
      user = request.user  # HTTP dependency
      return Response(...)  # HTTP response
  
  # ✅ Good: Pure service
  def create_addiction(user: User, data: dict) -> UserAddiction:
      # No HTTP dependencies
      return UserAddiction.objects.create(user=user, **data)
  ```

#### 🎯 Proper Layer Hierarchy ⭐

```
┌─────────────────────────────────────────┐
│   Views / ViewSets                      │  ← HTTP layer only
│   - Handle requests/responses           │     (authentication, permissions)
│   - Call serializers                    │
│   - Call services                       │
└────────────────┬────────────────────────┘
                 ↓
┌─────────────────────────────────────────┐
│   Serializers                           │  ← Data transformation
│   - Validate input                      │     (JSON ↔ Python objects)
│   - Transform data                      │
│   - No business logic                   │
└────────────────┬────────────────────────┘
                 ↓
┌─────────────────────────────────────────┐
│   Services                              │  ← Business logic
│   - Orchestrate operations              │     (pure Python, testable)
│   - Call multiple models                │
│   - Handle transactions                 │
└────────────────┬────────────────────────┘
                 ↓
┌─────────────────────────────────────────┐
│   Models                                │  ← Data layer
│   - Database schema                     │     (ORM, simple properties)
│   - Simple properties                   │
│   - No complex logic                    │
└─────────────────────────────────────────┘
```

**Example structure:**

```python
# ✅ Correct separation
# views.py - HTTP layer
class AddictionViewSet(viewsets.ModelViewSet):
    def create(self, request):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        addiction = AddictionService.create_addiction(request.user, serializer.validated_data)
        return Response(self.get_serializer(addiction).data, status=201)

# serializers.py - Data transformation
class AddictionSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserAddiction
        fields = ['addiction_type', 'baseline_amount', 'sobriety_start_date']
    
    def validate_sobriety_start_date(self, value):
        if value > timezone.now():
            raise ValidationError("Cannot be in the future")
        return value

# services.py - Business logic
class AddictionService:
    @staticmethod
    def create_addiction(user: User, data: dict) -> UserAddiction:
        addiction = UserAddiction.objects.create(user=user, **data)
        NotificationService.send_addiction_created(addiction)
        AnalyticsService.track_addiction_created(user, addiction)
        return addiction

# models.py - Data layer
class UserAddiction(TimeStampedModel):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='addictions')
    addiction_type = models.CharField(max_length=20, choices=AddictionType.choices)
    
    @property
    def sobriety_days(self) -> int:
        """Simple calculated property - OK in model."""
        return (timezone.now() - self.sobriety_start_date).days
```

---

### 2.2 Dependencies

#### ✅ Check for:

- [ ] **Circular imports** ⭐
  - Severity: 🔴 Critical
  - Use `TYPE_CHECKING` or restructure
  
  ```python
  # ❌ Bad: Circular import
  # addictions/models.py
  from assessments.models import AssessmentResult
  
  # assessments/models.py
  from addictions.models import UserAddiction
  
  # ✅ Good: Using TYPE_CHECKING
  from __future__ import annotations
  from typing import TYPE_CHECKING
  
  if TYPE_CHECKING:
      from assessments.models import AssessmentResult
  
  class UserAddiction(TimeStampedModel):
      def get_assessment(self) -> 'AssessmentResult':  # String annotation
          ...
  ```

- [ ] **Tight coupling between apps**
  - Severity: 🟡 Major
  - Apps should be loosely coupled
  
  ```python
  # ❌ Bad: Direct dependency
  # addictions/services.py
  from notifications.services import NotificationService
  
  # ✅ Good: Use signals
  # addictions/signals.py
  from django.db.models.signals import post_save
  
  @receiver(post_save, sender=UserAddiction)
  def addiction_created(sender, instance, created, **kwargs):
      if created:
          # Signal emitted, notifications app can listen
          pass
  ```

- [ ] **Direct imports from other apps**
  - Severity: 🟢 Minor
  - Consider using signals or shared `core` app

---

### 2.3 Single Responsibility Principle

#### ✅ Check for:

- [ ] **Classes doing too many things**
  - Severity: 🟡 Major
  
  ```python
  # ❌ Bad: Too many responsibilities
  class AddictionService:
      def create_addiction(self): ...
      def send_notification(self): ...
      def generate_pdf_report(self): ...
      def calculate_ai_recommendations(self): ...
      def log_analytics(self): ...
  
  # ✅ Good: Separate services
  class AddictionService:
      def create_addiction(self): ...
      def update_addiction(self): ...
  
  class NotificationService:
      def send_addiction_created(self): ...
  
  class ReportService:
      def generate_pdf_report(self): ...
  
  class RecommendationService:
      def calculate_recommendations(self): ...
  ```

---

## 3. Django Backend - Models

### 3.1 Model Inheritance & Base Classes

- [ ] All models inherit from `TimeStampedModel` or `SoftDeleteModel`
- [ ] No direct inheritance from `models.Model`
- [ ] Soft-deletable models use `SoftDeleteModel` correctly
- [ ] Abstract models marked with `class Meta: abstract = True`

**Reference:** `apps/core/models.py`

**Example Issue:**
```python
# 🔴 Critical
class MyModel(models.Model):  # Should inherit TimeStampedModel
    name = models.CharField(max_length=100)
```

### 3.2 Model Fields

- [ ] All `ForeignKey` fields have `related_name`
- [ ] Choice fields use `TextChoices` enum (not tuples)
- [ ] Frequently filtered/joined fields have `db_index=True`
- [ ] User references use `settings.AUTH_USER_MODEL`
- [ ] `CharField` has explicit `max_length`
- [ ] Date/time fields have `auto_now_add` or `auto_now` where appropriate
- [ ] **No `null=True` on CharField/TextField** ⭐
  - Severity: 🟡 Major
  - Django convention: use `blank=True, default=''`

**Example Issue:**
```python
# 🟡 Major
class UserAddiction(TimeStampedModel):
    user = models.ForeignKey(User)  # Should: settings.AUTH_USER_MODEL, related_name
    addiction_type = models.CharField(max_length=20)  # Should: db_index=True
    notes = models.CharField(max_length=500, null=True)  # ❌ Should: blank=True, default=''

# ✅ Fixed
class UserAddiction(TimeStampedModel):
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='addictions'
    )
    addiction_type = models.CharField(
        max_length=20,
        choices=AddictionType.choices,
        db_index=True
    )
    notes = models.CharField(max_length=500, blank=True, default='')
```

### 3.3 Model Meta

- [ ] `verbose_name` and `verbose_name_plural` defined
- [ ] `ordering` specified (usually `['-created_at']`)
- [ ] Appropriate `unique_together` or `UniqueConstraint`
- [ ] Complex indexes defined in `indexes = []`
- [ ] No missing translations (`_()` wrapper)

**Example Issue:**
```python
# 🟡 Major
class Meta:
    # Missing verbose_name, ordering, indexes
    unique_together = ('user', 'addiction_type')

# ✅ Fixed
class Meta:
    verbose_name = _('user addiction')
    verbose_name_plural = _('user addictions')
    ordering = ['-created_at']
    unique_together = ('user', 'addiction_type')
    indexes = [
        models.Index(fields=['user', 'addiction_type']),
        models.Index(fields=['user', 'is_primary']),
    ]
```

### 3.4 Model Methods

- [ ] `__str__()` method implemented and returns meaningful string
- [ ] Properties use `@property` decorator
- [ ] Methods don't perform expensive queries (use managers/querysets)
- [ ] No business logic that belongs in services
- [ ] Validation in `clean()` method when needed

**Example Issue:**
```python
# 🟡 Major
def get_recent_events(self):
    return self.events.all()[:10]  # N+1 query risk, should be in manager

# ✅ Fixed
# In manager:
class AddictionQuerySet(models.QuerySet):
    def with_recent_events(self):
        return self.prefetch_related(
            Prefetch('events', queryset=ConsumptionEvent.objects.all()[:10])
        )
```

---

## 4. Django Backend - Serializers

### 4.1 Serializer Hierarchy

- [ ] Three serializers per model: `ListSerializer`, `DetailSerializer`, `WriteSerializer`
- [ ] All inherit from `BaseSerializer`
- [ ] Read-only fields explicitly marked
- [ ] No duplication between serializers

**Reference:** `CONVENTIONS/DJANGO.md` Section 4

**Example Issue:**
```python
# 🔴 Critical
class UserAddictionSerializer(serializers.ModelSerializer):  # No List/Detail/Write split
    class Meta:
        model = UserAddiction
        fields = '__all__'  # Should: explicit fields list
```

### 4.2 Serializer Fields

- [ ] `id`, `created_at`, `updated_at` defined in `BaseSerializer` only
- [ ] No mutable defaults (e.g., `default=[]`)
- [ ] SerializerMethodField has corresponding `get_*` method
- [ ] Nested serializers use appropriate depth
- [ ] Write-only fields marked `write_only=True`

### 4.3 Serializer Methods

- [ ] `create()` and `update()` methods handle nested data correctly
- [ ] User assignment uses `self.context['request'].user`
- [ ] Validation in `validate_*()` methods
- [ ] No database queries in serializers (use prefetch in viewset)

---

## 5. Django Backend - ViewSets

### 5.1 ViewSet Structure

- [ ] Inherits from `BaseViewSet` when appropriate
- [ ] Has `queryset`, `serializer_class` attributes
- [ ] Defines `list_serializer_class`, `write_serializer_class` when needed
- [ ] Implements `get_queryset()` for user filtering
- [ ] Proper `permission_classes` defined

### 5.2 Query Optimization

- [ ] Uses `select_related()` for ForeignKey
- [ ] Uses `prefetch_related()` for ManyToMany
- [ ] No N+1 query problems
- [ ] Filters in queryset, not in Python
- [ ] Pagination enabled

**Example Issue:**
```python
# 🔴 Critical
def get_queryset(self):
    return UserAddiction.objects.all()  # Missing select_related('user')

# ✅ Fixed
def get_queryset(self):
    return UserAddiction.objects.select_related('user').prefetch_related('events')
```

### 5.3 Custom Actions

- [ ] Custom actions use `@action` decorator
- [ ] `detail=True/False` correctly set
- [ ] HTTP method specified in `methods=[]`
- [ ] Returns proper Response object
- [ ] Has docstring explaining endpoint

### 5.4 Permissions

- [ ] ViewSet-level permissions in `permission_classes`
- [ ] Object-level permissions in custom permission class
- [ ] No permission logic in views
- [ ] User ownership checked via permissions, not in code

---

## 6. Django Backend - API Design

### 6.1 URL Structure

- [ ] All API endpoints under `/api/v1/`
- [ ] Uses Django REST Framework routers
- [ ] Custom actions follow REST conventions
- [ ] No duplicate URLs
- [ ] `app_name` defined in urls.py

### 6.2 Response Format

- [ ] Success responses follow convention: `{id, field, created_at}`
- [ ] Error responses: `{error: true, message, status_code, details}`
- [ ] Pagination format consistent
- [ ] No raw Django QuerySet returns
- [ ] Status codes correct (200, 201, 204, 400, 401, 403, 404)

### 6.3 API Versioning

- [ ] Version in URL path (`/api/v1/`)
- [ ] Version-specific serializers when needed
- [ ] No breaking changes in same version
- [ ] Deprecated endpoints documented

---

## 7. Django Backend - Security

### 7.1 Authentication & Authorization

- [ ] JWT tokens configured correctly (1h access, 30d refresh)
- [ ] All endpoints require authentication (except public ones)
- [ ] User can only access their own data
- [ ] Admin-only endpoints protected
- [ ] No hardcoded credentials

### 7.2 Data Validation

- [ ] All input validated via serializers
- [ ] No raw SQL without parameterization
- [ ] File uploads validated (type, size)
- [ ] No user input in raw queries
- [ ] CSRF protection enabled

**Example Issue:**
```python
# 🔴 Critical
User.objects.raw(f"SELECT * FROM users WHERE name='{name}'")  # SQL injection

# ✅ Fixed
User.objects.raw("SELECT * FROM users WHERE name = %s", [name])

# ✅ Best: Use ORM
User.objects.filter(name=name)
```

### 7.3 Sensitive Data

- [ ] Passwords never in plain text
- [ ] Secrets in environment variables
- [ ] No sensitive data in logs
- [ ] Personal data encrypted at rest (if required)
- [ ] GDPR compliance (data export, deletion)

### 7.4 Rate Limiting

- [ ] Rate limiting on auth endpoints (login, register)
- [ ] Throttling on expensive endpoints
- [ ] DDoS protection configured
- [ ] No unlimited file uploads

---

## 8. Django Backend - Performance

### 8.1 Database Queries

- [ ] No queries in loops (N+1 problem)
  - Severity: 🔴 Critical
  
  ```python
  # ❌ Bad: N+1 queries
  addictions = UserAddiction.objects.all()
  for addiction in addictions:
      print(addiction.user.email)  # Query for each addiction!
  
  # ✅ Good: select_related
  addictions = UserAddiction.objects.select_related('user').all()
  for addiction in addictions:
      print(addiction.user.email)  # No extra queries
  ```

- [ ] Uses `bulk_create()` for multiple inserts
  - Severity: 🔴 Critical
  
  ```python
  # ❌ Bad
  for data in event_data_list:
      ConsumptionEvent.objects.create(**data)  # N queries
  
  # ✅ Good
  events = [ConsumptionEvent(**data) for data in event_data_list]
  ConsumptionEvent.objects.bulk_create(events)  # 1 query
  ```

- [ ] Indexes on filtered fields
  - Severity: 🟡 Major

- [ ] No `len(queryset)` (use `.count()`)
  - Severity: 🟡 Major
  
  ```python
  # ❌ Bad
  if len(queryset) > 0:  # Fetches all records
  
  # ✅ Good
  if queryset.exists():  # Database-level check
  if queryset.count() > 0:  # Count query only
  ```

- [ ] Uses `only()` or `defer()` when appropriate
  - Severity: 🟢 Minor

### 8.2 Inefficient Code

- [ ] **Unnecessary computations in loops**
  - Severity: 🟡 Major
  
  ```python
  # ❌ Bad
  for event in events:
      total_days = (timezone.now() - event.addiction.sobriety_start_date).days  # Recalculated every loop
  
  # ✅ Good
  current_time = timezone.now()
  for event in events:
      total_days = (current_time - event.addiction.sobriety_start_date).days
  ```

### 8.3 Caching

- [ ] Redis cache configured
- [ ] Expensive queries cached
- [ ] Cache invalidation strategy
- [ ] No caching of user-specific data

### 8.4 Background Tasks

- [ ] Celery tasks for long operations
- [ ] No email sending in request-response cycle
- [ ] File processing in background
- [ ] Retry logic for failed tasks

**Example Issue:**
```python
# 🟡 Major
def create(self, request):
    addiction = super().create(request)
    send_email_notification(addiction)  # Should: Celery task
    return Response(...)

# ✅ Fixed
from apps.notifications.tasks import send_addiction_created_email

def create(self, request):
    addiction = super().create(request)
    send_addiction_created_email.delay(addiction.id)  # Celery task
    return Response(...)
```

---

## 9. Django Backend - Testing

### 9.1 Test Coverage

- [ ] Models have unit tests
- [ ] API endpoints have integration tests
- [ ] Authentication tested
- [ ] Permissions tested
- [ ] Edge cases covered

### 9.2 Test Quality

- [ ] Tests use factories (Factory Boy)
- [ ] Tests are isolated (no shared state)
- [ ] Fixtures in `setUp()` method
- [ ] Tests have meaningful names
- [ ] No skipped tests without reason

**Example Issue:**
```python
# 🟢 Minor
def test_1(self):  # Should: test_create_addiction_success
    pass

# ✅ Fixed
def test_create_addiction_success(self):
    """Test creating a new addiction with valid data."""
    data = {'addiction_type': 'alcohol', 'baseline_amount': 20}
    response = self.client.post(self.url, data)
    self.assertEqual(response.status_code, 201)
```

### 9.3 Test Data

- [ ] Uses factories, not fixtures
- [ ] No hardcoded test data
- [ ] Faker for realistic data
- [ ] Clean database between tests

---

## 10. Error Handling ⭐ NEW

### 10.1 Exception Handling

#### ✅ Check for:

- [ ] **Bare except clauses**
  - Severity: 🔴 Critical
  
  ```python
  # ❌ Bad: Catches everything including KeyboardInterrupt
  try:
      process_data()
  except:
      pass
  
  # ✅ Good: Specific exceptions
  try:
      process_data()
  except (ValueError, KeyError) as e:
      logger.error(f"Failed to process data: {e}")
      raise ValidationError("Invalid data format")
  ```

- [ ] **Silent failures**
  - Severity: 🔴 Critical
  
  ```python
  # ❌ Bad
  try:
      send_notification()
  except Exception:
      pass  # Silent failure!
  
  # ✅ Good
  try:
      send_notification()
  except Exception as e:
      logger.error(f"Failed to send notification: {e}")
      # Maybe retry or alert admin
  ```

- [ ] **Vague error messages**
  - Severity: 🟡 Major
  
  ```python
  # ❌ Bad
  raise ValueError("Invalid input")
  
  # ✅ Good
  raise ValueError(
      f"Consumption amount {amount} is invalid. "
      f"Expected positive number, got {type(amount).__name__}"
  )
  ```

### 10.2 Logging ⭐

#### ✅ Check for:

- [ ] **Missing logging for important operations**
  - Severity: 🟡 Major
  - Log: errors, warnings, important state changes

- [ ] **Using print() instead of logger**
  - Severity: 🟢 Minor
  
  ```python
  # ❌ Bad
  print(f"Processing addiction {addiction.id}")
  
  # ✅ Good
  logger.info(f"Processing addiction {addiction.id}", extra={'addiction_id': addiction.id})
  ```

- [ ] **Logging sensitive data**
  - Severity: 🔴 Critical
  - Never log passwords, tokens, PII
  
  ```python
  # ❌ Critical
  logger.info(f"User logged in: {user.email}, password: {password}")
  
  # ✅ Good
  logger.info(f"User logged in", extra={'user_id': user.id})
  ```

### 10.3 Validation

#### ✅ Check for:

- [ ] **Missing input validation**
  - Severity: 🔴 Critical
  - Always validate user input

- [ ] **Validation in wrong layer**
  - Severity: 🟡 Major
  - Django: Use serializers, form validation, model validation
  
  ```python
  # ✅ Good: Serializer validation
  class ConsumptionEventSerializer(serializers.ModelSerializer):
      def validate_amount(self, value):
          if value <= 0:
              raise serializers.ValidationError("Amount must be positive")
          if value > 1000:
              raise serializers.ValidationError("Amount seems unrealistic")
          return value
      
      def validate(self, attrs):
          # Cross-field validation
          if attrs['event_datetime'] > timezone.now():
              raise serializers.ValidationError("Event cannot be in the future")
          return attrs
  ```

---

## 11. Flutter - Project Structure

### 11.1 Directory Organization

- [ ] Follows Clean Architecture (core, data, domain, presentation)
- [ ] No business logic in UI layer
- [ ] Constants in `core/constants/`
- [ ] Utils in `core/utils/`
- [ ] Localization in `l10n/`

**Reference:** `CONVENTIONS/FLUTTER.md` Section 4

### 11.2 Widget Organization

- [ ] Widgets follow Atomic Design (atoms → molecules → organisms → templates → screens)
- [ ] Atoms in `widgets/atoms/`
- [ ] Molecules in `widgets/molecules/`
- [ ] Organisms in `widgets/organisms/`
- [ ] No business logic in atoms/molecules

---

## 12. Flutter - Widget Composition

### 12.1 Widget Levels

- [ ] Atoms are StatelessWidget wrapping 1 base widget
- [ ] Molecules combine 2-5 atoms, minimal state
- [ ] Organisms are feature-specific, use ConsumerWidget
- [ ] Screens use ConsumerWidget with full logic
- [ ] Templates define layout only (no state)

**Example Issue:**
```dart
// 🔴 Critical
// atoms/custom_button.dart
class CustomButton extends StatefulWidget {  // Atom should be Stateless
  @override
  Widget build(BuildContext context) {
    final data = ref.watch(apiProvider);  // No state management in atoms
  }
}
```

### 12.2 Widget Reusability

- [ ] Widgets used 3+ times are extracted
- [ ] No duplicate code in widgets
- [ ] Widgets accept parameters, not hardcoded values
- [ ] No widget > 300 lines (extract sub-widgets)

### 12.3 Widget State

- [ ] Atoms are stateless
- [ ] Minimal state in molecules
- [ ] State management only in organisms/screens
- [ ] No setState in atoms/molecules

---

## 13. Flutter - State Management (Riverpod)

### 13.1 Provider Structure

- [ ] Providers in `presentation/providers/`
- [ ] Uses `@riverpod` code generation
- [ ] Async providers return `Future<T>`
- [ ] Provider names end with `Provider` (auto-generated)

### 13.2 Provider Usage

- [ ] Screens use `ConsumerWidget` or `ConsumerStatefulWidget`
- [ ] Uses `ref.watch()` for reactive data
- [ ] Uses `ref.read()` for one-time reads
- [ ] No direct provider access in atoms/molecules
- [ ] Proper error handling with `.when()`

### 13.3 Provider Scope

- [ ] Global providers in `providers/`
- [ ] Feature providers in feature folders
- [ ] No circular dependencies
- [ ] Providers invalidate correctly

---

## 14. Flutter - Navigation (GoRouter)

### 14.1 Route Definition

- [ ] All routes in single router config
- [ ] Uses named routes when appropriate
- [ ] Path parameters for detail views
- [ ] Query parameters for filters
- [ ] Nested navigation for tabs

### 14.2 Navigation Guards

- [ ] Auth check in `redirect:`
- [ ] Onboarding check for new users
- [ ] Deep linking handled
- [ ] Back button behavior correct

---

## 15. Flutter - UI/UX (Apple HIG)

### 15.1 Typography

- [ ] Uses `AlteaTypography` constants (no custom TextStyle)
- [ ] Correct font family (SF Pro Display/Text)
- [ ] Correct font sizes (34/28/22/20/17/16/15/13/12/11pt)
- [ ] Correct line heights and letter spacing
- [ ] No hardcoded font values

**Example Issue:**
```dart
// 🟡 Major
Text('Title', style: TextStyle(fontSize: 32))  // Should: AlteaTypography.largeTitle

// ✅ Fixed
Text('Title', style: AlteaTypography.largeTitle)
```

### 15.2 Spacing

- [ ] Uses `AlteaSpacing` constants (xs, sm, md, lg, xl, xxl, xxxl)
- [ ] Based on 4pt iOS grid
- [ ] No magic numbers (e.g., `padding: 13`)
- [ ] Consistent spacing throughout app

### 15.3 Colors

- [ ] Uses `AlteaColors` constants
- [ ] iOS System Colors for semantic meanings
- [ ] Addiction type colors for consistency
- [ ] Dark mode support
- [ ] No hardcoded hex colors

### 15.4 Dimensions

- [ ] Corner radius uses `AlteaDimensions` (8/10/12/16)
- [ ] Button height = 50pt
- [ ] Input height = 44pt
- [ ] Icon sizes = 24/32pt
- [ ] Consistent component sizes

### 15.5 iOS Components

- [ ] Uses Cupertino widgets for iOS feel
- [ ] `CupertinoButton` for buttons
- [ ] `CupertinoTextField` for inputs
- [ ] `CupertinoNavigationBar` for nav
- [ ] `CupertinoActivityIndicator` for loading

---

## 16. Flutter - API Integration

### 16.1 HTTP Client (Dio)

- [ ] Dio client configured in repository
- [ ] Base URL in constants
- [ ] Auth interceptor for JWT
- [ ] Error interceptor for handling errors
- [ ] Timeout configured

### 16.2 API Response Handling

- [ ] Proper error handling (try/catch)
- [ ] Network errors caught
- [ ] 401 triggers re-authentication
- [ ] User-friendly error messages
- [ ] Loading states shown

### 16.3 Data Models

- [ ] Models in `data/models/`
- [ ] `fromJson` and `toJson` methods
- [ ] Uses json_serializable for complex models
- [ ] Immutable models (final fields)
- [ ] Null safety handled

---

## 17. Flutter - Local Storage

### 17.1 Hive Configuration

- [ ] Hive initialized in main()
- [ ] Type adapters registered
- [ ] Boxes opened/closed properly
- [ ] No sensitive data in Hive (use Secure Storage)

### 17.2 Secure Storage

- [ ] Uses flutter_secure_storage for tokens
- [ ] Uses flutter_secure_storage for passwords
- [ ] Keys prefixed (e.g., `altea_access_token`)
- [ ] No plain text sensitive data

---

## 18. Flutter - Performance

### 18.1 Build Performance

- [ ] No heavy computations in build()
- [ ] Lists use `ListView.builder` (not `ListView`)
- [ ] Images cached
- [ ] Const constructors where possible
- [ ] No unnecessary rebuilds

**Example Issue:**
```dart
// 🟡 Major
Widget build(BuildContext context) {
  final data = expensiveComputation();  // Should: in provider/useMemo
  return ListView(children: items.map(...).toList());  // Should: ListView.builder
}

// ✅ Fixed
Widget build(BuildContext context) {
  return ListView.builder(
    itemCount: items.length,
    itemBuilder: (context, index) => ItemWidget(items[index]),
  );
}
```

### 18.2 Image Optimization

- [ ] Images compressed (< 500KB)
- [ ] Uses cached_network_image
- [ ] Placeholder while loading
- [ ] Error handling for failed loads
- [ ] Multiple resolutions (@2x, @3x)

---

## 19. Flutter - Localization

### 19.1 ARB Files

- [ ] All user-facing strings in .arb files
- [ ] Keys descriptive (e.g., `loginButtonText`)
- [ ] All 4 languages (de, fr, it, en)
- [ ] Placeholders for dynamic values
- [ ] No hardcoded UI strings

### 19.2 Pluralization

- [ ] Uses plural forms correctly
- [ ] Date formatting localized
- [ ] Numbers formatted by locale
- [ ] No English-only logic

---

## 20. Security - General

### 20.1 Authentication

- [ ] JWT tokens stored securely
- [ ] Auto-logout on token expiry
- [ ] Refresh token flow implemented
- [ ] No tokens in URLs
- [ ] Session timeout configured

### 20.2 Input Validation

- [ ] All user input validated
- [ ] Email validation
- [ ] Password strength check
- [ ] Phone number format validation
- [ ] No injection vulnerabilities

### 20.3 Data Protection

- [ ] HTTPS only
- [ ] Certificate pinning (if required)
- [ ] No sensitive data in logs
- [ ] Biometric auth for sensitive actions
- [ ] Data wiped on logout

---

## 21. GDPR Compliance

### 21.1 User Rights

- [ ] User can export their data
- [ ] User can delete their account
- [ ] Data deletion cascades properly
- [ ] Privacy policy linked
- [ ] Consent collected before data use

### 21.2 Data Minimization

- [ ] Only necessary data collected
- [ ] No excessive logging
- [ ] Data retention policy implemented
- [ ] Anonymization where possible

---

## 22. Testing - Flutter

### 22.1 Widget Tests

- [ ] Critical widgets tested
- [ ] User interactions tested
- [ ] Edge cases covered
- [ ] Golden tests for visual regression

### 22.2 Integration Tests

- [ ] Key user flows tested
- [ ] Navigation tested
- [ ] API integration tested
- [ ] Error scenarios tested

---

## 23. Documentation

### 23.1 Code Comments

- [ ] Complex logic explained
- [ ] Public APIs documented
- [ ] No outdated comments
- [ ] No commented-out code

### 23.2 API Documentation

- [ ] Swagger/OpenAPI docs generated
- [ ] Endpoints documented
- [ ] Request/response examples
- [ ] Error codes documented

### 23.3 README

- [ ] Setup instructions
- [ ] Environment variables documented
- [ ] Running tests documented
- [ ] Deployment steps documented

---

## 24. Tools & Commands ⭐ NEW

### 24.1 Django Tools

**Linting:**
```bash
# pylint
pylint apps/addictions/

# flake8
flake8 apps/addictions/ --max-line-length=100

# black (formatter)
black apps/addictions/
```

**Type Checking:**
```bash
# mypy
mypy apps/addictions/
```

**Test Coverage:**
```bash
# pytest with coverage
pytest --cov=apps/addictions --cov-report=html

# Django coverage
coverage run --source='apps' manage.py test
coverage html
```

**Query Analysis:**
```bash
# Django Debug Toolbar (in settings)
INSTALLED_APPS += ['debug_toolbar']

# Check for N+1 queries
python manage.py debugsqlshell

# django-silk for profiling
pip install django-silk
```

**Security:**
```bash
# Check for security issues
python manage.py check --deploy

# bandit (security linter)
bandit -r apps/
```

### 24.2 Flutter Tools

**Linting:**
```bash
# dart analyze
flutter analyze

# custom lint rules (analysis_options.yaml)
```

**Code Generation:**
```bash
# Riverpod + json_serializable
flutter pub run build_runner build --delete-conflicting-outputs

# Watch mode
flutter pub run build_runner watch
```

**Testing:**
```bash
# Run all tests
flutter test

# Coverage
flutter test --coverage
genhtml coverage/lcov.info -o coverage/html
```

**Performance:**
```bash
# Build size analysis
flutter build apk --analyze-size

# Performance profiling
flutter run --profile
```

### 24.3 Code Quality Metrics

**Python:**
```bash
# Complexity analysis
radon cc apps/ -a -nb

# Maintainability index
radon mi apps/

# Cyclomatic complexity > 10
radon cc apps/ --min C
```

**Flutter:**
```bash
# Dart metrics
flutter pub global activate dart_code_metrics
metrics lib/

# Complexity
metrics lib/ --cyclomatic-complexity=10
```

---

## Quick Reference - Issue Severity

### 🔴 Critical (Must Fix)

- Security vulnerabilities (SQL injection, XSS, password exposure)
- Data loss risks (missing transactions, cascade issues)
- N+1 query problems (on large datasets)
- Breaking API changes
- Silent failures (bare except, no error logging)
- Circular imports
- Tests modifying production database
- Missing authentication/authorization
- Heavy computations in Flutter build()

### 🟡 Major (Should Fix)

- Convention violations (no related_name, no TimeStampedModel)
- Performance issues (missing indexes, unnecessary computations)
- Missing tests (critical paths, edge cases)
- Code duplication (>5 lines)
- Architectural violations (business logic in views, HTTP in services)
- Functions > 50 lines
- Nested if-statements >3 levels
- Missing error handling
- null=True on CharField
- Using print() instead of logger
- No type hints
- ListView without builder (Flutter)

### 🟢 Minor (Nice to Have)

- Code style inconsistencies
- Missing comments (if code is clear)
- Optimization opportunities
- Incomplete documentation
- Minor UX improvements
- Missing __str__ methods
- Long method chains
- Outdated comments
- Functions 30-50 lines
- Using const constructors

---

## Usage Instructions

### During Phase 4: Refactoring

```bash
# 1. New chat - load context
# - docs/DEV/CURRENT_TASK.md
# - docs/DEV/REFACTORING_CHECKLIST.md
# - docs/DEV/CONVENTIONS/FLUTTER.md
# - docs/DEV/CONVENTIONS/DJANGO.md
# - All changed files

# 2. Prompt Claude
"""
Проведи code review фичи: [название]

Задача: пройди по REFACTORING_CHECKLIST.md и найди проблемы.

Для каждой проблемы укажи:
- Severity (🔴/🟡/🟢)
- File + line numbers
- Problem description
- Current code
- Suggested fix
- Why it's a problem
"""

# 3. Fix issues
# - 🔴 Critical first
# - Then 🟡 Major
# - 🟢 Minor optional

# 4. Run tools
pylint apps/addictions/
pytest --cov=apps/addictions
flutter analyze
flutter test

# 5. Commit
git commit -m "refactor: [feature] - fix critical issues

- Issue #1: Add db_index to addiction_type
- Issue #2: Add related_name to ForeignKey
- Issue #3: Split serializers into List/Detail/Write
"

# 6. Update CURRENT_TASK.md
## Refactoring
- [x] Issue #1 - fixed 2025-12-06
- [x] Issue #2 - fixed 2025-12-06
- [ ] Issue #3 - planned for later
```

---

## Severity Decision Tree

```
Is it a security vulnerability? → 🔴 Critical
Is it causing data loss/corruption? → 🔴 Critical
Is it an N+1 query on large dataset? → 🔴 Critical
Is it a silent failure? → 🔴 Critical
   ↓
Does it violate core conventions? → 🟡 Major
Does it cause performance issues? → 🟡 Major
Is critical code untested? → 🟡 Major
Is there significant duplication? → 🟡 Major
   ↓
Is it a style/cosmetic issue? → 🟢 Minor
Is it a minor optimization? → 🟢 Minor
```

---

**Remember:** 
- Refactoring is iterative - don't try to fix everything at once
- Focus on 🔴 Critical issues first
- Then tackle 🟡 Major issues
- 🟢 Minor issues can wait for dedicated cleanup sprint
- Run automated tools (pylint, mypy, flutter analyze) before manual review
- Update CURRENT_TASK.md with all findings
