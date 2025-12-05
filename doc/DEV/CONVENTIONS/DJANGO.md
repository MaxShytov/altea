# Django REST API Conventions - Altea

**Version:** 1.0 | **Last Updated:** December 2025

---

## 1. Architecture Overview

**Tech Stack:** Django 5.0+, DRF 3.14+, PostgreSQL, Redis, Celery, JWT (SimpleJWT), drf-spectacular

**Principles:** RESTful, Consistent, Versioned (`/api/v1/`), Documented, Secure, Performant

---

## 2. Project Structure

```
apps/
├── core/           # TimeStampedModel, BaseSerializer, BaseViewSet, permissions
├── accounts/       # User, UserProfile, Auth
├── addictions/     # UserAddiction, ConsumptionEvent
├── assessments/    # Questionnaire, AssessmentResult, AI services
└── notifications/  # Push notifications, Celery tasks
```

---

## 3. Model Conventions

**ALL models MUST inherit from `TimeStampedModel`:**

```python
# apps/core/models.py
class TimeStampedModel(models.Model):
    created_at = models.DateTimeField(auto_now_add=True, db_index=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True
        ordering = ['-created_at']

class SoftDeleteModel(TimeStampedModel):
    is_active = models.BooleanField(default=True, db_index=True)
    deleted_at = models.DateTimeField(null=True, blank=True)

    objects = models.Manager()
    active_objects = ActiveManager()

    class Meta:
        abstract = True

    def delete(self, hard=False, *args, **kwargs):
        if hard:
            super().delete(*args, **kwargs)
        else:
            self.is_active = False
            self.deleted_at = timezone.now()
            self.save()
```

### Model Pattern

```python
class UserAddiction(TimeStampedModel):
    class AddictionType(models.TextChoices):
        ALCOHOL = 'alcohol', _('Alcohol')
        TOBACCO = 'tobacco', _('Tobacco')

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='addictions'
    )
    addiction_type = models.CharField(max_length=20, choices=AddictionType.choices, db_index=True)
    sobriety_start_date = models.DateTimeField(db_index=True)

    class Meta:
        verbose_name = _('user addiction')
        verbose_name_plural = _('user addictions')
        unique_together = ('user', 'addiction_type')
        indexes = [models.Index(fields=['user', 'addiction_type'])]

    def __str__(self):
        return f"{self.user.email} - {self.get_addiction_type_display()}"
```

### Model Checklist

- Inherit from `TimeStampedModel` or `SoftDeleteModel`
- Add `verbose_name` and `verbose_name_plural`
- Use `TextChoices` for choice fields
- Add `db_index=True` for filtered/joined fields
- Use `related_name` for all ForeignKeys
- Implement `__str__()` method
- Use `settings.AUTH_USER_MODEL` for User references

---

## 4. Serializer Conventions

### Base Serializers

```python
# apps/core/serializers.py
class BaseSerializer(serializers.ModelSerializer):
    id = serializers.UUIDField(read_only=True)
    created_at = serializers.DateTimeField(read_only=True)
    updated_at = serializers.DateTimeField(read_only=True)
```

### Serializer Pattern (List / Detail / Write)

```python
class UserAddictionListSerializer(BaseSerializer):
    """Lightweight for list views."""
    icon = serializers.CharField(source='get_icon', read_only=True)

    class Meta:
        model = UserAddiction
        fields = ['id', 'addiction_type', 'icon', 'is_primary', 'created_at']

class UserAddictionDetailSerializer(BaseSerializer):
    """Full serializer for detail views."""
    recent_events = serializers.SerializerMethodField()

    class Meta:
        model = UserAddiction
        fields = ['id', 'addiction_type', 'baseline_amount', 'recent_events', 'created_at', 'updated_at']
        read_only_fields = ['current_streak_days']

    def get_recent_events(self, obj):
        return ConsumptionEventSerializer(obj.events.all()[:5], many=True).data

class UserAddictionWriteSerializer(BaseSerializer):
    """For create/update operations."""
    class Meta:
        model = UserAddiction
        fields = ['addiction_type', 'baseline_amount', 'sobriety_start_date', 'is_primary']

    def create(self, validated_data):
        validated_data['user'] = self.context['request'].user
        return super().create(validated_data)
```

