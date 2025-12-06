import 'package:flutter/material.dart';
import 'package:flutter_localizations/flutter_localizations.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:altea_mobile/l10n/app_localizations.dart';

/// Supported locales for testing.
const List<Locale> testSupportedLocales = [
  Locale('en'), // English (fallback)
  Locale('de'), // German
  Locale('fr'), // French
  Locale('it'), // Italian
];

/// Creates a test widget wrapped with localization support.
Widget createLocalizedWidget({
  required Widget child,
  Locale locale = const Locale('en'),
  List<Override>? overrides,
}) {
  return ProviderScope(
    overrides: overrides ?? [],
    child: MaterialApp(
      locale: locale,
      localizationsDelegates: const [
        AppLocalizations.delegate,
        GlobalMaterialLocalizations.delegate,
        GlobalWidgetsLocalizations.delegate,
        GlobalCupertinoLocalizations.delegate,
      ],
      supportedLocales: testSupportedLocales,
      home: child,
    ),
  );
}

/// Creates a test widget with router support and localization.
Widget createLocalizedRouterWidget({
  required Widget child,
  Locale locale = const Locale('en'),
  List<Override>? overrides,
}) {
  return ProviderScope(
    overrides: overrides ?? [],
    child: MaterialApp(
      locale: locale,
      localizationsDelegates: const [
        AppLocalizations.delegate,
        GlobalMaterialLocalizations.delegate,
        GlobalWidgetsLocalizations.delegate,
        GlobalCupertinoLocalizations.delegate,
      ],
      supportedLocales: testSupportedLocales,
      home: Scaffold(body: child),
    ),
  );
}

/// Test helper that provides access to AppLocalizations.
class LocalizationsTestHelper {
  final BuildContext context;

  LocalizationsTestHelper(this.context);

  AppLocalizations get l10n => AppLocalizations.of(context)!;
}

/// Extension for easier access to AppLocalizations in tests.
extension LocalizationTestExtension on BuildContext {
  AppLocalizations get l10n => AppLocalizations.of(this)!;
}
