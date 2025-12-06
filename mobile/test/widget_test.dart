import 'package:flutter_test/flutter_test.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';

import 'package:altea_mobile/main.dart';

void main() {
  testWidgets('App renders login screen', (WidgetTester tester) async {
    await tester.pumpWidget(
      const ProviderScope(
        child: AlteaApp(),
      ),
    );
    await tester.pumpAndSettle();

    // Verify that the login screen is displayed (now the initial screen)
    expect(find.text('Welcome Back'), findsOneWidget);
    expect(find.text('Sign in to continue your journey'), findsOneWidget);
  });
}
