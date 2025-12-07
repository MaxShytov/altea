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
  String get forgotPasswordTitle => 'Forgot Password';

  @override
  String get forgotPasswordSubtitle =>
      'Enter your email to receive reset instructions';

  @override
  String get sendResetLink => 'Send Reset Link';

  @override
  String get resetLinkSent => 'Reset link sent!';

  @override
  String get resetLinkSentMessage =>
      'If an account exists with this email, you will receive password reset instructions.';

  @override
  String get checkYourEmail => 'Check your email';

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

  @override
  String get appName => 'Altea';

  @override
  String get heroTagline => 'Break the Bad Habits';

  @override
  String get menu => 'Menu';

  @override
  String get dashboard => 'Dashboard';

  @override
  String get profile => 'Profile';

  @override
  String get logOut => 'Log Out';

  @override
  String get logOutConfirmTitle => 'Log Out?';

  @override
  String get logOutConfirmMessage => 'Are you sure you want to log out?';

  @override
  String get cancel => 'Cancel';

  @override
  String get confirm => 'Confirm';

  @override
  String get comingSoon => 'Coming Soon';

  @override
  String get home => 'Home';

  @override
  String get getStarted => 'Get Started';

  @override
  String get onboardingSlide1Title => 'Every Journey Starts Here';

  @override
  String get onboardingSlide1Subtitle =>
      'Take the first step towards freedom. You\'re not alone.';

  @override
  String get onboardingSlide2Title => 'See Your Progress Daily';

  @override
  String get onboardingSlide2Subtitle =>
      'Track every moment of strength. Celebrate small wins.';

  @override
  String get onboardingSlide3Title => 'You\'re Never Alone';

  @override
  String get onboardingSlide3Subtitle =>
      'Connect with others on the same path. Share, support, grow.';

  @override
  String get onboardingSlide4Title => 'Reclaim Your Life';

  @override
  String get onboardingSlide4Subtitle =>
      'Every day is a new beginning. Start your journey today.';

  @override
  String get continueWithGoogle => 'Continue with Google';

  @override
  String get continueWithApple => 'Continue with Apple';

  @override
  String get or => 'or';

  @override
  String get signUp => 'Sign Up';

  @override
  String get loginToAltea => 'Log in to Altea';

  @override
  String get byContinuing => 'By continuing, you are agreeing to our';

  @override
  String get otpTitle => 'We sent you a code';

  @override
  String otpSubtitle(String email) {
    return 'Please enter the 6-digit code we sent to $email';
  }

  @override
  String get getNewCode => 'Get a new code';

  @override
  String tryAgainIn(String seconds) {
    return 'Try again in $seconds';
  }

  @override
  String get openEmailApp => 'Open email app';

  @override
  String invalidCode(int attempts) {
    return 'Invalid code. $attempts attempts remaining.';
  }

  @override
  String get codeExpired => 'Code expired. Request a new one.';

  @override
  String tooManyAttempts(int minutes) {
    return 'Too many attempts. Try again in $minutes minutes.';
  }
}
