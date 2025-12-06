# Altea Design Tokens

**Reference:** Full design token specifications for Flutter implementation.

---

## Typography (SF Pro)

```dart
// lib/core/theme/typography.dart
class AlteaTypography {
  // Large Title - 34pt
  static const TextStyle largeTitle = TextStyle(
    fontFamily: 'SF Pro Display',
    fontSize: 34,
    fontWeight: FontWeight.w400,
    letterSpacing: 0.37,
    height: 1.176,
  );

  // Title 1 - 28pt
  static const TextStyle title1 = TextStyle(
    fontFamily: 'SF Pro Display',
    fontSize: 28,
    fontWeight: FontWeight.w400,
    letterSpacing: 0.36,
    height: 1.214,
  );

  // Title 2 - 22pt
  static const TextStyle title2 = TextStyle(
    fontFamily: 'SF Pro Display',
    fontSize: 22,
    fontWeight: FontWeight.w400,
    letterSpacing: 0.35,
    height: 1.273,
  );

  // Title 3 - 20pt
  static const TextStyle title3 = TextStyle(
    fontFamily: 'SF Pro Display',
    fontSize: 20,
    fontWeight: FontWeight.w400,
    letterSpacing: 0.38,
    height: 1.2,
  );

  // Headline - 17pt, Semibold
  static const TextStyle headline = TextStyle(
    fontFamily: 'SF Pro Text',
    fontSize: 17,
    fontWeight: FontWeight.w600,
    letterSpacing: -0.41,
    height: 1.294,
  );

  // Body - 17pt
  static const TextStyle body = TextStyle(
    fontFamily: 'SF Pro Text',
    fontSize: 17,
    fontWeight: FontWeight.w400,
    letterSpacing: -0.41,
    height: 1.294,
  );

  // Callout - 16pt
  static const TextStyle callout = TextStyle(
    fontFamily: 'SF Pro Text',
    fontSize: 16,
    fontWeight: FontWeight.w400,
    letterSpacing: -0.32,
    height: 1.3125,
  );

  // Subhead - 15pt
  static const TextStyle subhead = TextStyle(
    fontFamily: 'SF Pro Text',
    fontSize: 15,
    fontWeight: FontWeight.w400,
    letterSpacing: -0.24,
    height: 1.333,
  );

  // Footnote - 13pt
  static const TextStyle footnote = TextStyle(
    fontFamily: 'SF Pro Text',
    fontSize: 13,
    fontWeight: FontWeight.w400,
    letterSpacing: -0.08,
    height: 1.385,
  );

  // Caption 1 - 12pt
  static const TextStyle caption1 = TextStyle(
    fontFamily: 'SF Pro Text',
    fontSize: 12,
    fontWeight: FontWeight.w400,
    letterSpacing: 0,
    height: 1.333,
  );

  // Caption 2 - 11pt
  static const TextStyle caption2 = TextStyle(
    fontFamily: 'SF Pro Text',
    fontSize: 11,
    fontWeight: FontWeight.w400,
    letterSpacing: 0.06,
    height: 1.182,
  );
}
```

---

## Colors

```dart
// lib/core/theme/colors.dart
class AlteaColors {
  // Primary
  static const Color primary = Color(0xFF667EEA);
  static const Color primaryDark = Color(0xFF5568D3);
  static const Color primaryLight = Color(0xFF8B9EF7);

  // Secondary
  static const Color secondary = Color(0xFF764BA2);
  static const Color secondaryDark = Color(0xFF5D3C82);
  static const Color secondaryLight = Color(0xFF9466C4);

  // iOS System Colors
  static const Color systemRed = Color(0xFFFF3B30);
  static const Color systemOrange = Color(0xFFFF9500);
  static const Color systemYellow = Color(0xFFFFCC00);
  static const Color systemGreen = Color(0xFF34C759);
  static const Color systemTeal = Color(0xFF5AC8FA);
  static const Color systemBlue = Color(0xFF007AFF);
  static const Color systemIndigo = Color(0xFF5856D6);
  static const Color systemPurple = Color(0xFFAF52DE);
  static const Color systemPink = Color(0xFFFF2D55);

  // Status
  static const Color success = Color(0xFF10B981);
  static const Color error = Color(0xFFEF4444);
  static const Color warning = Color(0xFFF59E0B);
  static const Color info = Color(0xFF3B82F6);

  // Addiction Types
  static const Color alcohol = Color(0xFFF59E0B);
  static const Color drugs = Color(0xFFEF4444);
  static const Color tobacco = Color(0xFF8B5CF6);
  static const Color gambling = Color(0xFF10B981);
  static const Color smartphone = Color(0xFF3B82F6);

  // Gray Scale (iOS)
  static const Color gray1 = Color(0xFF8E8E93);
  static const Color gray2 = Color(0xFFAEAEB2);
  static const Color gray3 = Color(0xFFC7C7CC);
  static const Color gray4 = Color(0xFFD1D1D6);
  static const Color gray5 = Color(0xFFE5E5EA);
  static const Color gray6 = Color(0xFFF2F2F7);

  // Backgrounds (Light)
  static const Color systemBackground = Color(0xFFFFFFFF);
  static const Color secondarySystemBackground = Color(0xFFF2F2F7);
  static const Color tertiarySystemBackground = Color(0xFFFFFFFF);
  static const Color systemGroupedBackground = Color(0xFFF2F2F7);
  static const Color secondarySystemGroupedBackground = Color(0xFFFFFFFF);

  // Labels
  static const Color label = Color(0xFF000000);
  static const Color secondaryLabel = Color(0x993C3C43);
  static const Color tertiaryLabel = Color(0x4C3C3C43);
  static const Color quaternaryLabel = Color(0x2D3C3C43);

  // Separators
  static const Color separator = Color(0x493C3C43);
  static const Color opaqueSeparator = Color(0xFFC6C6C8);
}

// Dark Mode
class AlteaColorsDark {
  static const Color systemBackground = Color(0xFF000000);
  static const Color secondarySystemBackground = Color(0xFF1C1C1E);
  static const Color tertiarySystemBackground = Color(0xFF2C2C2E);
  static const Color label = Color(0xFFFFFFFF);
  static const Color secondaryLabel = Color(0x99EBEBF5);
  static const Color tertiaryLabel = Color(0x4CEBEBF5);
}
```

---

## Spacing

```dart
// lib/core/theme/spacing.dart
class AlteaSpacing {
  // Base unit: 4pt (iOS grid)
  static const double xs = 4.0;
  static const double sm = 8.0;
  static const double md = 12.0;
  static const double lg = 16.0;
  static const double xl = 20.0;
  static const double xxl = 24.0;
  static const double xxxl = 32.0;

  // Screen margins
  static const double screenHorizontal = 16.0;
  static const double screenVertical = 20.0;

  // Component spacing
  static const double betweenSections = 32.0;
  static const double betweenItems = 16.0;
  static const double betweenElements = 8.0;
}
```

---

## Dimensions

```dart
// lib/core/theme/dimensions.dart
class AlteaDimensions {
  // Corner radius (iOS standards)
  static const double cornerRadiusSmall = 8.0;
  static const double cornerRadiusMedium = 10.0;
  static const double cornerRadiusLarge = 12.0;
  static const double cornerRadiusXLarge = 16.0;

  // Component sizes
  static const double buttonHeight = 50.0;
  static const double inputHeight = 44.0;
  static const double listItemHeight = 44.0;
  static const double iconSize = 24.0;
  static const double iconSizeLarge = 32.0;
}
```
