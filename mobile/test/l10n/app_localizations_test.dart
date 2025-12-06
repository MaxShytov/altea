import 'package:flutter/material.dart';
import 'package:flutter_test/flutter_test.dart';
import 'package:altea_mobile/l10n/app_localizations.dart';

import '../helpers/l10n_test_helpers.dart';

/// Unit tests for AppLocalizations functionality.
void main() {
  group('AppLocalizations', () {
    group('Delegate', () {
      test('should support English locale', () {
        expect(
          AppLocalizations.delegate.isSupported(const Locale('en')),
          isTrue,
        );
      });

      test('should support German locale', () {
        expect(
          AppLocalizations.delegate.isSupported(const Locale('de')),
          isTrue,
        );
      });

      test('should support French locale', () {
        expect(
          AppLocalizations.delegate.isSupported(const Locale('fr')),
          isTrue,
        );
      });

      test('should support Italian locale', () {
        expect(
          AppLocalizations.delegate.isSupported(const Locale('it')),
          isTrue,
        );
      });

      test('should not support unsupported locales', () {
        expect(
          AppLocalizations.delegate.isSupported(const Locale('es')),
          isFalse,
        );
        expect(
          AppLocalizations.delegate.isSupported(const Locale('zh')),
          isFalse,
        );
        expect(
          AppLocalizations.delegate.isSupported(const Locale('ar')),
          isFalse,
        );
      });
    });

    group('Supported Locales', () {
      test('should have exactly 4 supported locales', () {
        expect(AppLocalizations.supportedLocales.length, equals(4));
      });

      test('should include English as supported locale', () {
        expect(
          AppLocalizations.supportedLocales.map((l) => l.languageCode),
          contains('en'),
        );
      });

      test('should contain all Swiss languages', () {
        final locales =
            AppLocalizations.supportedLocales.map((l) => l.languageCode).toList();
        expect(locales, containsAll(['en', 'de', 'fr', 'it']));
      });
    });

    group('English Translations', () {
      testWidgets('should return correct English strings', (tester) async {
        late AppLocalizations l10n;

        await tester.pumpWidget(
          createLocalizedWidget(
            locale: const Locale('en'),
            child: Builder(
              builder: (context) {
                l10n = AppLocalizations.of(context)!;
                return const SizedBox();
              },
            ),
          ),
        );

        // Login screen strings
        expect(l10n.signIn, equals('Sign In'));
        expect(l10n.welcomeBack, equals('Welcome Back'));
        expect(l10n.email, equals('Email'));
        expect(l10n.password, equals('Password'));
        expect(l10n.forgotPassword, equals('Forgot password?'));
        expect(l10n.noAccount, equals("Don't have an account?"));
        expect(l10n.register, equals('Register'));

        // Registration screen strings
        expect(l10n.createAccount, equals('Create Account'));
        expect(l10n.joinAltea, equals('Join Altea'));
        expect(l10n.firstName, equals('First Name'));
        expect(l10n.lastName, equals('Last Name'));
        expect(l10n.confirmPassword, equals('Confirm Password'));
        expect(l10n.termsOfService, equals('Terms of Service'));
        expect(l10n.privacyPolicy, equals('Privacy Policy'));

        // Email sent screen strings
        expect(l10n.checkEmail, equals('Check your email'));
        expect(l10n.resendEmail, equals('Resend Email'));
        expect(l10n.backToSignIn, equals('Back to Sign In'));
      });
    });

    group('German Translations', () {
      testWidgets('should return correct German strings', (tester) async {
        late AppLocalizations l10n;

        await tester.pumpWidget(
          createLocalizedWidget(
            locale: const Locale('de'),
            child: Builder(
              builder: (context) {
                l10n = AppLocalizations.of(context)!;
                return const SizedBox();
              },
            ),
          ),
        );

        // Login screen strings
        expect(l10n.signIn, equals('Anmelden'));
        expect(l10n.welcomeBack, equals('Willkommen zurück'));
        expect(l10n.email, equals('E-Mail'));
        expect(l10n.password, equals('Passwort'));
        expect(l10n.forgotPassword, equals('Passwort vergessen?'));

        // Registration screen strings
        expect(l10n.createAccount, equals('Konto erstellen'));
        expect(l10n.firstName, equals('Vorname'));
        expect(l10n.lastName, equals('Nachname'));
        expect(l10n.termsOfService, equals('Nutzungsbedingungen'));
        expect(l10n.privacyPolicy, equals('Datenschutzrichtlinie'));

        // Email sent screen strings
        expect(l10n.checkEmail, equals('Prüfen Sie Ihre E-Mail'));
        expect(l10n.backToSignIn, equals('Zurück zur Anmeldung'));
      });
    });

    group('French Translations', () {
      testWidgets('should return correct French strings', (tester) async {
        late AppLocalizations l10n;

        await tester.pumpWidget(
          createLocalizedWidget(
            locale: const Locale('fr'),
            child: Builder(
              builder: (context) {
                l10n = AppLocalizations.of(context)!;
                return const SizedBox();
              },
            ),
          ),
        );

        // Login screen strings
        expect(l10n.signIn, equals('Connexion'));
        expect(l10n.welcomeBack, equals('Bon retour'));
        expect(l10n.email, equals('E-mail'));
        expect(l10n.password, equals('Mot de passe'));
        expect(l10n.forgotPassword, equals('Mot de passe oublié ?'));

        // Registration screen strings
        expect(l10n.createAccount, equals('Créer un compte'));
        expect(l10n.firstName, equals('Prénom'));
        expect(l10n.lastName, equals('Nom'));
        expect(l10n.termsOfService, equals("Conditions d'utilisation"));
        expect(l10n.privacyPolicy, equals('Politique de confidentialité'));

        // Email sent screen strings
        expect(l10n.checkEmail, equals('Vérifiez votre e-mail'));
        expect(l10n.backToSignIn, equals('Retour à la connexion'));
      });
    });

    group('Italian Translations', () {
      testWidgets('should return correct Italian strings', (tester) async {
        late AppLocalizations l10n;

        await tester.pumpWidget(
          createLocalizedWidget(
            locale: const Locale('it'),
            child: Builder(
              builder: (context) {
                l10n = AppLocalizations.of(context)!;
                return const SizedBox();
              },
            ),
          ),
        );

        // Login screen strings
        expect(l10n.signIn, equals('Accedi'));
        expect(l10n.welcomeBack, equals('Bentornato'));
        expect(l10n.email, equals('Email'));
        expect(l10n.password, equals('Password'));
        expect(l10n.forgotPassword, equals('Password dimenticata?'));

        // Registration screen strings
        expect(l10n.createAccount, equals('Crea account'));
        expect(l10n.firstName, equals('Nome'));
        expect(l10n.lastName, equals('Cognome'));
        expect(l10n.termsOfService, equals('Termini di servizio'));
        expect(l10n.privacyPolicy, equals('Informativa sulla privacy'));

        // Email sent screen strings
        expect(l10n.checkEmail, equals('Controlla la tua email'));
        expect(l10n.backToSignIn, equals("Torna all'accesso"));
      });
    });

    group('Parameterized Strings', () {
      testWidgets('should interpolate fieldRequired correctly', (tester) async {
        late AppLocalizations l10n;

        await tester.pumpWidget(
          createLocalizedWidget(
            locale: const Locale('en'),
            child: Builder(
              builder: (context) {
                l10n = AppLocalizations.of(context)!;
                return const SizedBox();
              },
            ),
          ),
        );

        expect(l10n.fieldRequired('Email'), equals('Email is required'));
        expect(l10n.fieldRequired('Password'), equals('Password is required'));
      });

      testWidgets('should interpolate fieldMinLength correctly', (tester) async {
        late AppLocalizations l10n;

        await tester.pumpWidget(
          createLocalizedWidget(
            locale: const Locale('en'),
            child: Builder(
              builder: (context) {
                l10n = AppLocalizations.of(context)!;
                return const SizedBox();
              },
            ),
          ),
        );

        expect(
          l10n.fieldMinLength('Password', 8),
          equals('Password must be at least 8 characters'),
        );
        expect(
          l10n.fieldMinLength('First Name', 2),
          equals('First Name must be at least 2 characters'),
        );
      });

      testWidgets('should interpolate couldNotOpen correctly', (tester) async {
        late AppLocalizations l10n;

        await tester.pumpWidget(
          createLocalizedWidget(
            locale: const Locale('en'),
            child: Builder(
              builder: (context) {
                l10n = AppLocalizations.of(context)!;
                return const SizedBox();
              },
            ),
          ),
        );

        expect(
          l10n.couldNotOpen('Terms of Service'),
          equals('Could not open Terms of Service. Please try again.'),
        );
      });

      testWidgets('should interpolate failedToOpen correctly', (tester) async {
        late AppLocalizations l10n;

        await tester.pumpWidget(
          createLocalizedWidget(
            locale: const Locale('en'),
            child: Builder(
              builder: (context) {
                l10n = AppLocalizations.of(context)!;
                return const SizedBox();
              },
            ),
          ),
        );

        expect(
          l10n.failedToOpen('Privacy Policy', 'Network error'),
          equals('Failed to open Privacy Policy: Network error'),
        );
      });

      testWidgets('should interpolate in German correctly', (tester) async {
        late AppLocalizations l10n;

        await tester.pumpWidget(
          createLocalizedWidget(
            locale: const Locale('de'),
            child: Builder(
              builder: (context) {
                l10n = AppLocalizations.of(context)!;
                return const SizedBox();
              },
            ),
          ),
        );

        expect(l10n.fieldRequired('E-Mail'), equals('E-Mail ist erforderlich'));
        expect(
          l10n.fieldMinLength('Passwort', 8),
          equals('Passwort muss mindestens 8 Zeichen haben'),
        );
      });
    });

    group('Fallback Behavior', () {
      testWidgets('should fallback to English for unsupported locale',
          (tester) async {
        late AppLocalizations? l10n;

        await tester.pumpWidget(
          createLocalizedWidget(
            locale: const Locale('zh'), // Chinese - not supported
            child: Builder(
              builder: (context) {
                l10n = AppLocalizations.of(context);
                return const SizedBox();
              },
            ),
          ),
        );

        // Should fallback to English
        expect(l10n?.signIn, equals('Sign In'));
        expect(l10n?.welcomeBack, equals('Welcome Back'));
      });
    });
  });
}
