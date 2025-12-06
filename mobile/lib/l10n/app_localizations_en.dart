// ignore: unused_import
import 'package:intl/intl.dart' as intl;
import 'app_localizations.dart';

// ignore_for_file: type=lint

/// The translations for English (`en`).
class AppLocalizationsEn extends AppLocalizations {
  AppLocalizationsEn([String locale = 'en']) : super(locale);

  @override
  String get signIn => 'Sign In';

  @override
  String get welcomeBack => 'Welcome Back';

  @override
  String get signInSubtitle => 'Sign in to continue your journey';

  @override
  String get email => 'Email';

  @override
  String get emailHint => 'Enter your email';

  @override
  String get emailRequired => 'Email is required';

  @override
  String get emailInvalid => 'Please enter a valid email';

  @override
  String get password => 'Password';

  @override
  String get passwordHint => 'Enter your password';

  @override
  String get passwordRequired => 'Password is required';

  @override
  String get forgotPassword => 'Forgot password?';

  @override
  String get forgotPasswordComingSoon => 'Forgot password feature coming soon';

  @override
  String get noAccount => 'Don\'t have an account?';

  @override
  String get register => 'Register';

  @override
  String get resend => 'Resend';

  @override
  String get resendVerificationHint =>
      'Please register again to receive a new verification email.';

  @override
  String get createAccount => 'Create Account';

  @override
  String get joinAltea => 'Join Altea';

  @override
  String get createAccountSubtitle => 'Create your account to get started';

  @override
  String get firstName => 'First Name';

  @override
  String get firstNameHint => 'First name';

  @override
  String fieldRequired(String field) {
    return '$field is required';
  }

  @override
  String fieldMinLength(String field, int count) {
    return '$field must be at least $count characters';
  }

  @override
  String get lastName => 'Last Name';

  @override
  String get lastNameHint => 'Last name';

  @override
  String get passwordHintRegistration => 'At least 8 characters';

  @override
  String get passwordMinLength => 'Password must be at least 8 characters';

  @override
  String get confirmPassword => 'Confirm Password';

  @override
  String get confirmPasswordHint => 'Re-enter your password';

  @override
  String get confirmPasswordRequired => 'Please confirm your password';

  @override
  String get passwordsDoNotMatch => 'Passwords do not match';

  @override
  String get termsAgreement => 'I agree to the ';

  @override
  String get termsOfService => 'Terms of Service';

  @override
  String get and => ' and ';

  @override
  String get privacyPolicy => 'Privacy Policy';

  @override
  String get acceptTerms => 'Please accept the Terms & Conditions';

  @override
  String get alreadyHaveAccount => 'Already have an account?';

  @override
  String get checkEmail => 'Check your email';

  @override
  String get verificationSent => 'We sent a verification link to';

  @override
  String get clickLink =>
      'Click the link in the email to verify your account and get started.';

  @override
  String get resendEmail => 'Resend Email';

  @override
  String get backToSignIn => 'Back to Sign In';

  @override
  String get emailSentSuccess => 'Verification email sent successfully';

  @override
  String get emailSendFailed => 'Failed to send email. Please try again.';

  @override
  String get checkSpam =>
      'Didn\'t receive the email? Check your spam folder or try a different email address.';

  @override
  String get termsOfServiceTitle => 'Terms of Service';

  @override
  String get privacyPolicyTitle => 'Privacy Policy';

  @override
  String get openingInBrowser => 'Opening in browser...';

  @override
  String couldNotOpen(String title) {
    return 'Could not open $title. Please try again.';
  }

  @override
  String failedToOpen(String title, String error) {
    return 'Failed to open $title: $error';
  }

  @override
  String get anErrorOccurred => 'An error occurred';

  @override
  String get retry => 'Retry';
}
