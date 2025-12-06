import 'package:flutter/material.dart';
import 'package:flutter_localizations/flutter_localizations.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:flutter_test/flutter_test.dart';
import 'package:go_router/go_router.dart';
import 'package:altea_mobile/data/repositories/auth_repository.dart';
import 'package:altea_mobile/l10n/app_localizations.dart';
import 'package:altea_mobile/presentation/screens/auth/login_screen.dart';

import '../../../helpers/test_helpers.dart';

void main() {
  group('LoginScreen Localization Tests', () {
    late MockAuthRepository mockRepository;

    setUp(() {
      mockRepository = MockAuthRepository();
    });

    Widget createLocalizedLoginWidget({
      required Locale locale,
      MockAuthRepository? repository,
    }) {
      final repo = repository ?? mockRepository;

      return ProviderScope(
        overrides: [
          authRepositoryProvider.overrideWithValue(repo),
        ],
        child: MaterialApp.router(
          locale: locale,
          localizationsDelegates: const [
            AppLocalizations.delegate,
            GlobalMaterialLocalizations.delegate,
            GlobalWidgetsLocalizations.delegate,
            GlobalCupertinoLocalizations.delegate,
          ],
          supportedLocales: const [
            Locale('en'),
            Locale('de'),
            Locale('fr'),
            Locale('it'),
          ],
          routerConfig: GoRouter(
            initialLocation: '/login',
            routes: [
              GoRoute(
                path: '/login',
                builder: (context, state) => const LoginScreen(),
              ),
              GoRoute(
                path: '/register',
                builder: (context, state) =>
                    const Scaffold(body: Text('Register Screen')),
              ),
              GoRoute(
                path: '/dashboard',
                builder: (context, state) =>
                    const Scaffold(body: Text('Dashboard')),
              ),
            ],
          ),
        ),
      );
    }

    group('English Locale', () {
      testWidgets('should display all texts in English',
          (WidgetTester tester) async {
        await tester.pumpWidget(createLocalizedLoginWidget(
          locale: const Locale('en'),
        ));
        await tester.pumpAndSettle();

        // AppBar title
        expect(find.text('Sign In'), findsWidgets);

        // Header texts
        expect(find.text('Welcome Back'), findsOneWidget);
        expect(
            find.text('Sign in to continue your journey'), findsOneWidget);

        // Form labels
        expect(find.text('Email'), findsOneWidget);
        expect(find.text('Password'), findsOneWidget);

        // Links and buttons
        expect(find.text('Forgot password?'), findsOneWidget);
        expect(find.text("Don't have an account?"), findsOneWidget);
        expect(find.text('Register'), findsOneWidget);
      });

      testWidgets('should show English validation errors',
          (WidgetTester tester) async {
        await tester.pumpWidget(createLocalizedLoginWidget(
          locale: const Locale('en'),
        ));
        await tester.pumpAndSettle();

        // Try to submit empty form
        await tester.tap(find.widgetWithText(FilledButton, 'Sign In'));
        await tester.pumpAndSettle();

        // Check validation errors
        expect(find.text('Email is required'), findsOneWidget);
        expect(find.text('Password is required'), findsOneWidget);
      });

      testWidgets('should show English invalid email error',
          (WidgetTester tester) async {
        await tester.pumpWidget(createLocalizedLoginWidget(
          locale: const Locale('en'),
        ));
        await tester.pumpAndSettle();

        // Enter invalid email
        await tester.enterText(find.byType(TextField).first, 'invalid-email');
        await tester.tap(find.widgetWithText(FilledButton, 'Sign In'));
        await tester.pumpAndSettle();

        expect(find.text('Please enter a valid email'), findsOneWidget);
      });
    });

    group('German Locale', () {
      testWidgets('should display all texts in German',
          (WidgetTester tester) async {
        await tester.pumpWidget(createLocalizedLoginWidget(
          locale: const Locale('de'),
        ));
        await tester.pumpAndSettle();

        // AppBar title
        expect(find.text('Anmelden'), findsWidgets);

        // Header texts
        expect(find.text('Willkommen zurück'), findsOneWidget);
        expect(find.text('Melden Sie sich an, um Ihre Reise fortzusetzen'),
            findsOneWidget);

        // Form labels
        expect(find.text('E-Mail'), findsOneWidget);
        expect(find.text('Passwort'), findsOneWidget);

        // Links and buttons
        expect(find.text('Passwort vergessen?'), findsOneWidget);
        expect(find.text('Noch kein Konto?'), findsOneWidget);
        expect(find.text('Registrieren'), findsOneWidget);
      });

      testWidgets('should show German validation errors',
          (WidgetTester tester) async {
        await tester.pumpWidget(createLocalizedLoginWidget(
          locale: const Locale('de'),
        ));
        await tester.pumpAndSettle();

        // Try to submit empty form
        await tester.tap(find.widgetWithText(FilledButton, 'Anmelden'));
        await tester.pumpAndSettle();

        // Check validation errors
        expect(find.text('E-Mail ist erforderlich'), findsOneWidget);
        expect(find.text('Passwort ist erforderlich'), findsOneWidget);
      });
    });

    group('French Locale', () {
      testWidgets('should display all texts in French',
          (WidgetTester tester) async {
        await tester.pumpWidget(createLocalizedLoginWidget(
          locale: const Locale('fr'),
        ));
        await tester.pumpAndSettle();

        // AppBar title
        expect(find.text('Connexion'), findsWidgets);

        // Header texts
        expect(find.text('Bon retour'), findsOneWidget);
        expect(find.text('Connectez-vous pour continuer votre parcours'),
            findsOneWidget);

        // Form labels
        expect(find.text('E-mail'), findsOneWidget);
        expect(find.text('Mot de passe'), findsOneWidget);

        // Links and buttons
        expect(find.text('Mot de passe oublié ?'), findsOneWidget);
        expect(find.text('Pas encore de compte ?'), findsOneWidget);
        expect(find.text("S'inscrire"), findsOneWidget);
      });

      testWidgets('should show French validation errors',
          (WidgetTester tester) async {
        await tester.pumpWidget(createLocalizedLoginWidget(
          locale: const Locale('fr'),
        ));
        await tester.pumpAndSettle();

        // Try to submit empty form
        await tester.tap(find.widgetWithText(FilledButton, 'Connexion'));
        await tester.pumpAndSettle();

        // Check validation errors
        expect(find.text("L'e-mail est requis"), findsOneWidget);
        expect(find.text('Le mot de passe est requis'), findsOneWidget);
      });
    });

    group('Italian Locale', () {
      testWidgets('should display all texts in Italian',
          (WidgetTester tester) async {
        await tester.pumpWidget(createLocalizedLoginWidget(
          locale: const Locale('it'),
        ));
        await tester.pumpAndSettle();

        // AppBar title
        expect(find.text('Accedi'), findsWidgets);

        // Header texts
        expect(find.text('Bentornato'), findsOneWidget);
        expect(find.text('Accedi per continuare il tuo percorso'),
            findsOneWidget);

        // Form labels
        expect(find.text('Email'), findsWidgets); // Email is same in EN/IT
        expect(find.text('Password'), findsWidgets); // Password is same in EN/IT

        // Links and buttons
        expect(find.text('Password dimenticata?'), findsOneWidget);
        expect(find.text('Non hai un account?'), findsOneWidget);
        expect(find.text('Registrati'), findsOneWidget);
      });

      testWidgets('should show Italian validation errors',
          (WidgetTester tester) async {
        await tester.pumpWidget(createLocalizedLoginWidget(
          locale: const Locale('it'),
        ));
        await tester.pumpAndSettle();

        // Try to submit empty form
        await tester.tap(find.widgetWithText(FilledButton, 'Accedi'));
        await tester.pumpAndSettle();

        // Check validation errors
        expect(find.text("L'email è obbligatoria"), findsOneWidget);
        expect(find.text('La password è obbligatoria'), findsOneWidget);
      });
    });

    group('Fallback Behavior', () {
      testWidgets('should fallback to English for unsupported locale',
          (WidgetTester tester) async {
        await tester.pumpWidget(createLocalizedLoginWidget(
          locale: const Locale('zh'), // Chinese - not supported
        ));
        await tester.pumpAndSettle();

        // Should display English texts
        expect(find.text('Sign In'), findsWidgets);
        expect(find.text('Welcome Back'), findsOneWidget);
      });
    });
  });
}
