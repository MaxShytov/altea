# Flutter Development Conventions - Altea

**Version:** 1.0 | **Last Updated:** December 2025

---

## 1. Architecture Overview

### Tech Stack

```yaml
Framework: Flutter 3.16+
Language: Dart 3.2+
State Management: Riverpod 2.4+
HTTP Client: Dio 5.4+
Local Storage: Hive 2.2+
Secure Storage: flutter_secure_storage 9.0+
Navigation: go_router 13.0+
```

### Key Principles

- **Clean Architecture**: UI, Domain, Data layers separation
- **Widget Composition**: Reusable, composable widgets (Atomic Design)
- **Apple HIG Compliance**: Follow iOS design patterns

---

## 2. Design Tokens

> **Full specifications:** [DESIGN_TOKENS.md](DESIGN_TOKENS.md)

| Token | Key Values |
|-------|------------|
| **Typography** | largeTitle (34pt), title1 (28pt), headline (17pt semibold), body (17pt), caption1 (12pt) |
| **Spacing** | xs=4, sm=8, md=12, lg=16, xl=20, xxl=24, screenHorizontal=16 |
| **Dimensions** | cornerRadius: 8/10/12/16, buttonHeight=50, inputHeight=44 |
| **Colors** | primary=#667EEA, secondary=#764BA2, success=#10B981, error=#EF4444 |

---

## 3. Widget Composition (Atomic Design)

### Widget Hierarchy

```
lib/presentation/widgets/
├── atoms/           # Basic widgets (buttons, inputs, text)
├── molecules/       # 2-5 atoms combined (cards, list_items, form_fields)
├── organisms/       # Feature-specific (forms, lists, sections)
├── templates/       # Layout patterns
└── screens/         # Complete screens with business logic
```

### Level Characteristics

| Level | State | Business Logic | Reusability |
|-------|-------|----------------|-------------|
| **Atom** | StatelessWidget | None | High |
| **Molecule** | Stateless/Stateful | Minimal | High |
| **Organism** | Stateful/Consumer | Feature-specific | Medium |
| **Template** | StatelessWidget | None | High |
| **Screen** | ConsumerWidget | Full | None |

### Decision Matrix

| If widget... | Then it's a... |
|--------------|----------------|
| Wraps 1 base widget | **Atom** |
| Combines 2-5 atoms | **Molecule** |
| Feature-specific, combines molecules | **Organism** |
| Defines layout structure | **Template** |
| Connected to state management | **Screen** |

### Widget Examples

```dart
// ATOM: atoms/altea_button.dart
class AlteaButton extends StatelessWidget {
  final String text;
  final VoidCallback onPressed;
  final bool isLoading;

  @override
  Widget build(BuildContext context) {
    return CupertinoButton(
      onPressed: isLoading ? null : onPressed,
      color: AlteaColors.primary,
      child: isLoading
          ? const CupertinoActivityIndicator(color: Colors.white)
          : Text(text, style: AlteaTypography.headline.copyWith(color: Colors.white)),
    );
  }
}

// MOLECULE: molecules/stat_card.dart
class StatCard extends StatelessWidget {
  final IconData icon;
  final String label;
  final String value;
  final Color color;

  @override
  Widget build(BuildContext context) {
    return Container(
      padding: const EdgeInsets.all(AlteaSpacing.lg),
      decoration: BoxDecoration(
        color: AlteaColors.secondarySystemBackground,
        borderRadius: BorderRadius.circular(AlteaDimensions.cornerRadiusLarge),
      ),
      child: Column(
        children: [
          Icon(icon, color: color),
          Text(value, style: AlteaTypography.title1.copyWith(color: color)),
          Text(label, style: AlteaTypography.caption1),
        ],
      ),
    );
  }
}

// ORGANISM: organisms/addiction_list.dart
class AddictionList extends ConsumerWidget {
  @override
  Widget build(BuildContext context, WidgetRef ref) {
    final addictionsAsync = ref.watch(addictionsListProvider);

    return addictionsAsync.when(
      data: (addictions) => ListView.builder(
        itemCount: addictions.length,
        itemBuilder: (context, index) => AddictionListTile(addiction: addictions[index]),
      ),
      loading: () => const CupertinoActivityIndicator(),
      error: (error, _) => ErrorMessage(message: error.toString()),
    );
  }
}

// SCREEN: screens/dashboard_screen.dart
class DashboardScreen extends ConsumerWidget {
  @override
  Widget build(BuildContext context, WidgetRef ref) {
    return ScrollableScreenLayout(
      title: 'Dashboard',
      body: Column(
        children: [
          DashboardHeader(user: ref.watch(currentUserProvider)),
          StatsGrid(stats: ref.watch(dashboardStatsProvider)),
          AddictionList(onTap: (a) => context.push('/addictions/${a.id}')),
        ],
      ),
    );
  }
}
```

