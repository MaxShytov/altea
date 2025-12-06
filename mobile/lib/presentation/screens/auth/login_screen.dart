import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:go_router/go_router.dart';

import '../../../core/extensions/build_context_extensions.dart';
import '../../providers/login_provider.dart';
import '../../providers/login_state.dart';
import '../../widgets/atoms/app_button.dart';
import '../../widgets/atoms/app_text_field.dart';
import '../../widgets/molecules/password_field.dart';

/// Login screen for existing users.
class LoginScreen extends ConsumerStatefulWidget {
  const LoginScreen({super.key});

  @override
  ConsumerState<LoginScreen> createState() => _LoginScreenState();
}

class _LoginScreenState extends ConsumerState<LoginScreen> {
  final _formKey = GlobalKey<FormState>();
  final _emailController = TextEditingController();
  final _passwordController = TextEditingController();

  @override
  void dispose() {
    _emailController.dispose();
    _passwordController.dispose();
    super.dispose();
  }

  String? _validateEmail(String? value) {
    if (value == null || value.isEmpty) {
      return context.l10n.emailRequired;
    }
    final emailRegex = RegExp(r'^[\w\.\-\+]+@([\w\-]+\.)+[\w\-]{2,}$');
    if (!emailRegex.hasMatch(value)) {
      return context.l10n.emailInvalid;
    }
    return null;
  }

  String? _validatePassword(String? value) {
    if (value == null || value.isEmpty) {
      return context.l10n.passwordRequired;
    }
    return null;
  }

  Future<void> _handleSubmit() async {
    if (!_formKey.currentState!.validate()) {
      return;
    }

    await ref.read(loginProvider.notifier).login(
          email: _emailController.text.trim(),
          password: _passwordController.text,
        );
  }

  void _handleResendVerification() {
    // Navigate to a screen where user can resend verification
    // For now, show a snackbar with instructions
    ScaffoldMessenger.of(context).showSnackBar(
      SnackBar(
        content: Text(context.l10n.resendVerificationHint),
        duration: const Duration(seconds: 4),
      ),
    );
  }

  @override
  Widget build(BuildContext context) {
    final theme = Theme.of(context);
    final l10n = context.l10n;
    final state = ref.watch(loginProvider);

    // Listen for state changes and navigate on success
    ref.listen<LoginState>(loginProvider, (previous, next) {
      next.whenOrNull(
        success: (user) {
          // Update current user provider
          ref.read(currentUserProvider.notifier).state = user;
          // Navigate to dashboard
          context.go('/dashboard');
        },
        error: (message, code) {
          // Show error message
          ScaffoldMessenger.of(context).showSnackBar(
            SnackBar(
              content: Text(message),
              backgroundColor: theme.colorScheme.error,
              action: code == 'email_not_verified'
                  ? SnackBarAction(
                      label: l10n.resend,
                      textColor: Colors.white,
                      onPressed: _handleResendVerification,
                    )
                  : null,
            ),
          );
        },
      );
    });

    final isLoading = state is LoginLoading;

    return Scaffold(
      appBar: AppBar(
        title: Text(l10n.signIn),
        centerTitle: true,
      ),
      body: SafeArea(
        child: SingleChildScrollView(
          padding: const EdgeInsets.all(24),
          child: Form(
            key: _formKey,
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.stretch,
              children: [
                // Header
                Text(
                  l10n.welcomeBack,
                  style: theme.textTheme.headlineMedium?.copyWith(
                    fontWeight: FontWeight.bold,
                  ),
                ),
                const SizedBox(height: 8),
                Text(
                  l10n.signInSubtitle,
                  style: theme.textTheme.bodyLarge?.copyWith(
                    color: theme.colorScheme.onSurfaceVariant,
                  ),
                ),
                const SizedBox(height: 32),

                // Email field
                AppTextField(
                  label: l10n.email,
                  hint: l10n.emailHint,
                  controller: _emailController,
                  keyboardType: TextInputType.emailAddress,
                  textInputAction: TextInputAction.next,
                  validator: _validateEmail,
                  enabled: !isLoading,
                ),
                const SizedBox(height: 16),

                // Password field
                PasswordField(
                  label: l10n.password,
                  hint: l10n.passwordHint,
                  controller: _passwordController,
                  textInputAction: TextInputAction.done,
                  validator: _validatePassword,
                  enabled: !isLoading,
                  onSubmitted: (_) => _handleSubmit(),
                ),
                const SizedBox(height: 8),

                // Forgot password link
                Align(
                  alignment: Alignment.centerRight,
                  child: TextButton(
                    onPressed: isLoading ? null : () {
                      // TODO: Navigate to forgot password screen
                      ScaffoldMessenger.of(context).showSnackBar(
                        SnackBar(
                          content: Text(l10n.forgotPasswordComingSoon),
                        ),
                      );
                    },
                    child: Text(
                      l10n.forgotPassword,
                      style: TextStyle(
                        color: theme.colorScheme.primary,
                      ),
                    ),
                  ),
                ),
                const SizedBox(height: 24),

                // Submit button
                AppButton(
                  text: l10n.signIn,
                  onPressed: _handleSubmit,
                  isLoading: isLoading,
                  width: double.infinity,
                ),
                const SizedBox(height: 24),

                // Register link
                Row(
                  mainAxisAlignment: MainAxisAlignment.center,
                  children: [
                    Text(
                      l10n.noAccount,
                      style: theme.textTheme.bodyMedium,
                    ),
                    TextButton(
                      onPressed: isLoading ? null : () => context.go('/register'),
                      child: Text(l10n.register),
                    ),
                  ],
                ),
              ],
            ),
          ),
        ),
      ),
    );
  }
}
