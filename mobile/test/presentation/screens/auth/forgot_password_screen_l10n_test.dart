import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:flutter_test/flutter_test.dart';
import 'package:go_router/go_router.dart';
import 'package:altea_mobile/presentation/screens/auth/forgot_password_screen.dart';
import 'package:altea_mobile/data/repositories/auth_repository.dart';
import 'package:altea_mobile/l10n/app_localizations.dart';

import '../../../helpers/test_helpers.dart';

void main() {
  late MockAuthRepository mockRepository;

  setUp(() {
    mockRepository = MockAuthRepository();
  });

  Widget createTestWidget({required Locale locale}) {
    final router = GoRouter(
      initialLocation: '/forgot-password',
      routes: [
        GoRoute(
          path: '/forgot-password',
          builder: (context, state) => const ForgotPasswordScreen(),
        ),
      ],
    );

    return ProviderScope(
      overrides: [
        authRepositoryProvider.overrideWithValue(mockRepository),
      ],
      child: MaterialApp.router(
        routerConfig: router,
        localizationsDelegates: AppLocalizations.localizationsDelegates,
        supportedLocales: AppLocalizations.supportedLocales,
        locale: locale,
      ),
    );
  }

  group('ForgotPasswordScreen Localization', () {
    testWidgets('should display English text', (tester) async {
      await tester.pumpWidget(createTestWidget(locale: const Locale('en')));
      await tester.pumpAndSettle();

      expect(find.text('Forgot Password'), findsWidgets);
      expect(find.text('Enter your email to receive reset instructions'),
          findsOneWidget);
      expect(find.text('Send Reset Link'), findsOneWidget);
      expect(find.text('Back to Sign In'), findsOneWidget);
    });

    testWidgets('should display German text', (tester) async {
      await tester.pumpWidget(createTestWidget(locale: const Locale('de')));
      await tester.pumpAndSettle();

      expect(find.text('Passwort vergessen'), findsWidgets);
      expect(
          find.text(
              'Geben Sie Ihre E-Mail ein, um Anweisungen zum Zurücksetzen zu erhalten'),
          findsOneWidget);
      expect(find.text('Link senden'), findsOneWidget);
      expect(find.text('Zurück zur Anmeldung'), findsOneWidget);
    });

    testWidgets('should display French text', (tester) async {
      await tester.pumpWidget(createTestWidget(locale: const Locale('fr')));
      await tester.pumpAndSettle();

      expect(find.text('Mot de passe oublié'), findsWidgets);
      expect(find.text('Entrez votre e-mail pour recevoir les instructions'),
          findsOneWidget);
      expect(find.text('Envoyer le lien'), findsOneWidget);
      expect(find.text('Retour à la connexion'), findsOneWidget);
    });

    testWidgets('should display Italian text', (tester) async {
      await tester.pumpWidget(createTestWidget(locale: const Locale('it')));
      await tester.pumpAndSettle();

      expect(find.text('Password dimenticata'), findsWidgets);
      expect(
          find.text('Inserisci la tua email per ricevere le istruzioni'),
          findsOneWidget);
      expect(find.text('Invia link'), findsOneWidget);
      expect(find.text('Torna all\'accesso'), findsOneWidget);
    });

    testWidgets('should display localized success message in English',
        (tester) async {
      await tester.pumpWidget(createTestWidget(locale: const Locale('en')));
      await tester.pumpAndSettle();

      // Submit valid email
      await tester.enterText(find.byType(TextField), 'test@example.com');
      await tester.tap(find.text('Send Reset Link'));
      await tester.pumpAndSettle();

      expect(find.text('Check your email'), findsOneWidget);
      expect(
          find.text(
              'If an account exists with this email, you will receive password reset instructions.'),
          findsOneWidget);
    });

    testWidgets('should display localized success message in German',
        (tester) async {
      await tester.pumpWidget(createTestWidget(locale: const Locale('de')));
      await tester.pumpAndSettle();

      // Submit valid email
      await tester.enterText(find.byType(TextField), 'test@example.com');
      await tester.tap(find.text('Link senden'));
      await tester.pumpAndSettle();

      expect(find.text('Prüfen Sie Ihre E-Mail'), findsOneWidget);
      expect(
          find.text(
              'Wenn ein Konto mit dieser E-Mail existiert, erhalten Sie Anweisungen zum Zurücksetzen des Passworts.'),
          findsOneWidget);
    });

    testWidgets('should display localized success message in French',
        (tester) async {
      await tester.pumpWidget(createTestWidget(locale: const Locale('fr')));
      await tester.pumpAndSettle();

      // Submit valid email
      await tester.enterText(find.byType(TextField), 'test@example.com');
      await tester.tap(find.text('Envoyer le lien'));
      await tester.pumpAndSettle();

      expect(find.text('Vérifiez votre e-mail'), findsOneWidget);
      expect(
          find.text(
              'Si un compte existe avec cet e-mail, vous recevrez les instructions de réinitialisation.'),
          findsOneWidget);
    });

    testWidgets('should display localized success message in Italian',
        (tester) async {
      await tester.pumpWidget(createTestWidget(locale: const Locale('it')));
      await tester.pumpAndSettle();

      // Submit valid email
      await tester.enterText(find.byType(TextField), 'test@example.com');
      await tester.tap(find.text('Invia link'));
      await tester.pumpAndSettle();

      expect(find.text('Controlla la tua email'), findsOneWidget);
      expect(
          find.text(
              'Se esiste un account con questa email, riceverai le istruzioni per reimpostare la password.'),
          findsOneWidget);
    });
  });
}