### Serializer Patterns

| Pattern | When to Use |
|---------|-------------|
| `ListSerializer` | GET list - minimal fields |
| `DetailSerializer` | GET detail - all fields, nested data |
| `WriteSerializer` | POST/PUT/PATCH - validation |

---

## 5. ViewSet Conventions

### Base ViewSet

```python
# apps/core/views.py
class BaseViewSet(viewsets.ModelViewSet):
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        queryset = super().get_queryset()
        if hasattr(queryset.model, 'user'):
            return queryset.filter(user=self.request.user)
        return queryset

    def get_serializer_class(self):
        if self.action == 'list':
            return getattr(self, 'list_serializer_class', self.serializer_class)
        elif self.action in ['create', 'update', 'partial_update']:
            return getattr(self, 'write_serializer_class', self.serializer_class)
        return self.serializer_class
```

### ViewSet Pattern

```python
class UserAddictionViewSet(BaseViewSet):
    queryset = UserAddiction.objects.select_related('user').all()
    serializer_class = UserAddictionDetailSerializer
    list_serializer_class = UserAddictionListSerializer
    write_serializer_class = UserAddictionWriteSerializer
    filter_backends = [DjangoFilterBackend]
    filterset_class = UserAddictionFilterSet

    def get_queryset(self):
        return super().get_queryset().filter(user=self.request.user, is_active=True)

    @action(detail=True, methods=['post'])
    def set_primary(self, request, pk=None):
        """POST /api/v1/addictions/{id}/set-primary/"""
        addiction = self.get_object()
        UserAddiction.objects.filter(user=request.user, is_primary=True).update(is_primary=False)
        addiction.is_primary = True
        addiction.save()
        return Response(self.get_serializer(addiction).data)

    @action(detail=False, methods=['get'])
    def statistics(self, request):
        """GET /api/v1/addictions/statistics/"""
        addictions = self.get_queryset()
        return Response({
            'total_addictions': addictions.count(),
            'total_clean_days': sum(a.current_streak_days for a in addictions),
        })
```

### Custom Actions

```python
@action(detail=True, methods=['post'])   # POST /api/v1/resource/{id}/action/
@action(detail=False, methods=['get'])   # GET /api/v1/resource/action/
```

---

## 6. URL Configuration

```python
# apps/addictions/urls.py
app_name = 'addictions'
router = DefaultRouter()
router.register(r'addictions', views.UserAddictionViewSet, basename='addiction')
router.register(r'events', views.ConsumptionEventViewSet, basename='event')
urlpatterns = [path('', include(router.urls))]

# config/urls_api.py
urlpatterns = [
    path('auth/login/', TokenObtainPairView.as_view()),
    path('auth/refresh/', TokenRefreshView.as_view()),
    path('schema/', SpectacularAPIView.as_view()),
    path('docs/', SpectacularSwaggerView.as_view(url_name='schema')),
    path('accounts/', include('apps.accounts.urls')),
    path('addictions/', include('apps.addictions.urls')),
]

# config/urls.py
urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/v1/', include('config.urls_api')),
]
```

---

## 7. Authentication & Permissions

### Settings

```python
REST_FRAMEWORK = {
    'DEFAULT_AUTHENTICATION_CLASSES': ['rest_framework_simplejwt.authentication.JWTAuthentication'],
    'DEFAULT_PERMISSION_CLASSES': ['rest_framework.permissions.IsAuthenticated'],
    'DEFAULT_PAGINATION_CLASS': 'rest_framework.pagination.PageNumberPagination',
    'PAGE_SIZE': 20,
}

SIMPLE_JWT = {
    'ACCESS_TOKEN_LIFETIME': timedelta(hours=1),
    'REFRESH_TOKEN_LIFETIME': timedelta(days=30),
    'ROTATE_REFRESH_TOKENS': True,
    'AUTH_HEADER_TYPES': ('Bearer',),
}
```

