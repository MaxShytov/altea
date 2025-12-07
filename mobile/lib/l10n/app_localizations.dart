import 'dart:async';

import 'package:flutter/foundation.dart';
import 'package:flutter/widgets.dart';
import 'package:flutter_localizations/flutter_localizations.dart';
import 'package:intl/intl.dart' as intl;

import 'app_localizations_de.dart';
import 'app_localizations_en.dart';
import 'app_localizations_fr.dart';
import 'app_localizations_it.dart';

// ignore_for_file: type=lint

/// Callers can lookup localized strings with an instance of AppLocalizations
/// returned by `AppLocalizations.of(context)`.
///
/// Applications need to include `AppLocalizations.delegate()` in their app's
/// `localizationDelegates` list, and the locales they support in the app's
/// `supportedLocales` list. For example:
///
/// ```dart
/// import 'l10n/app_localizations.dart';
///
/// return MaterialApp(
///   localizationsDelegates: AppLocalizations.localizationsDelegates,
///   supportedLocales: AppLocalizations.supportedLocales,
///   home: MyApplicationHome(),
/// );
/// ```
///
/// ## Update pubspec.yaml
///
/// Please make sure to update your pubspec.yaml to include the following
/// packages:
///
/// ```yaml
/// dependencies:
///   # Internationalization support.
///   flutter_localizations:
///     sdk: flutter
///   intl: any # Use the pinned version from flutter_localizations
///
///   # Rest of dependencies
/// ```
///
/// ## iOS Applications
///
/// iOS applications define key application metadata, including supported
/// locales, in an Info.plist file that is built into the application bundle.
/// To configure the locales supported by your app, you’ll need to edit this
/// file.
///
/// First, open your project’s ios/Runner.xcworkspace Xcode workspace file.
/// Then, in the Project Navigator, open the Info.plist file under the Runner
/// project’s Runner folder.
///
/// Next, select the Information Property List item, select Add Item from the
/// Editor menu, then select Localizations from the pop-up menu.
///
/// Select and expand the newly-created Localizations item then, for each
/// locale your application supports, add a new item and select the locale
/// you wish to add from the pop-up menu in the Value field. This list should
/// be consistent with the languages listed in the AppLocalizations.supportedLocales
/// property.
abstract class AppLocalizations {
  AppLocalizations(String locale)
    : localeName = intl.Intl.canonicalizedLocale(locale.toString());

  final String localeName;

  static AppLocalizations? of(BuildContext context) {
    return Localizations.of<AppLocalizations>(context, AppLocalizations);
  }

  static const LocalizationsDelegate<AppLocalizations> delegate =
      _AppLocalizationsDelegate();

  /// A list of this localizations delegate along with the default localizations
  /// delegates.
  ///
  /// Returns a list of localizations delegates containing this delegate along with
  /// GlobalMaterialLocalizations.delegate, GlobalCupertinoLocalizations.delegate,
  /// and GlobalWidgetsLocalizations.delegate.
  ///
  /// Additional delegates can be added by appending to this list in
  /// MaterialApp. This list does not have to be used at all if a custom list
  /// of delegates is preferred or required.
  static const List<LocalizationsDelegate<dynamic>> localizationsDelegates =
      <LocalizationsDelegate<dynamic>>[
        delegate,
        GlobalMaterialLocalizations.delegate,
        GlobalCupertinoLocalizations.delegate,
        GlobalWidgetsLocalizations.delegate,
      ];

  /// A list of this localizations delegate's supported locales.
  static const List<Locale> supportedLocales = <Locale>[
    Locale('de'),
    Locale('en'),
    Locale('fr'),
    Locale('it'),
  ];

  /// Sign in button and title
  ///
  /// In en, this message translates to:
  /// **'Sign In'**
  String get signIn;

  /// Login screen header
  ///
  /// In en, this message translates to:
  /// **'Welcome Back'**
  String get welcomeBack;

  /// Login screen subtitle
  ///
  /// In en, this message translates to:
  /// **'Sign in to continue your journey'**
  String get signInSubtitle;

  /// Email field label
  ///
  /// In en, this message translates to:
  /// **'Email'**
  String get email;

  /// Email field hint
  ///
  /// In en, this message translates to:
  /// **'Enter your email'**
  String get emailHint;

  /// Email validation error
  ///
  /// In en, this message translates to:
  /// **'Email is required'**
  String get emailRequired;

