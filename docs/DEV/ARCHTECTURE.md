# Altea - System Architecture

**Version:** 1.0 | **Updated:** 2025-12-05 | **Status:** Draft

---

## 1. Overview

### 1.1 System Purpose

Altea - мобильное приложение для отслеживания восстановления от зависимостей.

| Component | Technology | Description |
|-----------|------------|-------------|
| Mobile Apps | Flutter | iOS/Android приложения (папка `mobile/`) |
| Backend API | Django REST | REST API, бизнес-логика |
| AI Engine | OpenAI GPT-4 | Персонализация, аналитика |

### 1.2 Target Users

| Role | Description |
|------|-------------|
| Patient | Отслеживание прогресса, дневник, поддержка |
| Doctor | Просмотр dashboard пациентов (read-only) |

### 1.3 High-Level Architecture

```
┌─────────────────────────────────────────────────┐
│           Mobile Apps (Flutter)                  │
│         mobile/altea_app/                        │
│   Patient UI  │  Doctor UI  │  Local Storage    │
└───────────────────────┬─────────────────────────┘
                        │ HTTPS/REST
┌───────────────────────▼─────────────────────────┐
│           Django REST Framework                  │
│     Auth  │  Business Logic  │  AI Engine       │
└───────────────────────┬─────────────────────────┘
                        │
┌───────────────────────▼─────────────────────────┐
│   PostgreSQL  │  Redis  │  OpenAI API  │  S3   │
└─────────────────────────────────────────────────┘
```

---

## 2. Technology Stack

### 2.1 Backend

| Component | Version | Purpose |
|-----------|---------|---------|
| Django | 5.0+ | Web framework |
| DRF | 3.14+ | REST API |
| PostgreSQL | 15+ | Database |
| Redis | 7.2+ | Cache, Celery broker |
| Celery | 5.3+ | Background tasks |
| Python | 3.12+ | Runtime |

> **Conventions:** [CONVENTIONS/DJANGO.md](CONVENTIONS/DJANGO.md)

### 2.2 Mobile (Flutter)

| Component | Version | Purpose |
|-----------|---------|---------|
| Flutter | 3.16+ | Cross-platform |
| Dart | 3.2+ | Language |
| Riverpod | 2.4+ | State management |
| Dio | 5.4+ | HTTP client |
| Hive | 2.2+ | Local storage |
| go_router | 13.0+ | Navigation |

> **Conventions:** [CONVENTIONS/FLUTTER.md](CONVENTIONS/FLUTTER.md)
> **Design Tokens:** [CONVENTIONS/DESIGN_TOKENS.md](CONVENTIONS/DESIGN_TOKENS.md)

### 2.3 Infrastructure

| Component | Technology |
|-----------|------------|
| Hosting | AWS / DigitalOcean |
| Database | AWS RDS PostgreSQL |
| Files | AWS S3 |
| CI/CD | GitHub Actions |
| Monitoring | Sentry |

---

## 3. Project Structure

### 3.1 Repository Layout

```
altea/
├── backend/                 # Django backend
│   ├── config/             # Settings, URLs, Celery
│   ├── apps/               # Django apps
│   ├── requirements/       # Dependencies
│   └── manage.py
│
├── mobile/                  # Flutter apps
│   └── altea_app/          # Main mobile app
│       ├── lib/
│       ├── ios/
│       ├── android/
│       └── pubspec.yaml
│
├── doc/                     # Documentation
│   ├── DEV/                # Development docs
│   │   ├── ARCHTECTURE.md
│   │   ├── SRS.md
│   │   └── CONVENTIONS/
│   └── METHODOLODY/        # Workflow
│
└── docker-compose.yml
```

### 3.2 Backend Structure

```
backend/
├── config/
│   ├── settings/
│   │   ├── base.py
│   │   ├── development.py
│   │   └── production.py
│   ├── urls.py
│   ├── urls_api.py
│   └── celery.py
│
├── apps/
│   ├── core/              # Base models, permissions, utils
│   ├── accounts/          # User, UserProfile, Auth
│   ├── addictions/        # UserAddiction, ConsumptionEvent
│   ├── assessments/       # Questionnaire, AssessmentResult
│   ├── notifications/     # Push notifications, Celery tasks
│   ├── analytics/         # Dashboard, statistics
│   ├── sharing/           # Doctor sharing
│   ├── exports/           # PDF generation
│   └── ai/                # OpenAI integration
│
└── requirements/
    ├── base.txt
    ├── development.txt
    └── production.txt
```

### 3.3 Mobile Structure

