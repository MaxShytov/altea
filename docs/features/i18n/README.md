# Multi-language Support (i18n) Feature

## Overview

Multi-language support allows the Altea mobile application to display all user interface text in the user's preferred language: English, German, French, or Italian.

### Problem Statement

Altea operates in Switzerland, a multilingual country with four official languages. Users expect applications to respect their language preferences automatically, using the device's system settings rather than requiring manual configuration within the app.

### Use Cases

| ID | Use Case | Actor |
|----|----------|-------|
| UC1 | App automatically uses device language | New User |
| UC2 | Change app language via iOS Settings | iOS User |
| UC3 | Change app language via Android Settings | Android 13+ User |
| UC4 | Use different language for Altea than other apps | Multilingual User |
| UC5 | Fallback to English for unsupported language | User with unsupported system language |

## User Flow

```
┌─────────────────────────────────────────────────────────────────────┐
│                    FIRST APP LAUNCH                                  │
└─────────────────────────────────────────────────────────────────────┘
                              │
                              ▼
                 ┌───────────────────────┐
                 │  Device Language?     │
                 └───────────┬───────────┘
                             │
         ┌───────────┬───────┼───────┬───────────┐
         │           │       │       │           │
         ▼           ▼       ▼       ▼           ▼
      ┌─────┐    ┌─────┐  ┌─────┐ ┌─────┐   ┌─────────┐
      │ EN  │    │ DE  │  │ FR  │ │ IT  │   │ Other   │
      └──┬──┘    └──┬──┘  └──┬──┘ └──┬──┘   └────┬────┘
         │          │       │       │            │
         ▼          ▼       ▼       ▼            ▼
      English    German  French  Italian     English
                                            (fallback)

┌─────────────────────────────────────────────────────────────────────┐
│                  CHANGING LANGUAGE                                   │
└─────────────────────────────────────────────────────────────────────┘

iOS:
  Settings → Altea → Language → [Select Language]
                                       │
                                       ▼
                              App restarts in
                              selected language

Android 13+:
  Settings → Apps → Altea → Language → [Select Language]
                                              │
                                              ▼
                                     App restarts in
                                     selected language
```

## Supported Languages

| Language | Code | Region | Status |
|----------|------|--------|--------|
| English | `en` | Default/Fallback | Primary |
| German | `de` | German-speaking Switzerland | Full support |
| French | `fr` | French-speaking Switzerland | Full support |
| Italian | `it` | Italian-speaking Switzerland | Full support |

## Screens Affected

All screens in the application are fully localized:

### 1. Login Screen
**Path:** `/login`
**File:** `mobile/lib/presentation/screens/auth/login_screen.dart`

| Element | EN | DE | FR | IT |
|---------|----|----|----|----|
| Title | Sign In | Anmelden | Connexion | Accedi |
| Subtitle | Sign in to continue your journey | Melden Sie sich an... | Connectez-vous... | Accedi per continuare... |
| Email label | Email | E-Mail | E-mail | Email |
| Password label | Password | Passwort | Mot de passe | Password |
| Submit button | Sign In | Anmelden | Connexion | Accedi |

### 2. Registration Screen
**Path:** `/register`
**File:** `mobile/lib/presentation/screens/auth/registration_screen.dart`

| Element | EN | DE | FR | IT |
|---------|----|----|----|----|
| Title | Create Account | Konto erstellen | Créer un compte | Crea account |
| First name | First Name | Vorname | Prénom | Nome |
| Last name | Last Name | Nachname | Nom | Cognome |
| Terms text | Terms of Service | Nutzungsbedingungen | Conditions d'utilisation | Termini di servizio |

### 3. Email Sent Screen
**Path:** `/email-sent`
**File:** `mobile/lib/presentation/screens/auth/email_sent_screen.dart`

| Element | EN | DE | FR | IT |
|---------|----|----|----|----|
| Title | Check your email | Prüfen Sie Ihre E-Mail | Vérifiez votre e-mail | Controlla la tua email |
| Resend button | Resend Email | E-Mail erneut senden | Renvoyer l'e-mail | Invia di nuovo l'email |