  /// Email format validation error
  ///
  /// In en, this message translates to:
  /// **'Please enter a valid email'**
  String get emailInvalid;

  /// Password field label
  ///
  /// In en, this message translates to:
  /// **'Password'**
  String get password;

  /// Password field hint
  ///
  /// In en, this message translates to:
  /// **'Enter your password'**
  String get passwordHint;

  /// Password validation error
  ///
  /// In en, this message translates to:
  /// **'Password is required'**
  String get passwordRequired;

  /// Forgot password link
  ///
  /// In en, this message translates to:
  /// **'Forgot password?'**
  String get forgotPassword;

  /// Forgot password screen title
  ///
  /// In en, this message translates to:
  /// **'Forgot Password'**
  String get forgotPasswordTitle;

  /// Forgot password screen subtitle
  ///
  /// In en, this message translates to:
  /// **'Enter your email to receive reset instructions'**
  String get forgotPasswordSubtitle;

  /// Send reset link button
  ///
  /// In en, this message translates to:
  /// **'Send Reset Link'**
  String get sendResetLink;

  /// Reset link sent success message
  ///
  /// In en, this message translates to:
  /// **'Reset link sent!'**
  String get resetLinkSent;

  /// Reset link sent detailed message
  ///
  /// In en, this message translates to:
  /// **'If an account exists with this email, you will receive password reset instructions.'**
  String get resetLinkSentMessage;

  /// Check email header after sending reset link
  ///
  /// In en, this message translates to:
  /// **'Check your email'**
  String get checkYourEmail;

  /// No account text before register link
  ///
  /// In en, this message translates to:
  /// **'Don\'t have an account?'**
  String get noAccount;

  /// Register link/button
  ///
  /// In en, this message translates to:
  /// **'Register'**
  String get register;

  /// Resend button
  ///
  /// In en, this message translates to:
  /// **'Resend'**
  String get resend;

  /// Hint for resending verification email
  ///
  /// In en, this message translates to:
  /// **'Please register again to receive a new verification email.'**
  String get resendVerificationHint;

  /// Create account button and title
  ///
  /// In en, this message translates to:
  /// **'Create Account'**
  String get createAccount;

  /// Registration screen header
  ///
  /// In en, this message translates to:
  /// **'Join Altea'**
  String get joinAltea;

  /// Registration screen subtitle
  ///
  /// In en, this message translates to:
  /// **'Create your account to get started'**
  String get createAccountSubtitle;

  /// First name field label
  ///
  /// In en, this message translates to:
  /// **'First Name'**
  String get firstName;

  /// First name field hint
  ///
  /// In en, this message translates to:
  /// **'First name'**
  String get firstNameHint;

  /// Generic required field error
  ///
  /// In en, this message translates to:
  /// **'{field} is required'**
  String fieldRequired(String field);

  /// Minimum length validation error
  ///
  /// In en, this message translates to:
  /// **'{field} must be at least {count} characters'**
  String fieldMinLength(String field, int count);

  /// Last name field label
  ///
  /// In en, this message translates to:
  /// **'Last Name'**
  String get lastName;

  /// Last name field hint
  ///
  /// In en, this message translates to:
  /// **'Last name'**
  String get lastNameHint;

  /// Password hint for registration
  ///
  /// In en, this message translates to:
  /// **'At least 8 characters'**
  String get passwordHintRegistration;

  /// Password minimum length error
  ///
  /// In en, this message translates to:
  /// **'Password must be at least 8 characters'**
  String get passwordMinLength;

  /// Confirm password field label
  ///
  /// In en, this message translates to:
  /// **'Confirm Password'**
  String get confirmPassword;

  /// Confirm password field hint
  ///
  /// In en, this message translates to:
  /// **'Re-enter your password'**
  String get confirmPasswordHint;

  /// Confirm password required error
  ///
  /// In en, this message translates to:
  /// **'Please confirm your password'**
  String get confirmPasswordRequired;

  /// Passwords mismatch error
  ///
  /// In en, this message translates to:
  /// **'Passwords do not match'**
  String get passwordsDoNotMatch;

  /// Terms agreement prefix
  ///
  /// In en, this message translates to:
  /// **'I agree to the '**
  String get termsAgreement;

  /// Terms of Service link text
  ///
  /// In en, this message translates to:
  /// **'Terms of Service'**
  String get termsOfService;

  /// Conjunction between terms and privacy
  ///
  /// In en, this message translates to:
  /// **' and '**
  String get and;

