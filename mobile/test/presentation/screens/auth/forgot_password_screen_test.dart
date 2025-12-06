import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:flutter_test/flutter_test.dart';
import 'package:go_router/go_router.dart';
import 'package:altea_mobile/presentation/screens/auth/forgot_password_screen.dart';
import 'package:altea_mobile/data/repositories/auth_repository.dart';
import 'package:altea_mobile/l10n/app_localizations.dart';

import '../../../helpers/test_helpers.dart';

void main() {
  late MockAuthRepository mockRepository;

  setUp(() {
    mockRepository = MockAuthRepository();
  });

  Widget createTestWidget({
    List<Override>? overrides,
  }) {
    final router = GoRouter(
      initialLocation: '/forgot-password',
      routes: [
        GoRoute(
          path: '/forgot-password',
          builder: (context, state) => const ForgotPasswordScreen(),
        ),
        GoRoute(
          path: '/login',
          builder: (context, state) => const Scaffold(body: Text('Login')),
        ),
      ],
    );

    return ProviderScope(
      overrides: [
        authRepositoryProvider.overrideWithValue(mockRepository),
        ...?overrides,
      ],
      child: MaterialApp.router(
        routerConfig: router,
        localizationsDelegates: AppLocalizations.localizationsDelegates,
        supportedLocales: AppLocalizations.supportedLocales,
        locale: const Locale('en'),
      ),
    );
  }

  group('ForgotPasswordScreen', () {
    testWidgets('should display all required elements', (tester) async {
      await tester.pumpWidget(createTestWidget());
      await tester.pumpAndSettle();

      // Title
      expect(find.text('Forgot Password'), findsWidgets);

      // Subtitle
      expect(find.text('Enter your email to receive reset instructions'),
          findsOneWidget);

      // Email field
      expect(find.text('Email'), findsOneWidget);

      // Submit button
      expect(find.text('Send Reset Link'), findsOneWidget);

      // Back to login link
      expect(find.text('Back to Sign In'), findsOneWidget);
    });

    testWidgets('should show validation error when email is empty',
        (tester) async {
      await tester.pumpWidget(createTestWidget());
      await tester.pumpAndSettle();

      // Tap submit button without entering email
      await tester.tap(find.text('Send Reset Link'));
      await tester.pumpAndSettle();

      // Should show email required error
      expect(find.text('Email is required'), findsOneWidget);
    });

    testWidgets('should show validation error for invalid email',
        (tester) async {
      await tester.pumpWidget(createTestWidget());
      await tester.pumpAndSettle();

      // Enter invalid email
      await tester.enterText(find.byType(TextField), 'invalid-email');
      await tester.tap(find.text('Send Reset Link'));
      await tester.pumpAndSettle();

      // Should show invalid email error
      expect(find.text('Please enter a valid email'), findsOneWidget);
    });

    testWidgets('should call forgotPassword when valid email is submitted',
        (tester) async {
      await tester.pumpWidget(createTestWidget());
      await tester.pumpAndSettle();

      // Enter valid email
      await tester.enterText(find.byType(TextField), 'test@example.com');
      await tester.tap(find.text('Send Reset Link'));
      await tester.pump();

      // Should show loading indicator
      expect(find.byType(CircularProgressIndicator), findsOneWidget);

      await tester.pumpAndSettle();

      // Should show success view
      expect(find.text('Check your email'), findsOneWidget);
      expect(
          find.text(
              'If an account exists with this email, you will receive password reset instructions.'),
          findsOneWidget);
    });

    testWidgets('should have back button in app bar',
        (tester) async {
      await tester.pumpWidget(createTestWidget());
      await tester.pumpAndSettle();

      // Back button should exist
      expect(find.byIcon(Icons.arrow_back), findsOneWidget);
    });

    testWidgets('should show success state with back to sign in button',
        (tester) async {
      await tester.pumpWidget(createTestWidget());
      await tester.pumpAndSettle();

      // Submit valid email
      await tester.enterText(find.byType(TextField), 'test@example.com');
      await tester.tap(find.text('Send Reset Link'));
      await tester.pumpAndSettle();

      // Should show success view with "Back to Sign In" button
      expect(find.text('Check your email'), findsOneWidget);
      expect(find.text('Back to Sign In'), findsOneWidget);
    });

  });

  group('ForgotPasswordScreen email validation', () {
    testWidgets('should reject invalid email formats', (tester) async {
      await tester.pumpWidget(createTestWidget());
      await tester.pumpAndSettle();

      // Enter invalid email
      await tester.enterText(find.byType(TextField), 'invalid');
      await tester.tap(find.text('Send Reset Link'));
      await tester.pumpAndSettle();

      // Should show validation error
      expect(find.text('Please enter a valid email'), findsOneWidget);
    });

    testWidgets('should reject email without domain extension', (tester) async {
      await tester.pumpWidget(createTestWidget());
      await tester.pumpAndSettle();

      // Enter email without proper domain
      await tester.enterText(find.byType(TextField), 'no@domain');
      await tester.tap(find.text('Send Reset Link'));
      await tester.pumpAndSettle();

      // Should show validation error
      expect(find.text('Please enter a valid email'), findsOneWidget);
    });
  });
}