---

## 4. Project Structure

```
lib/
├── main.dart
├── core/
│   ├── theme/         # colors, typography, spacing, dimensions
│   ├── constants/     # api_constants, app_constants
│   └── utils/         # date_utils, validators
├── data/
│   ├── models/        # user, addiction, consumption_event
│   ├── repositories/  # auth, addiction, assessment
│   └── data_sources/  # local/, remote/
├── domain/
│   ├── entities/
│   ├── repositories/  # Abstract interfaces
│   └── use_cases/
├── presentation/
│   ├── providers/     # Riverpod providers
│   ├── screens/       # auth/, onboarding/, dashboard/, addictions/
│   ├── widgets/       # atoms/, molecules/, organisms/
│   └── templates/
└── l10n/              # app_en.arb, app_de.arb, etc.
```

---

## 5. State Management (Riverpod)

```dart
// lib/presentation/providers/addiction_provider.dart
@riverpod
class AddictionsList extends _$AddictionsList {
  @override
  Future<List<UserAddiction>> build() async {
    return ref.watch(addictionRepositoryProvider).getAddictions();
  }

  Future<void> refresh() async {
    state = const AsyncValue.loading();
    state = await AsyncValue.guard(() => build());
  }
}

// Usage
class MyScreen extends ConsumerWidget {
  @override
  Widget build(BuildContext context, WidgetRef ref) {
    final addictionsAsync = ref.watch(addictionsListProvider);
    return addictionsAsync.when(
      data: (data) => ListView(...),
      loading: () => CupertinoActivityIndicator(),
      error: (e, _) => Text('Error: $e'),
    );
  }
}
```

---

## 6. Navigation (GoRouter)

```dart
final goRouter = GoRouter(
  initialLocation: '/splash',
  routes: [
    GoRoute(path: '/login', builder: (_, __) => const LoginScreen()),
    GoRoute(path: '/dashboard', builder: (_, __) => const DashboardScreen()),
    GoRoute(
      path: '/addictions/:id',
      builder: (_, state) => AddictionDetailScreen(id: state.pathParameters['id']!),
    ),
  ],
  redirect: (context, state) {
    final isLoggedIn = /* check auth */;
    if (!isLoggedIn && state.location != '/login') return '/login';
    return null;
  },
);

// Usage: context.push('/path'), context.go('/path'), context.pop()
```

---

## 7. API Integration (Dio)

```dart
class ApiClient {
  static const String baseUrl = 'https://api.altea.app/api/v1';
  final Dio _dio;

  ApiClient() : _dio = Dio(BaseOptions(baseUrl: baseUrl)) {
    _dio.interceptors.add(AuthInterceptor());
  }

  Future<List<UserAddiction>> getAddictions() async {
    final response = await _dio.get('/addictions/addictions/');
    return (response.data['results'] as List).map((j) => UserAddiction.fromJson(j)).toList();
  }
}

class AuthInterceptor extends Interceptor {
  @override
  Future<void> onRequest(RequestOptions options, handler) async {
    final token = await storage.read(key: 'access_token');
    if (token != null) options.headers['Authorization'] = 'Bearer $token';
    handler.next(options);
  }
}
```

---

## 8. Localization

```dart
// Usage
final l10n = AppLocalizations.of(context)!;
Text(l10n.dashboardTitle);
```

---

## Quick Reference

### New Feature Checklist

- [ ] Data model in `lib/data/models/`
- [ ] Repository in `lib/data/repositories/`
- [ ] Provider in `lib/presentation/providers/`
- [ ] Widgets (atoms → molecules → organisms)
- [ ] Screen in `lib/presentation/screens/`
- [ ] Route in `app_router.dart`
- [ ] Localization in `.arb` files

### Common Patterns

```dart
// Consumer Widget
class MyScreen extends ConsumerWidget {
  Widget build(BuildContext context, WidgetRef ref) {
    final state = ref.watch(myProvider);
  }
}

// Stateful with Riverpod
class MyScreen extends ConsumerStatefulWidget {
  ConsumerState<MyScreen> createState() => _MyScreenState();
}
```

---

**Remember:** Follow Apple HIG, keep widgets composable, maintain clean architecture!