  /// Privacy Policy link text
  ///
  /// In en, this message translates to:
  /// **'Privacy Policy'**
  String get privacyPolicy;

  /// Accept terms validation error
  ///
  /// In en, this message translates to:
  /// **'Please accept the Terms & Conditions'**
  String get acceptTerms;

  /// Already have account text before sign in link
  ///
  /// In en, this message translates to:
  /// **'Already have an account?'**
  String get alreadyHaveAccount;

  /// Email sent screen header
  ///
  /// In en, this message translates to:
  /// **'Check your email'**
  String get checkEmail;

  /// Verification email sent message
  ///
  /// In en, this message translates to:
  /// **'We sent a verification link to'**
  String get verificationSent;

  /// Instruction to click verification link
  ///
  /// In en, this message translates to:
  /// **'Click the link in the email to verify your account and get started.'**
  String get clickLink;

  /// Resend email button
  ///
  /// In en, this message translates to:
  /// **'Resend Email'**
  String get resendEmail;

  /// Back to sign in button
  ///
  /// In en, this message translates to:
  /// **'Back to Sign In'**
  String get backToSignIn;

  /// Email sent success message
  ///
  /// In en, this message translates to:
  /// **'Verification email sent successfully'**
  String get emailSentSuccess;

  /// Email send failure message
  ///
  /// In en, this message translates to:
  /// **'Failed to send email. Please try again.'**
  String get emailSendFailed;

  /// Check spam folder hint
  ///
  /// In en, this message translates to:
  /// **'Didn\'t receive the email? Check your spam folder or try a different email address.'**
  String get checkSpam;

  /// Terms of Service screen title
  ///
  /// In en, this message translates to:
  /// **'Terms of Service'**
  String get termsOfServiceTitle;

  /// Privacy Policy screen title
  ///
  /// In en, this message translates to:
  /// **'Privacy Policy'**
  String get privacyPolicyTitle;

  /// Loading message when opening browser
  ///
  /// In en, this message translates to:
  /// **'Opening in browser...'**
  String get openingInBrowser;

  /// Error message when cannot open document
  ///
  /// In en, this message translates to:
  /// **'Could not open {title}. Please try again.'**
  String couldNotOpen(String title);

  /// Error message with details
  ///
  /// In en, this message translates to:
  /// **'Failed to open {title}: {error}'**
  String failedToOpen(String title, String error);

  /// Generic error message
  ///
  /// In en, this message translates to:
  /// **'An error occurred'**
  String get anErrorOccurred;

  /// Retry button
  ///
  /// In en, this message translates to:
  /// **'Retry'**
  String get retry;

  /// Application name
  ///
  /// In en, this message translates to:
  /// **'Altea'**
  String get appName;

  /// Home screen hero tagline
  ///
  /// In en, this message translates to:
  /// **'Break the Bad Habits'**
  String get heroTagline;

  /// Menu title
  ///
  /// In en, this message translates to:
  /// **'Menu'**
  String get menu;

  /// Dashboard menu item
  ///
  /// In en, this message translates to:
  /// **'Dashboard'**
  String get dashboard;

  /// Profile menu item
  ///
  /// In en, this message translates to:
  /// **'Profile'**
  String get profile;

  /// Log out menu item
  ///
  /// In en, this message translates to:
  /// **'Log Out'**
  String get logOut;

  /// Logout confirmation dialog title
  ///
  /// In en, this message translates to:
  /// **'Log Out?'**
  String get logOutConfirmTitle;

  /// Logout confirmation dialog message
  ///
  /// In en, this message translates to:
  /// **'Are you sure you want to log out?'**
  String get logOutConfirmMessage;

  /// Cancel button
  ///
  /// In en, this message translates to:
  /// **'Cancel'**
  String get cancel;

  /// Confirm button
  ///
  /// In en, this message translates to:
  /// **'Confirm'**
  String get confirm;

  /// Coming soon label
  ///
  /// In en, this message translates to:
  /// **'Coming Soon'**
  String get comingSoon;

  /// Home menu item
  ///
  /// In en, this message translates to:
  /// **'Home'**
  String get home;

  /// Get started button
  ///
  /// In en, this message translates to:
  /// **'Get Started'**
  String get getStarted;

  /// Onboarding slide 1 title
  ///
  /// In en, this message translates to:
  /// **'Every Journey Starts Here'**
  String get onboardingSlide1Title;

