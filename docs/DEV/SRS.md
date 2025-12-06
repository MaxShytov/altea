# Software Requirements Specification (SRS)
## Addiction Recovery App - MVP v1.0

**Версия документа:** 1.0  
**Дата:** 05 декабря 2025  
**Статус:** Draft  
**Автор:** Development Team

---

## 📋 Содержание

1. [Введение](#1-введение)
2. [Общее описание системы](#2-общее-описание-системы)
3. [Функциональные требования](#3-функциональные-требования)
4. [Нефункциональные требования](#4-нефункциональные-требования)
5. [Технические требования](#5-технические-требования)
6. [AI/ML Компоненты](#6-aiml-компоненты)
7. [API Спецификация](#7-api-спецификация)
8. [UI/UX Требования](#8-uiux-требования)
9. [Безопасность и Privacy](#9-безопасность-и-privacy)
10. [Тестирование](#10-тестирование)
11. [Deployment](#11-deployment)

---

## 1. Введение

### 1.1 Цель документа
Данный документ определяет требования к разработке MVP версии мобильного приложения для отслеживания и поддержки процесса восстановления от различных типов зависимостей.

### 1.2 Область применения
Приложение предназначено для:
- Пациентов с различными видами зависимостей
- Врачей и терапевтов, ведущих пациентов
- Работы на территории Швейцарии (основной рынок)

### 1.3 Целевая аудитория документа
- Разработчики (Backend/Frontend/Mobile)
- UI/UX дизайнеры
- QA инженеры
- Product Owner
- Медицинские консультанты

### 1.4 Определения и аббревиатуры

| Термин | Описание |
|--------|----------|
| MVP | Minimum Viable Product - минимально жизнеспособный продукт |
| CBT | Cognitive Behavioral Therapy - когнитивно-поведенческая терапия |
| GDPR | General Data Protection Regulation |
| HIG | Human Interface Guidelines (Apple) |
| PHI | Protected Health Information |
| E2EE | End-to-End Encryption |

---

## 2. Общее описание системы

### 2.1 Архитектура системы

```
┌─────────────────────────────────────────────────────────────┐
│                     Mobile App (Flutter)                     │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐      │
│  │   Patient    │  │   Doctor     │  │    Local     │      │
│  │     UI       │  │     UI       │  │   Storage    │      │
│  └──────────────┘  └──────────────┘  └──────────────┘      │
└─────────────────────────────────────────────────────────────┘
                            ↕ HTTPS/REST API
┌─────────────────────────────────────────────────────────────┐
│                   Django REST Framework                      │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐      │
│  │     Auth     │  │   Business   │  │      AI      │      │
│  │    Layer     │  │    Logic     │  │    Engine    │      │
│  └──────────────┘  └──────────────┘  └──────────────┘      │
└─────────────────────────────────────────────────────────────┘
                            ↕
┌─────────────────────────────────────────────────────────────┐
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐      │
│  │  PostgreSQL  │  │    Redis     │  │   OpenAI     │      │
│  │   Database   │  │    Cache     │  │     API      │      │
│  └──────────────┘  └──────────────┘  └──────────────┘      │
└─────────────────────────────────────────────────────────────┘
```

### 2.2 Основные компоненты

#### 2.2.1 Mobile Application (Flutter)
- **Platform:** iOS 14+, Android 10+
- **Language:** Dart 3.0+
- **State Management:** Riverpod/Bloc
- **Local Storage:** Hive/SQLite
- **Network:** Dio + Retrofit

#### 2.2.2 Backend API (Django)
- **Framework:** Django 5.0+
- **API:** Django REST Framework 3.14+
- **Database:** PostgreSQL 15+
- **Cache:** Redis 7.2+
- **Task Queue:** Celery + Redis

#### 2.2.3 AI/ML Layer
- **Primary:** OpenAI API (GPT-4)
- **ML Framework:** scikit-learn
- **Analytics:** Custom scoring algorithms

---

## 3. Функциональные требования

### 3.1 Управление пользователями

####  ✅ FR-1.1: Регистрация пользователя

**Приоритет:** CRITICAL  
**Story Points:** 5

**Описание:**
Новый пользователь должен иметь возможность зарегистрироваться в приложении.

**Acceptance Criteria:**
```gherkin
Feature: User Registration

Scenario: Successful registration
  Given user opens registration screen
  When user enters valid email "user@example.com"
  And user enters password with 8+ characters
  And user confirms password
  And user accepts Terms & Conditions
  And user taps "Create Account"
  Then account is created
  And verification email is sent
  And user is redirected to onboarding

Scenario: Duplicate email
  Given user with email "existing@example.com" already exists
  When user tries to register with same email
  Then error message "Email already registered" is shown
  And user remains on registration screen
```

**Поля формы:**
- Email (required, unique)
- Password (required, min 8 chars, must include letter + number)
- Password confirmation (required, must match)
- First name (required)
- Last name (required)
- Terms acceptance (required checkbox)

**Backend endpoints:**
```python
POST /api/v1/auth/register/
{
    "email": "string",
    "password": "string",
    "password_confirm": "string",
    "first_name": "string",
    "last_name": "string",
    "terms_accepted": boolean
}

Response 201:
{
    "user_id": "uuid",
    "email": "string",
    "message": "Verification email sent"
}
```

---

#### FR-1.2: Авторизация

**Приоритет:** CRITICAL  
**Story Points:** 3

**Acceptance Criteria:**
```gherkin
Scenario: Successful login
  Given registered user exists
  When user enters correct email and password
  Then user is authenticated
  And JWT token is issued
  And user is redirected to main screen

Scenario: Failed login - wrong credentials
  When user enters wrong password
  Then error "Invalid credentials" is shown
  And user remains on login screen
  And attempt is logged

Scenario: Account not verified
  Given user has not verified email
  When user tries to login
  Then error "Please verify your email" is shown
  And option to resend verification is available
```

**Backend endpoints:**
```python
POST /api/v1/auth/login/
{
    "email": "string",
    "password": "string"
}

Response 200:
{
    "access_token": "string",
    "refresh_token": "string",
    "user": {
        "id": "uuid",
        "email": "string",
        "first_name": "string",
        "last_name": "string",
        "profile_completed": boolean,
        "language": "string"
    }
}
```

---

#### FR-1.3: Профиль пользователя

**Приоритет:** HIGH
**Story Points:** 5

> **TODO (from FR-1.2):** После реализации `UserProfile`, обновить `LoginUserSerializer` в `apps/accounts/api/serializers.py` для чтения `profile_completed` из `UserProfile.onboarding_completed` и `language` из `UserProfile.language` (сейчас возвращаются заглушки).

> **TODO (from FR-1.2 Flutter):** Настроить локализацию (l10n) во Flutter приложении. Сейчас строки захардкодены на английском в `LoginScreen` и `RegistrationScreen`. Необходимо:
> - Добавить `flutter_localizations` в `pubspec.yaml`
> - Создать ARB файлы: `lib/l10n/app_en.arb`, `app_de.arb`, `app_fr.arb`, `app_it.arb`
> - Настроить `MaterialApp.localizationsDelegates` и `supportedLocales`
> - Заменить hardcoded строки на `AppLocalizations.of(context)!.keyName`

**Поля профиля:**
```python
class UserProfile(models.Model):
    user = OneToOneField(User)
    date_of_birth = DateField(null=True)
    gender = CharField(choices=GENDER_CHOICES, null=True)
    country = CountryField(default='CH')
    language = CharField(
        choices=[('de', 'Deutsch'), ('fr', 'Français'), 
                 ('it', 'Italiano'), ('en', 'English')],
        default='en'
    )
    phone = CharField(validators=[validate_swiss_phone], blank=True)
    profile_picture = ImageField(upload_to='profiles/', null=True)
    onboarding_completed = BooleanField(default=False)
    severity_score = IntegerField(null=True)  # From AI assessment
    created_at = DateTimeField(auto_now_add=True)
    updated_at = DateTimeField(auto_now=True)
```

**API endpoints:**
```python
GET /api/v1/users/profile/
PUT /api/v1/users/profile/
PATCH /api/v1/users/profile/
```

---

### 3.2 Онбординг и AI-персонализация

#### FR-2.1: Выбор языка интерфейса

**Приоритет:** CRITICAL  
**Story Points:** 2

**Acceptance Criteria:**
```gherkin
Scenario: Language selection on first launch
  Given user opens app for the first time
  When welcome screen is shown
  Then 4 language options are displayed: DE, FR, IT, EN
  And user can select preferred language
  And interface switches to selected language immediately
  And language preference is saved
```

**Supported languages:**
- 🇩🇪 Deutsch (German)
- 🇫🇷 Français (French)
- 🇮🇹 Italiano (Italian)
- 🇬🇧 English

**Implementation:**
```dart
// Flutter - i18n setup
dependencies:
  flutter_localizations:
    sdk: flutter
  intl: ^0.18.0

// Language files structure
lib/
  l10n/
    app_de.arb
    app_fr.arb
    app_it.arb
    app_en.arb
```

---

#### FR-2.2: Тест на тяжесть зависимости

**Приоритет:** CRITICAL  
**Story Points:** 13

**Описание:**
Адаптивный опросник для оценки severity зависимости с использованием стандартизированных инструментов.

**Questionnaire structure:**

```yaml
Assessment Tools:
  - AUDIT (Alcohol Use Disorders Identification Test) - 10 вопросов
  - DAST-10 (Drug Abuse Screening Test) - 10 вопросов  
  - FTND (Fagerström Test) - 6 вопросов для табака
  - PGSI (Problem Gambling Severity Index) - 9 вопросов
  - Custom для смартфон-зависимости - 8 вопросов

Scoring:
  Low severity: 0-33%
  Moderate severity: 34-66%
  High severity: 67-100%
```

**Example questions (AUDIT):**
```json
{
  "questions": [
    {
      "id": "audit_q1",
      "type": "alcohol",
      "text": {
        "de": "Wie oft trinken Sie Alkohol?",
        "fr": "À quelle fréquence consommez-vous de l'alcool?",
        "it": "Con quale frequenza consuma alcol?",
        "en": "How often do you have a drink containing alcohol?"
      },
      "options": [
        {"value": 0, "text": {"en": "Never", "de": "Nie", ...}},
        {"value": 1, "text": {"en": "Monthly or less", "de": "Monatlich oder weniger", ...}},
        {"value": 2, "text": {"en": "2-4 times a month", ...}},
        {"value": 3, "text": {"en": "2-3 times a week", ...}},
        {"value": 4, "text": {"en": "4+ times a week", ...}}
      ]
    }
  ]
}
```

**Backend model:**
```python
class AssessmentResult(models.Model):
    user = ForeignKey(User)
    addiction_type = CharField(choices=ADDICTION_TYPES)
    questionnaire_type = CharField()  # AUDIT, DAST, etc.
    responses = JSONField()  # Store all Q&A
    raw_score = IntegerField()
    severity_level = CharField(choices=[
        ('low', 'Low'),
        ('moderate', 'Moderate'),
        ('high', 'High')
    ])
    ai_analysis = TextField(blank=True)  # AI interpretation
    created_at = DateTimeField(auto_now_add=True)
```

**API endpoint:**
```python
POST /api/v1/assessments/submit/
{
    "addiction_type": "alcohol",
    "responses": [
        {"question_id": "audit_q1", "value": 2},
        {"question_id": "audit_q2", "value": 3},
        ...
    ]
}

Response 201:
{
    "assessment_id": "uuid",
    "severity_level": "moderate",
    "raw_score": 15,
    "max_score": 40,
    "percentage": 37.5,
    "ai_insights": "Based on your responses...",
    "recommendations": [...]
}
```

---

#### FR-2.3: AI-анализ и персонализация

**Приоритет:** HIGH  
**Story Points:** 8

**AI Processing Pipeline:**
```python
# Pseudocode for AI analysis
def analyze_assessment(user, assessment_result):
    """
    Generate personalized insights and recommendations
    """
    # 1. Get severity score
    severity = assessment_result.severity_level
    
    # 2. Prepare prompt for OpenAI
    prompt = f"""
    Analyze addiction assessment results:
    - Type: {assessment_result.addiction_type}
    - Severity: {severity}
    - Score: {assessment_result.raw_score}/40
    - User age: {user.age}
    - Language: {user.profile.language}
    
    Provide in {user.profile.language}:
    1. Brief explanation of score (2-3 sentences)
    2. Top 3 personalized recommendations
    3. Suggested notification frequency
    4. Appropriate milestone schedule
    """
    
    # 3. Call OpenAI API
    response = openai.ChatCompletion.create(
        model="gpt-4-turbo",
        messages=[{
            "role": "system",
            "content": "You are an addiction recovery specialist..."
        }, {
            "role": "user",
            "content": prompt
        }],
        temperature=0.7,
        max_tokens=500
    )
    
    # 4. Parse and structure response
    insights = parse_ai_response(response)
    
    # 5. Create personalized plan
    create_recovery_plan(user, insights, severity)
    
    # 6. Configure notifications
    configure_notifications(user, insights['notification_frequency'])
    
    return insights
```

**Personalization outputs:**
```json
{
  "insights": {
    "explanation": "Deine Ergebnisse zeigen...",
    "recommendations": [
      "Setze dir kleine, erreichbare Tagesziele",
      "Führe ein Tagebuch über Trigger-Situationen",
      "Suche Unterstützung in schwierigen Momenten"
    ],
    "notification_frequency": "2x_daily",
    "milestone_schedule": "weekly",
    "suggested_activities": [...]
  },
  "recovery_plan": {
    "phase_1": {
      "duration_days": 7,
      "goals": [...],
      "resources": [...]
    }
  }
}
```

---

### 3.3 Типы зависимостей

#### FR-3.1: Выбор и настройка зависимостей

**Приоритет:** CRITICAL  
**Story Points:** 8

**Supported addiction types:**

```python
ADDICTION_TYPES = [
    ('alcohol', {
        'name': {
            'de': 'Alkohol',
            'fr': 'Alcool',
            'it': 'Alcol',
            'en': 'Alcohol'
        },
        'icon': '🍺',
        'color': '#F59E0B',  # Amber
        'measurement_unit': {
            'de': 'Getränke',
            'fr': 'Verres',
            'it': 'Bicchieri',
            'en': 'Drinks'
        },
        'baseline_question': {
            'de': 'Wie viele alkoholische Getränke haben Sie durchschnittlich pro Woche konsumiert?',
            'en': 'How many alcoholic drinks did you consume per week on average?'
        }
    }),
    ('drugs', {
        'name': {'de': 'Drogen', 'fr': 'Drogues', ...},
        'icon': '💊',
        'color': '#EF4444',  # Red
        'measurement_unit': {'de': 'Mal', 'en': 'Times', ...}
    }),
    ('tobacco', {
        'name': {'de': 'Tabak', 'fr': 'Tabac', ...},
        'icon': '🚬',
        'color': '#8B5CF6',  # Purple
        'measurement_unit': {'de': 'Zigaretten', 'en': 'Cigarettes', ...}
    }),
    ('gambling', {
        'name': {'de': 'Glücksspiel', 'fr': 'Jeux d\'argent', ...},
        'icon': '🎰',
        'color': '#10B981',  # Green
        'measurement_unit': {'de': 'CHF', 'en': 'CHF', ...}
    }),
    ('smartphone', {
        'name': {'de': 'Smartphone', 'fr': 'Smartphone', ...},
        'icon': '📱',
        'color': '#3B82F6',  # Blue
        'measurement_unit': {'de': 'Stunden', 'en': 'Hours', ...}
    })
]
```

**Database model:**
```python
class UserAddiction(models.Model):
    """
    User can track multiple addictions simultaneously
    """
    user = ForeignKey(User, related_name='addictions')
    addiction_type = CharField(choices=ADDICTION_TYPES)
    is_primary = BooleanField(default=False)  # Main addiction
    
    # Baseline data (what was consumed before recovery)
    baseline_amount = DecimalField(max_digits=10, decimal_places=2)
    baseline_frequency = CharField()  # daily, weekly, monthly
    baseline_cost_chf = DecimalField(null=True)  # For financial tracking
    
    # Recovery start
    sobriety_start_date = DateTimeField()
    
    # Current status
    is_active = BooleanField(default=True)
    current_streak_days = IntegerField(default=0)
    longest_streak_days = IntegerField(default=0)
    last_consumption_date = DateTimeField(null=True)
    
    # Settings
    track_triggers = BooleanField(default=True)
    track_mood = BooleanField(default=True)
    allow_partial_consumption = BooleanField(default=False)  # Harm reduction approach
    
    # Metadata
    created_at = DateTimeField(auto_now_add=True)
    updated_at = DateTimeField(auto_now=True)
    
    class Meta:
        unique_together = ('user', 'addiction_type')
```

**API endpoints:**
```python
# List user's addictions
GET /api/v1/addictions/

# Add new addiction to track
POST /api/v1/addictions/
{
    "addiction_type": "alcohol",
    "baseline_amount": 15,
    "baseline_frequency": "weekly",
    "sobriety_start_date": "2025-12-01T00:00:00Z",
    "is_primary": true
}

# Update addiction
PATCH /api/v1/addictions/{id}/

# Set primary addiction
POST /api/v1/addictions/{id}/set-primary/
```

---

### 3.4 Отслеживание прогресса

#### FR-4.1: Счётчик дней трезвости

**Приоритет:** CRITICAL  
**Story Points:** 5

**Real-time counter display:**
```dart
// Flutter Widget
class SobrietyCounter extends StatefulWidget {
  final UserAddiction addiction;
  
  @override
  Widget build(BuildContext context) {
    final duration = DateTime.now().difference(
      addiction.sobrietyStartDate
    );
    
    return Card(
      child: Column(
        children: [
          // Icon and name
          Row(
            children: [
              Text(addiction.icon, fontSize: 40),
              Text(addiction.name),
            ],
          ),
          
          // Time counters
          Row(
            mainAxisAlignment: MainAxisAlignment.spaceAround,
            children: [
              _buildTimeUnit('Days', duration.inDays),
              _buildTimeUnit('Hours', duration.inHours % 24),
              _buildTimeUnit('Minutes', duration.inMinutes % 60),
            ],
          ),
          
          // Progress bar to next milestone
          LinearProgressIndicator(
            value: _calculateProgressToNextMilestone(),
          ),
          Text('Next milestone: 7 days'),
        ],
      ),
    );
  }
}
```

**Backend calculation:**
```python
@property
def sobriety_duration(self):
    """Calculate current sobriety duration"""
    if not self.last_consumption_date:
        return timezone.now() - self.sobriety_start_date
    return timezone.now() - self.last_consumption_date

@property
def current_streak_days(self):
    """Get current streak in days"""
    return self.sobriety_duration.days
```

---

#### FR-4.2: Ручной ввод события потребления

**Приоритет:** CRITICAL  
**Story Points:** 8

**Entry form:**
```dart
class ConsumptionEntryForm extends StatefulWidget {
  // Fields
  - addiction_type (dropdown, если > 1 зависимости)
  - date (DatePicker)
  - time (TimePicker)
  - amount (NumberInput + unit)
  - context (TextArea - optional)
  - triggers (MultiSelect - optional)
  - mood (EmotionPicker - optional)
  - location (optional)
}
```

**Backend model:**
```python
class ConsumptionEvent(models.Model):
    """
    Log of consumption/relapse events
    """
    user = ForeignKey(User)
    addiction = ForeignKey(UserAddiction)
    
    # When and how much
    event_datetime = DateTimeField()
    amount = DecimalField(max_digits=10, decimal_places=2)
    
    # Context
    notes = TextField(blank=True)
    location = CharField(max_length=200, blank=True)
    
    # Triggers (if enabled)
    triggers = ManyToManyField('Trigger', blank=True)
    
    # Mood tracking (if enabled)
    mood_before = CharField(choices=MOOD_CHOICES, blank=True)
    mood_after = CharField(choices=MOOD_CHOICES, blank=True)
    
    # Photos (for journaling)
    photo = ImageField(upload_to='events/', blank=True, null=True)
    
    # Metadata
    created_at = DateTimeField(auto_now_add=True)
    updated_at = DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-event_datetime']
```

**API endpoint:**
```python
POST /api/v1/events/
{
    "addiction_id": "uuid",
    "event_datetime": "2025-12-05T18:30:00Z",
    "amount": 3,
    "notes": "Had a stressful day at work",
    "location": "Home",
    "triggers": ["stress", "alone"],
    "mood_before": "anxious",
    "mood_after": "guilty"
}

Response 201:
{
    "event_id": "uuid",
    "streak_broken": true,
    "new_streak_start": "2025-12-05T18:30:00Z",
    "previous_streak_days": 14,
    "message": {
        "de": "Das passiert. Morgen ist ein neuer Tag.",
        "en": "It happens. Tomorrow is a new day."
    }
}
```

**Business logic после события:**
```python
def handle_consumption_event(event):
    """
    Process consumption event and update related data
    """
    addiction = event.addiction
    
    # 1. Update streak
    if addiction.current_streak_days > addiction.longest_streak_days:
        addiction.longest_streak_days = addiction.current_streak_days
    
    # 2. Reset current streak
    addiction.current_streak_days = 0
    addiction.last_consumption_date = event.event_datetime
    addiction.save()
    
    # 3. Send supportive notification
    send_encouraging_notification(event.user, event.addiction)
    
    # 4. Analyze patterns if enough data
    if ConsumptionEvent.objects.filter(user=event.user).count() >= 5:
        analyze_relapse_patterns.delay(event.user.id)
    
    # 5. Alert doctor if critical
    if should_alert_doctor(event):
        notify_doctor(event)
```

---

#### FR-4.3: Календарь с визуализацией

**Приоритет:** HIGH  
**Story Points:** 8

**Calendar view:**
```dart
class RecoveryCalendar extends StatefulWidget {
  /*
  Визуализация:
  - Зелёные дни = no consumption
  - Красные дни = consumption occurred
  - Intensity = amount consumed (darker = more)
  - Multiple addictions = multiple indicators per day
  */
  
  Widget build(BuildContext context) {
    return TableCalendar(
      calendarBuilders: CalendarBuilders(
        defaultBuilder: (context, day, focusedDay) {
          return _buildDayCell(day);
        },
      ),
    );
  }
  
  Widget _buildDayCell(DateTime day) {
    final events = getEventsForDay(day);
    
    if (events.isEmpty) {
      // Clean day - green
      return Container(
        decoration: BoxDecoration(
          color: Colors.green.shade100,
          shape: BoxShape.circle,
        ),
      );
    } else {
      // Consumption day - show stacked indicators
      return Stack(
        children: events.map((e) => 
          _buildEventIndicator(e)
        ).toList(),
      );
    }
  }
}
```

**Backend endpoint:**
```python
GET /api/v1/calendar/?month=2025-12&addiction_id=uuid

Response 200:
{
  "days": [
    {
      "date": "2025-12-01",
      "is_clean": true,
      "events": []
    },
    {
      "date": "2025-12-05",
      "is_clean": false,
      "events": [
        {
          "addiction_type": "alcohol",
          "amount": 3,
          "severity": "moderate"
        }
      ]
    }
  ],
  "summary": {
    "total_days": 31,
    "clean_days": 28,
    "success_rate": 90.3
  }
}
```

---

### 3.5 Уведомления

#### FR-5.1: Push-уведомления

**Приоритет:** HIGH  
**Story Points:** 8

**Notification types:**
```python
class NotificationType(models.TextChoices):
    DAILY_PLEDGE = 'daily_pledge', 'Daily Pledge'
    MILESTONE = 'milestone', 'Milestone Reached'
    MOTIVATIONAL = 'motivational', 'Motivational Quote'
    REMINDER = 'reminder', 'Log Reminder'
    TRIGGER_ALERT = 'trigger_alert', 'Trigger Warning'
    DOCTOR_MESSAGE = 'doctor_msg', 'Doctor Message'
```

**Notification settings model:**
```python
class NotificationSettings(models.Model):
    user = OneToOneField(User)
    
    # Global settings
    enabled = BooleanField(default=True)
    quiet_hours_start = TimeField(default='22:00')
    quiet_hours_end = TimeField(default='08:00')
    
    # Per-type settings
    daily_pledge_enabled = BooleanField(default=True)
    daily_pledge_time = TimeField(default='09:00')
    
    motivational_enabled = BooleanField(default=True)
    motivational_frequency = CharField(
        choices=[
            ('none', 'None'),
            ('daily', 'Daily'),
            ('2x_daily', 'Twice daily'),
            ('3x_daily', '3 times daily'),
        ],
        default='daily'
    )
    
    reminder_enabled = BooleanField(default=True)
    reminder_time = TimeField(default='20:00')
    
    milestone_enabled = BooleanField(default=True)
    
    # Language for notifications
    language = CharField(max_length=2, default='en')
```

**Celery tasks для отправки:**
```python
@shared_task
def send_daily_pledge_notifications():
    """
    Send daily pledge reminder to all active users
    """
    now = timezone.now()
    current_time = now.time()
    
    # Get users who should receive notification now
    users = User.objects.filter(
        notification_settings__daily_pledge_enabled=True,
        notification_settings__daily_pledge_time=current_time,
        is_active=True
    )
    
    for user in users:
        message = get_localized_message(
            'daily_pledge',
            user.profile.language
        )
        
        send_push_notification(
            user=user,
            title=message['title'],
            body=message['body'],
            data={'type': 'daily_pledge'}
        )

@shared_task
def send_milestone_notification(user_id, addiction_id, milestone_days):
    """
    Celebrate milestone achievement
    """
    user = User.objects.get(id=user_id)
    addiction = UserAddiction.objects.get(id=addiction_id)
    
    message = get_localized_message(
        'milestone',
        user.profile.language,
        context={
            'days': milestone_days,
            'addiction': addiction.get_name()
        }
    )
    
    send_push_notification(
        user=user,
        title=message['title'],
        body=message['body'],
        data={
            'type': 'milestone',
            'addiction_id': str(addiction_id),
            'days': milestone_days
        }
    )
```

**Push notification content examples:**
```json
{
  "daily_pledge": {
    "de": {
      "title": "Dein tägliches Versprechen",
      "body": "Ich werde heute clean bleiben. Einen Tag nach dem anderen."
    },
    "en": {
      "title": "Your Daily Pledge",
      "body": "I will stay clean today. One day at a time."
    }
  },
  "milestone_7_days": {
    "de": {
      "title": "🎉 1 Woche geschafft!",
      "body": "Du bist seit 7 Tagen clean. Fantastische Leistung!"
    },
    "en": {
      "title": "🎉 One week milestone!",
      "body": "You've been clean for 7 days. Amazing achievement!"
    }
  }
}
```

---

### 3.6 Визуализация данных

#### FR-6.1: Dashboard

**Приоритет:** HIGH  
**Story Points:** 13

**Main dashboard components:**

```dart
class DashboardScreen extends StatelessWidget {
  Widget build(BuildContext context) {
    return ListView(
      children: [
        // 1. Header with active addictions counters
        _buildAddictionCounters(),
        
        // 2. Today's summary card
        _buildTodaySummary(),
        
        // 3. Progress chart (last 30 days)
        _buildProgressChart(),
        
        // 4. Milestones section
        _buildMilestones(),
        
        // 5. Quick stats
        _buildQuickStats(),
        
        // 6. Recent events
        _buildRecentEvents(),
      ],
    );
  }
}
```

**Dashboard API:**
```python
GET /api/v1/dashboard/

Response 200:
{
  "user": {
    "first_name": "Max",
    "language": "de"
  },
  "addictions": [
    {
      "id": "uuid",
      "type": "alcohol",
      "name": "Alkohol",
      "icon": "🍺",
      "color": "#F59E0B",
      "current_streak_days": 28,
      "longest_streak_days": 42,
      "sobriety_start_date": "2025-11-07T00:00:00Z",
      "is_primary": true
    }
  ],
  "today": {
    "date": "2025-12-05",
    "is_clean": true,
    "events_count": 0
  },
  "stats_30_days": {
    "clean_days": 27,
    "consumption_days": 3,
    "success_rate": 90.0,
    "total_events": 3,
    "average_per_event": 2.5
  },
  "next_milestones": [
    {
      "addiction_type": "alcohol",
      "milestone": 30,
      "days_to_go": 2,
      "date": "2025-12-07"
    }
  ],
  "savings": {
    "money_saved_chf": 280.50,
    "time_saved_hours": 42
  }
}
```

---

#### FR-6.2: Графики потребления

**Приоритет:** MEDIUM  
**Story Points:** 8

**Chart types:**

1. **Line Chart - Consumption over time**
```dart
LineChart(
  data: consumptionData,
  xAxis: dates,
  yAxis: amount,
  multipleLines: true,  // One line per addiction
  showTrendLine: true
)
```

2. **Bar Chart - Weekly comparison**
```dart
BarChart(
  data: weeklyData,
  comparison: [thisWeek, lastWeek],
  groupBy: 'addiction_type'
)
```

3. **Streak visualization**
```dart
StreakChart(
  showCurrentStreak: true,
  showLongestStreak: true,
  showAllBreaks: true
)
```

**Backend chart data API:**
```python
GET /api/v1/analytics/consumption-chart/
    ?addiction_id=uuid
    &period=30days
    &granularity=daily

Response 200:
{
  "chart_data": [
    {"date": "2025-11-05", "amount": 0, "is_clean": true},
    {"date": "2025-11-06", "amount": 0, "is_clean": true},
    {"date": "2025-11-07", "amount": 3, "is_clean": false},
    ...
  ],
  "statistics": {
    "average_per_day": 0.3,
    "median": 0,
    "mode": 0,
    "trend": "improving"
  }
}
```

---

### 3.7 Связь с врачом

#### FR-7.1: Sharing dashboard (Read-only link)

**Приоритет:** MEDIUM  
**Story Points:** 8

**Feature description:**
Пациент может поделиться read-only dashboard со своим врачом через уникальную ссылку.

**Database model:**
```python
class SharedDashboard(models.Model):
    """
    Shareable link for doctor access
    """
    patient = ForeignKey(User, related_name='shared_dashboards')
    share_token = UUIDField(unique=True, default=uuid.uuid4)
    
    # What to share
    share_all_addictions = BooleanField(default=True)
    shared_addictions = ManyToManyField(UserAddiction, blank=True)
    
    # Permissions
    can_view_notes = BooleanField(default=False)
    can_view_triggers = BooleanField(default=True)
    can_view_mood = BooleanField(default=True)
    can_view_photos = BooleanField(default=False)
    
    # Access control
    recipient_email = EmailField(blank=True)  # Optional
    password_protected = BooleanField(default=False)
    access_password = CharField(max_length=128, blank=True)
    
    # Expiration
    expires_at = DateTimeField(null=True, blank=True)
    is_active = BooleanField(default=True)
    
    # Audit
    created_at = DateTimeField(auto_now_add=True)
    last_accessed_at = DateTimeField(null=True)
    access_count = IntegerField(default=0)
```

**API endpoints:**
```python
# Create share link
POST /api/v1/share/create/
{
    "share_all_addictions": true,
    "can_view_notes": false,
    "expires_in_days": 30,
    "recipient_email": "doctor@hospital.ch",
    "password_protected": true,
    "password": "secretpass123"
}

Response 201:
{
    "share_token": "uuid",
    "share_url": "https://app.recovery.ch/shared/uuid",
    "expires_at": "2026-01-04T12:00:00Z",
    "qr_code": "data:image/png;base64,..."
}

# Access shared dashboard (public endpoint)
GET /shared/{share_token}/
    ?password=secretpass123  # if password protected

Response 200:
{
    "patient": {
        "first_name": "Max",
        "initials": "MT",
        "age": 35
    },
    "addictions": [...],
    "dashboard_data": {...},
    "last_updated": "2025-12-05T10:30:00Z"
}
```

---

#### FR-7.2: PDF Export

**Приоритет:** MEDIUM  
**Story Points:** 5

**PDF report structure:**
```
┌─────────────────────────────────────────┐
│  Recovery Progress Report               │
│  Patient: Max T.                        │
│  Period: Nov 1 - Dec 5, 2025           │
├─────────────────────────────────────────┤
│                                         │
│  1. Summary                             │
│     - Addictions tracked: 2             │
│     - Overall success rate: 90%         │
│     - Longest streak: 42 days           │
│                                         │
│  2. Per Addiction Details               │
│     🍺 Alcohol                          │
│        Current streak: 28 days          │
│        Events: 3 (last 30 days)         │
│        Baseline: 15 drinks/week         │
│        Current: 0.3 drinks/week (↓98%)  │
│                                         │
│  3. Timeline & Events                   │
│     [Calendar visualization]            │
│     [Event list with dates]             │
│                                         │
│  4. Charts                              │
│     [Consumption trend chart]           │
│     [Success rate by week]              │
│                                         │
│  5. Insights                            │
│     - Most common triggers              │
│     - Best performing days/times        │
│     - Doctor's notes (if any)           │
│                                         │
│  Generated: Dec 5, 2025 10:30           │
│  Report ID: RPT-20251205-001            │
└─────────────────────────────────────────┘
```

**API endpoint:**
```python
POST /api/v1/export/pdf/
{
    "period_start": "2025-11-01",
    "period_end": "2025-12-05",
    "include_addictions": ["all"],
    "include_notes": false,
    "include_photos": false,
    "language": "de"
}

Response 200:
{
    "pdf_url": "https://storage.../report_uuid.pdf",
    "expires_at": "2025-12-06T10:30:00Z",
    "file_size_bytes": 234567
}
```

**Backend implementation (ReportLab):**
```python
from reportlab.lib.pagesizes import A4
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Image
from reportlab.lib.styles import getSampleStyleSheet

def generate_pdf_report(user, params):
    """
    Generate PDF recovery report
    """
    buffer = BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=A4)
    
    elements = []
    styles = getSampleStyleSheet()
    
    # Title
    elements.append(Paragraph(
        f"Recovery Progress Report - {user.get_full_name()}",
        styles['Title']
    ))
    
    # Date range
    elements.append(Paragraph(
        f"Period: {params['period_start']} - {params['period_end']}",
        styles['Normal']
    ))
    
    # Summary statistics
    stats = calculate_summary_stats(user, params)
    elements.append(build_summary_table(stats))
    
    # Per-addiction details
    for addiction in user.addictions.filter(is_active=True):
        elements.extend(build_addiction_section(addiction, params))
    
    # Charts
    chart_images = generate_chart_images(user, params)
    for img in chart_images:
        elements.append(Image(img, width=400, height=200))
    
    # Build PDF
    doc.build(elements)
    buffer.seek(0)
    
    return buffer
```

---

## 4. Нефункциональные требования

### 4.1 Производительность

**NFR-1: Response Time**
- API response time: < 500ms (95th percentile)
- Page load time: < 2 seconds
- Real-time counter update: < 100ms
- Chart rendering: < 1 second

**NFR-2: Scalability**
- Support 10,000 concurrent users
- Handle 100 requests/second per server
- Database queries optimized (< 50ms)

### 4.2 Надёжность

**NFR-3: Uptime**
- 99.5% uptime SLA
- Planned maintenance windows < 4 hours/month

**NFR-4: Data Integrity**
- Zero data loss
- Automatic backups every 6 hours
- Point-in-time recovery (7 days)

### 4.3 Безопасность

**NFR-5: Authentication**
- JWT tokens with 1-hour expiry
- Refresh tokens valid 30 days
- Password complexity enforcement
- Rate limiting on login (5 attempts/15 min)

**NFR-6: Data Encryption**
- TLS 1.3 for all API communication
- Sensitive data encrypted at rest (AES-256)
- GDPR compliant data handling

### 4.4 Usability

**NFR-7: Accessibility**
- WCAG 2.1 Level AA compliance
- Support for screen readers
- Adjustable font sizes
- High contrast mode

**NFR-8: Internationalization**
- Full support for DE/FR/IT/EN
- RTL language support (future)
- Date/time formatting per locale
- Currency formatting (CHF)

---

## 5. Технические требования

### 5.1 Backend Stack

```yaml
Framework: Django 5.0+
Python: 3.12+
API: Django REST Framework 3.14+
Database: PostgreSQL 15.8
Cache: Redis 7.2
Task Queue: Celery 5.3+
Web Server: Gunicorn
Proxy: Nginx

Required Packages:
  - djangorestframework
  - djangorestframework-simplejwt
  - django-cors-headers
  - django-countries
  - django-phonenumber-field
  - celery[redis]
  - django-celery-beat
  - psycopg2-binary
  - Pillow
  - reportlab
  - openai
  - scikit-learn
  - pandas
  - numpy
```

### 5.2 Frontend Stack

```yaml
Framework: Flutter 3.16+
Dart: 3.2+
State Management: Riverpod 2.4+

Required Packages:
  - dio (HTTP client)
  - flutter_secure_storage (token storage)
  - hive (local database)
  - fl_chart (charts)
  - table_calendar (calendar widget)
  - intl (i18n)
  - firebase_messaging (push notifications)
  - shared_preferences
  - image_picker
  - permission_handler
```

### 5.3 Infrastructure

```yaml
Hosting: 
  - Backend: AWS EC2 / DigitalOcean
  - Database: AWS RDS PostgreSQL
  - Cache: AWS ElastiCache Redis
  - Storage: AWS S3 (media files)

CI/CD:
  - GitHub Actions
  - Docker containers
  - Automated testing

Monitoring:
  - Sentry (error tracking)
  - DataDog (APM)
  - CloudWatch (infrastructure)
```

---

## 6. AI/ML Компоненты

### 6.1 OpenAI Integration

**Purpose:**
- Персонализация рекомендаций после assessment
- Генерация мотивационного контента
- Анализ паттернов рецидивов
- Создание индивидуального плана восстановления

**Configuration:**
```python
# settings.py
OPENAI_API_KEY = env('OPENAI_API_KEY')
OPENAI_MODEL = 'gpt-4-turbo'
OPENAI_MAX_TOKENS = 500
OPENAI_TEMPERATURE = 0.7
```

**Usage examples:**

1. **Assessment analysis:**
```python
def generate_assessment_insights(assessment_result, user):
    prompt = f"""
    You are an addiction recovery specialist. Analyze these assessment results:
    
    - Addiction type: {assessment_result.addiction_type}
    - Severity score: {assessment_result.raw_score}/40 ({assessment_result.severity_level})
    - User age: {user.age}
    - Gender: {user.gender}
    
    Provide a compassionate, evidence-based response in {user.language}:
    1. Brief explanation of their score (2-3 sentences)
    2. Three specific, actionable recommendations
    3. Recommended notification frequency (1x, 2x, or 3x daily)
    4. Suggested milestone schedule (daily, weekly, or monthly)
    
    Keep language supportive and non-judgmental.
    """
    
    response = openai.ChatCompletion.create(
        model=settings.OPENAI_MODEL,
        messages=[
            {"role": "system", "content": "You are a compassionate addiction recovery specialist with expertise in evidence-based treatment methods."},
            {"role": "user", "content": prompt}
        ],
        temperature=settings.OPENAI_TEMPERATURE,
        max_tokens=settings.OPENAI_MAX_TOKENS
    )
    
    return response.choices[0].message.content
```

2. **Pattern analysis:**
```python
def analyze_relapse_patterns(user_id):
    """
    Analyze user's consumption events to identify patterns
    """
    user = User.objects.get(id=user_id)
    events = ConsumptionEvent.objects.filter(
        user=user
    ).order_by('-event_datetime')[:20]
    
    # Prepare event data
    event_data = []
    for event in events:
        event_data.append({
            'date': event.event_datetime.strftime('%Y-%m-%d'),
            'time': event.event_datetime.strftime('%H:%M'),
            'day_of_week': event.event_datetime.strftime('%A'),
            'amount': float(event.amount),
            'triggers': [t.name for t in event.triggers.all()],
            'mood_before': event.mood_before,
            'location': event.location
        })
    
    prompt = f"""
    Analyze these consumption/relapse events for patterns:
    {json.dumps(event_data, indent=2)}
    
    Identify:
    1. Most common triggers (top 3)
    2. Time patterns (day of week, time of day)
    3. Warning signs before relapse
    4. Protective factors (what helps them stay clean)
    
    Provide response in {user.profile.language}.
    """
    
    response = openai.ChatCompletion.create(
        model=settings.OPENAI_MODEL,
        messages=[
            {"role": "system", "content": "You are a data analyst specializing in addiction recovery patterns."},
            {"role": "user", "content": prompt}
        ]
    )
    
    insights = response.choices[0].message.content
    
    # Save insights
    PatternAnalysis.objects.create(
        user=user,
        analysis_text=insights,
        events_analyzed=len(events)
    )
    
    return insights
```

### 6.2 Severity Scoring Algorithm

**scikit-learn implementation:**

```python
from sklearn.preprocessing import StandardScaler
from sklearn.ensemble import RandomForestClassifier
import numpy as np

class SeverityPredictor:
    """
    Predict addiction severity and treatment needs
    """
    
    def __init__(self):
        self.scaler = StandardScaler()
        self.model = None
        
    def prepare_features(self, assessment_result, user):
        """
        Extract features for prediction
        """
        features = {
            'raw_score': assessment_result.raw_score,
            'score_percentage': (assessment_result.raw_score / 40) * 100,
            'age': user.age,
            'baseline_amount': user.addictions.first().baseline_amount,
            'previous_attempts': user.recovery_attempts.count(),
            # Add more features...
        }
        
        return np.array(list(features.values())).reshape(1, -1)
    
    def predict_severity(self, assessment_result, user):
        """
        Predict severity level and treatment recommendations
        """
        features = self.prepare_features(assessment_result, user)
        features_scaled = self.scaler.transform(features)
        
        # Predict severity
        severity_score = self.model.predict_proba(features_scaled)[0]
        
        # Determine treatment intensity
        if severity_score[2] > 0.6:  # High severity
            treatment_level = 'intensive'
            notification_frequency = '3x_daily'
            milestone_frequency = 'daily'
        elif severity_score[1] > 0.5:  # Moderate
            treatment_level = 'moderate'
            notification_frequency = '2x_daily'
            milestone_frequency = 'weekly'
        else:  # Low
            treatment_level = 'basic'
            notification_frequency = 'daily'
            milestone_frequency = 'weekly'
        
        return {
            'severity_score': severity_score,
            'treatment_level': treatment_level,
            'notification_frequency': notification_frequency,
            'milestone_frequency': milestone_frequency
        }
```

### 6.3 Cost Estimation

**OpenAI API costs:**
- GPT-4 Turbo: $0.01 per 1K input tokens, $0.03 per 1K output tokens
- Average assessment analysis: ~500 input + 300 output tokens
- Cost per assessment: ~$0.015
- Expected usage: ~10-20 API calls per user per month
- **Monthly cost per active user: $0.20 - $0.40**

**Budget considerations:**
- 1,000 users: $200-400/month
- 10,000 users: $2,000-4,000/month
- Fallback to rule-based system if budget exceeded

---

## 7. API Спецификация

### 7.1 API Overview

**Base URL:** `https://api.recovery-app.ch/api/v1/`  
**Authentication:** JWT Bearer tokens  
**Content-Type:** `application/json`  
**Rate Limiting:** 100 requests/minute per user

### 7.2 Authentication Endpoints

#### POST /auth/register/
Register new user account

**Request:**
```json
{
  "email": "user@example.com",
  "password": "SecurePass123",
  "password_confirm": "SecurePass123",
  "first_name": "Max",
  "last_name": "Mueller",
  "terms_accepted": true
}
```

**Response 201:**
```json
{
  "user_id": "uuid",
  "email": "user@example.com",
  "message": "Verification email sent"
}
```

**Errors:**
- 400: Validation error
- 409: Email already exists

---

#### POST /auth/login/
Authenticate user and get tokens

**Request:**
```json
{
  "email": "user@example.com",
  "password": "SecurePass123"
}
```

**Response 200:**
```json
{
  "access_token": "eyJ0eXAiOiJKV1QiLCJhbGc...",
  "refresh_token": "eyJ0eXAiOiJKV1QiLCJhbGc...",
  "user": {
    "id": "uuid",
    "email": "user@example.com",
    "first_name": "Max",
    "profile_completed": true,
    "language": "de"
  }
}
```

**Errors:**
- 401: Invalid credentials
- 403: Email not verified

---

#### POST /auth/refresh/
Refresh access token

**Request:**
```json
{
  "refresh_token": "eyJ0eXAiOiJKV1QiLCJhbGc..."
}
```

**Response 200:**
```json
{
  "access_token": "eyJ0eXAiOiJKV1QiLCJhbGc..."
}
```

---

### 7.3 User Profile Endpoints

#### GET /users/profile/
Get current user profile

**Headers:**
```
Authorization: Bearer {access_token}
```

**Response 200:**
```json
{
  "id": "uuid",
  "email": "user@example.com",
  "first_name": "Max",
  "last_name": "Mueller",
  "date_of_birth": "1990-05-15",
  "gender": "male",
  "country": "CH",
  "language": "de",
  "phone": "+41791234567",
  "profile_picture": "https://storage.../profile.jpg",
  "onboarding_completed": true,
  "severity_score": 15,
  "created_at": "2025-11-01T10:00:00Z"
}
```

---

#### PATCH /users/profile/
Update user profile

**Request:**
```json
{
  "first_name": "Maximilian",
  "language": "fr",
  "phone": "+41791234567"
}
```

**Response 200:**
```json
{
  "id": "uuid",
  "first_name": "Maximilian",
  "language": "fr",
  "phone": "+41791234567",
  "updated_at": "2025-12-05T10:30:00Z"
}
```

---

### 7.4 Addiction Management Endpoints

#### GET /addictions/
List user's tracked addictions

**Response 200:**
```json
{
  "count": 2,
  "results": [
    {
      "id": "uuid",
      "addiction_type": "alcohol",
      "name": "Alkohol",
      "icon": "🍺",
      "color": "#F59E0B",
      "is_primary": true,
      "baseline_amount": 15,
      "baseline_frequency": "weekly",
      "sobriety_start_date": "2025-11-07T00:00:00Z",
      "current_streak_days": 28,
      "longest_streak_days": 42,
      "last_consumption_date": "2025-11-10T18:00:00Z"
    },
    {
      "id": "uuid2",
      "addiction_type": "tobacco",
      "name": "Tabak",
      "icon": "🚬",
      "color": "#8B5CF6",
      "is_primary": false,
      "baseline_amount": 20,
      "baseline_frequency": "daily",
      "current_streak_days": 14,
      "longest_streak_days": 14
    }
  ]
}
```

---

#### POST /addictions/
Add new addiction to track

**Request:**
```json
{
  "addiction_type": "alcohol",
  "baseline_amount": 15,
  "baseline_frequency": "weekly",
  "baseline_cost_chf": 200,
  "sobriety_start_date": "2025-12-01T00:00:00Z",
  "is_primary": true
}
```

**Response 201:**
```json
{
  "id": "uuid",
  "addiction_type": "alcohol",
  "created_at": "2025-12-05T10:00:00Z",
  "message": "Addiction tracking started"
}
```

---

### 7.5 Events Endpoints

#### POST /events/
Log consumption event

**Request:**
```json
{
  "addiction_id": "uuid",
  "event_datetime": "2025-12-05T18:30:00Z",
  "amount": 3,
  "notes": "Stressful day at work",
  "location": "Home",
  "triggers": ["stress", "alone"],
  "mood_before": "anxious",
  "mood_after": "guilty"
}
```

**Response 201:**
```json
{
  "event_id": "uuid",
  "streak_broken": true,
  "new_streak_start": "2025-12-05T18:30:00Z",
  "previous_streak_days": 14,
  "message": {
    "de": "Das passiert. Morgen ist ein neuer Tag.",
    "en": "It happens. Tomorrow is a new day."
  }
}
```

---

#### GET /events/?addiction_id={uuid}&limit=20
Get consumption events

**Response 200:**
```json
{
  "count": 45,
  "next": "https://api.../events/?page=2",
  "previous": null,
  "results": [
    {
      "id": "uuid",
      "addiction": {
        "id": "uuid",
        "type": "alcohol",
        "name": "Alkohol"
      },
      "event_datetime": "2025-12-05T18:30:00Z",
      "amount": 3,
      "notes": "Stressful day",
      "location": "Home",
      "triggers": ["stress", "alone"],
      "mood_before": "anxious",
      "mood_after": "guilty",
      "created_at": "2025-12-05T18:35:00Z"
    }
  ]
}
```

---

### 7.6 Dashboard Endpoint

#### GET /dashboard/
Get comprehensive dashboard data

**Response 200:**
```json
{
  "user": {
    "first_name": "Max",
    "language": "de"
  },
  "addictions": [
    {
      "id": "uuid",
      "type": "alcohol",
      "name": "Alkohol",
      "icon": "🍺",
      "color": "#F59E0B",
      "current_streak_days": 28,
      "longest_streak_days": 42,
      "sobriety_start_date": "2025-11-07T00:00:00Z",
      "is_primary": true
    }
  ],
  "today": {
    "date": "2025-12-05",
    "is_clean": true,
    "events_count": 0
  },
  "stats_30_days": {
    "clean_days": 27,
    "consumption_days": 3,
    "success_rate": 90.0,
    "total_events": 3,
    "average_per_event": 2.5
  },
  "next_milestones": [
    {
      "addiction_type": "alcohol",
      "milestone": 30,
      "days_to_go": 2,
      "date": "2025-12-07"
    }
  ],
  "savings": {
    "money_saved_chf": 280.50,
    "time_saved_hours": 42
  }
}
```

---

### 7.7 Assessment Endpoints

#### POST /assessments/submit/
Submit assessment questionnaire

**Request:**
```json
{
  "addiction_type": "alcohol",
  "questionnaire_type": "AUDIT",
  "responses": [
    {"question_id": "audit_q1", "value": 2},
    {"question_id": "audit_q2", "value": 3},
    {"question_id": "audit_q3", "value": 1},
    ...
  ]
}
```

**Response 201:**
```json
{
  "assessment_id": "uuid",
  "severity_level": "moderate",
  "raw_score": 15,
  "max_score": 40,
  "percentage": 37.5,
  "ai_insights": {
    "explanation": "Deine Ergebnisse zeigen...",
    "recommendations": [
      "Setze dir kleine, erreichbare Tagesziele",
      "Führe ein Tagebuch über Trigger-Situationen"
    ],
    "notification_frequency": "2x_daily",
    "milestone_schedule": "weekly"
  },
  "recovery_plan_generated": true
}
```

---

### 7.8 Sharing Endpoints

#### POST /share/create/
Create shareable dashboard link

**Request:**
```json
{
  "share_all_addictions": true,
  "can_view_notes": false,
  "can_view_triggers": true,
  "expires_in_days": 30,
  "recipient_email": "doctor@hospital.ch",
  "password_protected": true,
  "password": "doctorpass123"
}
```

**Response 201:**
```json
{
  "share_token": "uuid",
  "share_url": "https://app.recovery.ch/shared/uuid",
  "expires_at": "2026-01-04T12:00:00Z",
  "qr_code": "data:image/png;base64,iVBORw0KG..."
}
```

---

#### GET /shared/{token}/
Access shared dashboard (public, no auth required)

**Query params:**
- `password` (optional, if password-protected)

**Response 200:**
```json
{
  "patient": {
    "first_name": "Max",
    "initials": "MT",
    "age": 35
  },
  "addictions": [...],
  "dashboard_data": {...},
  "last_updated": "2025-12-05T10:30:00Z"
}
```

---

## 8. UI/UX Требования

### 8.1 Design System

**Color Palette:**
```
Primary:
  - Main: #667eea (Purple-blue)
  - Light: #8b9ef7
  - Dark: #5568d3

Addiction Colors:
  - Alcohol: #F59E0B (Amber)
  - Drugs: #EF4444 (Red)
  - Tobacco: #8B5CF6 (Purple)
  - Gambling: #10B981 (Green)
  - Smartphone: #3B82F6 (Blue)

Status Colors:
  - Success: #10B981 (Green)
  - Warning: #F59E0B (Amber)
  - Error: #EF4444 (Red)
  - Info: #3B82F6 (Blue)

Neutrals:
  - Gray 50: #F9FAFB
  - Gray 100: #F3F4F6
  - Gray 200: #E5E7EB
  - Gray 300: #D1D5DB
  - Gray 400: #9CA3AF
  - Gray 500: #6B7280
  - Gray 600: #4B5563
  - Gray 700: #374151
  - Gray 800: #1F2937
  - Gray 900: #111827
```

**Typography:**
```
Font Family: SF Pro (iOS) / Roboto (Android)

Sizes:
  - Display: 34px, Bold
  - Title 1: 28px, Bold
  - Title 2: 22px, Bold
  - Title 3: 20px, Semibold
  - Headline: 17px, Semibold
  - Body: 17px, Regular
  - Callout: 16px, Regular
  - Subhead: 15px, Regular
  - Footnote: 13px, Regular
  - Caption 1: 12px, Regular
  - Caption 2: 11px, Regular
```

**Spacing:**
```
Base unit: 4px

Scale:
  - 0: 0px
  - 1: 4px
  - 2: 8px
  - 3: 12px
  - 4: 16px
  - 5: 20px
  - 6: 24px
  - 8: 32px
  - 10: 40px
  - 12: 48px
  - 16: 64px
```

### 8.2 Key Screens

#### 8.2.1 Onboarding Flow

**Screen 1: Welcome & Language Selection**
```
┌─────────────────────────────────┐
│                                 │
│         🏥 Recovery             │
│                                 │
│    Welcome to your journey      │
│                                 │
│   Choose your language:         │
│                                 │
│   [ 🇩🇪 Deutsch        ]        │
│   [ 🇫🇷 Français       ]        │
│   [ 🇮🇹 Italiano       ]        │
│   [ 🇬🇧 English        ]        │
│                                 │
│                                 │
│        [    Continue    ]       │
│                                 │
└─────────────────────────────────┘
```

**Screen 2: Addiction Selection**
```
┌─────────────────────────────────┐
│  ←    Select Addiction          │
│                                 │
│  What would you like to track?  │
│  (You can add more later)       │
│                                 │
│   ┌──────────────────┐         │
│   │   🍺 Alkohol     │ ✓       │
│   └──────────────────┘         │
│                                 │
│   ┌──────────────────┐         │
│   │   💊 Drogen      │         │
│   └──────────────────┘         │
│                                 │
│   ┌──────────────────┐         │
│   │   🚬 Tabak       │         │
│   └──────────────────┘         │
│                                 │
│                                 │
│        [    Continue    ]       │
│                                 │
└─────────────────────────────────┘
```

**Screen 3: Assessment Questionnaire**
```
┌─────────────────────────────────┐
│  ←    Assessment    (1/10)      │
│                                 │
│  How often do you have a        │
│  drink containing alcohol?      │
│                                 │
│   ○ Never                       │
│   ○ Monthly or less             │
│   ◉ 2-4 times a month           │
│   ○ 2-3 times a week            │
│   ○ 4+ times a week             │
│                                 │
│                                 │
│  ●●○○○○○○○○                      │
│                                 │
│        [    Next    ]           │
│                                 │
└─────────────────────────────────┘
```

#### 8.2.2 Main Dashboard

```
┌─────────────────────────────────┐
│  ☰    Dashboard         👤      │
├─────────────────────────────────┤
│                                 │
│  🍺 Alkohol                     │
│  ┌─────────────────────────┐   │
│  │  28 Days 14 Hours       │   │
│  │  12 Minutes             │   │
│  │                         │   │
│  │  Next: 30 days (2 days) │   │
│  │  ████████████░░░ 93%    │   │
│  └─────────────────────────┘   │
│                                 │
│  Today's Summary                │
│  ┌─────────────────────────┐   │
│  │  ✓ Clean Day            │   │
│  │  0 events logged        │   │
│  └─────────────────────────┘   │
│                                 │
│  30-Day Stats                   │
│  ┌─────────────────────────┐   │
│  │  Clean: 27/30 (90%)     │   │
│  │  [Chart visualization]  │   │
│  └─────────────────────────┘   │
│                                 │
│  Savings                        │
│  ┌─────────────────────────┐   │
│  │  💰 CHF 280.50 saved    │   │
│  │  ⏰ 42 hours gained     │   │
│  └─────────────────────────┘   │
│                                 │
└─────────────────────────────────┘
│  [Dashboard] [Calendar] [+]    │
│  [Stats] [Profile]              │
└─────────────────────────────────┘
```

#### 8.2.3 Log Event Screen

```
┌─────────────────────────────────┐
│  ×    Log Event                 │
├─────────────────────────────────┤
│                                 │
│  Addiction Type                 │
│  [ 🍺 Alkohol         ▼ ]      │
│                                 │
│  Date & Time                    │
│  [ 05.12.2025    18:30 ]        │
│                                 │
│  Amount                         │
│  [ 3         ] Getränke         │
│                                 │
│  Mood (before)                  │
│  [ 😟 😐 😊 😄 😁 ]            │
│     ^^                          │
│                                 │
│  Triggers (optional)            │
│  ☑ Stress  ☐ Boredom           │
│  ☑ Alone   ☐ Social             │
│                                 │
│  Notes (optional)               │
│  ┌─────────────────────────┐   │
│  │ Had a stressful day at  │   │
│  │ work...                 │   │
│  └─────────────────────────┘   │
│                                 │
│                                 │
│       [  Save Event  ]          │
│                                 │
└─────────────────────────────────┘
```

### 8.3 Apple HIG Compliance

**Navigation:**
- Use native iOS navigation patterns (tab bar, navigation bar)
- Implement swipe-back gesture
- Respect safe areas (notch, home indicator)

**Interactions:**
- Use system haptic feedback
- Implement pull-to-refresh where appropriate
- Support iOS gestures (swipe to delete, etc.)

**Components:**
- Use SF Symbols for icons
- Follow iOS design patterns (lists, cards, buttons)
- Support Dark Mode
- Implement accessibility features (VoiceOver, Dynamic Type)

**Animations:**
- Use natural, physics-based animations
- Timing: 0.3s for most transitions
- Easing: ease-in-out

---

## 9. Безопасность и Privacy

### 9.1 Data Protection

**GDPR Compliance:**
- ✅ User consent for data collection
- ✅ Right to access data (export)
- ✅ Right to be forgotten (delete account)
- ✅ Data portability
- ✅ Transparent privacy policy
- ✅ Data breach notification (<72 hours)

**Data Encryption:**
```python
# At rest (database)
from django.db import models
from django_cryptography.fields import encrypt

class SensitiveData(models.Model):
    # Encrypted fields
    notes = encrypt(models.TextField())
    location = encrypt(models.CharField(max_length=200))
    
# In transit
# Force HTTPS in production
SECURE_SSL_REDIRECT = True
SECURE_HSTS_SECONDS = 31536000
```

### 9.2 Authentication Security

**JWT Configuration:**
```python
SIMPLE_JWT = {
    'ACCESS_TOKEN_LIFETIME': timedelta(hours=1),
    'REFRESH_TOKEN_LIFETIME': timedelta(days=30),
    'ROTATE_REFRESH_TOKENS': True,
    'BLACKLIST_AFTER_ROTATION': True,
    'ALGORITHM': 'HS256',
    'SIGNING_KEY': SECRET_KEY,
}
```

**Password Requirements:**
- Minimum 8 characters
- Must contain: letter + number
- Optional: special character
- Not in common password list
- Not similar to email/name

**Rate Limiting:**
```python
# Login attempts
RATELIMIT_ENABLE = True
RATELIMIT_VIEW = '5/15m'  # 5 attempts per 15 minutes

# API requests
DEFAULT_THROTTLE_RATES = {
    'anon': '20/hour',
    'user': '100/minute',
}
```

### 9.3 Data Retention

**User Data:**
- Active accounts: Indefinite (while active)
- Deleted accounts: 30-day grace period, then purged
- Anonymized analytics: 2 years

**Backup Policy:**
- Full backups: Daily at 2 AM UTC
- Incremental backups: Every 6 hours
- Retention: 30 days of daily backups
- Off-site replication: AWS S3 (encrypted)

### 9.4 PHI Handling

**Medical Data Classification:**
- Level 1 (High): Assessment results, consumption events
- Level 2 (Medium): Notes, triggers, mood data
- Level 3 (Low): Statistics, aggregated data

**Access Controls:**
```python
class PHIAccessLog(models.Model):
    """Log all access to PHI data"""
    user = ForeignKey(User)
    accessed_by = ForeignKey(User, related_name='phi_accesses')
    data_type = CharField(max_length=50)
    action = CharField(choices=['view', 'edit', 'delete'])
    ip_address = GenericIPAddressField()
    timestamp = DateTimeField(auto_now_add=True)
```

---

## 10. Тестирование

### 10.1 Testing Strategy

**Pyramid:**
```
       /\
      /  \     E2E Tests (5%)
     /    \
    /------\   Integration Tests (15%)
   /        \
  /----------\ Unit Tests (80%)
```

### 10.2 Backend Testing

**Unit Tests (pytest):**
```python
# tests/test_models.py
import pytest
from apps.core.models import UserAddiction, ConsumptionEvent

@pytest.mark.django_db
class TestUserAddiction:
    def test_streak_calculation(self, user, alcohol_addiction):
        """Test streak days calculation"""
        assert alcohol_addiction.current_streak_days == 0
        
        # Add sobriety start date
        alcohol_addiction.sobriety_start_date = timezone.now() - timedelta(days=7)
        alcohol_addiction.save()
        
        assert alcohol_addiction.current_streak_days == 7
    
    def test_streak_reset_on_consumption(self, user, alcohol_addiction):
        """Test streak resets after consumption event"""
        alcohol_addiction.current_streak_days = 14
        alcohol_addiction.save()
        
        # Log consumption
        event = ConsumptionEvent.objects.create(
            user=user,
            addiction=alcohol_addiction,
            event_datetime=timezone.now(),
            amount=3
        )
        
        alcohol_addiction.refresh_from_db()
        assert alcohol_addiction.current_streak_days == 0
        assert alcohol_addiction.longest_streak_days == 14

# tests/test_api.py
class TestAuthenticationAPI:
    def test_register_success(self, api_client):
        """Test successful user registration"""
        data = {
            'email': 'test@example.com',
            'password': 'SecurePass123',
            'password_confirm': 'SecurePass123',
            'first_name': 'Test',
            'last_name': 'User',
            'terms_accepted': True
        }
        
        response = api_client.post('/api/v1/auth/register/', data)
        assert response.status_code == 201
        assert 'user_id' in response.data
    
    def test_login_invalid_credentials(self, api_client):
        """Test login with wrong password"""
        data = {
            'email': 'test@example.com',
            'password': 'WrongPassword'
        }
        
        response = api_client.post('/api/v1/auth/login/', data)
        assert response.status_code == 401
```

**Integration Tests:**
```python
@pytest.mark.django_db
class TestAddictionFlow:
    def test_complete_addiction_tracking_flow(self, authenticated_client):
        """Test full flow: add addiction → log event → check stats"""
        
        # 1. Add addiction
        response = authenticated_client.post('/api/v1/addictions/', {
            'addiction_type': 'alcohol',
            'baseline_amount': 15,
            'sobriety_start_date': timezone.now().isoformat()
        })
        assert response.status_code == 201
        addiction_id = response.data['id']
        
        # 2. Log consumption event
        response = authenticated_client.post('/api/v1/events/', {
            'addiction_id': addiction_id,
            'event_datetime': timezone.now().isoformat(),
            'amount': 3
        })
        assert response.status_code == 201
        
        # 3. Check dashboard reflects event
        response = authenticated_client.get('/api/v1/dashboard/')
        assert response.status_code == 200
        assert response.data['today']['is_clean'] == False
```

### 10.3 Frontend Testing

**Widget Tests (Flutter):**
```dart
// test/widgets/sobriety_counter_test.dart
import 'package:flutter_test/flutter_test.dart';

void main() {
  testWidgets('SobrietyCounter displays correct time', (WidgetTester tester) async {
    final startDate = DateTime.now().subtract(Duration(days: 7, hours: 5));
    
    await tester.pumpWidget(
      MaterialApp(
        home: SobrietyCounter(
          startDate: startDate,
          addictionType: 'alcohol',
        ),
      ),
    );
    
    // Verify days display
    expect(find.text('7'), findsOneWidget);
    expect(find.text('Days'), findsOneWidget);
    
    // Verify hours display
    expect(find.text('5'), findsOneWidget);
    expect(find.text('Hours'), findsOneWidget);
  });
}
```

**Integration Tests:**
```dart
// integration_test/app_test.dart
void main() {
  testWidgets('Complete onboarding flow', (WidgetTester tester) async {
    app.main();
    await tester.pumpAndSettle();
    
    // Select language
    await tester.tap(find.text('Deutsch'));
    await tester.pumpAndSettle();
    
    // Select addiction
    await tester.tap(find.text('Alkohol'));
    await tester.pumpAndSettle();
    
    // Complete assessment
    for (int i = 0; i < 10; i++) {
      await tester.tap(find.byType(RadioButton).first);
      await tester.tap(find.text('Next'));
      await tester.pumpAndSettle();
    }
    
    // Verify reached dashboard
    expect(find.text('Dashboard'), findsOneWidget);
  });
}
```

### 10.4 Test Coverage Goals

- Backend: > 80% code coverage
- Frontend: > 70% code coverage
- Critical paths: 100% coverage

---

## 11. Deployment

### 11.1 Environments

**Development:**
- Local Docker setup
- PostgreSQL (localhost:15432)
- Redis (localhost:16379)
- Django debug mode ON

**Staging:**
- AWS/DigitalOcean
- Smaller instance sizes
- Real PostgreSQL/Redis
- Test data only

**Production:**
- AWS/DigitalOcean
- High availability setup
- Automated backups
- SSL certificates

### 11.2 Backend Deployment (Docker)

**Dockerfile:**
```dockerfile
FROM python:3.12-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    postgresql-client \
    && rm -rf /var/lib/apt/lists/*

# Install Python dependencies
COPY requirements/production.txt .
RUN pip install --no-cache-dir -r production.txt

# Copy application
COPY . .

# Collect static files
RUN python manage.py collectstatic --noinput

# Run gunicorn
CMD ["gunicorn", "config.wsgi:application", "--bind", "0.0.0.0:8000"]
```

**docker-compose.production.yml:**
```yaml
version: '3.8'

services:
  db:
    image: postgres:15
    environment:
      POSTGRES_DB: ${DB_NAME}
      POSTGRES_USER: ${DB_USER}
      POSTGRES_PASSWORD: ${DB_PASSWORD}
    volumes:
      - postgres_data:/var/lib/postgresql/data
  
  redis:
    image: redis:7-alpine
    volumes:
      - redis_data:/data
  
  web:
    build: .
    command: gunicorn config.wsgi:application --bind 0.0.0.0:8000
    volumes:
      - static_volume:/app/staticfiles
      - media_volume:/app/media
    depends_on:
      - db
      - redis
    environment:
      - ENV_STAGE=production
  
  celery:
    build: .
    command: celery -A config worker -l info
    depends_on:
      - db
      - redis
  
  celery-beat:
    build: .
    command: celery -A config beat -l info
    depends_on:
      - db
      - redis
  
  nginx:
    image: nginx:alpine
    ports:
      - "80:80"
      - "443:443"
    volumes:
      - ./nginx.conf:/etc/nginx/nginx.conf
      - static_volume:/static
      - media_volume:/media
    depends_on:
      - web

volumes:
  postgres_data:
  redis_data:
  static_volume:
  media_volume:
```

### 11.3 CI/CD Pipeline (GitHub Actions)

```yaml
# .github/workflows/deploy.yml
name: Deploy to Production

on:
  push:
    branches: [main]

jobs:
  test:
    runs-on: ubuntu-latest
    
    services:
      postgres:
        image: postgres:15
        env:
          POSTGRES_PASSWORD: postgres
        options: >-
          --health-cmd pg_isready
          --health-interval 10s
          --health-timeout 5s
          --health-retries 5
    
    steps:
      - uses: actions/checkout@v3
      
      - name: Set up Python
        uses: actions/setup-python@v4
        with:
          python-version: '3.12'
      
      - name: Install dependencies
        run: |
          pip install -r requirements/development.txt
      
      - name: Run tests
        run: |
          pytest --cov=apps --cov-report=xml
      
      - name: Upload coverage
        uses: codecov/codecov-action@v3
  
  deploy:
    needs: test
    runs-on: ubuntu-latest
    
    steps:
      - uses: actions/checkout@v3
      
      - name: Deploy to server
        uses: appleboy/ssh-action@master
        with:
          host: ${{ secrets.SERVER_HOST }}
          username: ${{ secrets.SERVER_USER }}
          key: ${{ secrets.SSH_PRIVATE_KEY }}
          script: |
            cd /app
            git pull origin main
            docker-compose -f docker-compose.production.yml up -d --build
            docker-compose exec web python manage.py migrate
            docker-compose exec web python manage.py collectstatic --noinput
```

### 11.4 Mobile App Deployment

**iOS (TestFlight):**
```bash
# Build for iOS
flutter build ios --release

# Upload to App Store Connect
# (via Xcode or Transporter app)
```

**Android (Google Play):**
```bash
# Build for Android
flutter build appbundle --release

# Upload to Google Play Console
```

---

## 12. Milestones & Timeline

### Phase 1: Foundation (Weeks 1-4)

**Backend:**
- ✅ Project setup (Django, DRF)
- ✅ User authentication
- ✅ Database models
- ✅ Basic API endpoints

**Frontend:**
- ✅ Flutter project setup
- ✅ Design system
- ✅ Authentication screens
- ✅ Basic navigation

### Phase 2: Core Features (Weeks 5-8)

**Backend:**
- ✅ Addiction management
- ✅ Event logging
- ✅ Assessment questionnaires
- ✅ OpenAI integration

**Frontend:**
- ✅ Onboarding flow
- ✅ Dashboard
- ✅ Event logging
- ✅ Calendar view

### Phase 3: Polish & Testing (Weeks 9-10)

- ✅ Push notifications
- ✅ Charts & analytics
- ✅ Sharing functionality
- ✅ PDF export
- ✅ Comprehensive testing
- ✅ Bug fixes

### Phase 4: Deployment (Week 11-12)

- ✅ Production setup
- ✅ Beta testing
- ✅ App store submission
- ✅ Launch! 🚀

---

## Appendix A: Database Schema

```sql
-- Users and Authentication
CREATE TABLE users (
    id UUID PRIMARY KEY,
    email VARCHAR(255) UNIQUE NOT NULL,
    password_hash VARCHAR(255) NOT NULL,
    first_name VARCHAR(100),
    last_name VARCHAR(100),
    date_of_birth DATE,
    gender VARCHAR(20),
    country VARCHAR(2),
    language VARCHAR(2),
    phone VARCHAR(20),
    profile_picture VARCHAR(500),
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);

-- User Profiles
CREATE TABLE user_profiles (
    id UUID PRIMARY KEY,
    user_id UUID REFERENCES users(id),
    onboarding_completed BOOLEAN DEFAULT FALSE,
    severity_score INTEGER,
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);

-- Addictions
CREATE TABLE user_addictions (
    id UUID PRIMARY KEY,
    user_id UUID REFERENCES users(id),
    addiction_type VARCHAR(50),
    is_primary BOOLEAN DEFAULT FALSE,
    baseline_amount DECIMAL(10,2),
    baseline_frequency VARCHAR(20),
    baseline_cost_chf DECIMAL(10,2),
    sobriety_start_date TIMESTAMP,
    current_streak_days INTEGER DEFAULT 0,
    longest_streak_days INTEGER DEFAULT 0,
    last_consumption_date TIMESTAMP,
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW(),
    UNIQUE(user_id, addiction_type)
);

-- Consumption Events
CREATE TABLE consumption_events (
    id UUID PRIMARY KEY,
    user_id UUID REFERENCES users(id),
    addiction_id UUID REFERENCES user_addictions(id),
    event_datetime TIMESTAMP NOT NULL,
    amount DECIMAL(10,2),
    notes TEXT,
    location VARCHAR(200),
    mood_before VARCHAR(50),
    mood_after VARCHAR(50),
    photo VARCHAR(500),
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);

-- Assessment Results
CREATE TABLE assessment_results (
    id UUID PRIMARY KEY,
    user_id UUID REFERENCES users(id),
    addiction_type VARCHAR(50),
    questionnaire_type VARCHAR(50),
    responses JSONB,
    raw_score INTEGER,
    severity_level VARCHAR(20),
    ai_analysis TEXT,
    created_at TIMESTAMP DEFAULT NOW()
);

-- Triggers
CREATE TABLE triggers (
    id UUID PRIMARY KEY,
    name VARCHAR(100) UNIQUE,
    category VARCHAR(50)
);

CREATE TABLE event_triggers (
    event_id UUID REFERENCES consumption_events(id),
    trigger_id UUID REFERENCES triggers(id),
    PRIMARY KEY (event_id, trigger_id)
);

-- Shared Dashboards
CREATE TABLE shared_dashboards (
    id UUID PRIMARY KEY,
    patient_id UUID REFERENCES users(id),
    share_token UUID UNIQUE,
    share_all_addictions BOOLEAN DEFAULT TRUE,
    can_view_notes BOOLEAN DEFAULT FALSE,
    can_view_triggers BOOLEAN DEFAULT TRUE,
    can_view_mood BOOLEAN DEFAULT TRUE,
    recipient_email VARCHAR(255),
    password_protected BOOLEAN DEFAULT FALSE,
    access_password VARCHAR(128),
    expires_at TIMESTAMP,
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT NOW(),
    last_accessed_at TIMESTAMP,
    access_count INTEGER DEFAULT 0
);

-- Notification Settings
CREATE TABLE notification_settings (
    id UUID PRIMARY KEY,
    user_id UUID REFERENCES users(id) UNIQUE,
    enabled BOOLEAN DEFAULT TRUE,
    quiet_hours_start TIME,
    quiet_hours_end TIME,
    daily_pledge_enabled BOOLEAN DEFAULT TRUE,
    daily_pledge_time TIME,
    motivational_enabled BOOLEAN DEFAULT TRUE,
    motivational_frequency VARCHAR(20),
    reminder_enabled BOOLEAN DEFAULT TRUE,
    reminder_time TIME,
    milestone_enabled BOOLEAN DEFAULT TRUE,
    language VARCHAR(2)
);
```

---

## Appendix B: Glossary

| Term | Definition |
|------|------------|
| Addiction | A treatable, chronic medical disease involving complex interactions among brain circuits, genetics, the environment, and an individual's life experiences |
| Baseline | The starting point or reference level of consumption before recovery begins |
| Clean Day | A day without consumption of the addictive substance or behavior |
| Harm Reduction | An approach focused on reducing negative consequences rather than complete abstinence |
| Milestone | Significant achievement markers in recovery (e.g., 7 days, 30 days, 1 year) |
| PHI | Protected Health Information - sensitive medical data requiring special handling |
| Relapse | Return to substance use or addictive behavior after a period of abstinence |
| Severity Score | Numerical assessment of addiction intensity based on standardized questionnaires |
| Sobriety | The state of abstaining from addictive substances or behaviors |
| Streak | Consecutive days of clean time without consumption |
| Trigger | A stimulus that causes craving or leads to relapse |

---

## 13. Post-MVP Security Enhancements

### 13.1 Login Attempt Logging & Account Lockout

**Приоритет:** HIGH (Post-MVP)
**Story Points:** 8

**Описание:**
Расширенная система логирования попыток входа и блокировки аккаунтов.

**Требования:**

1. **Логирование попыток входа:**
   - ✅ БД: хранить 90 дней, показывать пользователю историю входов
   - ✅ Файлы: хранить 2 года для compliance
   - ✅ Sentry: мониторинг атак (Free Tier)

2. **Блокировка аккаунта (MVP):**
```python
LOCKOUT_SETTINGS = {
    'patient': {
        'max_attempts': 5,
        'lockout_duration': '30 minutes',
        'unlock_via': ['time', 'email']
    }
}
```

3. **Database model:**
```python
class LoginAttempt(TimeStampedModel):
    user = ForeignKey(User, null=True)  # null for non-existing emails
    email = EmailField()
    ip_address = GenericIPAddressField()
    user_agent = TextField()
    success = BooleanField()
    failure_reason = CharField(null=True)  # invalid_password, unverified, locked
    location = CharField(null=True)  # GeoIP
    created_at = DateTimeField(auto_now_add=True)

    class Meta:
        indexes = [
            models.Index(fields=['user', '-created_at']),
            models.Index(fields=['ip_address', '-created_at']),
        ]
```

---

### 13.2 Phase 2: Production Security

**Приоритет:** MEDIUM (Post-MVP)
**Story Points:** 21

**Расширенные функции безопасности:**

- ✅ Разные политики блокировки для пациентов/терапевтов
- ✅ Geolocation-based anomaly detection
- ✅ 2FA для medical staff (TOTP/SMS)
- ✅ Email уведомления о входе с новых устройств
- ✅ Emergency access для критических ситуаций
- ✅ Device fingerprinting
- ✅ Session management (view/revoke active sessions)

---

### 13.3 Compliance Requirements

#### HIPAA (США - если планируется выход):

| Requirement | Status | Notes |
|-------------|--------|-------|
| Audit trail | 🔲 | Хранить 6+ лет |
| Auto-logout | 🔲 | После неактивности |
| Unique user IDs | ✅ | UUID implemented |
| Emergency access | 🔲 | Break-glass mechanism |
| Encryption at rest | ✅ | AES-256 |
| Access controls | ✅ | Role-based |

#### GDPR (Европа/Швейцария):

| Requirement | Status | Notes |
|-------------|--------|-------|
| Right to be forgotten | 🔲 | Account deletion |
| Data export | 🔲 | JSON/PDF export |
| Consent management | ✅ | terms_accepted tracking |
| Breach notification | 🔲 | 24-48 часов |
| Data minimization | ✅ | Only necessary data |
| Privacy by design | ✅ | Architecture level |

#### Swiss Regulations:

| Requirement | Status | Notes |
|-------------|--------|-------|
| FADP compliance | 🔲 | Federal Act on Data Protection |
| Medical secrecy | 🔲 | Professional secrecy rules |
| Cross-border restrictions | 🔲 | Data localization |
| DSG (new law 2023) | 🔲 | Revised data protection |

---

### 13.4 Security Response Codes (Future)

**Refined HTTP responses for authentication:**

| Scenario | Current (MVP) | Future |
|----------|---------------|--------|
| Invalid credentials | 401 | 401 + attempt count |
| Email not verified | 403 | 403 + user_id for resend |
| Account locked | 403 | 423 Locked + unlock time |
| Too many attempts (IP) | 429 | 429 + retry-after header |
| Suspicious activity | N/A | 403 + verification required |

---

**Document Version:** 1.1
**Last Updated:** December 6, 2025
**Status:** Ready for Implementation
**Next Review:** After MVP completion

---

*This SRS document is a living document and will be updated as the project evolves.*