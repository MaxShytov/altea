import 'package:flutter/material.dart';
import 'package:flutter_localizations/flutter_localizations.dart';
import 'package:flutter_test/flutter_test.dart';
import 'package:altea_mobile/l10n/app_localizations.dart';

void main() {
  group('Locale Switching Integration Tests', () {
    Widget createTestApp({
      required Locale initialLocale,
      required ValueNotifier<Locale> localeNotifier,
    }) {
      return ValueListenableBuilder<Locale>(
        valueListenable: localeNotifier,
        builder: (context, locale, _) {
          return MaterialApp(
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
            home: Builder(
              builder: (context) {
                final l10n = AppLocalizations.of(context)!;
                return Scaffold(
                  appBar: AppBar(title: Text(l10n.signIn)),
                  body: Column(
                    children: [
                      Text(l10n.welcomeBack, key: const Key('welcomeBack')),
                      Text(l10n.email, key: const Key('email')),
                      Text(l10n.password, key: const Key('password')),
                      Text(l10n.createAccount, key: const Key('createAccount')),
                    ],
                  ),
                );
              },
            ),
          );
        },
      );
    }

    testWidgets('should switch from English to German',
        (WidgetTester tester) async {
      final localeNotifier = ValueNotifier(const Locale('en'));

      await tester.pumpWidget(createTestApp(
        initialLocale: const Locale('en'),
        localeNotifier: localeNotifier,
      ));
      await tester.pumpAndSettle();

      // Verify English texts
      expect(find.text('Sign In'), findsOneWidget);
      expect(find.text('Welcome Back'), findsOneWidget);
      expect(find.text('Email'), findsOneWidget);
      expect(find.text('Password'), findsOneWidget);

      // Switch to German
      localeNotifier.value = const Locale('de');
      await tester.pumpAndSettle();

      // Verify German texts
      expect(find.text('Anmelden'), findsOneWidget);
      expect(find.text('Willkommen zurück'), findsOneWidget);
      expect(find.text('E-Mail'), findsOneWidget);
      expect(find.text('Passwort'), findsOneWidget);
    });

    testWidgets('should switch from German to French',
        (WidgetTester tester) async {
      final localeNotifier = ValueNotifier(const Locale('de'));

      await tester.pumpWidget(createTestApp(
        initialLocale: const Locale('de'),
        localeNotifier: localeNotifier,
      ));
      await tester.pumpAndSettle();

      // Verify German texts
      expect(find.text('Anmelden'), findsOneWidget);
      expect(find.text('Willkommen zurück'), findsOneWidget);

      // Switch to French
      localeNotifier.value = const Locale('fr');
      await tester.pumpAndSettle();

      // Verify French texts
      expect(find.text('Connexion'), findsOneWidget);
      expect(find.text('Bon retour'), findsOneWidget);
      expect(find.text('E-mail'), findsOneWidget);
      expect(find.text('Mot de passe'), findsOneWidget);
    });

    testWidgets('should switch from French to Italian',
        (WidgetTester tester) async {
      final localeNotifier = ValueNotifier(const Locale('fr'));

      await tester.pumpWidget(createTestApp(
        initialLocale: const Locale('fr'),
        localeNotifier: localeNotifier,
      ));
      await tester.pumpAndSettle();

      // Verify French texts
      expect(find.text('Connexion'), findsOneWidget);
      expect(find.text('Bon retour'), findsOneWidget);

      // Switch to Italian
      localeNotifier.value = const Locale('it');
      await tester.pumpAndSettle();

      // Verify Italian texts
      expect(find.text('Accedi'), findsOneWidget);
      expect(find.text('Bentornato'), findsOneWidget);
      expect(find.text('Email'), findsOneWidget);
      expect(find.text('Password'), findsOneWidget);
    });

    testWidgets('should switch through all locales in sequence',
        (WidgetTester tester) async {
      final localeNotifier = ValueNotifier(const Locale('en'));

      await tester.pumpWidget(createTestApp(
        initialLocale: const Locale('en'),
        localeNotifier: localeNotifier,
      ));
      await tester.pumpAndSettle();

      // English
      expect(find.text('Welcome Back'), findsOneWidget);

      // Switch to German
      localeNotifier.value = const Locale('de');
      await tester.pumpAndSettle();
      expect(find.text('Willkommen zurück'), findsOneWidget);

      // Switch to French
      localeNotifier.value = const Locale('fr');
      await tester.pumpAndSettle();
      expect(find.text('Bon retour'), findsOneWidget);

      // Switch to Italian
      localeNotifier.value = const Locale('it');
      await tester.pumpAndSettle();
      expect(find.text('Bentornato'), findsOneWidget);

      // Switch back to English
      localeNotifier.value = const Locale('en');
      await tester.pumpAndSettle();
      expect(find.text('Welcome Back'), findsOneWidget);
    });

    testWidgets('should handle unsupported locale with fallback to English',
        (WidgetTester tester) async {
      final localeNotifier = ValueNotifier(const Locale('zh'));

      await tester.pumpWidget(createTestApp(
        initialLocale: const Locale('zh'),
        localeNotifier: localeNotifier,
      ));
      await tester.pumpAndSettle();

      // Should fallback to English
      expect(find.text('Sign In'), findsOneWidget);
      expect(find.text('Welcome Back'), findsOneWidget);
    });

    testWidgets('should switch from unsupported locale to supported locale',
        (WidgetTester tester) async {
      final localeNotifier = ValueNotifier(const Locale('es')); // Spanish - not supported

      await tester.pumpWidget(createTestApp(
        initialLocale: const Locale('es'),
        localeNotifier: localeNotifier,
      ));
      await tester.pumpAndSettle();

      // Should fallback to English
      expect(find.text('Welcome Back'), findsOneWidget);

      // Switch to German (supported)
      localeNotifier.value = const Locale('de');
      await tester.pumpAndSettle();

      // Should show German
      expect(find.text('Willkommen zurück'), findsOneWidget);
    });

    group('Locale Resolution', () {
      testWidgets('should handle locale with region code (de_CH)',
          (WidgetTester tester) async {
        final localeNotifier = ValueNotifier(const Locale('de', 'CH'));

        await tester.pumpWidget(createTestApp(
          initialLocale: const Locale('de', 'CH'),
          localeNotifier: localeNotifier,
        ));
        await tester.pumpAndSettle();

        // Should use German translations
        expect(find.text('Anmelden'), findsOneWidget);
        expect(find.text('Willkommen zurück'), findsOneWidget);
      });

      testWidgets('should handle locale with region code (fr_CH)',
          (WidgetTester tester) async {
        final localeNotifier = ValueNotifier(const Locale('fr', 'CH'));

        await tester.pumpWidget(createTestApp(
          initialLocale: const Locale('fr', 'CH'),
          localeNotifier: localeNotifier,
        ));
        await tester.pumpAndSettle();

        // Should use French translations
        expect(find.text('Connexion'), findsOneWidget);
        expect(find.text('Bon retour'), findsOneWidget);
      });

      testWidgets('should handle locale with region code (it_CH)',
          (WidgetTester tester) async {
        final localeNotifier = ValueNotifier(const Locale('it', 'CH'));

        await tester.pumpWidget(createTestApp(
          initialLocale: const Locale('it', 'CH'),
          localeNotifier: localeNotifier,
        ));
        await tester.pumpAndSettle();

        // Should use Italian translations
        expect(find.text('Accedi'), findsOneWidget);
        expect(find.text('Bentornato'), findsOneWidget);
      });
    });
  });
}
