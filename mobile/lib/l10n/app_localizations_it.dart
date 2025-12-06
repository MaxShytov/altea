// ignore: unused_import
import 'package:intl/intl.dart' as intl;
import 'app_localizations.dart';

// ignore_for_file: type=lint

/// The translations for Italian (`it`).
class AppLocalizationsIt extends AppLocalizations {
  AppLocalizationsIt([String locale = 'it']) : super(locale);

  @override
  String get signIn => 'Accedi';

  @override
  String get welcomeBack => 'Bentornato';

  @override
  String get signInSubtitle => 'Accedi per continuare il tuo percorso';

  @override
  String get email => 'Email';

  @override
  String get emailHint => 'Inserisci la tua email';

  @override
  String get emailRequired => 'L\'email è obbligatoria';

  @override
  String get emailInvalid => 'Inserisci un\'email valida';

  @override
  String get password => 'Password';

  @override
  String get passwordHint => 'Inserisci la tua password';

  @override
  String get passwordRequired => 'La password è obbligatoria';

  @override
  String get forgotPassword => 'Password dimenticata?';

  @override
  String get forgotPasswordComingSoon =>
      'Funzione password dimenticata in arrivo';

  @override
  String get noAccount => 'Non hai un account?';

  @override
  String get register => 'Registrati';

  @override
  String get resend => 'Invia di nuovo';

  @override
  String get resendVerificationHint =>
      'Per favore registrati di nuovo per ricevere una nuova email di verifica.';

  @override
  String get createAccount => 'Crea account';

  @override
  String get joinAltea => 'Unisciti a Altea';

  @override
  String get createAccountSubtitle => 'Crea il tuo account per iniziare';

  @override
  String get firstName => 'Nome';

  @override
  String get firstNameHint => 'Nome';

  @override
  String fieldRequired(String field) {
    return '$field è obbligatorio';
  }

  @override
  String fieldMinLength(String field, int count) {
    return '$field deve avere almeno $count caratteri';
  }

  @override
  String get lastName => 'Cognome';

  @override
  String get lastNameHint => 'Cognome';

  @override
  String get passwordHintRegistration => 'Almeno 8 caratteri';

  @override
  String get passwordMinLength => 'La password deve avere almeno 8 caratteri';

  @override
  String get confirmPassword => 'Conferma password';

  @override
  String get confirmPasswordHint => 'Reinserisci la tua password';

  @override
  String get confirmPasswordRequired => 'Per favore conferma la tua password';

  @override
  String get passwordsDoNotMatch => 'Le password non corrispondono';

  @override
  String get termsAgreement => 'Accetto i ';

  @override
  String get termsOfService => 'Termini di servizio';

  @override
  String get and => ' e ';

  @override
  String get privacyPolicy => 'Informativa sulla privacy';

  @override
  String get acceptTerms => 'Per favore accetta i termini e condizioni';

  @override
  String get alreadyHaveAccount => 'Hai già un account?';

  @override
  String get checkEmail => 'Controlla la tua email';

  @override
  String get verificationSent => 'Abbiamo inviato un link di verifica a';

  @override
  String get clickLink =>
      'Clicca sul link nell\'email per verificare il tuo account e iniziare.';

  @override
  String get resendEmail => 'Invia di nuovo l\'email';

  @override
  String get backToSignIn => 'Torna all\'accesso';

  @override
  String get emailSentSuccess => 'Email di verifica inviata con successo';

  @override
  String get emailSendFailed => 'Impossibile inviare l\'email. Riprova.';

  @override
  String get checkSpam =>
      'Non hai ricevuto l\'email? Controlla la cartella spam o prova con un altro indirizzo email.';

  @override
  String get termsOfServiceTitle => 'Termini di servizio';

  @override
  String get privacyPolicyTitle => 'Informativa sulla privacy';

  @override
  String get openingInBrowser => 'Apertura nel browser...';

  @override
  String couldNotOpen(String title) {
    return 'Impossibile aprire $title. Riprova.';
  }

  @override
  String failedToOpen(String title, String error) {
    return 'Impossibile aprire $title: $error';
  }

  @override
  String get anErrorOccurred => 'Si è verificato un errore';

  @override
  String get retry => 'Riprova';
}
