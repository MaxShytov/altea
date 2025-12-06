import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:flutter_test/flutter_test.dart';
import 'package:go_router/go_router.dart';
import 'package:altea_mobile/data/repositories/auth_repository.dart';
import 'package:altea_mobile/presentation/screens/auth/registration_screen.dart';

import '../../../helpers/test_helpers.dart';

void main() {
  group('RegistrationScreen', () {
    late MockAuthRepository mockRepository;

    setUp(() {
      mockRepository = MockAuthRepository();
    });

    Widget createWidget({MockAuthRepository? repository}) {
      final repo = repository ?? mockRepository;

      return ProviderScope(
        overrides: [
          authRepositoryProvider.overrideWithValue(repo),
        ],
        child: MaterialApp.router(
          routerConfig: GoRouter(
            initialLocation: '/register',
            routes: [
              GoRoute(
                path: '/register',
                builder: (context, state) => const RegistrationScreen(),
              ),
              GoRoute(
                path: '/email-sent',
                builder: (context, state) =>
                    const Scaffold(body: Text('Email Sent Screen')),
              ),
              GoRoute(
                path: '/login',
                builder: (context, state) =>
                    const Scaffold(body: Text('Login Screen')),
              ),
              GoRoute(
                path: '/terms',
                builder: (context, state) =>
                    const Scaffold(body: Text('Terms Screen')),
              ),
              GoRoute(
                path: '/privacy',
                builder: (context, state) =>
                    const Scaffold(body: Text('Privacy Screen')),
              ),
            ],
          ),
        ),
      );
    }

    group('Form Rendering', () {
      testWidgets('renders header texts', (WidgetTester tester) async {
        await tester.pumpWidget(createWidget());
        await tester.pumpAndSettle();

        expect(find.text('Join Altea'), findsOneWidget);
        expect(find.text('Create your account to get started'), findsOneWidget);
      });

      testWidgets('renders email field', (WidgetTester tester) async {
        await tester.pumpWidget(createWidget());
        await tester.pumpAndSettle();

        expect(find.text('Email'), findsOneWidget);
      });

      testWidgets('renders name fields', (WidgetTester tester) async {
        await tester.pumpWidget(createWidget());
        await tester.pumpAndSettle();

        expect(find.text('First Name'), findsOneWidget);
        expect(find.text('Last Name'), findsOneWidget);
      });

      testWidgets('renders password fields', (WidgetTester tester) async {
        await tester.pumpWidget(createWidget());
        await tester.pumpAndSettle();

        expect(find.text('Password'), findsOneWidget);
        expect(find.text('Confirm Password'), findsOneWidget);
      });

      testWidgets('renders terms checkbox', (WidgetTester tester) async {
        await tester.pumpWidget(createWidget());
        await tester.pumpAndSettle();

        expect(find.byType(Checkbox), findsOneWidget);
      });

      testWidgets('renders login link', (WidgetTester tester) async {
        await tester.pumpWidget(createWidget());
        await tester.pumpAndSettle();

        expect(find.text('Already have an account? '), findsOneWidget);
        expect(find.text('Sign In'), findsOneWidget);
      });
    });

    group('Navigation', () {
      testWidgets('navigates to login screen when Sign In is tapped',
          (WidgetTester tester) async {
        await tester.pumpWidget(createWidget());
        await tester.pumpAndSettle();

        // Scroll down to find Sign In button
        await tester.drag(find.byType(SingleChildScrollView), const Offset(0, -300));
        await tester.pumpAndSettle();

        await tester.tap(find.text('Sign In'));
        await tester.pumpAndSettle();

        expect(find.text('Login Screen'), findsOneWidget);
      });
    });

    group('Text Input', () {
      testWidgets('can enter email', (WidgetTester tester) async {
        await tester.pumpWidget(createWidget());
        await tester.pumpAndSettle();

        await tester.enterText(find.byType(TextField).first, 'test@example.com');
        await tester.pumpAndSettle();

        expect(find.text('test@example.com'), findsOneWidget);
      });

      testWidgets('can enter first name', (WidgetTester tester) async {
        await tester.pumpWidget(createWidget());
        await tester.pumpAndSettle();

        await tester.enterText(find.byType(TextField).at(1), 'John');
        await tester.pumpAndSettle();

        expect(find.text('John'), findsOneWidget);
      });

      testWidgets('can enter last name', (WidgetTester tester) async {
        await tester.pumpWidget(createWidget());
        await tester.pumpAndSettle();

        await tester.enterText(find.byType(TextField).at(2), 'Doe');
        await tester.pumpAndSettle();

        expect(find.text('Doe'), findsOneWidget);
      });
    });
  });
}
