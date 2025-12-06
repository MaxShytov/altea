import 'package:flutter/material.dart';
import 'package:flutter_localizations/flutter_localizations.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:flutter_test/flutter_test.dart';
import 'package:go_router/go_router.dart';
import 'package:altea_mobile/data/repositories/auth_repository.dart';
import 'package:altea_mobile/l10n/app_localizations.dart';
import 'package:altea_mobile/presentation/screens/auth/registration_screen.dart';

import '../../../helpers/test_helpers.dart';

void main() {
  group('RegistrationScreen Localization Tests', () {
    late MockAuthRepository mockRepository;

    setUp(() {
      mockRepository = MockAuthRepository();
    });

    Widget createLocalizedRegistrationWidget({
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
            initialLocation: '/register',
            routes: [
              GoRoute(
                path: '/register',
                builder: (context, state) => const RegistrationScreen(),
              ),
              GoRoute(
                path: '/login',
                builder: (context, state) =>
                    const Scaffold(body: Text('Login Screen')),
              ),
              GoRoute(
                path: '/email-sent',
                builder: (context, state) =>
                    const Scaffold(body: Text('Email Sent Screen')),
              ),
              GoRoute(
                path: '/terms',
                builder: (context, state) =>
                    const Scaffold(body: Text('Terms Screen')),
              ),
              GoRoute(
                path: '/privacy',
                builder: (context, state) =>
                    const Scaffold(body: Text('Privacy Screen')),
              ),
            ],
          ),
        ),
      );
    }

    group('English Locale', () {
      testWidgets('should display all texts in English',
          (WidgetTester tester) async {
        await tester.pumpWidget(createLocalizedRegistrationWidget(
          locale: const Locale('en'),
        ));
        await tester.pumpAndSettle();

        // AppBar title
        expect(find.text('Create Account'), findsWidgets);

        // Header texts
        expect(find.text('Join Altea'), findsOneWidget);
        expect(find.text('Create your account to get started'), findsOneWidget);

        // Form labels
        expect(find.text('Email'), findsOneWidget);
        expect(find.text('First Name'), findsOneWidget);
        expect(find.text('Last Name'), findsOneWidget);
        expect(find.text('Password'), findsOneWidget);
        expect(find.text('Confirm Password'), findsOneWidget);

        // Terms - uses RichText with Text.rich, check Checkbox exists
        expect(find.byType(Checkbox), findsOneWidget);

        // Links
        expect(find.text('Already have an account?'), findsOneWidget);
        expect(find.text('Sign In'), findsOneWidget);
      });

      testWidgets('should show English validation errors for empty fields',
          (WidgetTester tester) async {
        await tester.pumpWidget(createLocalizedRegistrationWidget(
          locale: const Locale('en'),
        ));
        await tester.pumpAndSettle();

        // Scroll to submit button and tap
        await tester.drag(
            find.byType(SingleChildScrollView), const Offset(0, -300));
        await tester.pumpAndSettle();
        await tester.tap(find.widgetWithText(FilledButton, 'Create Account'));
        await tester.pumpAndSettle();

        // Check validation errors
        expect(find.text('Email is required'), findsOneWidget);
        expect(find.text('First Name is required'), findsOneWidget);
        expect(find.text('Last Name is required'), findsOneWidget);
        expect(find.text('Password is required'), findsOneWidget);
        expect(find.text('Please confirm your password'), findsOneWidget);
      });

      testWidgets('should show English password mismatch error',
          (WidgetTester tester) async {
        await tester.pumpWidget(createLocalizedRegistrationWidget(
          locale: const Locale('en'),
        ));
        await tester.pumpAndSettle();

        // Fill all required fields
        await tester.enterText(
            find.byType(TextField).at(0), 'test@example.com');
        await tester.enterText(find.byType(TextField).at(1), 'John');
        await tester.enterText(find.byType(TextField).at(2), 'Doe');
        await tester.enterText(find.byType(TextField).at(3), 'password123');
        await tester.enterText(
            find.byType(TextField).at(4), 'different123'); // Different password

        // Scroll and submit
        await tester.drag(
            find.byType(SingleChildScrollView), const Offset(0, -300));
        await tester.pumpAndSettle();
        await tester.tap(find.widgetWithText(FilledButton, 'Create Account'));
        await tester.pumpAndSettle();

        expect(find.text('Passwords do not match'), findsOneWidget);
      });

      testWidgets('should show English min length errors',
          (WidgetTester tester) async {
        await tester.pumpWidget(createLocalizedRegistrationWidget(
          locale: const Locale('en'),
        ));
        await tester.pumpAndSettle();

        // Fill fields with short values
        await tester.enterText(
            find.byType(TextField).at(0), 'test@example.com');
        await tester.enterText(find.byType(TextField).at(1), 'J'); // Too short
        await tester.enterText(find.byType(TextField).at(2), 'D'); // Too short
        await tester.enterText(find.byType(TextField).at(3), 'pass'); // Too short
        await tester.enterText(find.byType(TextField).at(4), 'pass');

        // Scroll and submit
        await tester.drag(
            find.byType(SingleChildScrollView), const Offset(0, -300));
        await tester.pumpAndSettle();
        await tester.tap(find.widgetWithText(FilledButton, 'Create Account'));
        await tester.pumpAndSettle();

        expect(find.text('First Name must be at least 2 characters'),
            findsOneWidget);
        expect(find.text('Last Name must be at least 2 characters'),
            findsOneWidget);
        expect(find.text('Password must be at least 8 characters'),
            findsOneWidget);
      });
    });

    group('German Locale', () {
      testWidgets('should display all texts in German',
          (WidgetTester tester) async {
        await tester.pumpWidget(createLocalizedRegistrationWidget(
          locale: const Locale('de'),
        ));
        await tester.pumpAndSettle();

        // AppBar title
        expect(find.text('Konto erstellen'), findsWidgets);

        // Header texts
        expect(find.text('Altea beitreten'), findsOneWidget);
        expect(find.text('Erstellen Sie Ihr Konto, um zu beginnen'),
            findsOneWidget);

        // Form labels
        expect(find.text('E-Mail'), findsOneWidget);
        expect(find.text('Vorname'), findsWidgets);
        expect(find.text('Nachname'), findsWidgets);
        expect(find.text('Passwort'), findsOneWidget);
        expect(find.text('Passwort bestätigen'), findsOneWidget);

        // Terms - uses RichText with Text.rich, check Checkbox exists
        expect(find.byType(Checkbox), findsOneWidget);

        // Links
        expect(find.text('Bereits ein Konto?'), findsOneWidget);
        expect(find.text('Anmelden'), findsOneWidget);
      });

      testWidgets('should show German validation errors',
          (WidgetTester tester) async {
        await tester.pumpWidget(createLocalizedRegistrationWidget(
          locale: const Locale('de'),
        ));
        await tester.pumpAndSettle();

        // Scroll to submit button and tap
        await tester.drag(
            find.byType(SingleChildScrollView), const Offset(0, -300));
        await tester.pumpAndSettle();
        await tester
            .tap(find.widgetWithText(FilledButton, 'Konto erstellen'));
        await tester.pumpAndSettle();

        // Check validation errors
        expect(find.text('E-Mail ist erforderlich'), findsOneWidget);
        expect(find.text('Vorname ist erforderlich'), findsOneWidget);
        expect(find.text('Nachname ist erforderlich'), findsOneWidget);
        expect(find.text('Passwort ist erforderlich'), findsOneWidget);
        expect(
            find.text('Bitte bestätigen Sie Ihr Passwort'), findsOneWidget);
      });
    });

    group('French Locale', () {
      testWidgets('should display all texts in French',
          (WidgetTester tester) async {
        await tester.pumpWidget(createLocalizedRegistrationWidget(
          locale: const Locale('fr'),
        ));
        await tester.pumpAndSettle();

        // AppBar title
        expect(find.text('Créer un compte'), findsWidgets);

        // Header texts
        expect(find.text('Rejoignez Altea'), findsOneWidget);
        expect(find.text('Créez votre compte pour commencer'), findsOneWidget);

        // Form labels
        expect(find.text('E-mail'), findsOneWidget);
        expect(find.text('Prénom'), findsWidgets);
        expect(find.text('Nom'), findsWidgets);
        expect(find.text('Mot de passe'), findsOneWidget);
        expect(find.text('Confirmer le mot de passe'), findsOneWidget);

        // Terms - uses RichText with Text.rich, check Checkbox exists
        expect(find.byType(Checkbox), findsOneWidget);

        // Links
        expect(find.text('Déjà un compte ?'), findsOneWidget);
        expect(find.text('Connexion'), findsOneWidget);
      });

      testWidgets('should show French validation errors',
          (WidgetTester tester) async {
        await tester.pumpWidget(createLocalizedRegistrationWidget(
          locale: const Locale('fr'),
        ));
        await tester.pumpAndSettle();

        // Scroll to submit button and tap
        await tester.drag(
            find.byType(SingleChildScrollView), const Offset(0, -300));
        await tester.pumpAndSettle();
        await tester
            .tap(find.widgetWithText(FilledButton, 'Créer un compte'));
        await tester.pumpAndSettle();

        // Check validation errors
        expect(find.text("L'e-mail est requis"), findsOneWidget);
        expect(find.text('Prénom est requis'), findsOneWidget);
        expect(find.text('Nom est requis'), findsOneWidget);
        expect(find.text('Le mot de passe est requis'), findsOneWidget);
        expect(
            find.text('Veuillez confirmer votre mot de passe'), findsOneWidget);
      });
    });

    group('Italian Locale', () {
      testWidgets('should display all texts in Italian',
          (WidgetTester tester) async {
        await tester.pumpWidget(createLocalizedRegistrationWidget(
          locale: const Locale('it'),
        ));
        await tester.pumpAndSettle();

        // AppBar title
        expect(find.text('Crea account'), findsWidgets);

        // Header texts
        expect(find.text('Unisciti a Altea'), findsOneWidget);
        expect(
            find.text('Crea il tuo account per iniziare'), findsOneWidget);

        // Form labels
        expect(find.text('Email'), findsWidgets);
        expect(find.text('Nome'), findsWidgets);
        expect(find.text('Cognome'), findsWidgets);
        expect(find.text('Password'), findsWidgets);
        expect(find.text('Conferma password'), findsOneWidget);

        // Terms - uses RichText with Text.rich, check Checkbox exists
        expect(find.byType(Checkbox), findsOneWidget);

        // Links
        expect(find.text('Hai già un account?'), findsOneWidget);
        expect(find.text('Accedi'), findsOneWidget);
      });

      testWidgets('should show Italian validation errors',
          (WidgetTester tester) async {
        await tester.pumpWidget(createLocalizedRegistrationWidget(
          locale: const Locale('it'),
        ));
        await tester.pumpAndSettle();

        // Scroll to submit button and tap
        await tester.drag(
            find.byType(SingleChildScrollView), const Offset(0, -300));
        await tester.pumpAndSettle();
        await tester.tap(find.widgetWithText(FilledButton, 'Crea account'));
        await tester.pumpAndSettle();

        // Check validation errors
        expect(find.text("L'email è obbligatoria"), findsOneWidget);
        expect(find.text('Nome è obbligatorio'), findsOneWidget);
        expect(find.text('Cognome è obbligatorio'), findsOneWidget);
        expect(find.text('La password è obbligatoria'), findsOneWidget);
        expect(find.text('Per favore conferma la tua password'), findsOneWidget);
      });
    });

    group('Terms Acceptance Validation', () {
      testWidgets('should show English terms acceptance error',
          (WidgetTester tester) async {
        await tester.pumpWidget(createLocalizedRegistrationWidget(
          locale: const Locale('en'),
        ));
        await tester.pumpAndSettle();

        // Fill all required fields
        await tester.enterText(
            find.byType(TextField).at(0), 'test@example.com');
        await tester.enterText(find.byType(TextField).at(1), 'John');
        await tester.enterText(find.byType(TextField).at(2), 'Doe');
        await tester.enterText(find.byType(TextField).at(3), 'password123');
        await tester.enterText(find.byType(TextField).at(4), 'password123');

        // Don't check terms checkbox
        // Scroll and submit
        await tester.drag(
            find.byType(SingleChildScrollView), const Offset(0, -300));
        await tester.pumpAndSettle();
        await tester.tap(find.widgetWithText(FilledButton, 'Create Account'));
        await tester.pumpAndSettle();

        // Check snackbar message
        expect(find.text('Please accept the Terms & Conditions'), findsOneWidget);
      });

      testWidgets('should show German terms acceptance error',
          (WidgetTester tester) async {
        await tester.pumpWidget(createLocalizedRegistrationWidget(
          locale: const Locale('de'),
        ));
        await tester.pumpAndSettle();

        // Fill all required fields
        await tester.enterText(
            find.byType(TextField).at(0), 'test@example.com');
        await tester.enterText(find.byType(TextField).at(1), 'Hans');
        await tester.enterText(find.byType(TextField).at(2), 'Müller');
        await tester.enterText(find.byType(TextField).at(3), 'password123');
        await tester.enterText(find.byType(TextField).at(4), 'password123');

        // Scroll and submit without checking terms
        await tester.drag(
            find.byType(SingleChildScrollView), const Offset(0, -300));
        await tester.pumpAndSettle();
        await tester
            .tap(find.widgetWithText(FilledButton, 'Konto erstellen'));
        await tester.pumpAndSettle();

        // Check snackbar message
        expect(find.text('Bitte akzeptieren Sie die Nutzungsbedingungen'),
            findsOneWidget);
      });
    });
  });
}
