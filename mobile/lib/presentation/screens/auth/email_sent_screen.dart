import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:go_router/go_router.dart';

import '../../../core/extensions/build_context_extensions.dart';
import '../../providers/auth_provider.dart';
import '../../widgets/atoms/app_button.dart';

/// Screen shown after successful registration.
class EmailSentScreen extends ConsumerStatefulWidget {
  final String email;

  const EmailSentScreen({
    super.key,
    required this.email,
  });

  @override
  ConsumerState<EmailSentScreen> createState() => _EmailSentScreenState();
}

class _EmailSentScreenState extends ConsumerState<EmailSentScreen> {
  bool _isResending = false;
  bool _resendSuccess = false;

  Future<void> _handleResend() async {
    setState(() {
      _isResending = true;
      _resendSuccess = false;
    });

    final (success, errorMessage) = await ref
        .read(registrationProvider.notifier)
        .resendVerification(widget.email);

    setState(() {
      _isResending = false;
      _resendSuccess = success;
    });

    if (mounted) {
      final l10n = context.l10n;
      ScaffoldMessenger.of(context).showSnackBar(
        SnackBar(
          content: Text(
            success
                ? l10n.emailSentSuccess
                : errorMessage ?? l10n.emailSendFailed,
          ),
          backgroundColor: success ? Colors.green : Colors.red,
        ),
      );
    }
  }

  @override
  Widget build(BuildContext context) {
    final theme = Theme.of(context);
    final l10n = context.l10n;

    return Scaffold(
      body: SafeArea(
        child: Padding(
          padding: const EdgeInsets.all(24),
          child: Column(
            mainAxisAlignment: MainAxisAlignment.center,
            crossAxisAlignment: CrossAxisAlignment.stretch,
            children: [
              // Icon
              Container(
                width: 100,
                height: 100,
                decoration: BoxDecoration(
                  color: theme.colorScheme.primaryContainer,
                  shape: BoxShape.circle,
                ),
                child: Icon(
                  Icons.mark_email_read_outlined,
                  size: 50,
                  color: theme.colorScheme.primary,
                ),
              ),
              const SizedBox(height: 32),

              // Title
              Text(
                l10n.checkEmail,
                style: theme.textTheme.headlineMedium?.copyWith(
                  fontWeight: FontWeight.bold,
                ),
                textAlign: TextAlign.center,
              ),
              const SizedBox(height: 16),

              // Description
              Text(
                l10n.verificationSent,
                style: theme.textTheme.bodyLarge?.copyWith(
                  color: theme.colorScheme.onSurfaceVariant,
                ),
                textAlign: TextAlign.center,
              ),
              const SizedBox(height: 8),
              Text(
                widget.email,
                style: theme.textTheme.bodyLarge?.copyWith(
                  fontWeight: FontWeight.w600,
                ),
                textAlign: TextAlign.center,
              ),
              const SizedBox(height: 16),
              Text(
                l10n.clickLink,
                style: theme.textTheme.bodyMedium?.copyWith(
                  color: theme.colorScheme.onSurfaceVariant,
                ),
                textAlign: TextAlign.center,
              ),
              const SizedBox(height: 48),

              // Resend button
              AppButton(
                text: l10n.resendEmail,
                variant: AppButtonVariant.secondary,
                onPressed: _handleResend,
                isLoading: _isResending,
                icon: _resendSuccess ? Icons.check : Icons.refresh,
              ),
              const SizedBox(height: 16),

              // Back to login
              AppButton(
                text: l10n.backToSignIn,
                variant: AppButtonVariant.text,
                onPressed: () {
                  ref.read(registrationProvider.notifier).reset();
                  context.go('/login');
                },
              ),
              const SizedBox(height: 32),

              // Help text
              Text(
                l10n.checkSpam,
                style: theme.textTheme.bodySmall?.copyWith(
                  color: theme.colorScheme.onSurfaceVariant,
                ),
                textAlign: TextAlign.center,
              ),
            ],
          ),
        ),
      ),
    );
  }
}