### 4. Legal Screens
**Paths:** `/terms`, `/privacy`

| Element | EN | DE | FR | IT |
|---------|----|----|----|----|
| Terms title | Terms of Service | Nutzungsbedingungen | Conditions d'utilisation | Termini di servizio |
| Privacy title | Privacy Policy | Datenschutzrichtlinie | Politique de confidentialité | Informativa sulla privacy |

## Validation Messages

All validation error messages are localized:

| Error Type | EN | DE |
|------------|----|----|
| Required field | {field} is required | {field} ist erforderlich |
| Min length | {field} must be at least {count} characters | {field} muss mindestens {count} Zeichen haben |
| Invalid email | Please enter a valid email | Bitte geben Sie eine gültige E-Mail ein |
| Password mismatch | Passwords do not match | Passwörter stimmen nicht überein |

## How to Change Language

### iOS (13+)

1. Open **Settings** app
2. Scroll down and tap **Altea**
3. Tap **Language**
4. Select your preferred language
5. Return to Altea - it will restart in the new language

### Android (13+)

1. Open **Settings** app
2. Go to **Apps** → **Altea**
3. Tap **Language**
4. Select your preferred language
5. Return to Altea - it will restart in the new language

### Older Devices

On iOS < 13 or Android < 13, the app uses the system-wide language setting. Change your device language to change the app language.

## Technical Summary

| Aspect | Details |
|--------|---------|
| Framework | Flutter `flutter_localizations` |
| Format | ARB (Application Resource Bundle) |
| Generation | `flutter gen-l10n` |
| Total strings | 48 translation keys |
| Parameterized | 4 strings with placeholders |
| Tests | 71 automated tests |

For full technical details, see [i18n Architecture Documentation](../../architecture/flutter-apps/i18n.md).

## File Structure

```
mobile/
├── l10n.yaml                    # Generation config
├── lib/
│   └── l10n/
│       ├── app_en.arb           # English (template)
│       ├── app_de.arb           # German
│       ├── app_fr.arb           # French
│       └── app_it.arb           # Italian
└── test/
    └── l10n/                    # Localization tests
```

## Testing

### Automated Tests

```bash
cd mobile
flutter test test/l10n/
```

71 tests cover:
- ARB file structure validation
- Key consistency across all languages
- Placeholder format validation
- Locale switching behavior
- Fallback to English
- Regional variant resolution (de_CH → de)
- Screen-level localization (login, registration, email sent)

### Manual Testing Checklist

| Test | Steps | Expected |
|------|-------|----------|
| Default language | Install app with device in German | App displays in German |
| Fallback | Set device to Chinese, open app | App displays in English |
| iOS per-app | Settings → Altea → Language → French | App displays in French |
| Android per-app | Settings → Apps → Altea → Language → Italian | App displays in Italian |
| All screens | Navigate through all screens | All text in selected language |
| Validation | Submit empty login form | Error messages in selected language |

## Known Limitations

1. **No in-app language picker** - Uses native system settings (by design)
2. **Android < 13** - Only system-wide language, no per-app setting
3. **No RTL languages** - Arabic, Hebrew not supported
4. **Backend messages in English** - API errors not yet localized

## FAQ

**Q: Why can't I change language inside the app?**
A: Altea uses the native per-app language setting, which is the standard for Swiss apps (like Google Maps, banking apps). This provides a consistent experience with the rest of your device.

**Q: My device is in Swiss German (de_CH), will it work?**
A: Yes, regional variants like `de_CH`, `fr_CH`, `it_CH` automatically use the base language.

**Q: What happens if I use an unsupported language?**
A: The app will display in English as the fallback language.

**Q: How do I report a translation error?**
A: Contact support with the screen name, the incorrect text, and the suggested correction.

## Related Documentation

- [i18n Architecture](../../architecture/flutter-apps/i18n.md) - Full technical documentation
- [Mobile App Architecture](../../architecture/flutter-apps/mobile-app.md)
- [User Registration](../user-registration/README.md)
- [User Login](../user-login/README.md)
