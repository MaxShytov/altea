// ignore: unused_import
import 'package:intl/intl.dart' as intl;
import 'app_localizations.dart';

// ignore_for_file: type=lint

/// The translations for French (`fr`).
class AppLocalizationsFr extends AppLocalizations {
  AppLocalizationsFr([String locale = 'fr']) : super(locale);

  @override
  String get signIn => 'Connexion';

  @override
  String get welcomeBack => 'Bon retour';

  @override
  String get signInSubtitle => 'Connectez-vous pour continuer votre parcours';

  @override
  String get email => 'E-mail';

  @override
  String get emailHint => 'Entrez votre e-mail';

  @override
  String get emailRequired => 'L\'e-mail est requis';

  @override
  String get emailInvalid => 'Veuillez entrer un e-mail valide';

  @override
  String get password => 'Mot de passe';

  @override
  String get passwordHint => 'Entrez votre mot de passe';

  @override
  String get passwordRequired => 'Le mot de passe est requis';

  @override
  String get forgotPassword => 'Mot de passe oublié ?';

  @override
  String get forgotPasswordTitle => 'Mot de passe oublié';

  @override
  String get forgotPasswordSubtitle =>
      'Entrez votre e-mail pour recevoir les instructions';

  @override
  String get sendResetLink => 'Envoyer le lien';

  @override
  String get resetLinkSent => 'Lien envoyé !';

  @override
  String get resetLinkSentMessage =>
      'Si un compte existe avec cet e-mail, vous recevrez les instructions de réinitialisation.';

  @override
  String get checkYourEmail => 'Vérifiez votre e-mail';

  @override
  String get noAccount => 'Pas encore de compte ?';

  @override
  String get register => 'S\'inscrire';

  @override
  String get resend => 'Renvoyer';

  @override
  String get resendVerificationHint =>
      'Veuillez vous réinscrire pour recevoir un nouvel e-mail de vérification.';

  @override
  String get createAccount => 'Créer un compte';

  @override
  String get joinAltea => 'Rejoignez Altea';

  @override
  String get createAccountSubtitle => 'Créez votre compte pour commencer';

  @override
  String get firstName => 'Prénom';

  @override
  String get firstNameHint => 'Prénom';

  @override
  String fieldRequired(String field) {
    return '$field est requis';
  }

  @override
  String fieldMinLength(String field, int count) {
    return '$field doit contenir au moins $count caractères';
  }

  @override
  String get lastName => 'Nom';

  @override
  String get lastNameHint => 'Nom';

  @override
  String get passwordHintRegistration => 'Au moins 8 caractères';

  @override
  String get passwordMinLength =>
      'Le mot de passe doit contenir au moins 8 caractères';

  @override
  String get confirmPassword => 'Confirmer le mot de passe';

  @override
  String get confirmPasswordHint => 'Ressaisissez votre mot de passe';

  @override
  String get confirmPasswordRequired => 'Veuillez confirmer votre mot de passe';

  @override
  String get passwordsDoNotMatch => 'Les mots de passe ne correspondent pas';

  @override
  String get termsAgreement => 'J\'accepte les ';

  @override
  String get termsOfService => 'Conditions d\'utilisation';

  @override
  String get and => ' et ';

  @override
  String get privacyPolicy => 'Politique de confidentialité';

  @override
  String get acceptTerms => 'Veuillez accepter les conditions d\'utilisation';

  @override
  String get alreadyHaveAccount => 'Déjà un compte ?';

  @override
  String get checkEmail => 'Vérifiez votre e-mail';

  @override
  String get verificationSent => 'Nous avons envoyé un lien de vérification à';

  @override
  String get clickLink =>
      'Cliquez sur le lien dans l\'e-mail pour vérifier votre compte et commencer.';

  @override
  String get resendEmail => 'Renvoyer l\'e-mail';

  @override
  String get backToSignIn => 'Retour à la connexion';

  @override
  String get emailSentSuccess => 'E-mail de vérification envoyé avec succès';

  @override
  String get emailSendFailed =>
      'Échec de l\'envoi de l\'e-mail. Veuillez réessayer.';

  @override
  String get checkSpam =>
      'Vous n\'avez pas reçu l\'e-mail ? Vérifiez votre dossier spam ou essayez une autre adresse e-mail.';

  @override
  String get termsOfServiceTitle => 'Conditions d\'utilisation';

  @override
  String get privacyPolicyTitle => 'Politique de confidentialité';

  @override
  String get openingInBrowser => 'Ouverture dans le navigateur...';

  @override
  String couldNotOpen(String title) {
    return 'Impossible d\'ouvrir $title. Veuillez réessayer.';
  }

  @override
  String failedToOpen(String title, String error) {
    return 'Échec de l\'ouverture de $title : $error';
  }

  @override
  String get anErrorOccurred => 'Une erreur s\'est produite';

  @override
  String get retry => 'Réessayer';

  @override
  String get appName => 'Altea';

  @override
  String get heroTagline => 'Brisez les mauvaises habitudes';

  @override
  String get menu => 'Menu';

  @override
  String get dashboard => 'Tableau de bord';

  @override
  String get profile => 'Profil';

  @override
  String get logOut => 'Se déconnecter';

  @override
  String get logOutConfirmTitle => 'Se déconnecter?';

  @override
  String get logOutConfirmMessage =>
      'Êtes-vous sûr de vouloir vous déconnecter?';

  @override
  String get cancel => 'Annuler';

  @override
  String get confirm => 'Confirmer';

  @override
  String get comingSoon => 'Bientôt disponible';

  @override
  String get home => 'Accueil';

  @override
  String get getStarted => 'Commencer';
}
