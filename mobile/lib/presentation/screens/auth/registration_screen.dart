import 'package:flutter/gestures.dart';
import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:go_router/go_router.dart';

import '../../../core/extensions/build_context_extensions.dart';
import '../../providers/auth_provider.dart';
import '../../providers/registration_state.dart';
import '../../widgets/atoms/app_button.dart';
import '../../widgets/atoms/app_text_field.dart';
import '../../widgets/molecules/password_field.dart';
import '../../widgets/organisms/app_drawer.dart';

/// Registration screen for new users.
class RegistrationScreen extends ConsumerStatefulWidget {
  const RegistrationScreen({super.key});

  @override
  ConsumerState<RegistrationScreen> createState() => _RegistrationScreenState();
}

class _RegistrationScreenState extends ConsumerState<RegistrationScreen> {
  final _formKey = GlobalKey<FormState>();
  final _emailController = TextEditingController();
  final _firstNameController = TextEditingController();
  final _lastNameController = TextEditingController();
  final _passwordController = TextEditingController();
  final _confirmPasswordController = TextEditingController();
  bool _termsAccepted = false;

  // Gesture recognizers for Terms and Privacy links
  late final TapGestureRecognizer _termsRecognizer;
  late final TapGestureRecognizer _privacyRecognizer;

  @override
  void initState() {
    super.initState();
    _termsRecognizer = TapGestureRecognizer()
      ..onTap = () => context.push('/terms');
    _privacyRecognizer = TapGestureRecognizer()
      ..onTap = () => context.push('/privacy');
  }

