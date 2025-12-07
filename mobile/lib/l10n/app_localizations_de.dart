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
  String get forgotPasswordTitle => 'Passwort vergessen';

  @override
  String get forgotPasswordSubtitle =>
      'Geben Sie Ihre E-Mail ein, um Anweisungen zum Zurücksetzen zu erhalten';

  @override
  String get sendResetLink => 'Link senden';

  @override
  String get resetLinkSent => 'Link gesendet!';

  @override
  String get resetLinkSentMessage =>
      'Wenn ein Konto mit dieser E-Mail existiert, erhalten Sie Anweisungen zum Zurücksetzen des Passworts.';

  @override
  String get checkYourEmail => 'Prüfen Sie Ihre E-Mail';

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

  @override
  String get appName => 'Altea';

  @override
  String get heroTagline => 'Brechen Sie die schlechten Gewohnheiten';

  @override
  String get menu => 'Menü';

  @override
  String get dashboard => 'Dashboard';

  @override
  String get profile => 'Profil';

  @override
  String get logOut => 'Abmelden';

  @override
  String get logOutConfirmTitle => 'Abmelden?';

  @override
  String get logOutConfirmMessage => 'Möchten Sie sich wirklich abmelden?';

  @override
  String get cancel => 'Abbrechen';

  @override
  String get confirm => 'Bestätigen';

  @override
  String get comingSoon => 'Demnächst';

  @override
  String get home => 'Startseite';

  @override
  String get getStarted => 'Loslegen';

  @override
  String get onboardingSlide1Title => 'Jede Reise beginnt hier';

  @override
  String get onboardingSlide1Subtitle =>
      'Mach den ersten Schritt in die Freiheit. Du bist nicht allein.';

  @override
  String get onboardingSlide2Title => 'Sehe deinen Fortschritt täglich';

  @override
  String get onboardingSlide2Subtitle =>
      'Verfolge jeden Moment der Stärke. Feiere kleine Siege.';

  @override
  String get onboardingSlide3Title => 'Du bist niemals allein';

  @override
  String get onboardingSlide3Subtitle =>
      'Vernetze dich mit anderen auf demselben Weg. Teilen, unterstützen, wachsen.';

  @override
  String get onboardingSlide4Title => 'Erobere dein Leben zurück';

  @override
  String get onboardingSlide4Subtitle =>
      'Jeder Tag ist ein neuer Anfang. Beginne deine Reise heute.';

  @override
  String get continueWithGoogle => 'Mit Google fortfahren';

  @override
  String get continueWithApple => 'Mit Apple fortfahren';

  @override
  String get or => 'oder';

  @override
  String get signUp => 'Registrieren';

  @override
  String get loginToAltea => 'Bei Altea anmelden';

  @override
  String get byContinuing => 'Durch Fortfahren stimmen Sie unseren';

  @override
  String get otpTitle => 'Wir haben Ihnen einen Code gesendet';

  @override
  String otpSubtitle(String email) {
    return 'Bitte geben Sie den 6-stelligen Code ein, den wir an $email gesendet haben';
  }

  @override
  String get getNewCode => 'Neuen Code anfordern';

  @override
  String tryAgainIn(String seconds) {
    return 'Erneut versuchen in $seconds';
  }

  @override
  String get openEmailApp => 'E-Mail-App öffnen';

  @override
  String invalidCode(int attempts) {
    return 'Ungültiger Code. $attempts Versuche übrig.';
  }

  @override
  String get codeExpired => 'Code abgelaufen. Fordern Sie einen neuen an.';

  @override
  String tooManyAttempts(int minutes) {
    return 'Zu viele Versuche. Versuchen Sie es in $minutes Minuten erneut.';
  }
}