### Custom Permissions

```python
# apps/core/permissions.py
class IsOwner(permissions.BasePermission):
    def has_object_permission(self, request, view, obj):
        return hasattr(obj, 'user') and obj.user == request.user

class IsOwnerOrReadOnly(permissions.BasePermission):
    def has_object_permission(self, request, view, obj):
        if request.method in permissions.SAFE_METHODS:
            return True
        return hasattr(obj, 'user') and obj.user == request.user

# Usage
class MyViewSet(viewsets.ModelViewSet):
    permission_classes = [IsAuthenticated, IsOwner]
```

---

## 8. API Versioning

```python
REST_FRAMEWORK = {
    'DEFAULT_VERSIONING_CLASS': 'rest_framework.versioning.URLPathVersioning',
    'DEFAULT_VERSION': 'v1',
    'ALLOWED_VERSIONS': ['v1', 'v2'],
}

# Version-specific serializers
class UserAddictionViewSet(viewsets.ModelViewSet):
    def get_serializer_class(self):
        if self.request.version == 'v2':
            return UserAddictionSerializerV2
        return UserAddictionSerializerV1
```

---

## 9. Error Handling

```python
# apps/core/exceptions.py
def custom_exception_handler(exc, context):
    response = exception_handler(exc, context)
    if response is not None:
        response.data = {
            'error': True,
            'message': str(exc),
            'status_code': response.status_code,
            'details': response.data
        }
    return response

# settings.py
REST_FRAMEWORK = {
    'EXCEPTION_HANDLER': 'apps.core.exceptions.custom_exception_handler',
}
```

**Response format:** `{error: true, message: "...", status_code: 400, details: {...}}`

---

## 10. Testing

### Structure

```
apps/myapp/tests/
├── factories.py      # Factory Boy
├── test_models.py
├── test_views.py     # API tests
└── test_services.py
```

### API Tests

```python
class UserAddictionViewSetTest(APITestCase):
    def setUp(self):
        self.user = UserFactory()
        self.client.force_authenticate(user=self.user)
        self.addiction = UserAddictionFactory(user=self.user)

    def test_list_addictions(self):
        response = self.client.get(reverse('addictions:addiction-list'))
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_create_addiction(self):
        data = {'addiction_type': 'tobacco', 'baseline_amount': 20, 'sobriety_start_date': '2025-12-01T00:00:00Z'}
        response = self.client.post(reverse('addictions:addiction-list'), data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_unauthorized_access(self):
        self.client.force_authenticate(user=None)
        response = self.client.get(reverse('addictions:addiction-list'))
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
```

### Factory Pattern

```python
class UserAddictionFactory(DjangoModelFactory):
    class Meta:
        model = UserAddiction

    user = factory.SubFactory(UserFactory)
    addiction_type = 'alcohol'
    sobriety_start_date = factory.LazyFunction(lambda: datetime.now() - timedelta(days=7))
```

---

## Quick Reference

### New API Endpoint Checklist

- Create model (inherit TimeStampedModel)
- Create serializers (List, Detail, Write)
- Create ViewSet with permissions
- Add URL router
- Add filtering (django-filter)
- Write tests
- Test with Swagger UI

### Common Patterns

```python
# Queryset optimization
queryset = Model.objects.select_related('fk').prefetch_related('m2m')

# Filtering
class MyFilterSet(filters.FilterSet):
    search = filters.CharFilter(field_name='name', lookup_expr='icontains')

# Pagination
class CustomPagination(PageNumberPagination):
    page_size = 20
    max_page_size = 100
```
