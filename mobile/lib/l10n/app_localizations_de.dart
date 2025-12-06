// ignore: unused_import
import 'package:intl/intl.dart' as intl;
import 'app_localizations.dart';

// ignore_for_file: type=lint

/// The translations for German (`de`).
class AppLocalizationsDe extends AppLocalizations {
  AppLocalizationsDe([String locale = 'de']) : super(locale);

  @override
  String get signIn => 'Anmelden';

  @override
  String get welcomeBack => 'Willkommen zurück';

  @override
  String get signInSubtitle => 'Melden Sie sich an, um Ihre Reise fortzusetzen';

  @override
  String get email => 'E-Mail';

  @override
  String get emailHint => 'Geben Sie Ihre E-Mail ein';

  @override
  String get emailRequired => 'E-Mail ist erforderlich';

  @override
  String get emailInvalid => 'Bitte geben Sie eine gültige E-Mail ein';

  @override
  String get password => 'Passwort';

  @override
  String get passwordHint => 'Geben Sie Ihr Passwort ein';

  @override
  String get passwordRequired => 'Passwort ist erforderlich';

  @override
  String get forgotPassword => 'Passwort vergessen?';

  @override
  String get forgotPasswordComingSoon =>
      'Passwort vergessen Funktion kommt bald';

  @override
  String get noAccount => 'Noch kein Konto?';

  @override
  String get register => 'Registrieren';

  @override
  String get resend => 'Erneut senden';

  @override
  String get resendVerificationHint =>
      'Bitte registrieren Sie sich erneut, um eine neue Bestätigungs-E-Mail zu erhalten.';

  @override
  String get createAccount => 'Konto erstellen';

  @override
  String get joinAltea => 'Altea beitreten';

  @override
  String get createAccountSubtitle => 'Erstellen Sie Ihr Konto, um zu beginnen';

  @override
  String get firstName => 'Vorname';

  @override
  String get firstNameHint => 'Vorname';

  @override
  String fieldRequired(String field) {
    return '$field ist erforderlich';
  }

  @override
  String fieldMinLength(String field, int count) {
    return '$field muss mindestens $count Zeichen haben';
  }

  @override
  String get lastName => 'Nachname';

  @override
  String get lastNameHint => 'Nachname';

  @override
  String get passwordHintRegistration => 'Mindestens 8 Zeichen';

  @override
  String get passwordMinLength => 'Passwort muss mindestens 8 Zeichen haben';

  @override
  String get confirmPassword => 'Passwort bestätigen';

  @override
  String get confirmPasswordHint => 'Passwort erneut eingeben';

  @override
  String get confirmPasswordRequired => 'Bitte bestätigen Sie Ihr Passwort';

  @override
  String get passwordsDoNotMatch => 'Passwörter stimmen nicht überein';

  @override
  String get termsAgreement => 'Ich akzeptiere die ';

  @override
  String get termsOfService => 'Nutzungsbedingungen';

  @override
  String get and => ' und ';

  @override
  String get privacyPolicy => 'Datenschutzrichtlinie';

  @override
  String get acceptTerms => 'Bitte akzeptieren Sie die Nutzungsbedingungen';

  @override
  String get alreadyHaveAccount => 'Bereits ein Konto?';

  @override
  String get checkEmail => 'Prüfen Sie Ihre E-Mail';

  @override
  String get verificationSent => 'Wir haben einen Bestätigungslink gesendet an';

  @override
  String get clickLink =>
      'Klicken Sie auf den Link in der E-Mail, um Ihr Konto zu bestätigen und zu beginnen.';

  @override
  String get resendEmail => 'E-Mail erneut senden';

  @override
  String get backToSignIn => 'Zurück zur Anmeldung';

  @override
  String get emailSentSuccess => 'Bestätigungs-E-Mail erfolgreich gesendet';

  @override
  String get emailSendFailed =>
      'E-Mail konnte nicht gesendet werden. Bitte versuchen Sie es erneut.';

  @override
  String get checkSpam =>
      'E-Mail nicht erhalten? Prüfen Sie Ihren Spam-Ordner oder versuchen Sie eine andere E-Mail-Adresse.';

  @override
  String get termsOfServiceTitle => 'Nutzungsbedingungen';

  @override
  String get privacyPolicyTitle => 'Datenschutzrichtlinie';

  @override
  String get openingInBrowser => 'Wird im Browser geöffnet...';

  @override
  String couldNotOpen(String title) {
    return '$title konnte nicht geöffnet werden. Bitte versuchen Sie es erneut.';
  }

  @override
  String failedToOpen(String title, String error) {
    return 'Fehler beim Öffnen von $title: $error';
  }

  @override
  String get anErrorOccurred => 'Ein Fehler ist aufgetreten';

  @override
  String get retry => 'Erneut versuchen';
}