  @override
  void dispose() {
    _emailController.dispose();
    _firstNameController.dispose();
    _lastNameController.dispose();
    _passwordController.dispose();
    _confirmPasswordController.dispose();
    _termsRecognizer.dispose();
    _privacyRecognizer.dispose();
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

  String? _validateFirstName(String? value) {
    if (value == null || value.isEmpty) {
      return context.l10n.fieldRequired(context.l10n.firstName);
    }
    if (value.length < 2) {
      return context.l10n.fieldMinLength(context.l10n.firstName, 2);
    }
    return null;
  }

  String? _validateLastName(String? value) {
    if (value == null || value.isEmpty) {
      return context.l10n.fieldRequired(context.l10n.lastName);
    }
    if (value.length < 2) {
      return context.l10n.fieldMinLength(context.l10n.lastName, 2);
    }
    return null;
  }

  String? _validatePassword(String? value) {
    if (value == null || value.isEmpty) {
      return context.l10n.passwordRequired;
    }
    if (value.length < 8) {
      return context.l10n.passwordMinLength;
    }
    return null;
  }

  String? _validateConfirmPassword(String? value) {
    if (value == null || value.isEmpty) {
      return context.l10n.confirmPasswordRequired;
    }
    if (value != _passwordController.text) {
      return context.l10n.passwordsDoNotMatch;
    }
    return null;
  }

  Future<void> _handleSubmit() async {
    if (!_formKey.currentState!.validate()) {
      return;
    }

    if (!_termsAccepted) {
      ScaffoldMessenger.of(context).showSnackBar(
        SnackBar(
          content: Text(context.l10n.acceptTerms),
          backgroundColor: Colors.red,
        ),
      );
      return;
    }

    await ref.read(registrationProvider.notifier).register(
          email: _emailController.text.trim(),
          password: _passwordController.text,
          passwordConfirm: _confirmPasswordController.text,
          firstName: _firstNameController.text.trim(),
          lastName: _lastNameController.text.trim(),
          termsAccepted: _termsAccepted,
        );
  }

  @override
  Widget build(BuildContext context) {
    final theme = Theme.of(context);
    final l10n = context.l10n;
    final state = ref.watch(registrationProvider);

    // Listen for state changes and navigate on success
    ref.listen<RegistrationState>(registrationProvider, (previous, next) {
      next.whenOrNull(
        success: (user, email) {
          context.go('/email-sent', extra: email);
        },
        error: (message, fieldErrors) {
          ScaffoldMessenger.of(context).showSnackBar(
            SnackBar(
              content: Text(message),
              backgroundColor: theme.colorScheme.error,
            ),
          );
        },
      );
    });

    final isLoading = state is RegistrationLoading;

    // Get field errors from state
    final fieldErrors = state.maybeWhen(
      error: (_, errors) => errors,
      orElse: () => <String, List<String>>{},
    );

    return Scaffold(
      appBar: AppBar(
        title: Text(l10n.createAccount),
        centerTitle: true,
      ),
      drawer: const AppDrawer(),
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
                  l10n.joinAltea,
                  style: theme.textTheme.headlineMedium?.copyWith(
                    fontWeight: FontWeight.bold,
                  ),
                ),
                const SizedBox(height: 8),
                Text(
                  l10n.createAccountSubtitle,
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
                  errorText: fieldErrors['email']?.firstOrNull,
                ),
                const SizedBox(height: 16),

                // Name fields row
                Row(
                  children: [
                    Expanded(
                      child: AppTextField(
                        label: l10n.firstName,
                        hint: l10n.firstNameHint,
                        controller: _firstNameController,
                        textInputAction: TextInputAction.next,
                        validator: _validateFirstName,
                        enabled: !isLoading,
                        errorText: fieldErrors['first_name']?.firstOrNull,
                      ),
                    ),
                    const SizedBox(width: 16),
                    Expanded(
                      child: AppTextField(
                        label: l10n.lastName,
                        hint: l10n.lastNameHint,
                        controller: _lastNameController,
                        textInputAction: TextInputAction.next,
                        validator: _validateLastName,
                        enabled: !isLoading,
                        errorText: fieldErrors['last_name']?.firstOrNull,
                      ),
                    ),
                  ],
                ),
                const SizedBox(height: 16),

                // Password field
                PasswordField(
                  label: l10n.password,
                  hint: l10n.passwordHintRegistration,
                  controller: _passwordController,
                  textInputAction: TextInputAction.next,
                  validator: _validatePassword,
                  enabled: !isLoading,
                  errorText: fieldErrors['password']?.firstOrNull,
                ),
                const SizedBox(height: 16),

                // Confirm password field
                PasswordField(
                  label: l10n.confirmPassword,
                  hint: l10n.confirmPasswordHint,
                  controller: _confirmPasswordController,
                  textInputAction: TextInputAction.done,
                  validator: _validateConfirmPassword,
                  enabled: !isLoading,
                  errorText: fieldErrors['password_confirm']?.firstOrNull,
                  onSubmitted: (_) => _handleSubmit(),
                ),
                const SizedBox(height: 24),

                // Terms checkbox
                Row(
                  crossAxisAlignment: CrossAxisAlignment.start,
                  children: [
                    SizedBox(
                      height: 24,
                      width: 24,
                      child: Checkbox(
                        value: _termsAccepted,
                        onChanged: isLoading
                            ? null
                            : (value) {
                                setState(() {
                                  _termsAccepted = value ?? false;
                                });
                              },
                      ),
                    ),
                    const SizedBox(width: 12),
                    Expanded(
                      child: Text.rich(
                        TextSpan(
                          text: l10n.termsAgreement,
                          style: theme.textTheme.bodyMedium,
                          children: [
                            TextSpan(
                              text: l10n.termsOfService,
                              style: TextStyle(
                                color: theme.colorScheme.primary,
                                fontWeight: FontWeight.w500,
                              ),
                              recognizer: _termsRecognizer,
                            ),
                            TextSpan(text: l10n.and),
                            TextSpan(
                              text: l10n.privacyPolicy,
                              style: TextStyle(
                                color: theme.colorScheme.primary,
                                fontWeight: FontWeight.w500,
                              ),
                              recognizer: _privacyRecognizer,
                            ),
                          ],
                        ),
                      ),
                    ),
                  ],
                ),
                const SizedBox(height: 32),

                // Submit button
                AppButton(
                  text: l10n.createAccount,
                  onPressed: _handleSubmit,
                  isLoading: isLoading,
                  width: double.infinity,
                ),
                const SizedBox(height: 24),

                // Login link
                Row(
                  mainAxisAlignment: MainAxisAlignment.center,
                  children: [
                    Text(
                      l10n.alreadyHaveAccount,
                      style: theme.textTheme.bodyMedium,
                    ),
                    TextButton(
                      onPressed: isLoading ? null : () => context.go('/login'),
                      child: Text(l10n.signIn),
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