```
mobile/altea_app/lib/
├── main.dart
├── core/
│   ├── theme/            # Colors, typography, spacing
│   ├── constants/        # API, app constants
│   └── utils/            # Validators, formatters
│
├── data/
│   ├── models/           # User, Addiction, Event
│   ├── repositories/     # Auth, Addiction repos
│   └── data_sources/     # Local, Remote
│
├── domain/
│   ├── entities/
│   ├── repositories/     # Abstract interfaces
│   └── use_cases/
│
├── presentation/
│   ├── providers/        # Riverpod providers
│   ├── screens/          # auth/, dashboard/, addictions/
│   └── widgets/
│       ├── atoms/        # Buttons, inputs
│       ├── molecules/    # Cards, list items
│       └── organisms/    # Forms, lists
│
└── l10n/                 # Localization (DE, FR, IT, EN)
```

---

## 4. Django Apps

### 4.1 Apps Overview

| App | Models | Purpose |
|-----|--------|---------|
| `core` | TimeStampedModel | Base models, permissions |
| `accounts` | User, UserProfile | Authentication, profiles |
| `addictions` | UserAddiction, ConsumptionEvent, Trigger | Core tracking |
| `assessments` | Questionnaire, Question, AssessmentResult | Severity scoring |
| `notifications` | NotificationSettings, NotificationLog | Push notifications |
| `analytics` | - | Dashboard, statistics |
| `sharing` | SharedDashboard | Doctor access |
| `exports` | - | PDF reports |
| `ai` | - | OpenAI integration |

### 4.2 Key Models

```python
# All models inherit from TimeStampedModel
class TimeStampedModel(models.Model):
    created_at = models.DateTimeField(auto_now_add=True, db_index=True)
    updated_at = models.DateTimeField(auto_now=True)
    class Meta:
        abstract = True
```

**User & Profile:**
```python
class User(AbstractBaseUser):
    id = UUIDField(primary_key=True)
    email = EmailField(unique=True)  # USERNAME_FIELD
    first_name, last_name = CharField(max_length=100)
    is_verified = BooleanField(default=False)

class UserProfile(TimeStampedModel):
    user = OneToOneField(User)
    language = CharField(choices=['de','fr','it','en'])
    country = CountryField(default='CH')
    onboarding_completed = BooleanField(default=False)
    severity_score = IntegerField(null=True)
```

**Addiction Tracking:**
```python
class UserAddiction(TimeStampedModel):
    TYPES = ['alcohol', 'drugs', 'tobacco', 'gambling', 'smartphone']

    user = ForeignKey(User, related_name='addictions')
    addiction_type = CharField(choices=TYPES)
    is_primary = BooleanField(default=False)
    baseline_amount = DecimalField()
    sobriety_start_date = DateTimeField()
    current_streak_days = IntegerField(default=0)
    longest_streak_days = IntegerField(default=0)

class ConsumptionEvent(TimeStampedModel):
    addiction = ForeignKey(UserAddiction)
    event_datetime = DateTimeField()
    amount = DecimalField()
    triggers = ManyToManyField('Trigger')
    mood_before = CharField(choices=MOOD_CHOICES)
    mood_after = CharField(choices=MOOD_CHOICES)
    notes = TextField(blank=True)
```

---

## 5. API Design

### 5.1 Overview

- **Base URL:** `https://api.altea.ch/api/v1/`
- **Auth:** JWT Bearer tokens (SimpleJWT)
- **Format:** JSON
- **Docs:** `/api/v1/docs/` (Swagger)

### 5.2 Endpoints

| Endpoint | Methods | Description |
|----------|---------|-------------|
| `/auth/login/` | POST | Get JWT tokens |
| `/auth/refresh/` | POST | Refresh access token |
| `/auth/register/` | POST | User registration |
| `/accounts/profile/` | GET, PATCH | User profile |
| `/addictions/addictions/` | GET, POST | List/create addictions |
| `/addictions/addictions/{id}/` | GET, PATCH, DELETE | Manage addiction |
| `/addictions/addictions/{id}/set-primary/` | POST | Set primary |
| `/addictions/events/` | GET, POST | Log events |
| `/addictions/calendar/` | GET | Calendar data |
| `/assessments/submit/` | POST | Submit questionnaire |
| `/analytics/dashboard/` | GET | Dashboard data |
| `/analytics/statistics/` | GET | Detailed stats |
| `/sharing/create/` | POST | Create share link |
| `/exports/pdf/` | POST | Generate PDF |

### 5.3 Response Format

```json
// Success
{"id": "uuid", "field": "value", "created_at": "..."}

// Error
{"error": true, "message": "...", "status_code": 400, "details": {...}}

// Pagination
{"count": 100, "next": "...", "previous": null, "results": [...]}
```

### 5.4 Authentication Flow

