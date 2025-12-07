import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:go_router/go_router.dart';

import '../../../core/extensions/build_context_extensions.dart';
import '../../../core/theme/altea_colors.dart';
import '../../../core/theme/altea_input_decoration.dart';
import '../../../core/utils/validators.dart';
import '../../providers/otp_provider.dart';
import '../../providers/otp_state.dart';
import '../../widgets/atoms/gradient_button.dart';
import '../../widgets/molecules/or_divider.dart';
import '../../widgets/molecules/social_login_button.dart';
import '../../widgets/molecules/terms_privacy_text.dart';

/// Login screen with Strava-style dark theme (email first layout).
///
/// Follows the unified OTP flow - entering email triggers OTP send.
class LoginScreen extends ConsumerStatefulWidget {
  const LoginScreen({super.key});

  @override
  ConsumerState<LoginScreen> createState() => _LoginScreenState();
}

class _LoginScreenState extends ConsumerState<LoginScreen> {
  final _formKey = GlobalKey<FormState>();
  final _emailController = TextEditingController();
  final _emailFocusNode = FocusNode();

  @override
  void dispose() {
    _emailController.dispose();
    _emailFocusNode.dispose();
    super.dispose();
  }

  bool get _isEmailValid => Validators.isValidEmail(_emailController.text);

  Future<void> _handleSubmit() async {
    if (!_formKey.currentState!.validate()) {
      return;
    }

    final email = _emailController.text.trim();
    await ref.read(otpProvider.notifier).requestOtp(email: email);
  }

  @override
  Widget build(BuildContext context) {
    final l10n = context.l10n;
    final state = ref.watch(otpProvider);

    // Listen for state changes and navigate on success
    ref.listen<OtpState>(otpProvider, (previous, next) {
      next.whenOrNull(
        codeSent: (email, emailMasked) {
          context.push('/otp-verification', extra: {
            'email': email,
            'emailMasked': emailMasked,
          });
        },
        error: (message, attemptsRemaining, email) {
          ScaffoldMessenger.of(context).showSnackBar(
            SnackBar(
              content: Text(message),
              backgroundColor: AlteaColors.error,
            ),
          );
        },
      );
    });

    final isLoading = state is OtpRequestLoading;

    return Scaffold(
      backgroundColor: AlteaColors.backgroundDark,
      body: SafeArea(
        child: SingleChildScrollView(
          child: Padding(
            padding: const EdgeInsets.symmetric(horizontal: 24),
            child: Form(
              key: _formKey,
              child: Column(
                crossAxisAlignment: CrossAxisAlignment.stretch,
                children: [
                  // Close button row
                  Align(
                    alignment: Alignment.topRight,
                    child: IconButton(
                      onPressed: () => context.pop(),
                      icon: const Icon(
                        Icons.close,
                        color: AlteaColors.textOnDark,
                        size: 28,
                      ),
                    ),
                  ),
                  const SizedBox(height: 16),

                  // Title
                  Text(
                    l10n.loginToAltea,
                    style: const TextStyle(
                      fontSize: 28,
                      fontWeight: FontWeight.bold,
                      color: AlteaColors.textOnDark,
                    ),
                  ),
                  const SizedBox(height: 32),

                  // Email label
                  Text(
                    l10n.email,
                    style: const TextStyle(
                      fontSize: 14,
                      fontWeight: FontWeight.w500,
                      color: AlteaColors.textOnDark,
                    ),
                  ),
                  const SizedBox(height: 8),

                  // Email field
                  TextFormField(
                    controller: _emailController,
                    focusNode: _emailFocusNode,
                    keyboardType: TextInputType.emailAddress,
                    textInputAction: TextInputAction.done,
                    enabled: !isLoading,
                    validator: (value) => Validators.validateEmail(value, l10n),
                    onChanged: (_) => setState(() {}),
                    onFieldSubmitted: (_) {
                      if (_isEmailValid) _handleSubmit();
                    },
                    style: const TextStyle(
                      fontSize: 16,
                      color: AlteaColors.textOnDark,
                    ),
                    decoration: AlteaInputDecoration.email(l10n),
                  ),
                  const SizedBox(height: 24),

                  // Sign In button
                  GradientButton(
                    text: l10n.signIn,
                    onPressed: _isEmailValid ? _handleSubmit : null,
                    isLoading: isLoading,
                  ),
                  const SizedBox(height: 24),

                  // Divider with "or"
                  OrDivider(text: l10n.or),
                  const SizedBox(height: 24),

                  // Social login buttons (disabled)
                  const SocialLoginButton(
                    provider: SocialLoginProvider.google,
                    isEnabled: false,
                  ),
                  const SizedBox(height: 12),
                  const SocialLoginButton(
                    provider: SocialLoginProvider.apple,
                    isEnabled: false,
                  ),
                  const SizedBox(height: 24),

                  // Terms and privacy text
                  TermsPrivacyText(
                    onTermsTap: () => context.push('/terms'),
                    onPrivacyTap: () => context.push('/privacy'),
                  ),
                  const SizedBox(height: 32),

                  // Don't have account link
                  Row(
                    mainAxisAlignment: MainAxisAlignment.center,
                    children: [
                      Text(
                        l10n.noAccount,
                        style: const TextStyle(
                          fontSize: 14,
                          color: AlteaColors.textSecondaryOnDark,
                        ),
                      ),
                      TextButton(
                        onPressed: isLoading ? null : () => context.go('/register'),
                        child: Text(
                          l10n.register,
                          style: const TextStyle(
                            fontSize: 14,
                            fontWeight: FontWeight.w600,
                            color: AlteaColors.primaryPurple,
                          ),
                        ),
                      ),
                    ],
                  ),
                  const SizedBox(height: 24),
                ],
              ),
            ),
          ),
        ),
      ),
    );
  }
}
