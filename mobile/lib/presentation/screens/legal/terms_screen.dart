import 'package:flutter/material.dart';

import '../../../core/config/env_config.dart';
import '../../../core/extensions/build_context_extensions.dart';
import 'legal_document_screen.dart';

/// Screen that displays the Terms of Service.
class TermsScreen extends StatelessWidget {
  const TermsScreen({super.key});

  @override
  Widget build(BuildContext context) {
    return LegalDocumentScreen(
      title: context.l10n.termsOfServiceTitle,
      url: EnvConfig.termsUrl,
    );
  }
}