```
Client                          Server
  │── POST /auth/register/ ──────>│
  │<── 201: user_id ──────────────│
  │                               │
  │── POST /auth/login/ ─────────>│
  │<── {access_token, refresh} ───│
  │                               │
  │── GET /api/v1/... ───────────>│
  │   Authorization: Bearer token │
```

---

## 6. Flutter Architecture

### 6.1 Widget Composition (Atomic Design)

```
widgets/
├── atoms/       # Button, Input, Text (StatelessWidget)
├── molecules/   # Card, ListItem (2-5 atoms)
├── organisms/   # AddictionList, EventForm (feature-specific)
└── templates/   # Layout patterns
```

| Level | State | Reusability |
|-------|-------|-------------|
| Atom | Stateless | High |
| Molecule | Stateless/Stateful | High |
| Organism | ConsumerWidget | Medium |
| Screen | ConsumerWidget | None |

### 6.2 State Management (Riverpod)

```dart
// Provider pattern
@riverpod
class AddictionsList extends _$AddictionsList {
  @override
  Future<List<UserAddiction>> build() async {
    return ref.watch(addictionRepositoryProvider).getAddictions();
  }
}

// Screen usage
class DashboardScreen extends ConsumerWidget {
  Widget build(BuildContext context, WidgetRef ref) {
    final addictions = ref.watch(addictionsListProvider);
    return addictions.when(
      data: (data) => AddictionList(addictions: data),
      loading: () => CupertinoActivityIndicator(),
      error: (e, _) => ErrorWidget(error: e),
    );
  }
}
```

### 6.3 Navigation (GoRouter)

```dart
final router = GoRouter(
  routes: [
    GoRoute(path: '/login', builder: (_, __) => LoginScreen()),
    GoRoute(path: '/dashboard', builder: (_, __) => DashboardScreen()),
    GoRoute(path: '/addictions/:id', builder: (_, state) =>
      AddictionDetailScreen(id: state.pathParameters['id']!)),
  ],
  redirect: (context, state) {
    final isLoggedIn = /* check */;
    if (!isLoggedIn && state.location != '/login') return '/login';
    return null;
  },
);
```

---

## 7. AI Integration

### 7.1 OpenAI Use Cases

| Feature | Model | Purpose |
|---------|-------|---------|
| Assessment Analysis | GPT-4 Turbo | Insights after questionnaire |
| Pattern Detection | GPT-4 Turbo | Identify relapse triggers |
| Recovery Plan | GPT-4 Turbo | Personalized recommendations |
| Motivational Content | GPT-4 Turbo | Daily messages |

### 7.2 ML (scikit-learn)

**SeverityPredictor:**
- Input: Assessment scores, demographics
- Output: Severity level, treatment intensity
- Model: RandomForestClassifier

---

## 8. Security

### 8.1 Authentication

- JWT: 1h access, 30d refresh
- Password: PBKDF2 + SHA256
- Rate limit: 5 attempts / 15 min

### 8.2 Data Protection

- TLS 1.3 (all traffic)
- AES-256 (sensitive data at rest)
- GDPR compliant

### 8.3 Permissions

| Role | Access |
|------|--------|
| Patient | Own data only |
| Doctor | Shared dashboards (read-only) |

---

## 9. Deployment

### 9.1 Environments

| Env | Database | Purpose |
|-----|----------|---------|
| Development | SQLite/PostgreSQL | Local dev |
| Staging | PostgreSQL | Testing |
| Production | AWS RDS PostgreSQL | Live |

### 9.2 Docker

```yaml
services:
  db: postgres:15
  redis: redis:7-alpine
  web: gunicorn config.wsgi
  celery: celery -A config worker
  celery-beat: celery -A config beat
  nginx: nginx:alpine (80, 443)
```

### 9.3 CI/CD

```
Push → Test → Build Docker → Deploy
```

---

## 10. Localization

| Code | Language | Region |
|------|----------|--------|
| de | Deutsch | German Switzerland |
| fr | Français | French Switzerland |
| it | Italiano | Italian Switzerland |
| en | English | Default |

**Implementation:**
- Backend: Django i18n (gettext)
- Mobile: Flutter intl (ARB files)

---

## 11. Related Documentation

| Document | Description |
|----------|-------------|
| [SRS.md](SRS.md) | Detailed requirements |
| [CONVENTIONS/DJANGO.md](CONVENTIONS/DJANGO.md) | Backend conventions |
| [CONVENTIONS/FLUTTER.md](CONVENTIONS/FLUTTER.md) | Mobile conventions |
| [CONVENTIONS/DESIGN_TOKENS.md](CONVENTIONS/DESIGN_TOKENS.md) | UI design tokens |
| [../METHODOLODY/](../METHODOLODY/) | Development workflow |

---

**Maintainer:** Development Team
