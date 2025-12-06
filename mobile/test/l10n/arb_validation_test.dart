import 'dart:convert';
import 'dart:io';
import 'package:flutter_test/flutter_test.dart';

/// Unit tests for ARB file validation.
/// Ensures all translation files have consistent keys and proper structure.
void main() {
  group('ARB File Validation', () {
    late Map<String, dynamic> enArb;
    late Map<String, dynamic> deArb;
    late Map<String, dynamic> frArb;
    late Map<String, dynamic> itArb;
    late Set<String> templateKeys;

    setUpAll(() async {
      final l10nDir = 'lib/l10n';

      enArb = json.decode(await File('$l10nDir/app_en.arb').readAsString());
      deArb = json.decode(await File('$l10nDir/app_de.arb').readAsString());
      frArb = json.decode(await File('$l10nDir/app_fr.arb').readAsString());
      itArb = json.decode(await File('$l10nDir/app_it.arb').readAsString());

      // Get keys from template (English), excluding metadata keys
      templateKeys = enArb.keys
          .where((key) => !key.startsWith('@') && key != '@@locale')
          .toSet();
    });

    test('should have correct locale markers', () {
      expect(enArb['@@locale'], equals('en'));
      expect(deArb['@@locale'], equals('de'));
      expect(frArb['@@locale'], equals('fr'));
      expect(itArb['@@locale'], equals('it'));
    });

    test('should have all translation keys in German', () {
      final deKeys = deArb.keys
          .where((key) => !key.startsWith('@') && key != '@@locale')
          .toSet();

      final missingKeys = templateKeys.difference(deKeys);
      expect(
        missingKeys,
        isEmpty,
        reason: 'German translation is missing keys: $missingKeys',
      );
    });

    test('should have all translation keys in French', () {
      final frKeys = frArb.keys
          .where((key) => !key.startsWith('@') && key != '@@locale')
          .toSet();

      final missingKeys = templateKeys.difference(frKeys);
      expect(
        missingKeys,
        isEmpty,
        reason: 'French translation is missing keys: $missingKeys',
      );
    });

    test('should have all translation keys in Italian', () {
      final itKeys = itArb.keys
          .where((key) => !key.startsWith('@') && key != '@@locale')
          .toSet();

      final missingKeys = templateKeys.difference(itKeys);
      expect(
        missingKeys,
        isEmpty,
        reason: 'Italian translation is missing keys: $missingKeys',
      );
    });

    test('should not have empty translation values in German', () {
      final emptyKeys = deArb.entries
          .where((e) =>
              !e.key.startsWith('@') &&
              e.key != '@@locale' &&
              (e.value == null || e.value.toString().isEmpty))
          .map((e) => e.key)
          .toList();

      expect(
        emptyKeys,
        isEmpty,
        reason: 'German translation has empty values for: $emptyKeys',
      );
    });

    test('should not have empty translation values in French', () {
      final emptyKeys = frArb.entries
          .where((e) =>
              !e.key.startsWith('@') &&
              e.key != '@@locale' &&
              (e.value == null || e.value.toString().isEmpty))
          .map((e) => e.key)
          .toList();

      expect(
        emptyKeys,
        isEmpty,
        reason: 'French translation has empty values for: $emptyKeys',
      );
    });

    test('should not have empty translation values in Italian', () {
      final emptyKeys = itArb.entries
          .where((e) =>
              !e.key.startsWith('@') &&
              e.key != '@@locale' &&
              (e.value == null || e.value.toString().isEmpty))
          .map((e) => e.key)
          .toList();

      expect(
        emptyKeys,
        isEmpty,
        reason: 'Italian translation has empty values for: $emptyKeys',
      );
    });

    test('should have metadata descriptions for all English keys', () {
      final keysWithoutMeta = templateKeys.where((key) {
        final metaKey = '@$key';
        return !enArb.containsKey(metaKey);
      }).toList();

      expect(
        keysWithoutMeta,
        isEmpty,
        reason: 'English template missing @metadata for keys: $keysWithoutMeta',
      );
    });

    group('Placeholder Consistency', () {
      test('should have matching placeholders in German translations', () {
        _validatePlaceholders(enArb, deArb, 'German');
      });

      test('should have matching placeholders in French translations', () {
        _validatePlaceholders(enArb, frArb, 'French');
      });

      test('should have matching placeholders in Italian translations', () {
        _validatePlaceholders(enArb, itArb, 'Italian');
      });
    });

    group('Key Count Validation', () {
      test('should have expected number of translation keys', () {
        // Based on CURRENT_TASK.md: 45 strings
        expect(
          templateKeys.length,
          greaterThanOrEqualTo(40),
          reason: 'Expected at least 40 translation keys, got ${templateKeys.length}',
        );
      });

      test('all languages should have same key count', () {
        final deKeyCount = deArb.keys
            .where((k) => !k.startsWith('@') && k != '@@locale')
            .length;
        final frKeyCount = frArb.keys
            .where((k) => !k.startsWith('@') && k != '@@locale')
            .length;
        final itKeyCount = itArb.keys
            .where((k) => !k.startsWith('@') && k != '@@locale')
            .length;

        expect(deKeyCount, equals(templateKeys.length),
            reason: 'German key count mismatch');
        expect(frKeyCount, equals(templateKeys.length),
            reason: 'French key count mismatch');
        expect(itKeyCount, equals(templateKeys.length),
            reason: 'Italian key count mismatch');
      });
    });
  });
}

/// Validates that placeholders in translations match the template.
void _validatePlaceholders(
  Map<String, dynamic> template,
  Map<String, dynamic> translation,
  String languageName,
) {
  final placeholderRegex = RegExp(r'\{(\w+)\}');

  final keysWithMismatch = <String>[];

  for (final key in template.keys) {
    if (key.startsWith('@') || key == '@@locale') continue;

    final templateValue = template[key]?.toString() ?? '';
    final translationValue = translation[key]?.toString() ?? '';

    final templatePlaceholders =
        placeholderRegex.allMatches(templateValue).map((m) => m.group(1)).toSet();
    final translationPlaceholders =
        placeholderRegex.allMatches(translationValue).map((m) => m.group(1)).toSet();

    if (!templatePlaceholders.containsAll(translationPlaceholders) ||
        !translationPlaceholders.containsAll(templatePlaceholders)) {
      keysWithMismatch.add(key);
    }
  }

  expect(
    keysWithMismatch,
    isEmpty,
    reason: '$languageName has placeholder mismatches in keys: $keysWithMismatch',
  );
}