  /// Onboarding slide 1 subtitle
  ///
  /// In en, this message translates to:
  /// **'Take the first step towards freedom. You\'re not alone.'**
  String get onboardingSlide1Subtitle;

  /// Onboarding slide 2 title
  ///
  /// In en, this message translates to:
  /// **'See Your Progress Daily'**
  String get onboardingSlide2Title;

  /// Onboarding slide 2 subtitle
  ///
  /// In en, this message translates to:
  /// **'Track every moment of strength. Celebrate small wins.'**
  String get onboardingSlide2Subtitle;

  /// Onboarding slide 3 title
  ///
  /// In en, this message translates to:
  /// **'You\'re Never Alone'**
  String get onboardingSlide3Title;

  /// Onboarding slide 3 subtitle
  ///
  /// In en, this message translates to:
  /// **'Connect with others on the same path. Share, support, grow.'**
  String get onboardingSlide3Subtitle;

  /// Onboarding slide 4 title
  ///
  /// In en, this message translates to:
  /// **'Reclaim Your Life'**
  String get onboardingSlide4Title;

  /// Onboarding slide 4 subtitle
  ///
  /// In en, this message translates to:
  /// **'Every day is a new beginning. Start your journey today.'**
  String get onboardingSlide4Subtitle;

  /// Google social login button
  ///
  /// In en, this message translates to:
  /// **'Continue with Google'**
  String get continueWithGoogle;

  /// Apple social login button
  ///
  /// In en, this message translates to:
  /// **'Continue with Apple'**
  String get continueWithApple;

  /// Divider text between social and email login
  ///
  /// In en, this message translates to:
  /// **'or'**
  String get or;

  /// Sign up button
  ///
  /// In en, this message translates to:
  /// **'Sign Up'**
  String get signUp;

  /// Login screen title
  ///
  /// In en, this message translates to:
  /// **'Log in to Altea'**
  String get loginToAltea;

  /// Terms agreement prefix for auth screens
  ///
  /// In en, this message translates to:
  /// **'By continuing, you are agreeing to our'**
  String get byContinuing;

  /// OTP verification screen title
  ///
  /// In en, this message translates to:
  /// **'We sent you a code'**
  String get otpTitle;

  /// OTP verification screen subtitle
  ///
  /// In en, this message translates to:
  /// **'Please enter the 6-digit code we sent to {email}'**
  String otpSubtitle(String email);

  /// Resend OTP button
  ///
  /// In en, this message translates to:
  /// **'Get a new code'**
  String get getNewCode;

  /// Cooldown timer text
  ///
  /// In en, this message translates to:
  /// **'Try again in {seconds}'**
  String tryAgainIn(String seconds);

  /// Open email app link
  ///
  /// In en, this message translates to:
  /// **'Open email app'**
  String get openEmailApp;

  /// Invalid OTP error message
  ///
  /// In en, this message translates to:
  /// **'Invalid code. {attempts} attempts remaining.'**
  String invalidCode(int attempts);

  /// Expired OTP error message
  ///
  /// In en, this message translates to:
  /// **'Code expired. Request a new one.'**
  String get codeExpired;

  /// Max attempts error message
  ///
  /// In en, this message translates to:
  /// **'Too many attempts. Try again in {minutes} minutes.'**
  String tooManyAttempts(int minutes);
}

class _AppLocalizationsDelegate
    extends LocalizationsDelegate<AppLocalizations> {
  const _AppLocalizationsDelegate();

  @override
  Future<AppLocalizations> load(Locale locale) {
    return SynchronousFuture<AppLocalizations>(lookupAppLocalizations(locale));
  }

  @override
  bool isSupported(Locale locale) =>
      <String>['de', 'en', 'fr', 'it'].contains(locale.languageCode);

  @override
  bool shouldReload(_AppLocalizationsDelegate old) => false;
}

AppLocalizations lookupAppLocalizations(Locale locale) {
  // Lookup logic when only language code is specified.
  switch (locale.languageCode) {
    case 'de':
      return AppLocalizationsDe();
    case 'en':
      return AppLocalizationsEn();
    case 'fr':
      return AppLocalizationsFr();
    case 'it':
      return AppLocalizationsIt();
  }

  throw FlutterError(
    'AppLocalizations.delegate failed to load unsupported locale "$locale". This is likely '
    'an issue with the localizations generation tool. Please file an issue '
    'on GitHub with a reproducible sample app and the gen-l10n configuration '
    'that was used.',
  );
}
