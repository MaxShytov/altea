import 'package:flutter/material.dart';
import '../../l10n/app_localizations.dart';

/// Extension on BuildContext for easy access to localization.
extension BuildContextExtensions on BuildContext {
  /// Access localized strings via context.l10n.keyName
  AppLocalizations get l10n => AppLocalizations.of(this)!;
}
